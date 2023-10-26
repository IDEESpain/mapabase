
import time
import json
from lib.file_2FGB import transformar


with open ("./config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

# # # # Se llama a la clase con los parámetros de la ejecución
Proceso = transformar(path_carpetaSalidaGJSON)
Proceso.verbose = True

start_time = time.time()

### VRT ---> FGB ###
# Proceso.transformarVRT()

### GJSON ---> FGB ###
Proceso.transformarGJSON()

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )
