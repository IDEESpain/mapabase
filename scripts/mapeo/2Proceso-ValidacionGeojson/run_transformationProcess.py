import time
import json
from lib.file_2FGB import transformar
from lib.fusionar_vrt import fusionar_vrt
from lib.controlCalidad_GIT import control_calidad_GJSON
from lib.fusionar_vrt import fusionar_vrt

with open ("./config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

path_carpetaSalidaFGB = var_dict["fgb_folder_path"]

path_carpetaTempFGB = var_dict["fgb_temp_folder"]

from pathlib import Path
Path(path_carpetaSalidaFGB).mkdir(parents=True, exist_ok=True)
Path(path_carpetaTempFGB).mkdir(parents=True, exist_ok=True)


# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoA = transformar(path_carpetaSalidaGJSON)
ProcesoB = fusionar_vrt(path_carpetaSalidaGJSON)
ProcesoA.verbose = True
ProcesoB.verbose = True
ProcesoA.nNucleos = 1
ProcesoControlCalidad = control_calidad_GJSON(path_carpetaSalidaGJSON)
ProcesoControlCalidad.verbose = True


start_time = time.time()

#transformamos gson a fgb
ProcesoA.transformarGJSON(path_carpetaSalida=path_carpetaTempFGB)

#sacamos los n_fgb a vrt
ProcesoB.fgb_n_2VRT(path_carpeta_fgb=path_carpetaTempFGB)

#sacamos un solo fgb
ProcesoA.transformarVRT(path_carpetaFGB_origen=path_carpetaTempFGB, path_carpetaFGB_destino=path_carpetaSalidaFGB)

#hacemos un vrt que apuunte a ese fgb
ProcesoB.fgb2VRT(path_carpeta_fgb=path_carpetaSalidaFGB)

#borramos los n_fgb para liberar espacio
ProcesoB.deleteTempFiles(path_carpetaTempFGB)

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )
