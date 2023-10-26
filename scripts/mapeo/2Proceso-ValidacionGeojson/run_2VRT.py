import time
import json
from lib.fusionar_vrt import fusionar_vrt

with open ("./config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

# # # # Se llama a la clase con los parámetros de la ejecución
Proceso = fusionar_vrt(path_carpetaSalidaGJSON)
Proceso.verbose = True

start_time = time.time()

#### gjson -> vrt ####
# Proceso.gjson2VRT()

#### fgb n -> vrt ####
# Proceso.fgb_n_2VRT()

#### fgb -> vrt ####
Proceso.fgb2VRT()

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )
