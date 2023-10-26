
import time
import json
from lib.controlCalidad_GIT import control_calidad_GJSON

with open ("./config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoControlCalidad = control_calidad_GJSON(path_carpetaSalidaGJSON)
ProcesoControlCalidad.verbose = True

# # # # Pasar de repositorio e GIT a JSON
start_time = time.time()
ProcesoControlCalidad.git_carpeta_mapabase_gh_pages = './mapabase'
ProcesoControlCalidad.JSON_comprobacion = './lib/comprobacion.json'
ProcesoControlCalidad.elementosAJSON()

# # # # Pasar a JSON para proceso Tippecanoe
# destination_layers_geojson= '/var/datos/input_geojson/1CNIG/1Geojson/'
# destination_mbtiles = '/var/datos/input_geojson/1CNIG/1Geojson/'
# temp_directory = "/tmp/"
# project = {
#             "name": "vector-tile-prueba",
#             "description": "Datos del Sistema Cartografico Nacional",
#             "contact_name": "Ana Garcia de Vicuna",
#             "contact_email": "agvicuna@larioja.org"
#         }
# setup = { 
#             "compress_geojson": "no",
#             "tiling_layers": "yes"
#         }
# start_time = time.time()
# ProcesoControlCalidad.elementosAJSON_Tippecanoe(destination_layers_geojson,destination_mbtiles,temp_directory, project, setup)

# # # # Lanzar proceso
# start_time = time.time()
# ProcesoControlCalidad.procesoControlCalidad()
print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )







