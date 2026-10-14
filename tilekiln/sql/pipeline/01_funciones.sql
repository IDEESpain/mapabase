-- =============================================================================
-- Funciones ETL: carga / recorte / mezcla por clase / mosaicos / generalización
-- =============================================================================
-- Flujo por capa (lo orquesta tools/run_pipeline_sql.py, en paralelo por territorio):
--   ensure_capa_tables  → tablas vacías sin índices (carga masiva rápida)
--   (ogr2ogr + geom_carga por fichero)
--   finalizar_carga     → índices GiST/btree, ANALYZE y productor_resumen
--   build_servicio_nacional
--   procesar_territorio(regional, CCAA)   solo CCAA con productor propio
--   build_servicio_mosaico(regional)      generados + nacional fuera de esas CCAA
--   procesar_territorio(local, municipio) solo municipios con productor propio
--   build_servicio_mosaico(local)         generados + regional fuera de esos municipios
--   generalizar_capa                      tablas _gN para zooms bajos
-- procesar_capa_completa hace lo mismo en serie, para usarlo solo desde SQL.
-- =============================================================================

SET search_path TO public, public_modelo_2025, pg_catalog, mc_meta, mc_productores, mc_mascaras, mc_generados;

DROP FUNCTION IF EXISTS mc_meta.ensure_capa_tables(text, text[], text);
DROP FUNCTION IF EXISTS mc_meta.procesar_capa_regional(text);
DROP FUNCTION IF EXISTS mc_meta.procesar_capa_local(text);
DROP FUNCTION IF EXISTS mc_meta.build_servicio(text, text, text);

-- Covers(mask, geom) e Intersects reutilizan la máscara "preparada" entre filas;
-- CoveredBy(geom, mask) no, y con máscaras de miles de vértices es ~100 veces más lento.
-- Se usan _ST_Intersects/_ST_Covers (C) con && explícito: los envoltorios SQL de PostGIS
-- en CNIG apuntan a OPERATOR(public.&&), que dejó de existir al renombrar public.
CREATE OR REPLACE FUNCTION mc_meta.clip_geom(
	geom geometry,
	mask geometry,
	es_punto boolean DEFAULT false
) RETURNS geometry
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
	SELECT CASE
		WHEN geom IS NULL OR mask IS NULL THEN NULL
		WHEN es_punto THEN
			CASE WHEN geom && mask AND _ST_Intersects(geom, mask) THEN geom ELSE NULL END
		ELSE
			CASE
				WHEN NOT (geom && mask) THEN NULL
				WHEN _ST_Covers(mask, geom) THEN geom
				WHEN _ST_Intersects(geom, mask) THEN
					ST_CollectionExtract(
						ST_MakeValid(ST_Intersection(geom, mask)),
						GREATEST(ST_Dimension(geom), 0) + 1
					)
				ELSE NULL
			END
	END;
$$;

-- Las geometrías ya llegan válidas (geom_carga) y los recortes pasan por ST_MakeValid
-- en clip_geom, así que aquí solo se homogeneiza a Multi.
CREATE OR REPLACE FUNCTION mc_meta.normalize_geom(geom geometry)
RETURNS geometry
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
	SELECT CASE
		WHEN geom IS NULL OR ST_IsEmpty(geom) THEN NULL
		ELSE ST_Multi(geom)
	END;
$$;

-- Geometría de entrada desde ogr2ogr: 2D, Multi y válida (MakeValid solo si hace falta)
CREATE OR REPLACE FUNCTION mc_meta.geom_carga(g geometry)
RETURNS geometry
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
	SELECT CASE
		WHEN g IS NULL OR ST_IsEmpty(g) THEN NULL
		WHEN ST_IsValid(g) THEN ST_Multi(ST_Force2D(g))
		ELSE mc_meta.normalize_geom(ST_CollectionExtract(
			ST_MakeValid(ST_Force2D(g)),
			GREATEST(ST_Dimension(g), 0) + 1
		))
	END;
$$;

CREATE OR REPLACE FUNCTION mc_meta.attr_columns(p_capa text)
RETURNS text[]
LANGUAGE sql
STABLE
AS $$
	SELECT coalesce(
		(SELECT attrs FROM mc_meta.capas WHERE capa = p_capa),
		ARRAY['clase', 'proveedor']::text[]
	);
$$;

CREATE OR REPLACE FUNCTION mc_meta.servicio_schema(p_nivel text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
	SELECT CASE p_nivel
		WHEN 'nacional' THEN 'mc_servicio_nacional'
		WHEN 'regional' THEN 'mc_servicio_regional'
		WHEN 'local' THEN 'mc_servicio_local'
		ELSE NULL
	END;
$$;

-- Lista de columnas de atributos con prefijo opcional: ', a, b' o ', p.a, p.b'
CREATE OR REPLACE FUNCTION mc_meta.attr_sql(p_attrs text[], p_prefijo text DEFAULT '')
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
	SELECT coalesce(', ' || string_agg(p_prefijo || quote_ident(a), ', '), '')
	FROM unnest(p_attrs) AS a;
$$;

-- DROP de tabla o vista sin fallar por el tipo de relación
CREATE OR REPLACE FUNCTION mc_meta.drop_rel(p_schema text, p_name text)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	k "char";
BEGIN
	SELECT c.relkind INTO k
	  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
	 WHERE n.nspname = p_schema AND c.relname = p_name;
	IF k IS NULL THEN
		RETURN;
	ELSIF k = 'v' THEN
		EXECUTE format('DROP VIEW %I.%I CASCADE', p_schema, p_name);
	ELSIF k = 'm' THEN
		EXECUTE format('DROP MATERIALIZED VIEW %I.%I CASCADE', p_schema, p_name);
	ELSE
		EXECUTE format('DROP TABLE %I.%I CASCADE', p_schema, p_name);
	END IF;
END;
$$;

-- ---------------------------------------------------------------------------
-- DDL: tabla productora particionada por ambito + generados + servicio
-- Se crean SIN índices: finalizar_carga los construye cuando ya están los datos.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION mc_meta.ensure_servicio_table(
	p_capa text,
	p_nivel text,
	p_attrs text[]
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	sch text := mc_meta.servicio_schema(p_nivel);
	attr_cols text;
BEGIN
	SELECT coalesce(string_agg(format(', %I text', a), ''), '')
	INTO attr_cols FROM unnest(p_attrs) AS a;

	PERFORM mc_meta.drop_rel(sch, p_capa);
	EXECUTE format(
		'CREATE TABLE %I.%I (the_geom geometry(Geometry,3857)%s)',
		sch, p_capa, attr_cols
	);
	DELETE FROM mc_meta.servicio_link WHERE capa = p_capa AND nivel = p_nivel;
END;
$$;

CREATE OR REPLACE FUNCTION mc_meta.indexar_servicio(p_capa text, p_nivel text)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	sch text := mc_meta.servicio_schema(p_nivel);
BEGIN
	EXECUTE format(
		'CREATE INDEX IF NOT EXISTS %I ON %I.%I USING gist (the_geom)',
		left('sidx_svc_' || p_nivel || '_' || p_capa, 63), sch, p_capa
	);
	EXECUTE format('ANALYZE %I.%I', sch, p_capa);
END;
$$;

CREATE OR REPLACE FUNCTION mc_meta.ensure_capa_tables(
	p_capa text,
	p_attrs text[] DEFAULT NULL,
	p_perfil text DEFAULT 'normal',
	p_generalizar int[] DEFAULT '{}'
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	attrs text[];
	attr_cols text;
	perfil text;
	amb text;
BEGIN
	attrs := coalesce(p_attrs, ARRAY['clase', 'proveedor']);
	perfil := coalesce(NULLIF(p_perfil, ''), 'normal');
	IF perfil NOT IN ('ligera', 'normal', 'pesada') THEN
		RAISE EXCEPTION 'perfil inválido: %', perfil;
	END IF;

	SELECT coalesce(string_agg(format(', %I text', a), ''), '')
	INTO attr_cols FROM unnest(attrs) AS a;

	EXECUTE format('DROP TABLE IF EXISTS mc_productores.%I CASCADE', p_capa);
	EXECUTE format(
		'CREATE TABLE mc_productores.%I (
			the_geom geometry(Geometry,3857),
			ambito text NOT NULL,
			codigo text NOT NULL%s
		) PARTITION BY LIST (ambito)',
		p_capa, attr_cols
	);
	FOREACH amb IN ARRAY ARRAY['local', 'regional', 'nacional'] LOOP
		EXECUTE format(
			'CREATE TABLE mc_productores.%I PARTITION OF mc_productores.%I FOR VALUES IN (%L)',
			p_capa || '_' || amb, p_capa, amb
		);
	END LOOP;

	-- UNLOGGED: es intermedio y se regenera; evita escribir WAL
	EXECUTE format('DROP TABLE IF EXISTS mc_generados.%I CASCADE', p_capa);
	EXECUTE format(
		'CREATE UNLOGGED TABLE mc_generados.%I (
			the_geom geometry(Geometry,3857),
			ambito text NOT NULL,
			codigo text NOT NULL,
			nivel_origen text%s
		)',
		p_capa, attr_cols
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_generados.%I (ambito, codigo)',
		left('idx_gen_' || p_capa || '_ac', 63), p_capa
	);

	INSERT INTO mc_meta.capas (capa, tiene_clase, es_punto, perfil, purgar_generados, attrs, generalizar)
	VALUES (
		p_capa,
		'clase' = ANY (attrs),
		p_capa LIKE '%\_pto',
		perfil,
		perfil = 'pesada',
		attrs,
		coalesce(p_generalizar, '{}')
	)
	ON CONFLICT (capa) DO UPDATE SET
		tiene_clase = EXCLUDED.tiene_clase,
		es_punto = EXCLUDED.es_punto,
		perfil = EXCLUDED.perfil,
		purgar_generados = EXCLUDED.purgar_generados,
		attrs = EXCLUDED.attrs,
		generalizar = EXCLUDED.generalizar,
		updated_at = now();

	DELETE FROM mc_meta.servicio_link WHERE capa = p_capa;
	DELETE FROM mc_meta.productor_resumen WHERE capa = p_capa;

	-- Servicio vacío para que Tilekiln no falle mientras se procesa
	PERFORM mc_meta.ensure_servicio_table(p_capa, 'nacional', attrs);
	PERFORM mc_meta.link_servicio(p_capa, 'regional', 'nacional');
	PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
END;
$$;

-- Tras la carga masiva: índices, estadísticas y resumen por territorio
CREATE OR REPLACE FUNCTION mc_meta.finalizar_carga(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	tiene_clase boolean;
	amb text;
	part text;
	n_total bigint;
	n_terr bigint;
BEGIN
	SELECT c.tiene_clase INTO tiene_clase FROM mc_meta.capas c WHERE c.capa = p_capa;
	IF NOT FOUND THEN
		RAISE EXCEPTION 'capa % no registrada', p_capa;
	END IF;

	FOREACH amb IN ARRAY ARRAY['nacional', 'regional', 'local'] LOOP
		part := p_capa || '_' || amb;
		EXECUTE format(
			'CREATE INDEX IF NOT EXISTS %I ON mc_productores.%I USING gist (the_geom)',
			left('sidx_prod_' || part, 63), part
		);
		EXECUTE format(
			'CREATE INDEX IF NOT EXISTS %I ON mc_productores.%I (codigo%s)',
			left('idx_prod_' || part || '_cod', 63), part,
			CASE WHEN tiene_clase THEN ', clase' ELSE '' END
		);
	END LOOP;
	EXECUTE format('ANALYZE mc_productores.%I', p_capa);

	DELETE FROM mc_meta.productor_resumen WHERE capa = p_capa;
	EXECUTE format(
		'INSERT INTO mc_meta.productor_resumen (capa, ambito, codigo, n, clases)
		 SELECT %L, ambito, codigo, count(*), %s
		   FROM mc_productores.%I
		  GROUP BY ambito, codigo',
		p_capa,
		CASE WHEN tiene_clase
			THEN 'coalesce(array_agg(DISTINCT clase) FILTER (WHERE clase IS NOT NULL), ''{}'')'
			ELSE '''{}''::text[]'
		END,
		p_capa
	);

	SELECT coalesce(sum(n), 0), count(*) INTO n_total, n_terr
	  FROM mc_meta.productor_resumen WHERE capa = p_capa;
	RETURN format('productores=%s territorios=%s', n_total, n_terr);
END;
$$;

-- Sustituye un nivel de servicio por VIEW del nivel fuente (sin duplicar GB)
CREATE OR REPLACE FUNCTION mc_meta.link_servicio(
	p_capa text,
	p_nivel text,
	p_fuente text
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	sch text := mc_meta.servicio_schema(p_nivel);
	src text := mc_meta.servicio_schema(p_fuente);
BEGIN
	IF p_nivel = p_fuente THEN
		RAISE EXCEPTION 'link_servicio: nivel=fuente';
	END IF;
	PERFORM mc_meta.drop_rel(sch, p_capa);
	EXECUTE format(
		'CREATE VIEW %I.%I AS SELECT * FROM %I.%I',
		sch, p_capa, src, p_capa
	);
	INSERT INTO mc_meta.servicio_link (capa, nivel, fuente_nivel)
	VALUES (p_capa, p_nivel, p_fuente)
	ON CONFLICT (capa, nivel) DO UPDATE SET fuente_nivel = EXCLUDED.fuente_nivel;
END;
$$;


-- ---------------------------------------------------------------------------
-- Mezcla por clase (mun > CCAA > IGN) para un territorio
-- ---------------------------------------------------------------------------
-- Un productor "cubre" las clases que contiene en su territorio (como en el proceso
-- FGB, que mira el contenido de cada fichero). El último nivel de la cascada aporta
-- todas las clases que no haya cubierto nadie antes.
CREATE OR REPLACE FUNCTION mc_meta.mezcla_territorio(
	p_capa text,
	p_ambito_dest text,
	p_codigo text,
	p_mask geometry,
	p_cascade text[][]
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	es_punto boolean;
	tiene_clase boolean;
	attrs text[];
	nivel text;
	cod text;
	n_niveles int := coalesce(array_length(p_cascade, 1), 0);
	clases_cubiertas text[] := ARRAY[]::text[];
	clases_nivel text[];
	clases_tomar text[];
	n_ins bigint;
	total bigint := 0;
	detalle text[] := ARRAY[]::text[];
	sql_head text;
	sql_tail text := ') s WHERE s.g IS NOT NULL';
BEGIN
	SELECT c.es_punto, c.tiene_clase, c.attrs INTO es_punto, tiene_clase, attrs
	FROM mc_meta.capas c WHERE c.capa = p_capa;
	IF NOT FOUND THEN
		RETURN 'error:capa_no_registrada';
	END IF;

	EXECUTE format(
		'DELETE FROM mc_generados.%I WHERE ambito = %L AND codigo = %L',
		p_capa, p_ambito_dest, p_codigo
	);

	FOR i IN 1 .. n_niveles LOOP
		nivel := p_cascade[i][1];
		cod := p_cascade[i][2];
		IF cod IS NULL THEN
			detalle := detalle || (nivel || '@sin_codigo');
			CONTINUE;
		END IF;

		SELECT r.clases INTO clases_nivel
		  FROM mc_meta.productor_resumen r
		 WHERE r.capa = p_capa AND r.ambito = nivel AND r.codigo = cod;
		IF NOT FOUND THEN
			detalle := detalle || (nivel || '@sin_fuente');
			CONTINUE;
		END IF;

		sql_head := format(
			'INSERT INTO mc_generados.%1$I (the_geom, ambito, codigo, nivel_origen%2$s)
			 SELECT s.g, %3$L, %4$L, %5$L%6$s FROM (
				SELECT mc_meta.normalize_geom(mc_meta.clip_geom(p.the_geom, $1, $2)) AS g%7$s
				  FROM mc_productores.%8$I p
				 WHERE p.codigo = %9$L AND p.the_geom && $1',
			p_capa, mc_meta.attr_sql(attrs), p_ambito_dest, p_codigo, nivel,
			mc_meta.attr_sql(attrs, 's.'), mc_meta.attr_sql(attrs, 'p.'),
			p_capa || '_' || nivel, cod
		);

		IF NOT tiene_clase THEN
			EXECUTE sql_head || sql_tail USING p_mask, es_punto;
			GET DIAGNOSTICS n_ins = ROW_COUNT;
			total := total + n_ins;
			detalle := detalle || format('%s@capa_completa(%s)', nivel, n_ins);
			EXIT;
		END IF;

		IF i = n_niveles THEN
			EXECUTE sql_head || ' AND p.clase IS NOT NULL AND NOT (p.clase = ANY ($3))' || sql_tail
				USING p_mask, es_punto, clases_cubiertas;
			GET DIAGNOSTICS n_ins = ROW_COUNT;
			total := total + n_ins;
			detalle := detalle || format('%s[resto](%s)', nivel, n_ins);
			CONTINUE;
		END IF;

		SELECT coalesce(array_agg(x), ARRAY[]::text[]) INTO clases_tomar
		FROM unnest(clases_nivel) AS x WHERE NOT (x = ANY (clases_cubiertas));
		IF coalesce(array_length(clases_tomar, 1), 0) = 0 THEN
			detalle := detalle || (nivel || '@sin_clases_nuevas');
			CONTINUE;
		END IF;

		EXECUTE sql_head || ' AND p.clase = ANY ($3)' || sql_tail
			USING p_mask, es_punto, clases_tomar;
		GET DIAGNOSTICS n_ins = ROW_COUNT;
		IF n_ins > 0 THEN
			clases_cubiertas := clases_cubiertas || clases_tomar;
			total := total + n_ins;
			detalle := detalle || format('%s[%s](%s)', nivel, array_to_string(clases_tomar, ','), n_ins);
		ELSE
			detalle := detalle || (nivel || '@extract_vacio');
		END IF;
	END LOOP;

	RETURN format('rows=%s %s', total, array_to_string(detalle, ';'));
END;
$$;


-- ---------------------------------------------------------------------------
-- Territorios a procesar: solo los que tienen productor propio en ese nivel
-- (el resto se sirve directamente del nivel superior en build_servicio_mosaico).
-- Se devuelven de mayor a menor volumen para repartir mejor entre workers.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION mc_meta.territorios_pendientes(p_capa text, p_nivel text)
RETURNS SETOF text
LANGUAGE sql
STABLE
AS $$
	SELECT r.codigo
	  FROM mc_meta.productor_resumen r
	  JOIN mc_mascaras.voronoi_comunidades m ON m.codigo = r.codigo
	 WHERE p_nivel = 'regional' AND r.capa = p_capa AND r.ambito = 'regional'
	UNION ALL
	SELECT r.codigo
	  FROM mc_meta.productor_resumen r
	  JOIN mc_mascaras.voronoi_municipios m ON m.codigo = r.codigo
	  LEFT JOIN mc_meta.territorios_municipio t ON t.codigo = r.codigo
	  LEFT JOIN mc_meta.estrategia_ccaa e ON e.codigo_ccaa = coalesce(t.codigo_ccaa, m.codigo_ccaa)
	 WHERE p_nivel = 'local' AND r.capa = p_capa AND r.ambito = 'local'
	   AND coalesce(e.modo, '') <> 'use_ccaa_source_for_union'
	 ORDER BY 1;
$$;

CREATE OR REPLACE FUNCTION mc_meta.territorios_pendientes_ordenados(p_capa text, p_nivel text)
RETURNS TABLE (codigo text, n bigint)
LANGUAGE sql
STABLE
AS $$
	SELECT t.codigo, r.n
	  FROM mc_meta.territorios_pendientes(p_capa, p_nivel) AS t(codigo)
	  JOIN mc_meta.productor_resumen r
	    ON r.capa = p_capa AND r.ambito = p_nivel AND r.codigo = t.codigo
	 ORDER BY r.n DESC, t.codigo;
$$;

-- Productores cuyo código no casa con ninguna máscara (se ignorarían sin avisar)
CREATE OR REPLACE FUNCTION mc_meta.codigos_sin_mascara(p_capa text, p_nivel text)
RETURNS SETOF text
LANGUAGE sql
STABLE
AS $$
	SELECT r.codigo
	  FROM mc_meta.productor_resumen r
	 WHERE r.capa = p_capa AND r.ambito = p_nivel
	   AND NOT EXISTS (
		SELECT 1 FROM mc_mascaras.voronoi_comunidades m
		 WHERE p_nivel = 'regional' AND m.codigo = r.codigo
		UNION ALL
		SELECT 1 FROM mc_mascaras.voronoi_municipios m
		 WHERE p_nivel = 'local' AND m.codigo = r.codigo
	   )
	 ORDER BY 1;
$$;

CREATE OR REPLACE FUNCTION mc_meta.procesar_territorio(
	p_capa text,
	p_nivel text,
	p_codigo text
)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	mask geometry;
	ccaa text;
BEGIN
	IF p_nivel = 'regional' THEN
		SELECT m.the_geom INTO mask
		  FROM mc_mascaras.voronoi_comunidades m WHERE m.codigo = p_codigo;
		IF mask IS NULL THEN
			RETURN 'sin_mascara';
		END IF;
		RETURN mc_meta.mezcla_territorio(
			p_capa, 'regional', p_codigo, mask,
			ARRAY[ARRAY['regional', p_codigo], ARRAY['nacional', '00']]
		);
	ELSIF p_nivel = 'local' THEN
		SELECT m.the_geom, coalesce(t.codigo_ccaa, m.codigo_ccaa) INTO mask, ccaa
		  FROM mc_mascaras.voronoi_municipios m
		  LEFT JOIN mc_meta.territorios_municipio t ON t.codigo = m.codigo
		 WHERE m.codigo = p_codigo;
		IF mask IS NULL THEN
			RETURN 'sin_mascara';
		END IF;
		RETURN mc_meta.mezcla_territorio(
			p_capa, 'local', p_codigo, mask,
			ARRAY[ARRAY['local', p_codigo], ARRAY['regional', ccaa], ARRAY['nacional', '00']]
		);
	END IF;
	RAISE EXCEPTION 'procesar_territorio: nivel % no válido', p_nivel;
END;
$$;


-- ---------------------------------------------------------------------------
-- Mosaicos de servicio
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION mc_meta.build_servicio_nacional(p_capa text)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
	attrs text[] := mc_meta.attr_columns(p_capa);
	n bigint;
BEGIN
	PERFORM mc_meta.ensure_servicio_table(p_capa, 'nacional', attrs);
	-- ORDER BY the_geom deja juntas en disco las geometrías cercanas:
	-- cada tesela lee muchas menos páginas
	EXECUTE format(
		'INSERT INTO mc_servicio_nacional.%1$I (the_geom%2$s)
		 SELECT src.the_geom%3$s FROM mc_productores.%4$I src
		  WHERE src.codigo = ''00'' AND src.the_geom IS NOT NULL
		  ORDER BY src.the_geom',
		p_capa, mc_meta.attr_sql(attrs), mc_meta.attr_sql(attrs, 'src.'), p_capa || '_nacional'
	);
	GET DIAGNOSTICS n = ROW_COUNT;
	PERFORM mc_meta.indexar_servicio(p_capa, 'nacional');
	-- Las vistas dependientes caen con el DROP de la tabla nacional
	PERFORM mc_meta.link_servicio(p_capa, 'regional', 'nacional');
	PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
	RETURN n;
END;
$$;

-- Mosaico regional (o local) = generados de los territorios procesados
--                            + nivel superior fuera de esos territorios.
-- Si no se procesó ningún territorio, el nivel es una VIEW del superior.
CREATE OR REPLACE FUNCTION mc_meta.build_servicio_mosaico(p_capa text, p_nivel text)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
	attrs text[] := mc_meta.attr_columns(p_capa);
	sch text := mc_meta.servicio_schema(p_nivel);
	src_nivel text := CASE p_nivel WHEN 'regional' THEN 'nacional' WHEN 'local' THEN 'regional' END;
	mask_tbl text := CASE p_nivel WHEN 'regional' THEN 'voronoi_comunidades' WHEN 'local' THEN 'voronoi_municipios' END;
	es_punto boolean;
	hay boolean;
	n bigint;
BEGIN
	IF src_nivel IS NULL THEN
		RAISE EXCEPTION 'build_servicio_mosaico: nivel % no válido', p_nivel;
	END IF;
	SELECT c.es_punto INTO es_punto FROM mc_meta.capas c WHERE c.capa = p_capa;

	EXECUTE format('SELECT EXISTS (SELECT 1 FROM mc_generados.%I WHERE ambito = %L)', p_capa, p_nivel)
	INTO hay;
	IF NOT hay THEN
		PERFORM mc_meta.link_servicio(p_capa, p_nivel, src_nivel);
		IF p_nivel = 'regional' THEN
			PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
		END IF;
		RETURN 0;
	END IF;

	-- Máscaras de los territorios procesados troceadas: el test "¿está dentro?" usa índice
	DROP TABLE IF EXISTS pg_temp._mc_mask;
	EXECUTE format(
		'CREATE TEMP TABLE _mc_mask AS
		 SELECT ST_Subdivide(m.the_geom, 256) AS g
		   FROM mc_mascaras.%I m
		  WHERE m.codigo IN (SELECT DISTINCT codigo FROM mc_generados.%I WHERE ambito = %L)',
		mask_tbl, p_capa, p_nivel
	);
	EXECUTE 'CREATE INDEX ON pg_temp._mc_mask USING gist (g)';
	EXECUTE 'ANALYZE pg_temp._mc_mask';

	PERFORM mc_meta.ensure_servicio_table(p_capa, p_nivel, attrs);
	EXECUTE format(
		$f$
		INSERT INTO %1$I.%2$I (the_geom%3$s)
		SELECT q.g%4$s FROM (
			SELECT gen.the_geom AS g%5$s
			  FROM mc_generados.%2$I gen
			 WHERE gen.ambito = %6$L AND gen.the_geom IS NOT NULL
			UNION ALL
			SELECT CASE
				WHEN NOT EXISTS (
					SELECT 1 FROM pg_temp._mc_mask k
					 WHERE k.g && s.the_geom AND _ST_Intersects(k.g, s.the_geom)
				) THEN s.the_geom
				WHEN %7$L::boolean THEN NULL
				ELSE (
					SELECT mc_meta.normalize_geom(ST_CollectionExtract(
						ST_MakeValid(ST_Difference(s.the_geom, ST_Union(k.g))),
						GREATEST(ST_Dimension(s.the_geom), 0) + 1
					))
					  FROM pg_temp._mc_mask k
					 WHERE k.g && s.the_geom
				)
			END AS g%8$s
			  FROM %9$I.%2$I s
		) q
		WHERE q.g IS NOT NULL AND NOT ST_IsEmpty(q.g)
		ORDER BY q.g
		$f$,
		sch, p_capa, mc_meta.attr_sql(attrs), mc_meta.attr_sql(attrs, 'q.'),
		mc_meta.attr_sql(attrs, 'gen.'), p_nivel, es_punto,
		mc_meta.attr_sql(attrs, 's.'), mc_meta.servicio_schema(src_nivel)
	);
	GET DIAGNOSTICS n = ROW_COUNT;
	DROP TABLE IF EXISTS pg_temp._mc_mask;

	PERFORM mc_meta.indexar_servicio(p_capa, p_nivel);
	IF p_nivel = 'regional' THEN
		PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
	END IF;
	RETURN n;
END;
$$;


-- ---------------------------------------------------------------------------
-- Generalización para zooms bajos (peso de tesela y tiempo de render)
-- ---------------------------------------------------------------------------
-- mc_servicio_nacional.{capa}_g{z} sirve los zooms <= z. Tolerancia en unidades
-- Web Mercator de un píxel de pantalla (tesela de 256 px) en ese zoom:
--   simplificación = 1/4 px, se descartan polígonos < (1/2 px)^2 y líneas < 1/2 px.
-- Diferencias por debajo de medio píxel no se ven, pero pesan en la tesela.
CREATE OR REPLACE FUNCTION mc_meta.generalizar_capa(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	attrs text[] := mc_meta.attr_columns(p_capa);
	zs int[];
	es_punto boolean;
	z int;
	px float8;
	tabla text;
	n bigint;
	detalle text[] := ARRAY[]::text[];
BEGIN
	SELECT c.generalizar, c.es_punto INTO zs, es_punto FROM mc_meta.capas c WHERE c.capa = p_capa;
	FOR z IN 0 .. 13 LOOP
		PERFORM mc_meta.drop_rel('mc_servicio_nacional', p_capa || '_g' || z);
	END LOOP;
	IF es_punto OR coalesce(array_length(zs, 1), 0) = 0 THEN
		RETURN 'sin_generalizar';
	END IF;

	FOREACH z IN ARRAY zs LOOP
		px := 40075016.68557849 / (2 ^ z) / 256.0;
		tabla := p_capa || '_g' || z;
		EXECUTE format(
			$f$
			CREATE TABLE mc_servicio_nacional.%1$I AS
			SELECT q.g AS the_geom%2$s FROM (
				SELECT mc_meta.normalize_geom(ST_SimplifyPreserveTopology(s.the_geom, %3$s)) AS g%4$s
				  FROM mc_servicio_nacional.%5$I s
				 WHERE CASE ST_Dimension(s.the_geom)
						WHEN 2 THEN ST_Area(s.the_geom) >= %6$s
						WHEN 1 THEN ST_Length(s.the_geom) >= %7$s
						ELSE true
					END
			) q
			WHERE q.g IS NOT NULL AND NOT ST_IsEmpty(q.g)
			ORDER BY q.g
			$f$,
			tabla, mc_meta.attr_sql(attrs, 'q.'), px / 4, mc_meta.attr_sql(attrs, 's.'),
			p_capa, (px / 2) ^ 2, px / 2
		);
		GET DIAGNOSTICS n = ROW_COUNT;
		EXECUTE format(
			'CREATE INDEX %I ON mc_servicio_nacional.%I USING gist (the_geom)',
			left('sidx_svc_nacional_' || tabla, 63), tabla
		);
		EXECUTE format('ANALYZE mc_servicio_nacional.%I', tabla);
		detalle := detalle || format('g%s=%s', z, n);
	END LOOP;
	RETURN array_to_string(detalle, ' ');
END;
$$;

-- Tablas de servicio vacías para las capas aún no cargadas: Tilekiln consulta todas
-- las capas en cada tesela y falla si falta alguna. No toca las que ya existen.
CREATE OR REPLACE FUNCTION mc_meta.asegurar_servicio_vacio(
	p_capa text,
	p_attrs text[],
	p_generalizar int[] DEFAULT '{}'
)
RETURNS int
LANGUAGE plpgsql
AS $$
DECLARE
	attr_cols text;
	tabla text;
	sch text;
	z int;
	n int := 0;
BEGIN
	SELECT coalesce(string_agg(format(', %I text', a), ''), '')
	INTO attr_cols FROM unnest(p_attrs) AS a;
	FOR sch, tabla IN
		SELECT s, p_capa FROM unnest(ARRAY['mc_servicio_nacional', 'mc_servicio_regional', 'mc_servicio_local']) AS s
		UNION ALL
		SELECT 'mc_servicio_nacional', p_capa || '_g' || g FROM unnest(coalesce(p_generalizar, '{}')) AS g
	LOOP
		IF to_regclass(format('%I.%I', sch, tabla)) IS NULL THEN
			EXECUTE format('CREATE TABLE %I.%I (the_geom geometry(Geometry,3857)%s)', sch, tabla, attr_cols);
			EXECUTE format(
				'CREATE INDEX %I ON %I.%I USING gist (the_geom)',
				left('sidx_' || sch || '_' || tabla, 63), sch, tabla
			);
			n := n + 1;
		END IF;
	END LOOP;
	RETURN n;
END;
$$;

CREATE OR REPLACE FUNCTION mc_meta.purgar_generados(p_capa text)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
	purgar boolean;
BEGIN
	SELECT c.purgar_generados INTO purgar FROM mc_meta.capas c WHERE c.capa = p_capa;
	IF coalesce(purgar, false) THEN
		EXECUTE format('TRUNCATE mc_generados.%I', p_capa);
		RETURN true;
	END IF;
	RETURN false;
END;
$$;


-- Versión en serie de todo el procesado (para lanzarlo desde psql).
-- Desde Python es preferible run_pipeline_sql.py: paraleliza y confirma por territorio.
CREATE OR REPLACE FUNCTION mc_meta.procesar_capa_completa(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	cod text;
	n_nac bigint;
	n_reg bigint;
	n_loc bigint;
	t_reg int := 0;
	t_loc int := 0;
	gen text;
	msg text;
	t0 timestamptz := clock_timestamp();
	rid bigint;
BEGIN
	INSERT INTO mc_meta.run_log (capa, fase, detalle)
	VALUES (p_capa, 'completa', 'start') RETURNING id INTO rid;

	EXECUTE format('TRUNCATE mc_generados.%I', p_capa);
	n_nac := mc_meta.build_servicio_nacional(p_capa);

	FOR cod IN SELECT codigo FROM mc_meta.territorios_pendientes_ordenados(p_capa, 'regional') LOOP
		PERFORM mc_meta.procesar_territorio(p_capa, 'regional', cod);
		t_reg := t_reg + 1;
	END LOOP;
	n_reg := mc_meta.build_servicio_mosaico(p_capa, 'regional');

	FOR cod IN SELECT codigo FROM mc_meta.territorios_pendientes_ordenados(p_capa, 'local') LOOP
		PERFORM mc_meta.procesar_territorio(p_capa, 'local', cod);
		t_loc := t_loc + 1;
	END LOOP;
	n_loc := mc_meta.build_servicio_mosaico(p_capa, 'local');

	gen := mc_meta.generalizar_capa(p_capa);
	PERFORM mc_meta.purgar_generados(p_capa);

	msg := format(
		'nacional=%s regional=%s (ccaa=%s) local=%s (mun=%s) %s elapsed=%s',
		n_nac, n_reg, t_reg, n_loc, t_loc, gen, clock_timestamp() - t0
	);
	UPDATE mc_meta.run_log
	   SET finished_at = clock_timestamp(), ok = true, detalle = msg
	 WHERE id = rid;
	RETURN msg;
EXCEPTION WHEN OTHERS THEN
	UPDATE mc_meta.run_log
	   SET finished_at = clock_timestamp(), ok = false, detalle = SQLERRM
	 WHERE id = rid;
	RAISE;
END;
$$;

-- Perfiles sugeridos: "pesada" vacía mc_generados al terminar la capa
CREATE OR REPLACE FUNCTION mc_meta.sugerir_perfil(p_capa text)
RETURNS text
LANGUAGE sql
IMMUTABLE
AS $$
	SELECT CASE
		WHEN p_capa IN (
			'altimetria_lin', 'altimetria_pto',
			'cubierta_vegetal_pol', 'cubierta_vegetal_bosque_pol',
			'hidrografia_lin', 'hidrografia_pol',
			'lamina_agua_pol', 'via_urbana_lin',
			'edificio_pol', 'construccion_pol', 'construccion_lin'
		) THEN 'pesada'
		WHEN p_capa LIKE 'contexto_%' THEN 'pesada'
		WHEN p_capa LIKE 'nombre_%' THEN 'ligera'
		ELSE 'normal'
	END;
$$;
