-- =============================================================================
-- Optimización lectura Tilekiln: GiST + ANALYZE (+ CLUSTER opcional)
-- Las consultas jinja son: WHERE the_geom && bbox  → el índice útil es GiST(the_geom).
-- Índices en atributos del tippecanoe filter casi no ayudan al bbox.
--
-- Uso:
--   psql -d mapabasexyz -v ON_ERROR_STOP=1 \
--     -c "SET search_path TO public, public_modelo_2025, pg_catalog;" \
--     -f 02_optimizar_servicio.sql
--
-- CLUSTER reescribe tablas (bloquea cada una un rato). Por defecto OFF.
--   psql ... -v cluster=1 -f 02_optimizar_servicio.sql
-- =============================================================================

SET search_path TO public, public_modelo_2025, pg_catalog;

DO $$
DECLARE
	r record;
	idx text;
	do_cluster boolean := (current_setting('cluster', true) = '1');
BEGIN
	FOR r IN
		SELECT n.nspname AS sch, c.relname AS tbl, c.oid
		  FROM pg_class c
		  JOIN pg_namespace n ON n.oid = c.relnamespace
		 WHERE n.nspname IN (
				'mc_servicio_nacional',
				'mc_servicio_regional',
				'mc_servicio_local'
		       )
		   AND c.relkind = 'r'
		 ORDER BY 1, 2
	LOOP
		idx := left('sidx_' || replace(r.sch, 'mc_servicio_', 'svc_') || '_' || r.tbl, 63);
		EXECUTE format(
			'CREATE INDEX IF NOT EXISTS %I ON %I.%I USING gist (the_geom)',
			idx, r.sch, r.tbl
		);
		EXECUTE format('ANALYZE %I.%I', r.sch, r.tbl);
		RAISE NOTICE 'OK índice+analyze %.%', r.sch, r.tbl;

		IF do_cluster THEN
			EXECUTE format('CLUSTER %I.%I USING %I', r.sch, r.tbl, idx);
			EXECUTE format('ANALYZE %I.%I', r.sch, r.tbl);
			RAISE NOTICE 'CLUSTER %.%', r.sch, r.tbl;
		END IF;
	END LOOP;
END;
$$;
