-- =============================================================================
-- Funciones ETL: clip / mezcla / unión / perfiles pesados
-- =============================================================================

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
			CASE WHEN geom && mask AND ST_Intersects(geom, mask) THEN geom ELSE NULL END
		ELSE
			CASE
				WHEN NOT (geom && mask) THEN NULL
				WHEN ST_CoveredBy(geom, mask) THEN geom
				WHEN ST_Intersects(geom, mask) THEN
					ST_CollectionExtract(
						ST_MakeValid(ST_Intersection(geom, mask)),
						GREATEST(ST_Dimension(geom), 0) + 1
					)
				ELSE NULL
			END
	END;
$$;

CREATE OR REPLACE FUNCTION mc_meta.normalize_geom(geom geometry)
RETURNS geometry
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
	SELECT CASE
		WHEN geom IS NULL OR ST_IsEmpty(geom) THEN NULL
		ELSE ST_Multi(ST_MakeValid(geom))
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

-- ---------------------------------------------------------------------------
-- DDL: tabla productora particionada por ambito + generados + servicio
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION mc_meta.ensure_capa_tables(
	p_capa text,
	p_attrs text[] DEFAULT NULL,
	p_perfil text DEFAULT 'normal'
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
	attrs text[];
	attr_cols text;
	perfil text;
	purgar boolean;
BEGIN
	attrs := coalesce(p_attrs, ARRAY['clase', 'proveedor']);
	perfil := coalesce(NULLIF(p_perfil, ''), 'normal');
	IF perfil NOT IN ('ligera', 'normal', 'pesada') THEN
		RAISE EXCEPTION 'perfil inválido: %', perfil;
	END IF;
	purgar := (perfil = 'pesada');

	SELECT coalesce(string_agg(format('%I text', a), ', '), '')
	INTO attr_cols FROM unnest(attrs) AS a;

	-- Productores: PARTITION BY LIST (ambito)
	EXECUTE format('DROP TABLE IF EXISTS mc_productores.%I CASCADE', p_capa);
	EXECUTE format(
		'CREATE TABLE mc_productores.%I (
			the_geom geometry(Geometry,3857),
			ambito text NOT NULL,
			codigo text NOT NULL%s%s
		) PARTITION BY LIST (ambito)',
		p_capa,
		CASE WHEN attr_cols = '' THEN '' ELSE ', ' END,
		attr_cols
	);
	EXECUTE format(
		'CREATE TABLE mc_productores.%I_local PARTITION OF mc_productores.%I FOR VALUES IN (''local'')',
		p_capa, p_capa
	);
	EXECUTE format(
		'CREATE TABLE mc_productores.%I_regional PARTITION OF mc_productores.%I FOR VALUES IN (''regional'')',
		p_capa, p_capa
	);
	EXECUTE format(
		'CREATE TABLE mc_productores.%I_nacional PARTITION OF mc_productores.%I FOR VALUES IN (''nacional'')',
		p_capa, p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_productores.%I_local USING gist (the_geom)',
		'sidx_prod_' || p_capa || '_loc', p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_productores.%I_regional USING gist (the_geom)',
		'sidx_prod_' || p_capa || '_reg', p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_productores.%I_nacional USING gist (the_geom)',
		'sidx_prod_' || p_capa || '_nac', p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_productores.%I_local (codigo)',
		'idx_prod_' || p_capa || '_loc_cod', p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_productores.%I_regional (codigo)',
		'idx_prod_' || p_capa || '_reg_cod', p_capa
	);

	-- Generados (staging, heap simple — se puede purgar)
	EXECUTE format('DROP TABLE IF EXISTS mc_generados.%I CASCADE', p_capa);
	EXECUTE format(
		'CREATE TABLE mc_generados.%I (
			the_geom geometry(Geometry,3857),
			ambito text NOT NULL,
			codigo text NOT NULL,
			nivel_origen text%s%s
		)',
		p_capa,
		CASE WHEN attr_cols = '' THEN '' ELSE ', ' END,
		attr_cols
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_generados.%I USING gist (the_geom)',
		'sidx_gen_' || p_capa, p_capa
	);
	EXECUTE format(
		'CREATE INDEX %I ON mc_generados.%I (ambito, codigo)',
		'idx_gen_' || p_capa || '_ac', p_capa
	);

	-- Servicios: tablas físicas (pueden sustituirse por VIEW vía link_servicio)
	PERFORM mc_meta.ensure_servicio_table(p_capa, 'nacional', attrs);
	PERFORM mc_meta.ensure_servicio_table(p_capa, 'regional', attrs);
	PERFORM mc_meta.ensure_servicio_table(p_capa, 'local', attrs);

	INSERT INTO mc_meta.capas (capa, tiene_clase, es_punto, perfil, purgar_generados, attrs)
	VALUES (
		p_capa,
		'clase' = ANY (attrs),
		position('_pto' IN p_capa) > 0,
		perfil,
		purgar,
		attrs
	)
	ON CONFLICT (capa) DO UPDATE SET
		tiene_clase = EXCLUDED.tiene_clase,
		es_punto = EXCLUDED.es_punto,
		perfil = EXCLUDED.perfil,
		purgar_generados = EXCLUDED.purgar_generados,
		attrs = EXCLUDED.attrs,
		updated_at = now();

	DELETE FROM mc_meta.servicio_link WHERE capa = p_capa;
END;
$$;

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
	SELECT coalesce(string_agg(format('%I text', a), ', '), '')
	INTO attr_cols FROM unnest(p_attrs) AS a;

	EXECUTE format('DROP TABLE IF EXISTS %I.%I CASCADE', sch, p_capa);
	EXECUTE format('DROP VIEW IF EXISTS %I.%I CASCADE', sch, p_capa);
	EXECUTE format(
		'CREATE TABLE %I.%I (
			the_geom geometry(Geometry,3857)%s%s
		)',
		sch, p_capa,
		CASE WHEN attr_cols = '' THEN '' ELSE ', ' END,
		attr_cols
	);
	EXECUTE format(
		'CREATE INDEX %I ON %I.%I USING gist (the_geom) WITH (fillfactor = 70)',
		'sidx_svc_' || p_nivel || '_' || p_capa, sch, p_capa
	);
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
	EXECUTE format('DROP TABLE IF EXISTS %I.%I CASCADE', sch, p_capa);
	EXECUTE format('DROP VIEW IF EXISTS %I.%I CASCADE', sch, p_capa);
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
	nivel text;
	cod text;
	clases_cubiertas text[] := ARRAY[]::text[];
	clases_nivel text[];
	clases_tomar text[];
	hay_prod boolean;
	n_ins int;
	total int := 0;
	detalle text[] := ARRAY[]::text[];
	attrs text[];
	attr_list text := '';
	attr_select text := '';
	sql_ins text;
BEGIN
	SELECT c.es_punto, c.tiene_clase INTO es_punto, tiene_clase
	FROM mc_meta.capas c WHERE c.capa = p_capa;
	IF NOT FOUND THEN
		RETURN 'error:capa_no_registrada';
	END IF;

	attrs := mc_meta.attr_columns(p_capa);
	IF coalesce(array_length(attrs, 1), 0) > 0 THEN
		SELECT string_agg(quote_ident(a), ', '), string_agg('p.' || quote_ident(a), ', ')
		INTO attr_list, attr_select FROM unnest(attrs) AS a;
		attr_list := ', ' || attr_list;
		attr_select := ', ' || attr_select;
	END IF;

	EXECUTE format(
		'DELETE FROM mc_generados.%I WHERE ambito = %L AND codigo = %L',
		p_capa, p_ambito_dest, p_codigo
	);

	FOR i IN 1 .. coalesce(array_length(p_cascade, 1), 0) LOOP
		nivel := p_cascade[i][1];
		cod := p_cascade[i][2];

		EXECUTE format(
			'SELECT EXISTS (
				SELECT 1 FROM mc_productores.%I WHERE ambito = %L AND codigo = %L LIMIT 1
			)',
			p_capa, nivel, cod
		) INTO hay_prod;

		IF NOT hay_prod THEN
			detalle := detalle || (nivel || '@sin_fuente');
			CONTINUE;
		END IF;

		IF NOT tiene_clase OR NOT ('clase' = ANY (attrs)) THEN
			sql_ins := format(
				'INSERT INTO mc_generados.%I (the_geom, ambito, codigo, nivel_origen%s)
				 SELECT mc_meta.normalize_geom(mc_meta.clip_geom(p.the_geom, $1, $2)),
				        %L, %L, %L%s
				   FROM mc_productores.%I p
				  WHERE p.ambito = %L AND p.codigo = %L AND p.the_geom && $1',
				p_capa, attr_list, p_ambito_dest, p_codigo, nivel, attr_select,
				p_capa, nivel, cod
			);
			EXECUTE sql_ins USING p_mask, es_punto;
			GET DIAGNOSTICS n_ins = ROW_COUNT;
			EXECUTE format(
				'DELETE FROM mc_generados.%I WHERE ambito=%L AND codigo=%L
				 AND (the_geom IS NULL OR ST_IsEmpty(the_geom))',
				p_capa, p_ambito_dest, p_codigo
			);
			total := total + n_ins;
			detalle := detalle || (nivel || '@capa_completa');
			EXIT;
		END IF;

		EXECUTE format(
			'SELECT coalesce(array_agg(DISTINCT clase), ARRAY[]::text[])
			   FROM mc_productores.%I
			  WHERE ambito = %L AND codigo = %L AND the_geom && $1 AND clase IS NOT NULL',
			p_capa, nivel, cod
		) INTO clases_nivel USING p_mask;

		IF coalesce(array_length(clases_nivel, 1), 0) = 0 THEN
			detalle := detalle || (nivel || '@vacio');
			CONTINUE;
		END IF;

		IF coalesce(array_length(clases_cubiertas, 1), 0) = 0 THEN
			clases_tomar := clases_nivel;
		ELSE
			SELECT coalesce(array_agg(x), ARRAY[]::text[]) INTO clases_tomar
			FROM unnest(clases_nivel) AS x WHERE NOT (x = ANY (clases_cubiertas));
		END IF;

		IF coalesce(array_length(clases_tomar, 1), 0) = 0 THEN
			detalle := detalle || (nivel || '@sin_clases_nuevas');
			CONTINUE;
		END IF;

		sql_ins := format(
			'INSERT INTO mc_generados.%I (the_geom, ambito, codigo, nivel_origen%s)
			 SELECT mc_meta.normalize_geom(mc_meta.clip_geom(p.the_geom, $1, $2)),
			        %L, %L, %L%s
			   FROM mc_productores.%I p
			  WHERE p.ambito = %L AND p.codigo = %L AND p.the_geom && $1 AND p.clase = ANY ($3)',
			p_capa, attr_list, p_ambito_dest, p_codigo, nivel, attr_select,
			p_capa, nivel, cod
		);
		EXECUTE sql_ins USING p_mask, es_punto, clases_tomar;
		EXECUTE format(
			'DELETE FROM mc_generados.%I WHERE ambito=%L AND codigo=%L
			 AND (the_geom IS NULL OR ST_IsEmpty(the_geom))',
			p_capa, p_ambito_dest, p_codigo
		);
		EXECUTE format(
			'SELECT count(*) FROM mc_generados.%I WHERE ambito=%L AND codigo=%L AND nivel_origen=%L',
			p_capa, p_ambito_dest, p_codigo, nivel
		) INTO n_ins;

		IF n_ins > 0 THEN
			clases_cubiertas := clases_cubiertas || clases_tomar;
			total := total + n_ins;
			detalle := detalle || format('%s[%s]', nivel, array_to_string(clases_tomar, ','));
		ELSE
			detalle := detalle || (nivel || '@extract_vacio');
		END IF;
	END LOOP;

	IF total = 0 THEN
		RETURN 'mezcla_auto_sin_fragmentos:' || array_to_string(detalle, ';');
	END IF;
	RETURN 'mezcla_auto:' || array_to_string(detalle, ';') || format(' rows=%s', total);
END;
$$;


CREATE OR REPLACE FUNCTION mc_meta.build_servicio(
	p_capa text,
	p_servicio text,
	p_ambito_generado text DEFAULT NULL
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
	n bigint;
	attrs text[];
	attr_list text := '';
	attr_select text := '';
	dest_schema text;
	is_view boolean;
BEGIN
	dest_schema := mc_meta.servicio_schema(p_servicio);

	-- Si hay VIEW enlazada, recrear tabla física antes de materializar
	SELECT EXISTS (
		SELECT 1 FROM information_schema.views
		WHERE table_schema = dest_schema AND table_name = p_capa
	) INTO is_view;
	IF is_view THEN
		PERFORM mc_meta.ensure_servicio_table(p_capa, p_servicio, mc_meta.attr_columns(p_capa));
		DELETE FROM mc_meta.servicio_link WHERE capa = p_capa AND nivel = p_servicio;
	END IF;

	attrs := mc_meta.attr_columns(p_capa);
	IF coalesce(array_length(attrs, 1), 0) > 0 THEN
		SELECT string_agg(quote_ident(a), ', '), string_agg('src.' || quote_ident(a), ', ')
		INTO attr_list, attr_select FROM unnest(attrs) AS a;
		attr_list := ', ' || attr_list;
		attr_select := ', ' || attr_select;
	END IF;

	EXECUTE format('TRUNCATE %I.%I', dest_schema, p_capa);

	IF p_ambito_generado IS NULL THEN
		EXECUTE format(
			'INSERT INTO %I.%I (the_geom%s)
			 SELECT src.the_geom%s FROM mc_productores.%I src
			  WHERE src.ambito = ''nacional'' AND src.codigo = ''00''
			    AND src.the_geom IS NOT NULL AND NOT ST_IsEmpty(src.the_geom)',
			dest_schema, p_capa, attr_list, attr_select, p_capa
		);
	ELSE
		EXECUTE format(
			'INSERT INTO %I.%I (the_geom%s)
			 SELECT src.the_geom%s FROM mc_generados.%I src
			  WHERE src.ambito = %L
			    AND src.the_geom IS NOT NULL AND NOT ST_IsEmpty(src.the_geom)',
			dest_schema, p_capa, attr_list, attr_select, p_capa, p_ambito_generado
		);
	END IF;

	GET DIAGNOSTICS n = ROW_COUNT;
	EXECUTE format('ANALYZE %I.%I', dest_schema, p_capa);
	RETURN n;
END;
$$;


CREATE OR REPLACE FUNCTION mc_meta.has_productores(
	p_capa text,
	p_ambito text
) RETURNS boolean
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
	ok boolean;
BEGIN
	EXECUTE format(
		'SELECT EXISTS (SELECT 1 FROM mc_productores.%I WHERE ambito = %L LIMIT 1)',
		p_capa, p_ambito
	) INTO ok;
	RETURN ok;
END;
$$;


CREATE OR REPLACE FUNCTION mc_meta.procesar_capa_regional(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	r record;
	mask geometry;
	msg text;
	n int := 0;
	perfil text;
BEGIN
	SELECT c.perfil INTO perfil FROM mc_meta.capas c WHERE c.capa = p_capa;

	IF NOT mc_meta.has_productores(p_capa, 'regional')
	   AND mc_meta.has_productores(p_capa, 'nacional') THEN
		-- Sin CCAA: mosaico nacional y enlaces (típico altimetría / capas IGN-only)
		PERFORM mc_meta.build_servicio(p_capa, 'nacional', NULL);
		PERFORM mc_meta.link_servicio(p_capa, 'regional', 'nacional');
		RETURN 'regional_linked_to_nacional (sin productores CCAA)';
	END IF;

	FOR r IN SELECT codigo FROM mc_mascaras.voronoi_comunidades ORDER BY codigo LOOP
		SELECT the_geom INTO mask FROM mc_mascaras.voronoi_comunidades WHERE codigo = r.codigo;
		msg := mc_meta.mezcla_territorio(
			p_capa, 'regional', r.codigo, mask,
			ARRAY[ARRAY['regional', r.codigo], ARRAY['nacional', '00']]
		);
		n := n + 1;
		RAISE NOTICE 'CCAA % → %', r.codigo, msg;
	END LOOP;

	PERFORM mc_meta.build_servicio(p_capa, 'nacional', NULL);
	PERFORM mc_meta.build_servicio(p_capa, 'regional', 'regional');
	RETURN format('regional_ok territorios=%s perfil=%s', n, perfil);
END;
$$;


CREATE OR REPLACE FUNCTION mc_meta.procesar_capa_local(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	r record;
	mask geometry;
	msg text;
	modo text;
	n int := 0;
	ccaa text;
	attrs text[];
	attr_list text := '';
	attr_select text := '';
	hay_local boolean;
	perfil text;
BEGIN
	SELECT c.perfil INTO perfil FROM mc_meta.capas c WHERE c.capa = p_capa;
	attrs := mc_meta.attr_columns(p_capa);
	IF coalesce(array_length(attrs, 1), 0) > 0 THEN
		SELECT string_agg(quote_ident(a), ', '), string_agg('g.' || quote_ident(a), ', ')
		INTO attr_list, attr_select FROM unnest(attrs) AS a;
		attr_list := ', ' || attr_list;
		attr_select := ', ' || attr_select;
	END IF;

	-- Capas pesadas sin productores municipales: no clipar 8000 municipios
	IF perfil = 'pesada' AND NOT mc_meta.has_productores(p_capa, 'local') THEN
		PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
		RETURN 'local_linked_to_regional (perfil=pesada, sin productores mun)';
	END IF;

	-- Sin productores locales en absoluto → reutilizar regional
	IF NOT mc_meta.has_productores(p_capa, 'local') THEN
		PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
		RETURN 'local_linked_to_regional (sin productores mun)';
	END IF;

	FOR r IN
		SELECT m.codigo,
		       coalesce(
				(SELECT t.codigo_ccaa FROM mc_meta.territorios_municipio t WHERE t.codigo = m.codigo),
				m.codigo_ccaa,
				left(m.codigo, 2)
		       ) AS codigo_ccaa
		  FROM mc_mascaras.voronoi_municipios m
		 ORDER BY m.codigo
	LOOP
		ccaa := r.codigo_ccaa;
		SELECT e.modo INTO modo FROM mc_meta.estrategia_ccaa e WHERE e.codigo_ccaa = ccaa;
		IF modo IS NULL THEN
			EXECUTE format(
				'SELECT EXISTS (
					SELECT 1 FROM mc_productores.%I p
					 WHERE p.ambito = ''local''
					   AND p.codigo IN (
						SELECT codigo FROM mc_mascaras.voronoi_municipios WHERE codigo_ccaa = %L
					   ) LIMIT 1
				)',
				p_capa, ccaa
			) INTO hay_local;
			modo := CASE WHEN hay_local
				THEN 'individual_municipal_processing'
				ELSE 'use_ccaa_source_for_union' END;
		END IF;

		-- En perfil pesada: solo municipios CON productor local
		IF perfil = 'pesada' THEN
			EXECUTE format(
				'SELECT EXISTS (SELECT 1 FROM mc_productores.%I WHERE ambito=''local'' AND codigo=%L LIMIT 1)',
				p_capa, r.codigo
			) INTO hay_local;
			IF NOT hay_local THEN
				CONTINUE;
			END IF;
			modo := 'individual_municipal_processing';
		END IF;

		SELECT the_geom INTO mask FROM mc_mascaras.voronoi_municipios WHERE codigo = r.codigo;

		IF modo = 'use_ccaa_source_for_union' THEN
			EXECUTE format('DELETE FROM mc_generados.%I WHERE ambito=''local'' AND codigo=%L', p_capa, r.codigo);
			EXECUTE format(
				'INSERT INTO mc_generados.%I (the_geom, ambito, codigo, nivel_origen%s)
				 SELECT mc_meta.normalize_geom(mc_meta.clip_geom(g.the_geom, $1, false)),
				        ''local'', %L, coalesce(g.nivel_origen, ''regional'')%s
				   FROM mc_generados.%I g
				  WHERE g.ambito = ''regional'' AND g.codigo = %L AND g.the_geom && $1',
				p_capa, attr_list, r.codigo, attr_select, p_capa, ccaa
			) USING mask;
			EXECUTE format(
				'DELETE FROM mc_generados.%I WHERE ambito=''local'' AND codigo=%L
				 AND (the_geom IS NULL OR ST_IsEmpty(the_geom))',
				p_capa, r.codigo
			);
		ELSE
			msg := mc_meta.mezcla_territorio(
				p_capa, 'local', r.codigo, mask,
				ARRAY[
					ARRAY['local', r.codigo],
					ARRAY['regional', ccaa],
					ARRAY['nacional', '00']
				]
			);
			RAISE NOTICE 'MUN % → %', r.codigo, msg;
		END IF;
		n := n + 1;
	END LOOP;

	-- Si perfil pesada y solo se procesaron municipios con datos:
	-- rellenar el resto del país desde regional (sin N clips)
	IF perfil = 'pesada' AND n > 0 THEN
		-- Insertar en servicio: primero regional completo, luego overlay local generados
		PERFORM mc_meta.build_servicio(p_capa, 'local', 'regional');
		-- Overlay features de municipios procesados (reemplazo espacial simple: append)
		-- Mejor: truncar y unir regional-fuera-de-muns + generados local
		EXECUTE format(
			'DELETE FROM mc_servicio_local.%I s
			  USING mc_mascaras.voronoi_municipios m
			 WHERE m.codigo IN (SELECT DISTINCT codigo FROM mc_generados.%I WHERE ambito=''local'')
			   AND s.the_geom && m.the_geom AND ST_Intersects(s.the_geom, m.the_geom)',
			p_capa, p_capa
		);
		EXECUTE format(
			'INSERT INTO mc_servicio_local.%I (the_geom%s)
			 SELECT g.the_geom%s FROM mc_generados.%I g
			  WHERE g.ambito = ''local'' AND g.the_geom IS NOT NULL',
			p_capa,
			CASE WHEN attr_list = '' THEN '' ELSE attr_list END,
			CASE WHEN attr_select = '' THEN '' ELSE replace(attr_select, 'g.', 'g.') END,
			p_capa
		);
		EXECUTE format('ANALYZE mc_servicio_local.%I', p_capa);
		RETURN format('local_pesada_overlay municipios=%s', n);
	END IF;

	IF n = 0 THEN
		PERFORM mc_meta.link_servicio(p_capa, 'local', 'regional');
		RETURN 'local_linked_to_regional (ningún municipio procesado)';
	END IF;

	PERFORM mc_meta.build_servicio(p_capa, 'local', 'local');
	RETURN format('local_ok territorios=%s', n);
END;
$$;


CREATE OR REPLACE FUNCTION mc_meta.procesar_capa_completa(p_capa text)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
	m1 text;
	m2 text;
	purgar boolean;
	t0 timestamptz := clock_timestamp();
	rid bigint;
BEGIN
	INSERT INTO mc_meta.run_log (capa, fase, detalle)
	VALUES (p_capa, 'completa', 'start') RETURNING id INTO rid;

	m1 := mc_meta.procesar_capa_regional(p_capa);
	m2 := mc_meta.procesar_capa_local(p_capa);

	SELECT c.purgar_generados INTO purgar FROM mc_meta.capas c WHERE c.capa = p_capa;
	IF coalesce(purgar, false) THEN
		EXECUTE format('TRUNCATE mc_generados.%I', p_capa);
		m2 := m2 || ' | generados_purgados';
	END IF;

	UPDATE mc_meta.run_log
	   SET finished_at = clock_timestamp(),
	       ok = true,
	       detalle = m1 || ' | ' || m2 || format(' elapsed=%s', clock_timestamp() - t0)
	 WHERE id = rid;

	RETURN m1 || ' | ' || m2;
EXCEPTION WHEN OTHERS THEN
	UPDATE mc_meta.run_log
	   SET finished_at = clock_timestamp(), ok = false, detalle = SQLERRM
	 WHERE id = rid;
	RAISE;
END;
$$;

-- Perfiles sugeridos para capas típicas del modelo
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
