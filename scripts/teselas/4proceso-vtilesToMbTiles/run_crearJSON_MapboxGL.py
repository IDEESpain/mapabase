
import time
from lib.controlCalidad_GIT import control_calidad_GJSON

# # # # parámetros del programa
path_carpetaSalidaGJSON = '/var/datos/input_geojson/1CNIG/1Geojson/'

# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoControlCalidad = control_calidad_GJSON(path_carpetaSalidaGJSON)
ProcesoControlCalidad.verbose = True

# # # # Crear JSON de estilos MapboxGL
confDic = {
            "version": 8,
            "name": "Capa base mapboxGL",
            "sprite": "http://10.67.33.105:8085/sprite/sprite",
            "glyphs": "http://10.67.33.105:8085/font/{fontstack}/{range}.pbf",
            "id": "adwe687dsf",
            "owner": "CNIG"
        }
metadata = { 
            "compress_geojson": "no",
            "tiling_layers": "yes"
        }
sources = { 
            "fuenteCNIG": {"type":"vector",
                           "tiles": ["http://10.67.33.105:8085/vt/{z}/{x}/{y}.pbf"],
                            "minZoom":	0,
                            "maxZoom":	22
                        }
        }

start_time = time.time()
ProcesoControlCalidad.JSON_comprobacion = './lib/comprobacion.json'
ProcesoControlCalidad.JSON_MapboxGL = "./lib/estiloMapboxGL.json"
ProcesoControlCalidad.crearJSON_MapboxGL_desdeComprobacionJSON(confDic, metadata, sources)

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )







