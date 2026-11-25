-- =============================================================================
-- Puesta a punto de los esquemas mc_* tras copiar la BD a PostgreSQL 18 + PostGIS 3.6
-- =============================================================================
-- NO borra datos de capas. Se lanza UNA vez tras la migración (y se puede repetir).
-- Antes: aplicar 00_schemas.sql y 01_funciones.sql (versión PostGIS 3).
--
--   cd /var/proyectos/mapaBaseXYZ/tilekiln/mapabase/tilekiln
--   set -a; source .env; set +a
--   psql -X -v ON_ERROR_STOP=1 -f sql/pipeline/00_schemas.sql
--   psql -X -v ON_ERROR_STOP=1 -f sql/pipeline/01_funciones.sql
--   psql -X -f sql/pipeline/03_post_migracion_pg18.sql 2>&1 | tee post_migracion.log
--
-- Qué hace (usuario del pipeline, sin permisos especiales sobre la BD):
--   1. Borra restos de cargas interrumpidas en mc_staging.
--   2. Crea el GiST que falte en tablas de servicio.
--   3. VACUUM (ANALYZE) de todo mc_*: estadísticas para el planificador (una copia
--      dump/restore llega SIN estadísticas) y visibility map/hint bits, para que la
--      primera lectura de cada tesela no escriba en disco.
-- Duración: proporcional al volumen (altimetria_pto, la mayor, unos minutos).
-- =============================================================================
\pset pager off
SET search_path TO public, public_modelo_2025, pg_catalog;
SET maintenance_work_mem = '1GB';
SET client_min_messages = warning;

\echo '--- 1. Limpieza de mc_staging'
SELECT format('DROP TABLE IF EXISTS mc_staging.%I', c.relname)
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'mc_staging' AND c.relkind = 'r'
\gexec

\echo '--- 2. GiST que falten en servicio'
SELECT format('CREATE INDEX IF NOT EXISTS %I ON %I.%I USING gist (the_geom)',
              left('sidx_' || replace(n.nspname, 'mc_servicio_', 'svc_') || '_' || c.relname, 63),
              n.nspname, c.relname)
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname LIKE 'mc_servicio_%' AND c.relkind = 'r'
   AND NOT EXISTS (SELECT 1 FROM pg_index i JOIN pg_class ic ON ic.oid = i.indexrelid
                    JOIN pg_am am ON am.oid = ic.relam
                    WHERE i.indrelid = c.oid AND am.amname = 'gist')
\gexec

\echo '--- 3. VACUUM (ANALYZE) de mc_* con datos (de menor a mayor)'
\timing on
SELECT format('VACUUM (ANALYZE) %I.%I', n.nspname, c.relname)
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname LIKE 'mc\_%' AND n.nspname <> 'mc_staging'
   AND c.relkind = 'r' AND pg_relation_size(c.oid) > 0
 ORDER BY pg_relation_size(c.oid)
\gexec
-- Las tablas particionadas (mc_productores.{capa}) guardan estadísticas propias del padre
SELECT format('ANALYZE %I.%I', n.nspname, c.relname)
  FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
 WHERE n.nspname = 'mc_productores' AND c.relkind = 'p'
\gexec
\timing off

\echo '--- Hecho. Comprobar con: psql -X -f sql/diagnostico_pg18.sql'

-- =============================================================================
-- PARA EL DBA DE CNIG (requiere propietario de la BD / superusuario)
-- No se ejecuta: copiar y lanzar a mano o enviar a sistemas.
-- =============================================================================
-- a) Si postgis_full_version() dice "procs need upgrade" (BD copiada de PostGIS 2.5):
--      ALTER EXTENSION postgis UPDATE;
--      SELECT postgis_extensions_upgrade();
--
-- b) search_path por defecto de la BD (así ni Tilekiln ni el pipeline necesitan PGOPTIONS):
--      ALTER DATABASE mapabasexyz SET search_path = public, public_modelo_2025;
--
-- c) Usuario que sirve teselas: JIT desactivado (compilar cada consulta de tesela
--    cuesta más que ejecutarla) y algo más de memoria por consulta:
--      ALTER ROLE guadaltel_servicios_cnig IN DATABASE mapabasexyz SET jit = off;
--      ALTER ROLE guadaltel_servicios_cnig IN DATABASE mapabasexyz SET work_mem = '64MB';
--
-- d) postgresql.conf (orientativo; ajustar a la RAM real de la 10.67.33.159):
--      shared_buffers           = 25% RAM
--      effective_cache_size     = 60-75% RAM
--      random_page_cost         = 1.1      # si el almacenamiento es SSD/cabina
--      effective_io_concurrency = 200      # SSD
--      io_method                = worker   # PG18: E/S asíncrona, ya es el valor por defecto (io_uring si el kernel lo permite)
--      max_parallel_workers_per_gather = 4
--      jit                      = off      # o solo por rol, como en c)
--
-- e) Caché de teselas (tilekiln live): el usuario necesita poder crear el esquema tilekiln:
--      GRANT CREATE ON DATABASE mapabasexyz TO guadaltel_servicios_cnig;
-- =============================================================================
