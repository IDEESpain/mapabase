-- =============================================================================
-- Mapa Ciudadano · Pipeline PostGIS (equiv. Proceso 3 + consumo Proceso 4)
-- Remodelado para capas pesadas (millones de registros / decenas de GB)
-- =============================================================================
-- Equivalencia FGB:
--   productores/{mun,com_aut,nacional}  → mc_productores.{capa}  PARTITION BY ambito
--   voronoi_*.fgb                       → mc_mascaras.*
--   generados/mun|ccaa                  → mc_generados.{capa}    (staging; opcional)
--   nacional/comunidades/00             → mc_servicio_regional   → Tilekiln z14–16
--   nacional/municipios/00              → mc_servicio_local      → Tilekiln z17+
--   productores/nacional/00             → mc_servicio_nacional   → Tilekiln z0–13
-- =============================================================================

-- PostGIS ya instalado por CNIG (p. ej. en public_modelo_2025). No tocar ese esquema:
-- solo incluirlo en search_path para resolver el tipo geometry (lectura de tipos, sin DDL ahí).
-- Tablas y funciones del pipeline van en mc_*; public queda libre para uso acordado.
SET search_path TO public, public_modelo_2025, pg_catalog;

-- Limpieza controlada de schemas del pipeline (no toca tilekiln/public OSM)
DROP SCHEMA IF EXISTS mc_generados CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_local CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_regional CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_nacional CASCADE;
DROP SCHEMA IF EXISTS mc_productores CASCADE;
DROP SCHEMA IF EXISTS mc_mascaras CASCADE;
DROP SCHEMA IF EXISTS mc_meta CASCADE;

-- Schema legado de la primera prueba (84 tablas planas): fuera del diseño
DROP SCHEMA IF EXISTS mapa_ciudadano CASCADE;

CREATE SCHEMA mc_meta;
CREATE SCHEMA mc_productores;
CREATE SCHEMA mc_mascaras;
CREATE SCHEMA mc_generados;           -- staging de recortes (se puede vaciar tras unión)
CREATE SCHEMA mc_servicio_nacional;   -- mosaico IGN        z0–13
CREATE SCHEMA mc_servicio_regional;   -- mosaico CCAA       z14–16
CREATE SCHEMA mc_servicio_local;      -- mosaico municipios z17+

COMMENT ON SCHEMA mc_productores IS 'Productores crudos (FGB proceso 2). Tablas particionadas por ambito.';
COMMENT ON SCHEMA mc_generados IS 'Staging recorte/mezcla por territorio. En capas pesadas: solo CCAA o vacío.';
COMMENT ON SCHEMA mc_servicio_nacional IS 'Equiv. productores/nacional/00 — Tilekiln z0-13';
COMMENT ON SCHEMA mc_servicio_regional IS 'Equiv. generados/nacional/comunidades/00 — Tilekiln z14-16';
COMMENT ON SCHEMA mc_servicio_local IS 'Equiv. generados/nacional/municipios/00 — Tilekiln z17+';

-- ---------------------------------------------------------------------------
-- Catálogo
-- ---------------------------------------------------------------------------
CREATE TABLE mc_meta.capas (
	capa text PRIMARY KEY,
	tiene_clase boolean NOT NULL DEFAULT true,
	es_punto boolean NOT NULL DEFAULT false,
	-- ligera: flujo completo mun; normal: completo; pesada: evita mun y materialización extra
	perfil text NOT NULL DEFAULT 'normal'
		CHECK (perfil IN ('ligera', 'normal', 'pesada')),
	-- tras build_servicio, vaciar mc_generados (ahorra disco en capas grandes)
	purgar_generados boolean NOT NULL DEFAULT false,
	attrs text[] NOT NULL DEFAULT ARRAY['clase', 'proveedor'],
	notas text,
	updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE mc_meta.zoom_bands (
	nivel text PRIMARY KEY CHECK (nivel IN ('nacional', 'regional', 'local')),
	minzoom int NOT NULL,
	maxzoom int NOT NULL,
	schema_servicio text NOT NULL,
	equiv_fgb text NOT NULL
);

INSERT INTO mc_meta.zoom_bands (nivel, minzoom, maxzoom, schema_servicio, equiv_fgb) VALUES
	('nacional', 0, 13, 'mc_servicio_nacional', 'productores/nacional/00/'),
	('regional', 14, 16, 'mc_servicio_regional', 'generados/nacional/comunidades/00/'),
	('local', 17, 22, 'mc_servicio_local', 'generados/nacional/municipios/00/');

CREATE TABLE mc_meta.territorios_ccaa (
	codigo text PRIMARY KEY,
	nombre text
);

CREATE TABLE mc_meta.territorios_municipio (
	codigo text PRIMARY KEY,
	nombre text,
	codigo_ccaa text NOT NULL REFERENCES mc_meta.territorios_ccaa(codigo)
);
CREATE INDEX idx_mun_ccaa ON mc_meta.territorios_municipio (codigo_ccaa);

CREATE TABLE mc_meta.estrategia_ccaa (
	codigo_ccaa text PRIMARY KEY REFERENCES mc_meta.territorios_ccaa(codigo),
	modo text NOT NULL CHECK (modo IN (
		'individual_municipal_processing',
		'use_ccaa_source_for_union'
	)),
	detalle text
);

-- Enlace de servicio: si regional/local no aportan detalle, se sirven como VIEW del nivel superior
CREATE TABLE mc_meta.servicio_link (
	capa text NOT NULL REFERENCES mc_meta.capas(capa) ON DELETE CASCADE,
	nivel text NOT NULL CHECK (nivel IN ('regional', 'local')),
	fuente_nivel text NOT NULL CHECK (fuente_nivel IN ('nacional', 'regional', 'local')),
	PRIMARY KEY (capa, nivel)
);

CREATE TABLE mc_meta.run_log (
	id bigserial PRIMARY KEY,
	capa text,
	fase text,
	detalle text,
	started_at timestamptz NOT NULL DEFAULT now(),
	finished_at timestamptz,
	ok boolean
);

-- ---------------------------------------------------------------------------
-- Máscaras Voronoi (EPSG:3857)
-- ---------------------------------------------------------------------------
CREATE TABLE mc_mascaras.voronoi_comunidades (
	codigo text PRIMARY KEY,
	the_geom geometry(Geometry, 3857) NOT NULL
);
CREATE INDEX sidx_voronoi_ccaa ON mc_mascaras.voronoi_comunidades USING gist (the_geom);

CREATE TABLE mc_mascaras.voronoi_municipios (
	codigo text PRIMARY KEY,
	codigo_ccaa text NOT NULL,
	the_geom geometry(Geometry, 3857) NOT NULL
);
CREATE INDEX sidx_voronoi_mun ON mc_mascaras.voronoi_municipios USING gist (the_geom);
CREATE INDEX idx_voronoi_mun_ccaa ON mc_mascaras.voronoi_municipios (codigo_ccaa);
