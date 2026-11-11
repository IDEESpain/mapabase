-- =============================================================================
-- Borra TODO lo del pipeline (mc_*) para empezar de cero.
-- No toca public ni public_modelo_2025. Después hay que aplicar 00_schemas.sql.
-- =============================================================================

DROP SCHEMA IF EXISTS mc_generados CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_local CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_regional CASCADE;
DROP SCHEMA IF EXISTS mc_servicio_nacional CASCADE;
DROP SCHEMA IF EXISTS mc_productores CASCADE;
DROP SCHEMA IF EXISTS mc_staging CASCADE;
DROP SCHEMA IF EXISTS mc_mascaras CASCADE;
DROP SCHEMA IF EXISTS mc_meta CASCADE;

-- Esquema de la primera prueba (84 tablas planas): fuera del diseño
DROP SCHEMA IF EXISTS mapa_ciudadano CASCADE;
