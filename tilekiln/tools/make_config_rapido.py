#!/usr/bin/env python3
"""Genera config_rapido.yaml solo con capas que tienen filas en servicio.

Cada tesela de Tilekiln ejecuta 1 SQL por capa del config. Con 84 capas
(casi todas vacías) el mapa va lento aunque el GiST esté perfecto.

Uso en la 105 (venv + .env):
  python tools/make_config_rapido.py --db mapabasexyz
  # reiniciar tilekiln con --config config_rapido.yaml
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


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


def capas_con_datos(db: str) -> set[str]:
    import psycopg2

    kw = {"dbname": db}
    for key, env in (("host", "PGHOST"), ("port", "PGPORT"), ("user", "PGUSER"), ("password", "PGPASSWORD")):
        if os.environ.get(env):
            kw[key] = os.environ[env]
    conn = psycopg2.connect(**kw)
    conn.autocommit = True
    capas: set[str] = set()
    with conn.cursor() as cur:
        cur.execute("SET search_path TO public, public_modelo_2025, pg_catalog")
        cur.execute(
            """
            SELECT c.relname
              FROM pg_class c
              JOIN pg_namespace n ON n.oid = c.relnamespace
             WHERE n.nspname = 'mc_servicio_nacional'
               AND c.relkind = 'r'
               AND c.relname !~ '_g[0-9]+$'
               AND c.reltuples > 0
            """
        )
        for (name,) in cur.fetchall():
            capas.add(name)
        # también las que acabaron OK en run_log (por si reltuples aún es -1)
        cur.execute(
            """
            SELECT DISTINCT capa FROM mc_meta.run_log
             WHERE fase = 'completa' AND ok AND capa IS NOT NULL
            """
        )
        for (name,) in cur.fetchall():
            capas.add(name)
    conn.close()
    return capas


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.environ.get("PGDATABASE", "mapabasexyz"))
    ap.add_argument("--in", dest="src", type=Path, default=ROOT / "config.yaml")
    ap.add_argument("--out", type=Path, default=ROOT / "config_rapido.yaml")
    ap.add_argument("--capas", default="", help="lista forzada (coma); si vacía, lee la BD")
    args = ap.parse_args()

    if args.capas.strip():
        keep = {c.strip() for c in args.capas.split(",") if c.strip()}
    else:
        keep = capas_con_datos(args.db)

    cfg = yaml.safe_load(args.src.read_text(encoding="utf-8"))
    layers = cfg.get("vector_layers") or {}
    before = len(layers)
    cfg["vector_layers"] = {k: v for k, v in layers.items() if k in keep}
    after = len(cfg["vector_layers"])
    if after == 0:
        sys.exit("Ninguna capa seleccionada; aborto")

    meta = cfg.setdefault("metadata", {})
    meta["id"] = (meta.get("id") or "mapa_ciudadano") + "_rapido"
    meta["name"] = (meta.get("name") or "Mapa Ciudadano") + " (rápido)"
    meta["description"] = (
        f"Subset {after}/{before} capas con datos en mc_servicio_* — demo rendimiento"
    )

    args.out.write_text(
        yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"OK {args.out}: {after} capas (de {before})")
    print("Capas:", ", ".join(sorted(cfg["vector_layers"])))


if __name__ == "__main__":
    main()
