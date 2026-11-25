#!/usr/bin/env python3
"""Mide el coste de las teselas: por capa (SQL directo) o de punta a punta (HTTP).

Sirve para comparar antes/después (PG11 → PG18, índices, config_rapido...) y
para encontrar la capa que hace lenta una tesela.

Modo SQL (por defecto): genera el SQL de cada capa con el propio Tilekiln
(mismas plantillas que el servidor) y lo ejecuta contra la BD (variables PG*).
  ../.venv/bin/python bench_teselas.py --config ../config.yaml
  ../.venv/bin/python bench_teselas.py --config ../config_rapido.yaml --zooms 10,14,17
  ../.venv/bin/python bench_teselas.py --explain edificio_pol --tile 14/8026/6176

Modo HTTP: pide las teselas al servicio (tilekiln dev/live) y mide tiempo y tamaño.
  ../.venv/bin/python bench_teselas.py --http http://127.0.0.1:8099

--csv fichero.csv guarda el detalle para el informe.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import statistics
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Zonas de prueba: ciudad (denso), periurbano y rural
ZONAS = {
    "madrid": (-3.7038, 40.4168),
    "sevilla": (-5.9845, 37.3891),
    "barcelona": (2.1734, 41.3851),
    "valencia": (-0.3763, 39.4699),
    "teruel_rural": (-1.1065, 40.3457),
}
ZOOMS_DEF = (6, 8, 10, 12, 13, 14, 15, 16, 17)


def load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip("'\"")
        if k and k not in os.environ:
            os.environ[k] = v


def lonlat_to_tile(lon: float, lat: float, z: int) -> tuple[int, int]:
    n = 2 ** z
    x = int((lon + 180.0) / 360.0 * n)
    lat_r = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def lista_teselas(zonas: list[str], zooms: list[int]) -> list[tuple[str, int, int, int]]:
    out = []
    for nombre in zonas:
        lon, lat = ZONAS[nombre]
        for z in zooms:
            x, y = lonlat_to_tile(lon, lat, z)
            out.append((nombre, z, x, y))
    return out


def pct(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    vals = sorted(vals)
    k = min(len(vals) - 1, max(0, int(round(p / 100.0 * (len(vals) - 1)))))
    return vals[k]


def bench_sql(args, teselas) -> list[dict]:
    import psycopg
    import tilekiln
    from tilekiln.tile import Tile

    os.chdir(Path(args.config).resolve().parent)
    config = tilekiln.load_config(Path(args.config).name)
    capas = [lyr for lyr in config.layers if not args.capas or lyr.id in args.capas]
    conn = psycopg.connect(application_name="mc_bench", autocommit=True)
    conn.execute("SET default_transaction_read_only = true")
    if args.statement_timeout:
        conn.execute(f"SET statement_timeout = '{int(args.statement_timeout)}s'")
    filas = []
    for rep in range(args.repeticiones):
        for zona, z, x, y in teselas:
            tile = Tile(z, x, y)
            for lyr in capas:
                q = lyr.render_sql(tile)
                if q is None:
                    continue
                t0 = time.perf_counter()
                try:
                    with conn.cursor() as cur:
                        cur.execute(q, binary=True)
                        data = cur.fetchone()[0] or b""
                    err = ""
                except psycopg.Error as e:
                    data, err = b"", str(e).strip().splitlines()[0][:200]
                    conn.rollback() if not conn.autocommit else None
                ms = (time.perf_counter() - t0) * 1000
                filas.append({"rep": rep, "zona": zona, "tile": f"{z}/{x}/{y}", "z": z,
                              "capa": lyr.id, "ms": round(ms, 2), "bytes": len(data), "error": err})
    conn.close()
    return filas


def bench_http(args, teselas) -> list[dict]:
    # Sin proxy: en la 105 el proxy del entorno devuelve 403 a 127.0.0.1
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    base = args.http.rstrip("/")
    filas = []
    for rep in range(args.repeticiones):
        for zona, z, x, y in teselas:
            url = f"{base}/tiles/{z}/{x}/{y}.mvt"
            t0 = time.perf_counter()
            try:
                with opener.open(url, timeout=args.statement_timeout or 120) as r:
                    data = r.read()
                err = ""
            except Exception as e:  # noqa: BLE001
                data, err = b"", str(e)[:200]
            ms = (time.perf_counter() - t0) * 1000
            filas.append({"rep": rep, "zona": zona, "tile": f"{z}/{x}/{y}", "z": z,
                          "capa": "(tesela)", "ms": round(ms, 2), "bytes": len(data), "error": err})
    return filas


def resumen(filas: list[dict], top: int) -> None:
    errores = [f for f in filas if f["error"]]
    # Por tesela (suma de capas en modo SQL)
    por_tile: dict[tuple, list] = defaultdict(lambda: [0.0, 0])
    for f in filas:
        k = (f["rep"], f["zona"], f["tile"], f["z"])
        por_tile[k][0] += f["ms"]
        por_tile[k][1] += f["bytes"]
    por_z: dict[int, list] = defaultdict(list)
    tam_z: dict[int, list] = defaultdict(list)
    for (_, _, _, z), (ms, b) in por_tile.items():
        por_z[z].append(ms)
        tam_z[z].append(b)
    print("\n== Por zoom (ms por tesela) ==")
    print(f"{'z':>3} {'n':>4} {'mediana':>9} {'p95':>9} {'max':>9} {'KB med':>8}")
    for z in sorted(por_z):
        v = por_z[z]
        print(f"{z:>3} {len(v):>4} {statistics.median(v):>9.1f} {pct(v, 95):>9.1f} "
              f"{max(v):>9.1f} {statistics.median(tam_z[z]) / 1024:>8.1f}")
    todas = [ms for ms, _ in por_tile.values()]
    if todas:
        print(f"TOTAL {len(todas)} teselas: mediana {statistics.median(todas):.1f} ms, "
              f"p95 {pct(todas, 95):.1f} ms, max {max(todas):.1f} ms")

    por_capa: dict[str, list] = defaultdict(list)
    for f in filas:
        if f["capa"] != "(tesela)":
            por_capa[f["capa"]].append(f["ms"])
    if por_capa:
        print(f"\n== Top {top} capas más caras (ms acumulados) ==")
        orden = sorted(por_capa.items(), key=lambda kv: -sum(kv[1]))[:top]
        print(f"{'capa':<40} {'total':>9} {'max':>9} {'consultas':>9}")
        for capa, v in orden:
            print(f"{capa:<40} {sum(v):>9.1f} {max(v):>9.1f} {len(v):>9}")
    if errores:
        print(f"\n!! {len(errores)} consultas con error. Primeras:")
        vistos = set()
        for f in errores:
            k = (f["capa"], f["error"])
            if k in vistos:
                continue
            vistos.add(k)
            print(f"  {f['capa']} {f['tile']}: {f['error']}")
            if len(vistos) >= 10:
                break


def explain(args) -> None:
    import psycopg
    import tilekiln
    from tilekiln.tile import Tile

    os.chdir(Path(args.config).resolve().parent)
    config = tilekiln.load_config(Path(args.config).name)
    lyr = next((l for l in config.layers if l.id == args.explain), None)
    if lyr is None:
        sys.exit(f"capa {args.explain} no está en {args.config}")
    z, x, y = (int(p) for p in args.tile.split("/"))
    q = lyr.render_sql(Tile(z, x, y))
    if q is None:
        sys.exit(f"{args.explain} no se sirve en z{z} ({lyr.minzoom}-{lyr.maxzoom})")
    print(q)
    print("-" * 78)
    with psycopg.connect(autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, BUFFERS, SETTINGS) " + q)
        for (line,) in cur.fetchall():
            print(line)


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "config.yaml"))
    ap.add_argument("--http", help="URL base del servicio (p.ej. http://127.0.0.1:8099)")
    ap.add_argument("--zonas", default="madrid,sevilla,teruel_rural",
                    help=f"lista de {','.join(ZONAS)} o 'todas'")
    ap.add_argument("--zooms", default=",".join(map(str, ZOOMS_DEF)))
    ap.add_argument("--capas", default="", help="solo estas capas (coma)")
    ap.add_argument("--repeticiones", type=int, default=2,
                    help="la 1ª pasada lee de disco, la 2ª mide con caché caliente")
    ap.add_argument("--statement-timeout", type=int, default=60, help="segundos (0 = sin límite)")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--explain", help="capa a la que hacer EXPLAIN ANALYZE")
    ap.add_argument("--tile", default="14/8023/6177", help="z/x/y para --explain")
    args = ap.parse_args()
    args.capas = {c.strip() for c in args.capas.split(",") if c.strip()}

    if args.explain:
        explain(args)
        return
    zonas = list(ZONAS) if args.zonas == "todas" else [z.strip() for z in args.zonas.split(",") if z.strip()]
    zooms = [int(z) for z in args.zooms.split(",") if z.strip()]
    teselas = lista_teselas(zonas, zooms)
    modo = f"HTTP {args.http}" if args.http else f"SQL {args.config}"
    print(f"{modo}: {len(teselas)} teselas x {args.repeticiones} pasadas, BD={os.environ.get('PGDATABASE')}")
    t0 = time.perf_counter()
    filas = bench_http(args, teselas) if args.http else bench_sql(args, teselas)
    print(f"tiempo total {time.perf_counter() - t0:.1f} s")
    # Resumen con la última pasada (caché caliente) si hay más de una
    ultima = max(f["rep"] for f in filas) if filas else 0
    resumen([f for f in filas if f["rep"] == ultima], args.top)
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
            w.writeheader()
            w.writerows(filas)
        print(f"\ndetalle: {args.csv}")


if __name__ == "__main__":
    main()
