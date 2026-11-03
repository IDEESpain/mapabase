#!/usr/bin/env python3
# Parchea Tilekiln para PostGIS 2.5 (sin ST_TileEnvelope).
#
# Tilekiln genera el bbox con ST_TileEnvelope(..., margin=>...), PostGIS >= 3.1.
# En CNIG hay PostGIS 2.5.5: esa funcion no existe.
# Este script sustituye Tile.bbox() por ST_MakeEnvelope equivalente EPSG:3857.
#
# Uso:
#   python3 patch_tilekiln_postgis25.py
#   python3 patch_tilekiln_postgis25.py --check
#   python3 patch_tilekiln_postgis25.py --revert

from __future__ import annotations

import argparse
import importlib.util
import re
import shutil
import sys
from pathlib import Path

MARKER = "# mc_postgis25_bbox"
BACKUP_SUFFIX = ".bak_pre_postgis25"

# Compatible con tilekiln 0.2.x (Py3.9) y 0.5+/0.6.x (Py3.10+)
NEW_BBOX = """    def bbox(self, buffer):
        '''Returns the bounding box for a tile (PostGIS 2.5: ST_MakeEnvelope).'''
        # mc_postgis25_bbox
        # Equivalente a ST_TileEnvelope(z,x,y, margin=>buffer) de PostGIS 3.1+.
        # buffer llega ya como fraccion del lado (Tilekiln pasa buffer/extent).
        return (
            "ST_MakeEnvelope("
            f"-20037508.342789244+({self.x}-({buffer}))*(40075016.685578488/2^{self.zoom}),"
            f"20037508.342789244-({self.y}+1+({buffer}))*(40075016.685578488/2^{self.zoom}),"
            f"-20037508.342789244+({self.x}+1+({buffer}))*(40075016.685578488/2^{self.zoom}),"
            f"20037508.342789244-({self.y}-({buffer}))*(40075016.685578488/2^{self.zoom}),"
            "3857)"
        )
"""


def find_tile_py() -> Path:
    spec = importlib.util.find_spec("tilekiln.tile")
    if spec is None or not spec.origin:
        raise SystemExit(
            "No se encuentra el paquete tilekiln.\n"
            "Instala el bueno (Paul Norman, >=0.5) con Python 3.10+:\n"
            "  /ruta/python3.10 -m pip install --user 'tilekiln==0.6.5'"
        )
    return Path(spec.origin)


def patch(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("Ya estaba parcheado:", path)
        return
    if "ST_TileEnvelope" not in text:
        raise SystemExit(
            "No hay ST_TileEnvelope en %s.\n"
            "Seguro que instalaste tilekiln viejo 0.0.6 (mal). "
            "Necesitas tilekiln>=0.5 de pnorman." % path
        )
    new, n = re.subn(
        r"    def bbox\(self, buffer\) -> str:\n"
        r"(?:.*\n)*?"
        r"        return f'''ST_TileEnvelope\([^']+'''\n",
        NEW_BBOX,
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("No se pudo localizar bbox() en %s" % path)
    bak = path.with_name(path.name + BACKUP_SUFFIX)
    if not bak.exists():
        shutil.copy2(path, bak)
        print("Backup:", bak)
    path.write_text(new, encoding="utf-8")
    print("Parcheado:", path)


def revert(path: Path) -> None:
    bak = path.with_name(path.name + BACKUP_SUFFIX)
    if not bak.is_file():
        raise SystemExit("No hay backup %s" % bak)
    shutil.copy2(bak, path)
    print("Restaurado desde", bak)


def check(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if MARKER in text and "ST_MakeEnvelope" in text:
        print("OK: parche PostGIS 2.5 activo en", path)
        sys.exit(0)
    if "ST_TileEnvelope" in text:
        print("SIN PARCHE: sigue ST_TileEnvelope ->", path)
        sys.exit(2)
    print("Estado desconocido / tilekiln incorrecto en", path)
    sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    args = ap.parse_args()
    path = find_tile_py()
    print("tile.py:", path)
    if args.check:
        check(path)
    elif args.revert:
        revert(path)
    else:
        patch(path)
        check(path)


if __name__ == "__main__":
    main()
