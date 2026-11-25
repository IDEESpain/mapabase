-- =============================================================================
-- Diagnóstico de la BD tras la migración a PostgreSQL 18 + PostGIS 3.6
-- SOLO LECTURA: no modifica nada. Se puede lanzar en cualquier momento.
--
--   cd /var/proyectos/mapaBaseXYZ/tilekiln/mapabase/tilekiln
--   set -a; source .env; set +a
--   psql -X -f sql/diagnostico_pg18.sql 2>&1 | tee diagnostico_$(date +%F).txt
-- =============================================================================
\pset pager off
\pset null '·'
SET search_path TO public, public_modelo_2025, pg_catalog;

\echo
\echo '=== 1. Versiones ==='
SELECT current_setting('server_version') AS postgres,
       postgis_lib_version() AS postgis_lib,
       postgis_geos_version() AS geos,
       current_database() AS bd, current_user AS usuario;
SELECT postgis_full_version();
\echo '   (si aparece «procs need upgrade» o «need upgrade» → paso DBA: ALTER EXTENSION postgis UPDATE)'

\echo
\echo '=== 2. Extensiones y esquema donde viven ==='
SELECT e.extname, e.extversion, n.nspname AS esquema
  FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace
 ORDER BY 1;
SELECT n.nspname AS esquema_tipo_geometry
  FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace
 WHERE t.typname = 'geometry';

\echo
\echo '=== 3. Funciones que necesita Tilekiln sin parches (deben dar t) ==='
SELECT to_regprocedure('st_tileenvelope(integer,integer,integer,geometry,double precision)') IS NOT NULL AS st_tileenvelope,
       (SELECT count(*) FROM pg_proc WHERE proname = 'st_asmvt') >= 5 AS st_asmvt_feature_id,
       ST_AsText(ST_TileEnvelope(0, 0, 0)) IS NOT NULL AS tileenvelope_funciona;

\echo
\echo '=== 4. Funciones del pipeline: ¿versión PG11 (con _ST_*) o PG18? ==='
SELECT count(*) FILTER (WHERE p.prosrc ~* '_st_(intersects|covers)') AS funciones_version_pg11,
       count(*) AS funciones_mc_meta
  FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
 WHERE n.nspname = 'mc_meta';
\echo '   (funciones_version_pg11 > 0 → reaplicar sql/pipeline/01_funciones.sql)'

\echo
\echo '=== 5. Esquemas: nº de objetos y tamaño ==='
SELECT n.nspname AS esquema,
       count(*) FILTER (WHERE c.relkind IN ('r', 'p')) AS tablas,
       count(*) FILTER (WHERE c.relkind = 'v') AS vistas,
       pg_size_pretty(sum(pg_total_relation_size(c.oid)) FILTER (WHERE c.relkind = 'r')) AS tamano
  FROM pg_namespace n LEFT JOIN pg_class c ON c.relnamespace = n.oid
 WHERE n.nspname NOT LIKE 'pg\_%' AND n.nspname <> 'information_schema'
 GROUP BY 1 ORDER BY 1;
SELECT pg_size_pretty(pg_database_size(current_database())) AS tamano_bd;

\echo
\echo '=== 6. Capas procesadas (último estado en run_log) ==='
SELECT DISTINCT ON (capa, fase) capa, fase, ok, finished_at::timestamp(0) AS fin, left(detalle, 90) AS detalle
  FROM mc_meta.run_log
 WHERE capa IS NOT NULL
 ORDER BY capa, fase, id DESC;

\echo
\echo '=== 7. Tablas de servicio con datos (lo que ve Tilekiln; regional/local sin fila = vista del nivel superior) ==='
SELECT replace(n.nspname, 'mc_servicio_', '') AS nivel, c.relname AS tabla,
       CASE WHEN c.reltuples < 0 THEN 'sin ANALYZE' ELSE c.reltuples::bigint::text END AS filas_est,
       pg_size_pretty(pg_total_relation_size(c.oid)) AS tamano,
       EXISTS (SELECT 1 FROM pg_index i JOIN pg_class ic ON ic.oid = i.indexrelid
                JOIN pg_am am ON am.oid = ic.relam
                WHERE i.indrelid = c.oid AND am.amname = 'gist') AS gist,
       coalesce(s.last_analyze, s.last_autoanalyze)::timestamp(0) AS ultimo_analyze
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
  LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
 WHERE n.nspname LIKE 'mc_servicio_%' AND c.relkind = 'r'
   AND pg_relation_size(c.oid) > 0
 ORDER BY c.relname, 1;

\echo
\echo '=== 8. Problemas ==='
\echo '--- 8a. Tablas mc_* nunca analizadas (planes malos → teselas lentas)'
SELECT s.schemaname, count(*) AS sin_analyze
  FROM pg_stat_user_tables s
 WHERE s.schemaname LIKE 'mc\_%'
   AND s.last_analyze IS NULL AND s.last_autoanalyze IS NULL
   AND pg_relation_size(s.relid) > 0
 GROUP BY 1 ORDER BY 1;
\echo '--- 8b. Tablas de servicio sin índice GiST'
SELECT n.nspname, c.relname
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname LIKE 'mc_servicio_%' AND c.relkind = 'r'
   AND NOT EXISTS (SELECT 1 FROM pg_index i JOIN pg_class ic ON ic.oid = i.indexrelid
                    JOIN pg_am am ON am.oid = ic.relam
                    WHERE i.indrelid = c.oid AND am.amname = 'gist')
 ORDER BY 1, 2;
\echo '--- 8c. Índices inválidos (restore o CREATE INDEX interrumpido)'
SELECT n.nspname, c.relname AS indice
  FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE NOT i.indisvalid;
\echo '--- 8d. Restos en mc_staging (cargas interrumpidas; se pueden borrar)'
SELECT c.relname, pg_size_pretty(pg_total_relation_size(c.oid)) AS tamano
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'mc_staging' AND c.relkind = 'r';
\echo '--- 8e. Tablas UNLOGGED (mc_generados lo es a propósito; se vacían si el servidor cae)'
SELECT n.nspname, count(*) AS unlogged
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE c.relpersistence = 'u' AND c.relkind = 'r'
 GROUP BY 1;

\echo
\echo '=== 9. Configuración del servidor relevante para teselas ==='
SELECT name, setting, unit, source
  FROM pg_settings
 WHERE name IN ('shared_buffers', 'effective_cache_size', 'work_mem', 'maintenance_work_mem',
                'random_page_cost', 'effective_io_concurrency', 'io_method', 'io_workers',
                'jit', 'max_parallel_workers_per_gather', 'max_parallel_maintenance_workers',
                'max_worker_processes', 'max_connections', 'search_path',
                'default_statistics_target', 'autovacuum')
 ORDER BY name;
\echo '   Recomendado para servir teselas: jit=off, random_page_cost=1.1 (SSD),'
\echo '   effective_cache_size ≈ 50-75% RAM, shared_buffers ≈ 25% RAM.'

\echo
\echo '=== 10. Prueba de tesela real (Madrid z10 y z14) con las capas cargadas ==='
\timing on
SELECT 'nacional z10' AS prueba, count(*) AS elementos
  FROM mc_servicio_nacional.altimetria_pto
 WHERE the_geom && ST_TileEnvelope(10, 501, 386);
SELECT 'regional z14' AS prueba, count(*) AS elementos
  FROM mc_servicio_regional.aerodromo_pto
 WHERE the_geom && ST_TileEnvelope(14, 8023, 6177);
\timing off
\echo
\echo 'Fin del diagnóstico.'
