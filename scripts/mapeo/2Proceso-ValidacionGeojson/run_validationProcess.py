import json
import time
from lib.controlCalidad_GIT import control_calidad_GJSON

with open ("./config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoControlCalidad = control_calidad_GJSON(path_carpetaSalidaGJSON)
ProcesoControlCalidad.verbose = True

# # # # Pasar de repositorio e GIT a JSON
# ProcesoControlCalidad.elementosAJSON()


# # # # Lanzar proceso
start_time = time.time()
ProcesoControlCalidad.JSON_comprobacion = './lib/comprobacion.json'
ProcesoControlCalidad.procesoControlCalidad()

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )
