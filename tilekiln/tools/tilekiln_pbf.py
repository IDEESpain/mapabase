"""Servidores de Tilekiln 0.2.1 con rutas .pbf además de .mvt (mismo contenido).

Una tesela MVT ya es un mensaje Protocol Buffers: .pbf y .mvt son la misma tesela
con distinta extensión. Tilekiln 0.2.1 solo publica .mvt; este módulo reutiliza sus
aplicaciones (dev = sin caché, live = caché en BD) y añade:

  /tiles/{z}/{x}/{y}.pbf     misma tesela, Content-Type application/x-protobuf
  /tilejson-pbf.json         TileJSON cuyas URL de teselas acaban en .pbf

Lo arranca tools/tilekiln_servicio.sh (uvicorn tilekiln_pbf:dev | tilekiln_pbf:live).
Variables que usa Tilekiln: TILEKILN_CONFIG (ruta del yaml) y TILEKILN_URL
(base pública de las teselas, p.ej. http://10.67.33.105:8099/tiles).
"""
import os
import re

from fastapi import Request, Response

import tilekiln.dev as _dev
import tilekiln.server as _srv
from tilekiln.tile import Tile

PBF = "application/x-protobuf"
RUTA_PBF = _dev.TILE_PREFIX + "/{zoom}/{x}/{y}.pbf"


def _tilejson_pbf(config) -> Response:
    texto = config.tilejson(os.environ[_dev.TILEKILN_URL]).replace("/{z}/{x}/{y}.mvt", "/{z}/{x}/{y}.pbf")
    return Response(content=texto, media_type="application/json")


# --- dev: genera cada tesela al vuelo -------------------------------------------
dev = _dev.dev


@dev.head(RUTA_PBF)
@dev.get(RUTA_PBF)
def dev_tile_pbf(zoom: int, x: int, y: int):
    return Response(_dev.kiln.render(Tile(zoom, x, y)), media_type=PBF, headers=_dev.STANDARD_HEADERS)


@dev.head("/tilejson-pbf.json")
@dev.get("/tilejson-pbf.json")
def dev_tilejson_pbf():
    return _tilejson_pbf(_dev.config)


# --- live: caché en BD (esquema tilekiln); genera y guarda si no existe -------------
live = _srv.live
_RE_TESELA = re.compile(r"^" + re.escape(_dev.TILE_PREFIX) + r"/(\d+)/\d+/\d+\.(mvt|pbf)$")


@live.middleware("http")
async def live_fuera_de_rango(request: Request, call_next):
    """Zoom fuera del rango del config → tesela vacía (como dev).

    Tilekiln 0.2.1 live intenta guardarla en una partición de caché que no existe
    y responde 500; los visores piden zooms bajos aunque no haya capas en ellos.
    """
    m = _RE_TESELA.match(request.url.path)
    if m:
        z = int(m.group(1))
        cfg = _srv.config
        if cfg.minzoom is not None and not (cfg.minzoom <= z <= cfg.maxzoom):
            tipo = PBF if m.group(2) == "pbf" else "application/vnd.mapbox-vector-tile"
            return Response(b"", media_type=tipo, headers=_srv.STANDARD_HEADERS)
    return await call_next(request)


@live.head(RUTA_PBF)
@live.get(RUTA_PBF)
def live_tile_pbf(zoom: int, x: int, y: int):
    tile = Tile(zoom, x, y)
    data = _srv.storage.get_tile(tile)
    if data is None:
        data = _srv.kiln.render(tile)
        _srv.storage.save_tile(tile, data)
    return Response(data, media_type=PBF, headers=_srv.STANDARD_HEADERS)


@live.head("/tilejson-pbf.json")
@live.get("/tilejson-pbf.json")
def live_tilejson_pbf():
    return _tilejson_pbf(_srv.config)
