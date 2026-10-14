#!/usr/bin/env python3
"""
Pipeline PostGIS de Mapa Ciudadano (equivalente al Proceso 3 en FGB).

Por cada capa:
  1. Carga de los FGB de productores (nacional, CCAA, municipios) en paralelo.
  2. Índices y resumen de productores (una vez cargado todo).
  3. Mosaico nacional + tablas generalizadas para zooms bajos.
  4. Mezcla por clase solo en los territorios con productor propio
     (CCAA -> mc_servicio_regional, municipios -> mc_servicio_local). El resto
     del territorio se rellena desde el nivel superior sin recortar.

Cada territorio se confirma por separado: si se corta la conexión solo se pierde
el territorio en curso y --resume continúa desde ahí.

Uso (lanzar dentro de tmux o con nohup):
  python run_pipeline_sql.py --db mapabasexyz \\
      --datos-base /var/MVT_MapaBaseXYZ/DatosProcesados \\
      --capas aerodromo_pto,edificio_pol --workers 6

  --resume   continúa una ejecución interrumpida (salta lo ya terminado)
  --reset    borra y recrea todos los esquemas mc_* antes de empezar
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

TILEKILN_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = TILEKILN_ROOT / "sql" / "pipeline"
REPO = Path(__file__).resolve().parents[2]
MODELO_FILE = TILEKILN_ROOT / "capas_modelo.json"
NIVELES_MEZCLA = ("regional", "local")


def _load_dotenv() -> None:
    """Carga tilekiln/.env si existe (PGHOST, PGUSER, etc.)."""
    env_file = TILEKILN_ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val


_load_dotenv()

# PostGIS en CNIG está en public_modelo_2025 (solo tipos; sin DDL en ese esquema)
MC_SEARCH_PATH = "public, public_modelo_2025, pg_catalog"

SESSION_SETTINGS = (
    f"SET work_mem = '{os.environ.get('MC_WORK_MEM', '256MB')}'",
    f"SET maintenance_work_mem = '{os.environ.get('MC_MAINTENANCE_WORK_MEM', '1GB')}'",
    "SET synchronous_commit = off",
    "SET jit = off",
    "SET client_min_messages = warning",
)

_print_lock = threading.Lock()
_avisos_sesion: set[str] = set()


def log(msg: str) -> None:
    with _print_lock:
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def fmt_dur(segundos: float) -> str:
    s = int(segundos)
    if s < 60:
        return f"{segundos:.1f}s"
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m}m{s:02d}s"


def _ident(nombre: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", nombre.lower())[:63]


def psql_file(db: str, path: Path) -> None:
    subprocess.run(
        [
            "psql", "-X", "-q", "-d", db,
            "-v", "ON_ERROR_STOP=1",
            "-c", f"SET search_path TO {MC_SEARCH_PATH};",
            "-c", "SET client_min_messages = warning;",
            "-f", str(path),
        ],
        check=True,
        env=os.environ.copy(),
    )


def connect(db: str):
    """Conexión en autocommit con search_path y ajustes de sesión para carga masiva."""
    kw = {"dbname": db or os.environ.get("PGDATABASE")}
    for key, env in (("host", "PGHOST"), ("port", "PGPORT"), ("user", "PGUSER"), ("password", "PGPASSWORD")):
        val = os.environ.get(env)
        if val:
            kw[key] = val
    try:
        conn = psycopg2.connect(
            **kw,
            application_name="mc_pipeline",
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=6,
        )
    except psycopg2.OperationalError as e:
        if "password" in str(e).lower():
            raise SystemExit(
                "Sin contraseña PostgreSQL. Exporta PGPASSWORD, usa ~/.pgpass "
                "o añade PGPASSWORD en tilekiln/.env (no subir a git)."
            ) from e
        raise
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f"SET search_path TO {MC_SEARCH_PATH}")
        for stmt in SESSION_SETTINGS:
            try:
                cur.execute(stmt)
            except psycopg2.Error as e:
                if stmt not in _avisos_sesion:
                    _avisos_sesion.add(stmt)
                    log(f"aviso: no se pudo aplicar «{stmt}»: {(e.pgerror or str(e)).strip()}")
    return conn


class ConnPool:
    """Hilos de trabajo fijos para toda la ejecución, con una conexión por hilo."""

    def __init__(self, db: str, workers: int):
        self.db = db
        self.ex = ThreadPoolExecutor(max_workers=workers)
        self._local = threading.local()
        self._todas: list = []
        self._lock = threading.Lock()

    def get(self):
        conn = getattr(self._local, "conn", None)
        if conn is None or conn.closed:
            conn = connect(self.db)
            self._local.conn = conn
            with self._lock:
                self._todas.append(conn)
        return conn

    def descartar(self) -> None:
        """Cierra la conexión del hilo actual (tras un error de red)."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except psycopg2.Error:
                pass
            self._local.conn = None

    def close(self) -> None:
        self.ex.shutdown(wait=True)
        for conn in self._todas:
            try:
                conn.close()
            except psycopg2.Error:
                pass


def query(pool: ConnPool, q, params=None):
    with pool.get().cursor() as cur:
        cur.execute(q, params)
        return cur.fetchall() if cur.description else []


def scalar(pool: ConnPool, q, params=None):
    rows = query(pool, q, params)
    return rows[0][0] if rows else None


# ---------------------------------------------------------------------------
# Modelo de capas (generado por generate_tilekiln.py)
# ---------------------------------------------------------------------------
def cargar_modelo() -> dict:
    if not MODELO_FILE.is_file():
        log(f"aviso: falta {MODELO_FILE.name}; ejecuta tools/generate_tilekiln.py. "
            "Se usarán solo clase/proveedor y sin generalización.")
        return {}
    return json.loads(MODELO_FILE.read_text(encoding="utf-8"))


def info_capa(modelo: dict, capa: str) -> tuple[list[str], list[int]]:
    info = modelo.get(capa)
    if not info:
        if modelo:
            log(f"aviso: {capa} no está en {MODELO_FILE.name}; atributos clase/proveedor")
        return ["clase", "proveedor"], []
    return list(info["attrs"]), list(info.get("generalizar") or [])


# ---------------------------------------------------------------------------
# Registro de ejecución (para --resume)
# ---------------------------------------------------------------------------
def ultimo_ok(pool: ConnPool, capa: str, fase: str) -> int | None:
    """id del último registro ok de esa fase, o None si el último no fue ok."""
    row = query(
        pool,
        "SELECT id, ok FROM mc_meta.run_log WHERE capa = %s AND fase = %s ORDER BY id DESC LIMIT 1",
        (capa, fase),
    )
    if row and row[0][1]:
        return row[0][0]
    return None


def registrar(pool: ConnPool, capa: str, fase: str, ok: bool, detalle: str, inicio: datetime) -> None:
    try:
        query(
            pool,
            """INSERT INTO mc_meta.run_log (capa, fase, detalle, started_at, finished_at, ok)
               VALUES (%s, %s, %s, %s, now(), %s)""",
            (capa, fase, detalle[:4000], inicio, ok),
        )
    except psycopg2.Error as e:
        pool.descartar()
        log(f"aviso: no se pudo escribir run_log ({capa}/{fase}): {e}")


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def ogr2ogr_staging(db: str, fgb: Path, destino: str, s_srs: str | None) -> None:
    """FGB -> tabla UNLOGGED sin índice en mc_staging, vía COPY y transacciones grandes."""
    cmd = [
        "ogr2ogr", "--config", "PG_USE_COPY", "YES",
        "-f", "PostgreSQL", f"PG:dbname={db}", str(fgb),
        "-nln", destino, "-overwrite",
        "-t_srs", "EPSG:3857",
        "-dim", "2", "-nlt", "PROMOTE_TO_MULTI",
        "-lco", "GEOMETRY_NAME=the_geom", "-lco", "FID=ogc_fid",
        "-lco", "SPATIAL_INDEX=NO", "-lco", "UNLOGGED=ON", "-lco", "PRECISION=NO",
    ]
    # Primero con el SRS que declara el fichero; si no declara (o falla), con s_srs forzado.
    # -skipfailures obliga a una transacción por elemento: solo como último recurso.
    intentos = [["-gt", "65536"]]
    if s_srs:
        intentos.append(["-s_srs", s_srs, "-gt", "65536"])
    intentos.append((["-s_srs", s_srs] if s_srs else []) + ["-skipfailures"])
    for i, extra in enumerate(intentos):
        r = subprocess.run(cmd + extra, capture_output=True, text=True, env=os.environ.copy())
        if r.returncode == 0:
            if i:
                log(f"aviso: {fgb} cargado con {' '.join(extra)}")
            return
        error = r.stderr.strip()[-300:]
    raise RuntimeError(f"ogr2ogr {fgb}: {error}")


def cargar_fgb(pool: ConnPool, db: str, capa: str, attrs: list[str], fgb: Path,
               ambito: str, codigo: str, s_srs: str | None) -> int:
    tabla_stg = _ident(f"s_{capa}_{ambito}_{codigo}")
    ogr2ogr_staging(db, fgb, f"mc_staging.{tabla_stg}", s_srs)

    conn = pool.get()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT column_name, udt_name FROM information_schema.columns
               WHERE table_schema = 'mc_staging' AND table_name = %s""",
            (tabla_stg,),
        )
        cols = dict(cur.fetchall())
        geom = next((c for c, t in cols.items() if t == "geometry"), None)
        if geom is None:
            cur.execute(sql.SQL("DROP TABLE IF EXISTS mc_staging.{}").format(sql.Identifier(tabla_stg)))
            return 0
        comunes = [a for a in attrs if a in cols]
        faltan = [a for a in attrs if a not in cols]
        if faltan and ambito == "nacional":
            log(f"  {capa}: el FGB nacional no trae {faltan} (quedan a NULL)")

        destino = sql.Identifier("mc_productores", f"{capa}_{ambito}")
        col_dest = sql.SQL(", ").join(
            [sql.Identifier("the_geom"), sql.Identifier("ambito"), sql.Identifier("codigo")]
            + [sql.Identifier(a) for a in comunes]
        )
        col_src = sql.SQL(", ").join(
            [sql.SQL("mc_meta.geom_carga(t.{}) AS g").format(sql.Identifier(geom)),
             sql.Literal(ambito), sql.Literal(codigo)]
            + [sql.SQL("t.{}::text").format(sql.Identifier(a)) for a in comunes]
        )
        cur.execute(
            sql.SQL(
                "INSERT INTO {dest} ({cols}) SELECT * FROM (SELECT {src} FROM mc_staging.{stg} t) q "
                "WHERE q.g IS NOT NULL"
            ).format(dest=destino, cols=col_dest, src=col_src, stg=sql.Identifier(tabla_stg))
        )
        n = cur.rowcount
        cur.execute(sql.SQL("DROP TABLE IF EXISTS mc_staging.{}").format(sql.Identifier(tabla_stg)))
    return n


CARPETA_VALIDA = {"regional": re.compile(r"^\d{2}$"), "local": re.compile(r"^\d{5}$")}
_carpetas_avisadas: set[Path] = set()


def fuentes_capa(datos_base: Path, capa: str) -> list[tuple[Path, str, str]]:
    prod = datos_base / "productores"
    fuentes = []
    fgb = prod / "nacional" / "00" / f"{capa}.fgb"
    if fgb.exists():
        fuentes.append((fgb, "nacional", "00"))
    for nivel, carpeta in (("regional", "com_aut"), ("local", "municipios")):
        for d in sorted((prod / carpeta).glob("*")):
            if not d.is_dir():
                continue
            # copias tipo 17_202407 o 16_completo no son un territorio
            if not CARPETA_VALIDA[nivel].match(d.name):
                if d not in _carpetas_avisadas:
                    _carpetas_avisadas.add(d)
                    log(f"aviso: se ignora la carpeta {carpeta}/{d.name} (no es un código de territorio)")
                continue
            fgb = d / f"{capa}.fgb"
            if fgb.exists():
                fuentes.append((fgb, nivel, d.name))
    return fuentes


def cargar_capa(pool: ConnPool, db: str, capa: str, attrs: list[str], generalizar: list[int],
                datos_base: Path, workers: int, s_srs: str | None) -> str:
    fuentes = fuentes_capa(datos_base, capa)
    if not fuentes:
        raise RuntimeError(f"no hay FGB de {capa} en {datos_base / 'productores'}")
    perfil = scalar(pool, "SELECT mc_meta.sugerir_perfil(%s)", (capa,))
    query(pool, "SELECT mc_meta.ensure_capa_tables(%s, %s, %s, %s)", (capa, attrs, perfil, generalizar))

    mb = sum(f.stat().st_size for f, _, _ in fuentes) / 1e6
    log(f"{capa}: carga de {len(fuentes)} FGB ({mb:,.0f} MB) con {workers} workers")
    t0 = time.monotonic()
    total = 0
    hechos = 0
    # el nacional (el más grande) va primero para que arranque cuanto antes
    futuros = {
        pool.ex.submit(cargar_fgb, pool, db, capa, attrs, f, amb, cod, s_srs): (f, amb, cod)
        for f, amb, cod in fuentes
    }
    errores = []
    for fut in as_completed(futuros):
        f, amb, cod = futuros[fut]
        try:
            n = fut.result()
        except Exception as e:  # noqa: BLE001 — se esperan todos y se falla al final
            errores.append(f"{amb}/{cod}: {e}")
            log(f"  ERROR {capa} {amb}/{cod}: {e}")
            continue
        total += n
        hechos += 1
        if n == 0:
            log(f"  aviso: {f} no aportó ningún elemento (¿vacío o SRS erróneo? revisa con ogrinfo -so)")
        log(f"  {capa} {amb}/{cod}: {n:,} elementos ({hechos}/{len(fuentes)}, {fmt_dur(time.monotonic() - t0)})")
    if errores:
        raise RuntimeError(f"{len(errores)} FGB con error: {'; '.join(errores[:5])}")

    t1 = time.monotonic()
    log(f"{capa}: índices y estadísticas…")
    msg = scalar(pool, "SELECT mc_meta.finalizar_carga(%s)", (capa,))
    log(f"{capa}: carga lista: {msg} (ficheros {fmt_dur(t1 - t0)}, índices {fmt_dur(time.monotonic() - t1)})")
    return msg


# ---------------------------------------------------------------------------
# Procesado
# ---------------------------------------------------------------------------
def _procesar_territorio(pool: ConnPool, capa: str, nivel: str, codigo: str) -> tuple[str, float]:
    t0 = time.monotonic()
    try:
        msg = scalar(pool, "SELECT mc_meta.procesar_territorio(%s, %s, %s)", (capa, nivel, codigo))
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        pool.descartar()
        raise
    return msg, time.monotonic() - t0


def procesar_nivel(pool: ConnPool, capa: str, nivel: str, resume: bool) -> int:
    for (cod,) in query(pool, "SELECT mc_meta.codigos_sin_mascara(%s, %s)", (capa, nivel)):
        log(f"  aviso: {capa} {nivel}/{cod} tiene productor pero no máscara Voronoi: se ignora")

    pendientes = [c for c, _ in query(
        pool, "SELECT codigo, n FROM mc_meta.territorios_pendientes_ordenados(%s, %s)", (capa, nivel)
    )]
    if resume and pendientes:
        hechos = {c for (c,) in query(
            pool,
            sql.SQL("SELECT DISTINCT codigo FROM mc_generados.{} WHERE ambito = %s").format(sql.Identifier(capa)),
            (nivel,),
        )}
        saltar = [c for c in pendientes if c in hechos]
        if saltar:
            log(f"  {capa} {nivel}: {len(saltar)} territorios ya hechos (resume)")
        pendientes = [c for c in pendientes if c not in hechos]

    if not pendientes:
        log(f"  {capa} {nivel}: sin territorios con productor propio")
        return 0

    log(f"  {capa} {nivel}: {len(pendientes)} territorios con productor propio")
    t0 = time.monotonic()
    errores = []
    futuros = {pool.ex.submit(_procesar_territorio, pool, capa, nivel, c): c for c in pendientes}
    for i, fut in enumerate(as_completed(futuros), 1):
        cod = futuros[fut]
        try:
            msg, dur = fut.result()
        except Exception as e:  # noqa: BLE001 — se reintenta con --resume
            errores.append(cod)
            log(f"  ERROR {capa} {nivel}/{cod}: {e}".rstrip())
            continue
        transcurrido = time.monotonic() - t0
        eta = transcurrido / i * (len(pendientes) - i)
        log(f"  {capa} {nivel}/{cod} {fmt_dur(dur)} {msg} [{i}/{len(pendientes)}, ETA {fmt_dur(eta)}]")
    if errores:
        raise RuntimeError(f"{len(errores)} territorios {nivel} con error: {', '.join(errores[:20])}")
    return len(pendientes)


def procesar_capa(pool: ConnPool, capa: str, resume: bool) -> str:
    t0 = time.monotonic()
    if not resume:
        query(pool, sql.SQL("TRUNCATE mc_generados.{}").format(sql.Identifier(capa)))

    log(f"{capa}: mosaico nacional…")
    n_nac = scalar(pool, "SELECT mc_meta.build_servicio_nacional(%s)", (capa,))
    log(f"{capa}: nacional {n_nac:,} elementos ({fmt_dur(time.monotonic() - t0)})")

    resumen = [f"nacional={n_nac}"]
    for nivel in NIVELES_MEZCLA:
        n_terr = procesar_nivel(pool, capa, nivel, resume)
        t1 = time.monotonic()
        n = scalar(pool, "SELECT mc_meta.build_servicio_mosaico(%s, %s)", (capa, nivel))
        if n:
            log(f"{capa}: mosaico {nivel} {n:,} elementos ({fmt_dur(time.monotonic() - t1)})")
        else:
            log(f"{capa}: {nivel} = vista del nivel superior")
        resumen.append(f"{nivel}={n} (territorios={n_terr})")

    t1 = time.monotonic()
    gen = scalar(pool, "SELECT mc_meta.generalizar_capa(%s)", (capa,))
    log(f"{capa}: generalización {gen} ({fmt_dur(time.monotonic() - t1)})")
    resumen.append(gen)
    if scalar(pool, "SELECT mc_meta.purgar_generados(%s)", (capa,)):
        resumen.append("generados_purgados")
    resumen.append(f"elapsed={fmt_dur(time.monotonic() - t0)}")
    return " ".join(resumen)


# ---------------------------------------------------------------------------
# Máscaras y territorios
# ---------------------------------------------------------------------------
def cargar_mascara(pool: ConnPool, db: str, fgb: Path, tipo: str) -> int:
    tabla_stg = f"s_mask_{tipo}"
    ogr2ogr_staging(db, fgb, f"mc_staging.{tabla_stg}", "EPSG:4258")
    conn = pool.get()
    with conn.cursor() as cur:
        cur.execute(
            """SELECT column_name, udt_name FROM information_schema.columns
               WHERE table_schema = 'mc_staging' AND table_name = %s""",
            (tabla_stg,),
        )
        cols = dict(cur.fetchall())
        geom = next(c for c, t in cols.items() if t == "geometry")
        code_col = "codigo" if "codigo" in cols else next(c for c in cols if c not in (geom, "ogc_fid"))
        g = sql.SQL("ST_Multi(ST_MakeValid(ST_Force2D(t.{})))").format(sql.Identifier(geom))
        c = sql.SQL("trim(t.{}::text)").format(sql.Identifier(code_col))
        stg = sql.Identifier("mc_staging", tabla_stg)
        if tipo == "comunidades":
            cur.execute("TRUNCATE mc_mascaras.voronoi_comunidades")
            cur.execute(sql.SQL(
                """INSERT INTO mc_mascaras.voronoi_comunidades (codigo, the_geom)
                   SELECT CASE WHEN length({c}) >= 4 THEN substring({c} from 3 for 2)
                               ELSE lpad({c}, 2, '0') END, {g}
                     FROM {stg} t WHERE t.{geom} IS NOT NULL"""
            ).format(c=c, g=g, stg=stg, geom=sql.Identifier(geom)))
        else:
            ine = sql.SQL("right(regexp_replace({c}, '[^0-9]', '', 'g'), 5)").format(c=c)
            cur.execute("TRUNCATE mc_mascaras.voronoi_municipios")
            cur.execute(sql.SQL(
                """INSERT INTO mc_mascaras.voronoi_municipios (codigo, codigo_ccaa, the_geom)
                   SELECT {ine}, NULL, {g} FROM {stg} t WHERE t.{geom} IS NOT NULL"""
            ).format(ine=ine, g=g, stg=stg, geom=sql.Identifier(geom)))
        n = cur.rowcount
        cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(stg))
        cur.execute(sql.SQL("ANALYZE mc_mascaras.{}").format(sql.Identifier(f"voronoi_{tipo}")))
    return n


def cargar_municipios_meta(pool: ConnPool, xlsx: Path) -> None:
    """INE -> CCAA desde municipios.xlsx (cod_com_aut)."""
    import openpyxl

    wb = openpyxl.load_workbook(xlsx, read_only=True)
    rows = list(wb.active.iter_rows(values_only=True))
    if not rows:
        return
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]

    def idx(*names):
        return next((headers.index(n) for n in names if n in headers), None)

    i_ine, i_ccaa, i_nom = idx("codigo_ine_mun", "codigo"), idx("cod_com_aut", "codigo_ccaa"), idx("nombre")
    if i_ine is None or i_ccaa is None:
        log(f"aviso: no se pudieron mapear columnas en {xlsx}: {headers}")
        return

    def norm(v, ancho):
        if isinstance(v, (int, float)):
            return str(int(v)).zfill(ancho)
        s = str(v).strip()
        return s.zfill(ancho) if s.isdigit() else s[-ancho:]

    municipios = {}
    for row in rows[1:]:
        if not row or row[i_ine] is None or row[i_ccaa] is None:
            continue
        municipios[norm(row[i_ine], 5)] = (row[i_nom] if i_nom is not None else None, norm(row[i_ccaa], 2))

    conn = pool.get()
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO mc_meta.territorios_ccaa (codigo) VALUES %s ON CONFLICT DO NOTHING",
            sorted({(ccaa,) for _, ccaa in municipios.values()}),
        )
        execute_values(
            cur,
            """INSERT INTO mc_meta.territorios_municipio (codigo, nombre, codigo_ccaa) VALUES %s
               ON CONFLICT (codigo) DO UPDATE SET codigo_ccaa = EXCLUDED.codigo_ccaa,
                   nombre = COALESCE(EXCLUDED.nombre, mc_meta.territorios_municipio.nombre)""",
            [(ine, nom, ccaa) for ine, (nom, ccaa) in municipios.items()],
            page_size=2000,
        )
        cur.execute(
            """UPDATE mc_mascaras.voronoi_municipios v SET codigo_ccaa = t.codigo_ccaa
                 FROM mc_meta.territorios_municipio t WHERE v.codigo = t.codigo"""
        )
    log(f"territorios: {len(municipios):,} municipios desde {xlsx.name}")


def cargar_territorios(pool: ConnPool, db: str, datos_base: Path | None, forzar: bool) -> None:
    n_ccaa = scalar(pool, "SELECT count(*) FROM mc_mascaras.voronoi_comunidades")
    n_mun = scalar(pool, "SELECT count(*) FROM mc_mascaras.voronoi_municipios")
    if not forzar and n_ccaa and n_mun:
        log(f"máscaras ya cargadas ({n_ccaa} CCAA, {n_mun:,} municipios)")
        return
    lib = (datos_base / "lib") if datos_base else None
    if lib is None or not (lib / "voronoi_comunidades.fgb").exists():
        lib = REPO / "scripts/teselas/3ProcesoUnionDatos/lib"
    log(f"máscaras desde {lib}")
    n_ccaa = cargar_mascara(pool, db, lib / "voronoi_comunidades.fgb", "comunidades")
    n_mun = cargar_mascara(pool, db, lib / "voronoi_municipios.fgb", "municipios")
    log(f"máscaras: {n_ccaa} CCAA, {n_mun:,} municipios")
    if (lib / "municipios.xlsx").exists():
        cargar_municipios_meta(pool, lib / "municipios.xlsx")
    else:
        log("aviso: sin municipios.xlsx; la CCAA de cada municipio queda sin asignar")


# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------
def imprimir_resumen(pool: ConnPool, capas: list[str]) -> None:
    filas = query(
        pool,
        """SELECT c.relname, n.nspname, c.relkind, c.reltuples::bigint,
                  pg_total_relation_size(c.oid)
             FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname IN ('mc_servicio_nacional', 'mc_servicio_regional', 'mc_servicio_local')
              AND c.relkind IN ('r', 'v')
              AND c.relname = ANY (%s || ARRAY(SELECT x || '_g' || z FROM unnest(%s::text[]) x,
                                                generate_series(0, 13) z))""",
        (capas, capas),
    )
    por_capa: dict[str, list[str]] = {}
    for rel, sch, kind, tuplas, size in filas:
        base = re.sub(r"_g\d+$", "", rel)
        etiqueta = sch.replace("mc_servicio_", "") + rel[len(base):]
        valor = "vista" if kind == "v" else f"≈{max(tuplas, 0):,} ({size / 1e6:,.0f} MB)"
        por_capa.setdefault(base, []).append(f"{etiqueta}={valor}")
    log("resumen de servicio:")
    for capa in capas:
        log(f"  {capa}: {', '.join(sorted(por_capa.get(capa, ['sin tablas'])))}")


def main():
    ap = argparse.ArgumentParser(description="Pipeline SQL Mapa Ciudadano (equiv. Proceso 3)")
    ap.add_argument("--db", required=True, help="nombre PostgreSQL (p. ej. mapabasexyz)")
    ap.add_argument("--datos-base", type=Path, help="raíz con productores/ y lib/")
    ap.add_argument("--capas", default="", help="lista separada por comas (por defecto, todas las del nacional)")
    ap.add_argument("--workers", type=int, default=int(os.environ.get("MC_WORKERS", "4")),
                    help="conexiones en paralelo (carga y territorios). Por defecto 4")
    ap.add_argument("--s-srs", default="EPSG:4258",
                    help="SRS de los FGB de productores; 'auto' para leerlo del fichero")
    ap.add_argument("--resume", action="store_true", help="salta capas/territorios ya terminados")
    ap.add_argument("--reset", action="store_true", help="BORRA todos los esquemas mc_* antes de empezar")
    ap.add_argument("--recargar-mascaras", action="store_true", help="vuelve a cargar las Voronoi")
    ap.add_argument("--skip-load", action="store_true")
    ap.add_argument("--skip-process", action="store_true")
    args = ap.parse_args()
    s_srs = None if args.s_srs.lower() == "auto" else args.s_srs
    t_inicio = time.monotonic()

    if args.reset:
        log("RESET: borrando esquemas mc_*")
        psql_file(args.db, SQL_DIR / "00_reset.sql")
    log("aplicando 00_schemas.sql y 01_funciones.sql")
    psql_file(args.db, SQL_DIR / "00_schemas.sql")
    psql_file(args.db, SQL_DIR / "01_funciones.sql")

    pool = ConnPool(args.db, args.workers)
    modelo = cargar_modelo()
    capas = [c.strip() for c in args.capas.split(",") if c.strip()]
    if not args.skip_load:
        if not args.datos_base:
            sys.exit("Indica --datos-base (ruta a DatosProcesados o equivalente CNIG)")
        if not capas:
            capas = sorted(p.stem for p in (args.datos_base / "productores" / "nacional" / "00").glob("*.fgb"))
    if not capas:
        sys.exit("Sin capas: usa --capas o --datos-base")

    if not args.skip_process or not args.skip_load:
        cargar_territorios(pool, args.db, args.datos_base, args.recargar_mascaras or args.reset)

    log(f"{len(capas)} capas, {args.workers} workers{' (resume)' if args.resume else ''}")
    fallidas = []
    for i, capa in enumerate(capas, 1):
        log(f"=== [{i}/{len(capas)}] {capa} ===")
        attrs, generalizar = info_capa(modelo, capa)
        try:
            id_carga = ultimo_ok(pool, capa, "carga")
            if not args.skip_load:
                if args.resume and id_carga:
                    log(f"{capa}: carga ya hecha (resume)")
                else:
                    inicio = datetime.now()
                    try:
                        msg = cargar_capa(pool, args.db, capa, attrs, generalizar,
                                          args.datos_base, args.workers, s_srs)
                    except Exception as e:
                        registrar(pool, capa, "carga", False, str(e), inicio)
                        raise
                    registrar(pool, capa, "carga", True, msg, inicio)
                    id_carga = ultimo_ok(pool, capa, "carga")

            if not args.skip_process:
                id_proc = ultimo_ok(pool, capa, "completa")
                if args.resume and id_proc and (id_carga is None or id_proc > id_carga):
                    log(f"{capa}: procesado ya hecho (resume)")
                    continue
                inicio = datetime.now()
                try:
                    msg = procesar_capa(pool, capa, args.resume)
                except Exception as e:
                    registrar(pool, capa, "completa", False, str(e), inicio)
                    raise
                registrar(pool, capa, "completa", True, msg, inicio)
                log(f"{capa}: OK {msg}")
        except Exception as e:  # noqa: BLE001 — se sigue con la siguiente capa
            fallidas.append(capa)
            log(f"ERROR en {capa}: {e}")
            pool.descartar()

    vacias = sum(
        scalar(pool, "SELECT mc_meta.asegurar_servicio_vacio(%s, %s, %s)",
               (capa, info["attrs"], info.get("generalizar") or []))
        for capa, info in modelo.items()
    )
    if vacias:
        log(f"{vacias} tablas de servicio vacías creadas para capas aún sin cargar (Tilekiln no falla)")

    imprimir_resumen(pool, capas)
    pool.close()
    log(f"fin en {fmt_dur(time.monotonic() - t_inicio)}"
        + (f"; capas con error: {', '.join(fallidas)} (relanza con --resume)" if fallidas else ""))
    sys.exit(1 if fallidas else 0)


if __name__ == "__main__":
    main()
