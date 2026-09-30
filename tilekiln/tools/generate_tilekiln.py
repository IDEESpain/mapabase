#!/usr/bin/env python3
"""Genera schema SQL + config.yaml + plantillas Jinja2 para Tilekiln.

Fuentes:
  - scripts/mapeo/1Proceso-PostGISToGeojson/crear_base_de_datos.sql
  - scripts/mapeo/2Proceso-ValidacionGeojson/lib/comprobacion.json
  - scripts/teselas/4proceso-vtilesToMbTiles/config_vtiles.json
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TILEKILN_ROOT = Path(__file__).resolve().parents[1]
OUT = TILEKILN_ROOT
SQL_SRC = ROOT / "scripts/mapeo/1Proceso-PostGISToGeojson/crear_base_de_datos.sql"
COMPROBACION = ROOT / "scripts/mapeo/2Proceso-ValidacionGeojson/lib/comprobacion.json"
VTILES = ROOT / "scripts/teselas/4proceso-vtilesToMbTiles/config_vtiles.json"


def parse_tables(sql_text: str) -> dict[str, list[tuple[str, str]]]:
    blocks = re.split(r"CREATE TABLE public\.", sql_text)[1:]
    tables: dict[str, list[tuple[str, str]]] = {}
    for block in blocks:
        name = block.split("(", 1)[0].strip()
        body = block.split("(", 1)[1]
        cols_part = (
            body.split(");\nALTER TABLE", 1)[0]
            if ");\nALTER TABLE" in body
            else body.split(");", 1)[0]
        )
        cols: list[tuple[str, str]] = []
        for line in cols_part.split("\n"):
            line = line.strip().rstrip(",")
            if not line or line.upper().startswith("CONSTRAINT"):
                continue
            m = re.match(r"(\w+)\s+(.+)", line)
            if m:
                cols.append((m.group(1), m.group(2)))
        tables[name] = cols
    return tables


def extract_comments(sql_text: str) -> dict[str, dict[str, str]]:
    """table -> {None: table comment, col: col comment}."""
    out: dict[str, dict[str, str]] = defaultdict(dict)
    for m in re.finditer(
        r"COMMENT ON TABLE (\w+) IS\s*'((?:[^']|'')*)';",
        sql_text,
        re.S,
    ):
        out[m.group(1)][None] = m.group(2).replace("''", "'")
    for m in re.finditer(
        r"COMMENT ON COLUMN (\w+)\.(\w+) IS\s*'((?:[^']|'')*)';",
        sql_text,
        re.S,
    ):
        out[m.group(1)][m.group(2)] = m.group(3).replace("''", "'")
    return out


def to_3857_type(col_type: str) -> str:
    return re.sub(
        r"public\.geometry\((\w+),25830\)",
        r"public.geometry(\1,3857)",
        col_type,
    )


def build_schema(tables: dict, comments: dict) -> str:
    lines = [
        "-- Esquema PostGIS para servir Mapa Ciudadano con Tilekiln.",
        "-- Geometría en EPSG:3857 (Web Mercator). Cargar con ST_Transform desde 4258/25830.",
        "-- Generado por tools/generate_tilekiln.py — no editar a mano.",
        "",
        "CREATE EXTENSION IF NOT EXISTS postgis;",
        "",
    ]
    for name, cols in sorted(tables.items()):
        lines.append(f"CREATE TABLE IF NOT EXISTS public.{name} (")
        col_defs = []
        for col, ctype in cols:
            col_defs.append(f"\t{col} {to_3857_type(ctype)}")
        lines.append(",\n".join(col_defs))
        lines.append(");")
        lines.append(f"ALTER TABLE public.{name} OWNER TO postgres;")
        lines.append(
            f"CREATE INDEX IF NOT EXISTS sidx_{name}_the_geom "
            f"ON public.{name} USING gist (the_geom);"
        )
        tcomment = comments.get(name, {}).get(None)
        if tcomment:
            esc = tcomment.replace("'", "''")
            lines.append(f"COMMENT ON TABLE {name} IS '{esc}';")
        for col, _ in cols:
            if col == "the_geom":
                continue
            ccomment = comments.get(name, {}).get(col)
            if ccomment:
                esc = ccomment.replace("'", "''")
                lines.append(f"COMMENT ON COLUMN {name}.{col} IS '{esc}';")
        lines.append("")
    return "\n".join(lines)


def mapbox_filter_to_sql(expr) -> str | None:
    if expr is None:
        return None
    if not isinstance(expr, list) or not expr:
        raise ValueError(f"Filtro inválido: {expr!r}")
    op = expr[0]
    if op == "==":
        field, value = expr[1], expr[2]
        if value is None:
            return f"{field} IS NULL"
        return f"{field} = '{_esc(value)}'"
    if op == "!=":
        field, value = expr[1], expr[2]
        if value is None:
            return f"{field} IS NOT NULL"
        return f"{field} IS DISTINCT FROM '{_esc(value)}'"
    if op == "in":
        field = expr[1]
        values = expr[2:]
        if len(values) == 1 and isinstance(values[0], list) and values[0] and values[0][0] == "literal":
            values = values[0][1]
        quoted = ", ".join(f"'{_esc(v)}'" for v in values)
        return f"{field} IN ({quoted})"
    if op == "!in":
        field = expr[1]
        values = expr[2:]
        quoted = ", ".join(f"'{_esc(v)}'" for v in values)
        return f"{field} NOT IN ({quoted})"
    if op == "has":
        return f"{expr[1]} IS NOT NULL"
    if op == "!has":
        return f"{expr[1]} IS NULL"
    if op == "any":
        # Compactar igualdad sobre el mismo campo: clase IN (...)
        eqs = expr[1:]
        if eqs and all(
            isinstance(e, list) and len(e) == 3 and e[0] == "==" for e in eqs
        ):
            fields = {e[1] for e in eqs}
            if len(fields) == 1:
                field = next(iter(fields))
                values = ", ".join(f"'{_esc(e[2])}'" for e in eqs)
                return f"{field} IN ({values})"
        parts = [mapbox_filter_to_sql(e) for e in eqs]
        parts = [p for p in parts if p]
        return f"({' OR '.join(parts)})" if parts else None
    if op == "all":
        parts = [mapbox_filter_to_sql(e) for e in expr[1:]]
        parts = [p for p in parts if p]
        if len(parts) == 1:
            return parts[0]
        return f"({' AND '.join(parts)})" if parts else None
    raise ValueError(f"Operador de filtro no soportado: {op}")


def _esc(value) -> str:
    return str(value).replace("'", "''")


def layer_presence_and_filters(cv: dict):
    presence: dict[str, list[int]] = defaultdict(list)
    filters: dict[str, dict[int, object]] = defaultdict(dict)
    for z in cv["zoom_levels"]:
        level = z["level"]
        for group in ("layers", "layers_no_coalesce", "layers_with_labels"):
            for item in z.get(group) or []:
                name = item["name"] if isinstance(item, dict) else item
                presence[name].append(level)
        for layer, filt in (z.get("filter") or {}).items():
            filters[layer][level] = filt
    return presence, filters


def filter_ranges(filt_by_z: dict, all_zs: list[int]):
    items = []
    for z in sorted(set(all_zs)):
        f = filt_by_z.get(z)
        key = json.dumps(f, ensure_ascii=False, sort_keys=True) if f is not None else None
        items.append((z, key, f))
    ranges = []
    if not items:
        return ranges
    start_z, cur_key, cur_f = items[0]
    prev = start_z
    for z, key, f in items[1:]:
        if key == cur_key and z == prev + 1:
            prev = z
        else:
            ranges.append((start_z, prev, cur_f))
            start_z, cur_key, cur_f = z, key, f
            prev = z
    ranges.append((start_z, prev, cur_f))
    return ranges


def attr_columns(cols: list[tuple[str, str]]) -> list[str]:
    return [c for c, _ in cols if c != "the_geom"]


# Bandas de servicio (= proceso 4 / mosaicos FGB nacionales)
ZOOM_NACIONAL_MAX = 13   # IGN — proceso 4 max_zoom_IGN
ZOOM_REGIONAL_MAX = 16   # CCAA — proceso 4 max_zoom_comunidades
# z >= 17 → municipios (proceso 4 min_zoom_municipios)


def render_jinja(layer: str, cols: list[str], ranges) -> str:
    """Jinja con 3 fuentes (nacional/regional/local) + filtros tippecanoe por zoom."""
    select_cols = ",\n    ".join(["ST_AsMVTGeom(the_geom, {{bbox}}, {{extent}}) AS way"] + cols)
    lines = [
        f"-- Capa {layer} (Tilekiln / Mapa Ciudadano)",
        "-- Fuente por zoom: nacional z0-13 | regional z14-16 | local z17+",
        "SELECT",
        f"    {select_cols}",
        "{% if zoom <= " + str(ZOOM_NACIONAL_MAX) + " %}",
        f"  FROM mc_servicio_nacional.{layer}",
        "{% elif zoom <= " + str(ZOOM_REGIONAL_MAX) + " %}",
        f"  FROM mc_servicio_regional.{layer}",
        "{% else %}",
        f"  FROM mc_servicio_local.{layer}",
        "{% endif %}",
        "  WHERE the_geom && {{bbox}}",
    ]
    conditional = [(a, b, f) for a, b, f in ranges if f is not None]
    if conditional:
        for i, (zmin, zmax, filt) in enumerate(conditional):
            sql_f = mapbox_filter_to_sql(filt)
            if zmin == zmax:
                zoom_expr = f"zoom == {zmin}"
            else:
                zoom_expr = f"zoom >= {zmin} and zoom <= {zmax}"
            tag = "if" if i == 0 else "elif"
            lines.append(f"{{% {tag} {zoom_expr} %}}")
            lines.append(f"  AND {sql_f}")
        no_filter = [(a, b) for a, b, f in ranges if f is None]
        if no_filter:
            parts = []
            for zmin, zmax in no_filter:
                if zmin == zmax:
                    parts.append(f"zoom == {zmin}")
                else:
                    parts.append(f"(zoom >= {zmin} and zoom <= {zmax})")
            lines.append(f"{{% elif {' or '.join(parts)} %}}")
            lines.append("  -- sin filtro tippecanoe en este zoom")
        lines.append("{% endif %}")
    lines.append("")
    return "\n".join(lines)


def field_descriptions(layer: str, cols: list[str], comments: dict, comp: dict) -> dict:
    fields = {}
    for col in cols:
        c = comments.get(layer, {}).get(col)
        if c and c.strip():
            fields[col] = c.strip().split("\n")[0][:120]
        elif col in (comp.get(layer) or {}):
            fields[col] = f"Atributo {col}"
        else:
            fields[col] = col
    return fields


def extent_for_zoom(zmin: int, zmax: int) -> int:
    # Alineado con tippecanoe: más detalle en zooms altos
    if zmax <= 10:
        return 1024
    if zmax <= 14:
        return 2048
    return 4096


def buffer_for_layer(layer: str) -> int:
    if layer.endswith("_lin"):
        return 4
    if layer.endswith("_pto"):
        return 8
    return 2


def build_config(tables, presence, filters, comments, comp) -> dict:
    vector_layers = {}
    for layer in sorted(presence):
        if layer not in tables:
            continue
        zs = sorted(set(presence[layer]))
        zmin, zmax = zs[0], zs[-1]
        cols = attr_columns(tables[layer])
        fields = field_descriptions(layer, cols, comments, comp)
        desc = comments.get(layer, {}).get(None) or f"Capa {layer}"
        desc = " ".join(desc.split())[:200]
        vector_layers[layer] = {
            "description": desc,
            "fields": fields,
            "sql": [
                {
                    "minzoom": zmin,
                    "maxzoom": zmax,
                    "extent": extent_for_zoom(zmin, zmax),
                    "buffer": buffer_for_layer(layer),
                    "file": f"layers/{layer}.sql.jinja2",
                }
            ],
        }
    # Capas del modelo sin presencia en tippecanoe (p.ej. tierra_firme_pol)
    for layer in sorted(tables):
        if layer in vector_layers:
            continue
        cols = attr_columns(tables[layer])
        fields = field_descriptions(layer, cols, comments, comp)
        desc = comments.get(layer, {}).get(None) or f"Capa {layer}"
        desc = " ".join(desc.split())[:200]
        vector_layers[layer] = {
            "description": desc + " (sin zooms tippecanoe; incluir bajo demanda)",
            "fields": fields,
            "sql": [
                {
                    "minzoom": 0,
                    "maxzoom": 22,
                    "extent": 4096,
                    "buffer": buffer_for_layer(layer),
                    "file": f"layers/{layer}.sql.jinja2",
                }
            ],
        }
    return {
        "metadata": {
            "id": "mapa_ciudadano_v1",
            "name": "Mapa Ciudadano",
            "description": "Teselas vectoriales Mapa Ciudadano (migración Tippecanoe → Tilekiln)",
            "version": "1.0.0",
            "attribution": "IGN / CNIG y administraciones colaboradoras",
            "center": [-3.7, 40.4, 6],
            "bounds": [-19.0, 27.0, 5.5, 44.5],
        },
        "vector_layers": vector_layers,
    }


def dump_yaml(data: dict) -> str:
    """YAML mínimo sin dependencia pyyaml (suficiente para Tilekiln)."""

    def emit(obj, indent=0):
        sp = "  " * indent
        if isinstance(obj, dict):
            lines = []
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{sp}{k}:")
                    lines.append(emit(v, indent + 1))
                else:
                    lines.append(f"{sp}{k}: {fmt_scalar(v)}")
            return "\n".join(lines)
        if isinstance(obj, list):
            lines = []
            for item in obj:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        prefix = "- " if first else "  "
                        first = False
                        if isinstance(v, (dict, list)):
                            lines.append(f"{sp}{prefix}{k}:")
                            lines.append(emit(v, indent + 2))
                        else:
                            lines.append(f"{sp}{prefix}{k}: {fmt_scalar(v)}")
                else:
                    lines.append(f"{sp}- {fmt_scalar(item)}")
            return "\n".join(lines)
        return f"{sp}{fmt_scalar(obj)}"

    def fmt_scalar(v):
        if isinstance(v, bool):
            return "true" if v else "false"
        if isinstance(v, (int, float)):
            return str(v)
        s = str(v)
        if s == "":
            return '""'
        if any(c in s for c in ":#{}[]&*?|>!%@`'\"\n") or s.strip() != s:
            return json.dumps(s, ensure_ascii=False)
        return s

    return emit(data) + "\n"


def main():
    sql_text = SQL_SRC.read_text(encoding="utf-8")
    tables = parse_tables(sql_text)
    comments = extract_comments(sql_text)
    comp = json.loads(COMPROBACION.read_text(encoding="utf-8"))
    cv = json.loads(VTILES.read_text(encoding="utf-8"))
    presence, filters = layer_presence_and_filters(cv)

    (OUT / "sql").mkdir(parents=True, exist_ok=True)
    (OUT / "layers").mkdir(parents=True, exist_ok=True)

    schema = build_schema(tables, comments)
    (OUT / "sql" / "schema.sql").write_text(schema, encoding="utf-8")

    load_sql = """-- Ejemplo de carga FGB (EPSG:4258) → tabla Tilekiln (EPSG:3857).
-- Ajustar rutas y capa. Requiere GDAL/OGR con soporte FlatGeobuf.
--
-- ogr2ogr -f PostgreSQL PG:"dbname=mapa_ciudadano" \\
--   cubierta_vegetal_pol.fgb \\
--   -nln cubierta_vegetal_pol -append \\
--   -t_srs EPSG:3857 -s_srs EPSG:4258 \\
--   -lco GEOMETRY_NAME=the_geom -nlt PROMOTE_TO_MULTI
--
-- Alternativa in-DB si ya hay geometría en 4258/25830:
-- UPDATE cubierta_vegetal_pol SET the_geom = ST_Transform(the_geom, 3857);
"""
    (OUT / "sql" / "load_fgb_ejemplo.sql").write_text(load_sql, encoding="utf-8")

    config = build_config(tables, presence, filters, comments, comp)
    (OUT / "config.yaml").write_text(dump_yaml(config), encoding="utf-8")

    # Jinjas: capas con presencia tippecanoe + resto del modelo
    all_layers = sorted(set(tables) | set(presence))
    for layer in all_layers:
        if layer not in tables:
            continue
        cols = attr_columns(tables[layer])
        zs = presence.get(layer) or list(range(0, 23))
        ranges = filter_ranges(filters.get(layer, {}), zs)
        if not ranges:
            ranges = [(min(zs), max(zs), None)]
        text = render_jinja(layer, cols, ranges)
        (OUT / "layers" / f"{layer}.sql.jinja2").write_text(text, encoding="utf-8")

    print(f"Tablas schema: {len(tables)}")
    print(f"Capas config: {len(config['vector_layers'])}")
    print(f"Jinjas: {len(list((OUT / 'layers').glob('*.sql.jinja2')))}")
    print(f"Salida: {OUT}")


if __name__ == "__main__":
    main()
