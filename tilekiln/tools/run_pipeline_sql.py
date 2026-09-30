#!/usr/bin/env python3
"""
Pipeline PostGIS equivalente al Proceso 3 (FGB):
  productores → recorte/mezcla (mun>CCAA>IGN) → mosaicos servicio → Tilekiln

Uso con árbol productores (p. ej. DatosProcesados en CNIG):
  python run_pipeline_sql.py --db mapabasexyz \\
      --datos-base /var/MVT_MapaBaseXYZ/DatosProcesados \\
      --capas cubierta_vegetal_pol,edificio_pol
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

TILEKILN_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = TILEKILN_ROOT / "sql" / "pipeline"
REPO = Path(__file__).resolve().parents[2]


def psql_file(db: str, path: Path) -> None:
    subprocess.run(
        ["psql", "-d", db, "-v", "ON_ERROR_STOP=1", "-f", str(path)],
        check=True,
    )


def connect(db: str):
    return psycopg2.connect(f"dbname={db}")


def ogr_load(db: str, fgb: Path, schema: str, table: str, s_srs: str, extras: dict | None = None):
    """Carga FGB a tabla existente (append) en 3857. extras: columnas constantes."""
    # Carga a tabla temporal y luego INSERT con columnas extra
    tmp = f"_tmp_{table}"
    subprocess.run(
        [
            "ogr2ogr",
            "-f",
            "PostgreSQL",
            f"PG:dbname={db}",
            str(fgb),
            "-nln",
            f"public.{tmp}",
            "-overwrite",
            "-t_srs",
            "EPSG:3857",
            "-s_srs",
            s_srs,
            "-nlt",
            "PROMOTE_TO_MULTI",
            "-lco",
            "GEOMETRY_NAME=the_geom",
            "-lco",
            "FID=ogc_fid",
            "-skipfailures",
        ],
        check=False,
    )
    extras = extras or {}
    with connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema=%s AND table_name=%s
                  AND column_name NOT IN ('the_geom','ambito','codigo','nivel_origen','ogc_fid')
                """,
                (schema, table),
            )
            dest_attrs = [r[0] for r in cur.fetchall()]
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name=%s
                  AND column_name NOT IN ('the_geom','ogc_fid','wkb_geometry')
                """,
                (tmp,),
            )
            src_attrs = {r[0] for r in cur.fetchall()}
            # geom column name in tmp
            cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name=%s
                  AND udt_name='geometry'
                """,
                (tmp,),
            )
            geom_cols = [r[0] for r in cur.fetchall()]
            geom = geom_cols[0] if geom_cols else "the_geom"

            common = [a for a in dest_attrs if a in src_attrs]
            extra_cols = [k for k in extras]
            col_list = ["the_geom"] + list(extras.keys()) + common
            select_parts = [f"t.{geom}"] + [f"%({k})s" for k in extras] + [f"t.{a}" for a in common]
            # Use literal extras via format
            select_sql = f"t.{geom}"
            for k, v in extras.items():
                select_sql += f", '{v}'"
            for a in common:
                select_sql += f", t.{a}"
            cols_sql = ", ".join(col_list)
            cur.execute(f"DELETE FROM {schema}.{table} WHERE ambito=%s AND codigo=%s", (extras.get("ambito"), extras.get("codigo")))
            # If no ambito filter (shouldn't), truncate not needed
            sql = f"""
                INSERT INTO {schema}.{table} ({cols_sql})
                SELECT {select_sql}
                FROM public.{tmp} t
                WHERE t.{geom} IS NOT NULL
            """
            cur.execute(sql)
            cur.execute(f"DROP TABLE IF EXISTS public.{tmp}")
        conn.commit()


def ensure_ddl(db: str, capas: list[str], attrs_by_capa: dict[str, list[str]] | None = None, perfiles: dict[str, str] | None = None):
    with connect(db) as conn:
        with conn.cursor() as cur:
            for capa in capas:
                attrs = (attrs_by_capa or {}).get(capa) or ["clase", "proveedor"]
                if capa == "edificio_pol" and "tipo" not in attrs:
                    attrs = ["clase", "proveedor", "tipo"]
                if capa == "aerodromo_pto":
                    attrs = ["clase", "nombre", "proveedor", "ref", "tipo", "uso", "estado"]
                if capa == "hidrografia_lin" and "orden" not in attrs:
                    attrs = ["clase", "nombre", "orden", "persistencia", "situacion", "proveedor"]
                perfil = (perfiles or {}).get(capa)
                if not perfil:
                    cur.execute("SELECT mc_meta.sugerir_perfil(%s)", (capa,))
                    perfil = cur.fetchone()[0]
                # pocas filas en catálogo: perfil normal salvo override en mc_meta.capas
                cur.execute(
                    "SELECT mc_meta.ensure_capa_tables(%s, %s, %s)",
                    (capa, attrs, perfil),
                )
        conn.commit()


def load_mask_from_fgb(db: str, fgb: Path, kind: str, codigo_filter: set[str] | None = None):
    """Carga voronoi FGB (EPSG:4258) a mc_mascaras."""
    tmp = f"_tmp_mask_{kind}"
    subprocess.run(
        [
            "ogr2ogr",
            "-f",
            "PostgreSQL",
            f"PG:dbname={db}",
            str(fgb),
            "-nln",
            f"public.{tmp}",
            "-overwrite",
            "-t_srs",
            "EPSG:3857",
            "-s_srs",
            "EPSG:4258",
            "-nlt",
            "PROMOTE_TO_MULTI",
            "-lco",
            "GEOMETRY_NAME=the_geom",
            "-skipfailures",
        ],
        check=False,
    )
    with connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name='{tmp}' AND udt_name='geometry'
                """
            )
            geom = cur.fetchone()[0]
            cur.execute(
                f"""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema='public' AND table_name='{tmp}'
                """
            )
            cols = [r[0] for r in cur.fetchall()]
            code_col = "codigo" if "codigo" in cols else cols[0]
            if kind == "comunidades":
                cur.execute("TRUNCATE mc_mascaras.voronoi_comunidades")
                cur.execute(
                    f"""
                    INSERT INTO mc_mascaras.voronoi_comunidades (codigo, the_geom)
                    SELECT
                      CASE
                        WHEN length(trim(codigo::text)) >= 4 THEN substring(trim(codigo::text) from 3 for 2)
                        ELSE lpad(trim(codigo::text), 2, '0')
                      END,
                      ST_Multi(ST_MakeValid({geom}))
                    FROM public.{tmp}
                    WHERE {geom} IS NOT NULL
                    """
                )
                if codigo_filter:
                    cur.execute(
                        "DELETE FROM mc_mascaras.voronoi_comunidades WHERE codigo <> ALL(%s)",
                        (list(codigo_filter),),
                    )
            else:
                cur.execute("TRUNCATE mc_mascaras.voronoi_municipios")
                # codigo INE 5 dígitos al final
                cur.execute(
                    f"""
                    INSERT INTO mc_mascaras.voronoi_municipios (codigo, codigo_ccaa, the_geom)
                    SELECT
                      right(regexp_replace(trim(codigo::text), '[^0-9]', '', 'g'), 5),
                      CASE
                        WHEN length(right(regexp_replace(trim(codigo::text), '[^0-9]', '', 'g'), 5)) = 5
                          THEN left(right(regexp_replace(trim(codigo::text), '[^0-9]', '', 'g'), 5), 2)
                        ELSE NULL
                      END,
                      ST_Multi(ST_MakeValid({geom}))
                    FROM public.{tmp}
                    WHERE {geom} IS NOT NULL
                    """
                )
                if codigo_filter:
                    cur.execute(
                        "DELETE FROM mc_mascaras.voronoi_municipios WHERE codigo <> ALL(%s)",
                        (list(codigo_filter),),
                    )
            cur.execute(f"DROP TABLE IF EXISTS public.{tmp}")
        conn.commit()


def load_municipios_meta(db: str, xlsx: Path):
    """Carga INE→CCAA desde municipios.xlsx (cod_com_aut)."""
    try:
        import openpyxl
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "openpyxl", "-q"])
        import openpyxl
    wb = openpyxl.load_workbook(xlsx, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    def idx(*names):
        for n in names:
            if n in headers:
                return headers.index(n)
        return None
    i_ine = idx("codigo_ine_mun", "codigo")
    i_ccaa = idx("cod_com_aut", "codigo_ccaa")
    i_nom = idx("nombre")
    if i_ine is None or i_ccaa is None:
        print(f"ADVERTENCIA: no se pudo mapear columnas en {xlsx}: {headers}")
        return
    with connect(db) as conn:
        with conn.cursor() as cur:
            for row in rows[1:]:
                if not row:
                    continue
                ine = row[i_ine]
                ccaa = row[i_ccaa]
                if ine is None or ccaa is None:
                    continue
                ine_s = str(int(ine)).zfill(5) if str(ine).isdigit() or isinstance(ine, (int, float)) else str(ine).strip()[-5:]
                ccaa_s = str(int(ccaa)).zfill(2) if isinstance(ccaa, (int, float)) or str(ccaa).isdigit() else str(ccaa).zfill(2)
                nom = row[i_nom] if i_nom is not None else None
                cur.execute(
                    """
                    INSERT INTO mc_meta.territorios_ccaa (codigo, nombre) VALUES (%s, NULL)
                    ON CONFLICT DO NOTHING
                    """,
                    (ccaa_s,),
                )
                cur.execute(
                    """
                    INSERT INTO mc_meta.territorios_municipio (codigo, nombre, codigo_ccaa)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (codigo) DO UPDATE
                      SET codigo_ccaa = EXCLUDED.codigo_ccaa,
                          nombre = COALESCE(EXCLUDED.nombre, mc_meta.territorios_municipio.nombre)
                    """,
                    (ine_s, nom, ccaa_s),
                )
            # alinear mascara con meta
            cur.execute(
                """
                UPDATE mc_mascaras.voronoi_municipios v
                   SET codigo_ccaa = t.codigo_ccaa
                  FROM mc_meta.territorios_municipio t
                 WHERE v.codigo = t.codigo
                """
            )
        conn.commit()
    print(f"→ meta municipios desde {xlsx.name}")


def load_datos_base(db: str, datos_base: Path, capas: list[str] | None):
    """Carga árbol productores estándar (nacional/com_aut/municipios)."""
    prod = datos_base / "productores"
    # descubrir capas si no se pasan
    if not capas:
        capas = sorted({p.stem for p in (prod / "nacional" / "00").glob("*.fgb")})
    ensure_ddl(db, capas)

    for capa in capas:
        fgb = prod / "nacional" / "00" / f"{capa}.fgb"
        if fgb.exists():
            ogr_load(db, fgb, "mc_productores", capa, "EPSG:4258", {"ambito": "nacional", "codigo": "00"})
        for ccaa_dir in sorted((prod / "com_aut").glob("*")):
            if not ccaa_dir.is_dir():
                continue
            fgb = ccaa_dir / f"{capa}.fgb"
            if fgb.exists():
                ogr_load(db, fgb, "mc_productores", capa, "EPSG:4258", {"ambito": "regional", "codigo": ccaa_dir.name})
        for mun_dir in sorted((prod / "municipios").glob("*")):
            if not mun_dir.is_dir():
                continue
            fgb = mun_dir / f"{capa}.fgb"
            if fgb.exists():
                ogr_load(db, fgb, "mc_productores", capa, "EPSG:4258", {"ambito": "local", "codigo": mun_dir.name})

    lib = datos_base / "lib"
    if not (lib / "voronoi_comunidades.fgb").exists():
        lib = REPO / "scripts/teselas/3ProcesoUnionDatos/lib"
    load_mask_from_fgb(db, lib / "voronoi_comunidades.fgb", "comunidades")
    load_mask_from_fgb(db, lib / "voronoi_municipios.fgb", "municipios")
    mun_xlsx = lib / "municipios.xlsx"
    if mun_xlsx.exists():
        load_municipios_meta(db, mun_xlsx)
    return capas


def run_pipeline(db: str, capas: list[str]):
    with connect(db) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            for capa in capas:
                print(f"=== procesar {capa} ===")
                cur.execute("SELECT mc_meta.procesar_capa_completa(%s)", (capa,))
                print(cur.fetchone()[0])


def print_stats(db: str, capas: list[str]):
    with connect(db) as conn:
        with conn.cursor() as cur:
            for capa in capas:
                for sch in ("mc_productores", "mc_generados", "mc_servicio_nacional", "mc_servicio_regional", "mc_servicio_local"):
                    cur.execute(f"SELECT count(*) FROM {sch}.{capa}")
                    print(f"  {sch}.{capa}: {cur.fetchone()[0]}")
                cur.execute(
                    f"""
                    SELECT ambito, codigo, nivel_origen, clase, count(*)
                    FROM mc_generados.{capa}
                    GROUP BY 1,2,3,4 ORDER BY 1,2,3,4
                    """
                )
                rows = cur.fetchall()
                if rows:
                    print("  generados detalle:")
                    for r in rows:
                        print(f"    {r}")


def main():
    ap = argparse.ArgumentParser(description="Pipeline SQL Mapa Ciudadano (equiv. Proceso 3)")
    ap.add_argument("--db", required=True, help="nombre PostgreSQL (p. ej. mapabasexyz)")
    ap.add_argument("--datos-base", type=Path, required=False, help="raíz con productores/ y lib/")
    ap.add_argument("--capas", default="", help="lista separada por comas")
    ap.add_argument("--skip-load", action="store_true")
    ap.add_argument("--skip-process", action="store_true")
    args = ap.parse_args()

    # instalar extensión psycopg2 si falta
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "psycopg2-binary"])

    print("→ aplicando SQL schemas/funciones")
    psql_file(args.db, SQL_DIR / "00_schemas.sql")
    psql_file(args.db, SQL_DIR / "01_funciones.sql")

    capas = [c.strip() for c in args.capas.split(",") if c.strip()]
    if not args.skip_load:
        if not args.datos_base:
            print("Indica --datos-base (ruta a DatosProcesados o equivalente CNIG)")
            sys.exit(1)
        print(f"→ carga datos_base {args.datos_base}")
        capas = load_datos_base(args.db, args.datos_base, capas or None)

    if not capas:
        print("Sin capas")
        sys.exit(1)

    if not args.skip_process:
        run_pipeline(args.db, capas)

    print("→ stats")
    print_stats(args.db, capas)


if __name__ == "__main__":
    main()
