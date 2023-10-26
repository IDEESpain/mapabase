
import time
from lib.controlCalidad_GIT import control_calidad_GJSON

# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoControlCalidad = control_calidad_GJSON("")
ProcesoControlCalidad.verbose = True

# # # # Pasar de repositorio e GIT a JSON
# start_time = time.time()
# ProcesoControlCalidad.git_carpeta_mapabase_gh_pages = './mapabase-gh-pages'
# ProcesoControlCalidad.JSON_comprobacion = './lib/comprobacion.json'
# ProcesoControlCalidad.elementosAJSON()

# # # # Pasar a JSON para proceso Tippecanoe
# input_vrt= './pruebas/datos_origen/10/'
# gz_folder="./pruebas/gz/"
# destination_mbtiles = './pruebas/mbtiles/'
# temp_directory = "./pruebas/tmp/"
# final_folder="./pruebas/teselas/"

project = {
            "name": "vector-tile-prueba",
            "description": "Datos del Sistema Cartografico Nacional",
            "contact_name": "A^2",
            "contact_email": "aurelio.aragon@cnig.es"
        }
# setup = { 
#             "compress_geojson": "yes",
#             "tiling_layers": "yes",
#             "to_folder":"yes",
#             "move_to_final_folder" : "yes",
#             "join_json" : "yes"
#         }
start_time = time.time()
ProcesoControlCalidad.git_carpeta_mapabase_gh_pages = './mapabase-gh-pages'
ProcesoControlCalidad.JSON_config_Tippecanoe = "./config_vtiles.json"
#ProcesoControlCalidad.elementosAJSON_Tippecanoe(input_vrt,gz_folder,destination_mbtiles,temp_directory, project, setup,final_folder)
ProcesoControlCalidad.niveles_AJSON_Tippecanoe()


# # # # Lanzar proceso
# start_time = time.time()
# ProcesoControlCalidad.procesoControlCalidad()
print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )







