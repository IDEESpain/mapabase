#!/usr/bin/env python3
"""Tandas de carga de capas para run_pipeline_sql.py (orden de prioridad visual).

  python tandas.py                      # lista tandas y capas
  python tandas.py --db mapabasexyz     # + estado de cada capa en la BD
  python tandas.py capas 1              # imprime "a,b,c" para --capas
  python tandas.py capas pendientes --db mapabasexyz   # todas las no procesadas aún

Uso típico (en tilekiln/tools, dentro de tmux o con nohup):
  ../.venv/bin/python run_pipeline_sql.py --db mapabasexyz \\
     --datos-base /var/MVT_MapaBaseXYZ/DatosProcesados \\
     --capas "$(../.venv/bin/python tandas.py capas 1)" --workers 6 2>&1 | tee -a pipeline.log
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (nombre, descripción, capas). Las capas del modelo no listadas van a la tanda "resto".
TANDAS = [
    ("1", "Base y límites (visibles desde z0, ligeras)", [
        "tierra_firme_pol", "comunidad_autonoma_pol", "provincia_pol", "municipio_pol",
        "linea_limite_lin", "contexto_territorios_pol", "contexto_territorios_lin",
    ]),
    ("2", "Red de transporte principal", [
        "autopista_lin", "autovia_lin", "carretera_general_lin",
        "carretera_autonomica_1er_nivel_lin", "carretera_autonomica_2do_nivel_lin",
        "carretera_autonomica_3er_nivel_lin", "carretera_otros_lin", "via_servicio_lin",
        "ferrocarril_lin", "contexto_carreteras_lin", "contexto_ferrocarril_lin",
        "peaje_pto", "peaje_pol", "area_servicio_pol", "aerodromo_pol",
        "estacion_ferrocarril_pto", "estacion_ferrocarril_pol",
        "estacion_autobus_pto", "estacion_autobus_pol", "puerto_pto", "puerto_pol",
    ]),
    ("3", "Agua", [
        "hidrografia_lin", "hidrografia_pol", "lamina_agua_pol",
        "contexto_hidrografia_lin", "contexto_lamina_agua_pol",
    ]),
    ("4", "Urbano y usos del suelo", [
        "nucleo_urbano_pol", "manzana_pol", "via_urbana_lin",
        "zona_verde_pol", "zona_industrial_pol", "zona_dotacional_pol",
        "zona_militar_pol", "zona_protegida_pol", "zona_protegida_pto",
        "espacio_natural_protegido_pol", "aparcamiento_pol", "aparcamiento_pto",
    ]),
    ("5", "Rótulos", [
        "nombre_division_administrativa_pto", "nombre_poblacion_construccion_pto",
        "nombre_hidrografia_pto", "nombre_orografia_pto", "nombre_transporte_pto",
        "nombre_toponimo_lin", "contexto_nombre_poblacion_pto",
        "contexto_nombre_hidrografia_lin", "contexto_nombre_hidrografia_pol",
        "contexto_nombre_orografia_pto", "contexto_nombre_orografia_lin",
        "contexto_nombre_orografia_pol",
    ]),
    ("6", "Pesadas (planificar disco y tiempo; de una en una)", [
        "edificio_pol", "construccion_pol", "construccion_lin", "portal_pto",
        "cubierta_vegetal_pol", "cubierta_vegetal_bosque_pol", "altimetria_lin",
        "camino_lin", "senda_lin",
    ]),
]


def modelo() -> list[str]:
    return sorted(json.loads((ROOT / "capas_modelo.json").read_text(encoding="utf-8")))


def todas_las_tandas() -> list[tuple[str, str, list[str]]]:
    capas_modelo = modelo()
    asignadas = {c for _, _, cs in TANDAS for c in cs}
    desconocidas = sorted(asignadas - set(capas_modelo))
    if desconocidas:
        sys.exit(f"capas en TANDAS que no están en capas_modelo.json: {desconocidas}")
    resto = [c for c in capas_modelo if c not in asignadas]
    return TANDAS + [("resto", "Resto del modelo (instalaciones, PK, rutas...)", resto)]


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


def estado_bd(db: str) -> dict[str, str]:
    import psycopg2

    conn = psycopg2.connect(dbname=db)
    conn.autocommit = True
    out: dict[str, str] = {}
    with conn.cursor() as cur:
        cur.execute(
            """SELECT DISTINCT ON (capa) capa,
                      CASE WHEN ok THEN 'OK ' || to_char(finished_at, 'YYYY-MM-DD')
                           WHEN ok IS FALSE THEN 'ERROR (relanzar con --resume)'
                           ELSE 'en curso' END
                 FROM mc_meta.run_log
                WHERE fase IN ('carga', 'completa') AND capa IS NOT NULL
                ORDER BY capa, (fase = 'completa') DESC, id DESC"""
        )
        out.update(dict(cur.fetchall()))
        cur.execute(
            """SELECT c.relname, pg_size_pretty(pg_total_relation_size(c.oid))
                 FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'mc_servicio_nacional' AND c.relkind = 'r'
                  AND pg_relation_size(c.oid) > 0 AND c.relname !~ '_g[0-9]+$'"""
        )
        for capa, tam in cur.fetchall():
            out[capa] = out.get(capa, "datos") + f" · nacional {tam}"
    conn.close()
    return out


def main() -> None:
    load_dotenv()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", nargs="?", default="listar", choices=["listar", "capas"])
    ap.add_argument("tanda", nargs="?", help="1..6, resto, todas o pendientes")
    ap.add_argument("--db", default=None, help="consulta el estado en la BD (variables PG* / .env)")
    args = ap.parse_args()
    tandas = todas_las_tandas()

    if args.accion == "capas":
        if not args.tanda:
            sys.exit("indica la tanda: 1..6, resto, todas o pendientes")
        if args.tanda == "todas":
            capas = [c for _, _, cs in tandas for c in cs]
        elif args.tanda == "pendientes":
            if not args.db:
                sys.exit("'pendientes' necesita --db")
            est = estado_bd(args.db)
            capas = [c for _, _, cs in tandas for c in cs if not est.get(c, "").startswith("OK")]
        else:
            capas = next((cs for t, _, cs in tandas if t == args.tanda), None)
            if capas is None:
                sys.exit(f"tanda desconocida: {args.tanda}")
        print(",".join(capas))
        return

    est = estado_bd(args.db) if args.db else {}
    for t, desc, cs in tandas:
        print(f"\nTanda {t}: {desc} ({len(cs)} capas)")
        for c in cs:
            print(f"   {c:<40} {est.get(c, '-' if args.db else '')}")


if __name__ == "__main__":
    main()
