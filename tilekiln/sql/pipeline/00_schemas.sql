-- =============================================================================
-- Mapa Ciudadano · Pipeline PostGIS (equiv. Proceso 3 + consumo Proceso 4)
-- =============================================================================
-- Equivalencia FGB:
--   productores/{mun,com_aut,nacional}  → mc_productores.{capa}  PARTITION BY ambito
--   voronoi_*.fgb                       → mc_mascaras.*
--   generados/mun|ccaa                  → mc_generados.{capa}    (staging UNLOGGED)
--   productores/nacional/00             → mc_servicio_nacional   → Tilekiln z0–13
--   nacional/comunidades/00             → mc_servicio_regional   → Tilekiln z14–16
--   nacional/municipios/00              → mc_servicio_local      → Tilekiln z17+
--
-- Idempotente: se puede aplicar en cada ejecución sin perder capas ya procesadas.
-- Para empezar de cero: 00_reset.sql (o run_pipeline_sql.py --reset).
-- =============================================================================

-- PostGIS ya instalado por CNIG en public_modelo_2025. Ese esquema no se modifica:
-- solo se incluye en search_path para resolver el tipo geometry.
SET search_path TO public, public_modelo_2025, pg_catalog;

CREATE SCHEMA IF NOT EXISTS mc_meta;
CREATE SCHEMA IF NOT EXISTS mc_productores;
CREATE SCHEMA IF NOT EXISTS mc_mascaras;
CREATE SCHEMA IF NOT EXISTS mc_staging;             -- tablas temporales de ogr2ogr
CREATE SCHEMA IF NOT EXISTS mc_generados;           -- recortes por territorio (se puede vaciar)
CREATE SCHEMA IF NOT EXISTS mc_servicio_nacional;   -- mosaico IGN        z0–13
CREATE SCHEMA IF NOT EXISTS mc_servicio_regional;   -- mosaico CCAA       z14–16
CREATE SCHEMA IF NOT EXISTS mc_servicio_local;      -- mosaico municipios z17+

COMMENT ON SCHEMA mc_productores IS 'Productores crudos (FGB proceso 2). Tablas particionadas por ambito.';
COMMENT ON SCHEMA mc_staging IS 'Carga intermedia de ogr2ogr. Se vacía tras cada fichero.';
COMMENT ON SCHEMA mc_generados IS 'Recorte/mezcla por territorio con productor propio (UNLOGGED).';
COMMENT ON SCHEMA mc_servicio_nacional IS 'Equiv. productores/nacional/00 — Tilekiln z0-13 (+ tablas _gN generalizadas)';
COMMENT ON SCHEMA mc_servicio_regional IS 'Equiv. generados/nacional/comunidades/00 — Tilekiln z14-16';
COMMENT ON SCHEMA mc_servicio_local IS 'Equiv. generados/nacional/municipios/00 — Tilekiln z17+';

-- ---------------------------------------------------------------------------
-- Catálogo
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mc_meta.capas (
	capa text PRIMARY KEY,
	tiene_clase boolean NOT NULL DEFAULT true,
	es_punto boolean NOT NULL DEFAULT false,
	perfil text NOT NULL DEFAULT 'normal'
		CHECK (perfil IN ('ligera', 'normal', 'pesada')),
	-- tras construir los mosaicos, vaciar mc_generados (ahorra disco en capas grandes)
	purgar_generados boolean NOT NULL DEFAULT false,
	attrs text[] NOT NULL DEFAULT ARRAY['clase', 'proveedor'],
	notas text,
	updated_at timestamptz NOT NULL DEFAULT now()
);
-- Zooms con tabla generalizada mc_servicio_nacional.{capa}_g{z} (vacío = sin generalizar)
ALTER TABLE mc_meta.capas ADD COLUMN IF NOT EXISTS generalizar int[] NOT NULL DEFAULT '{}';

CREATE TABLE IF NOT EXISTS mc_meta.zoom_bands (
	nivel text PRIMARY KEY CHECK (nivel IN ('nacional', 'regional', 'local')),
	minzoom int NOT NULL,
	maxzoom int NOT NULL,
	schema_servicio text NOT NULL,
	equiv_fgb text NOT NULL
);

INSERT INTO mc_meta.zoom_bands (nivel, minzoom, maxzoom, schema_servicio, equiv_fgb) VALUES
	('nacional', 0, 13, 'mc_servicio_nacional', 'productores/nacional/00/'),
	('regional', 14, 16, 'mc_servicio_regional', 'generados/nacional/comunidades/00/'),
	('local', 17, 22, 'mc_servicio_local', 'generados/nacional/municipios/00/')
ON CONFLICT (nivel) DO NOTHING;

CREATE TABLE IF NOT EXISTS mc_meta.territorios_ccaa (
	codigo text PRIMARY KEY,
	nombre text
);

CREATE TABLE IF NOT EXISTS mc_meta.territorios_municipio (
	codigo text PRIMARY KEY,
	nombre text,
	codigo_ccaa text NOT NULL REFERENCES mc_meta.territorios_ccaa(codigo)
);
CREATE INDEX IF NOT EXISTS idx_mun_ccaa ON mc_meta.territorios_municipio (codigo_ccaa);

CREATE TABLE IF NOT EXISTS mc_meta.estrategia_ccaa (
	codigo_ccaa text PRIMARY KEY REFERENCES mc_meta.territorios_ccaa(codigo),
	modo text NOT NULL CHECK (modo IN (
		'individual_municipal_processing',
		'use_ccaa_source_for_union'
	)),
	detalle text
);

-- Si regional/local no aportan detalle, se sirven como VIEW del nivel superior
CREATE TABLE IF NOT EXISTS mc_meta.servicio_link (
	capa text NOT NULL REFERENCES mc_meta.capas(capa) ON DELETE CASCADE,
	nivel text NOT NULL CHECK (nivel IN ('regional', 'local')),
	fuente_nivel text NOT NULL CHECK (fuente_nivel IN ('nacional', 'regional', 'local')),
	PRIMARY KEY (capa, nivel)
);

-- Resumen de productores por territorio: evita recorrer las tablas grandes en cada mezcla
CREATE TABLE IF NOT EXISTS mc_meta.productor_resumen (
	capa text NOT NULL,
	ambito text NOT NULL,
	codigo text NOT NULL,
	n bigint NOT NULL,
	clases text[] NOT NULL DEFAULT '{}',
	PRIMARY KEY (capa, ambito, codigo)
);

CREATE TABLE IF NOT EXISTS mc_meta.run_log (
	id bigserial PRIMARY KEY,
	capa text,
	fase text,
	detalle text,
	started_at timestamptz NOT NULL DEFAULT now(),
	finished_at timestamptz,
	ok boolean
);
CREATE INDEX IF NOT EXISTS idx_run_log_capa ON mc_meta.run_log (capa, fase, id);

-- ---------------------------------------------------------------------------
-- Máscaras Voronoi (EPSG:3857)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mc_mascaras.voronoi_comunidades (
	codigo text PRIMARY KEY,
	the_geom geometry(Geometry, 3857) NOT NULL
);
CREATE INDEX IF NOT EXISTS sidx_voronoi_ccaa ON mc_mascaras.voronoi_comunidades USING gist (the_geom);

CREATE TABLE IF NOT EXISTS mc_mascaras.voronoi_municipios (
	codigo text PRIMARY KEY,
	codigo_ccaa text,
	the_geom geometry(Geometry, 3857) NOT NULL
);
ALTER TABLE mc_mascaras.voronoi_municipios ALTER COLUMN codigo_ccaa DROP NOT NULL;
CREATE INDEX IF NOT EXISTS sidx_voronoi_mun ON mc_mascaras.voronoi_municipios USING gist (the_geom);
CREATE INDEX IF NOT EXISTS idx_voronoi_mun_ccaa ON mc_mascaras.voronoi_municipios (codigo_ccaa);
