import json
import time
from lib.controlCalidad_GIT import control_calidad_GJSON
from lib.fusionar_vrt import fusionar_vrt

### Para Windows
#with open ("scripts\\mapeo\\2Proceso-ValidacionGeojson\\config.json") as f:
#    var_dict=json.load(f)

### Para Linux	
with open ("config.json") as f:
    var_dict=json.load(f)

# # # # parámetros del programa
path_carpetaSalidaGJSON = var_dict["geojson_folder_path"]

# # # # Se llama a la clase con los parámetros de la ejecución
ProcesoControlCalidad = control_calidad_GJSON(path_carpetaSalidaGJSON)
ProcesoControlCalidad.verbose = True

# # # # Pasar de repositorio e GIT a JSON
# ProcesoControlCalidad.elementosAJSON()


start_time = time.time()
#transformar los n geojson en un vrt
ProcesoFusion = fusionar_vrt(path_carpetaSalidaGJSON)
ProcesoFusion.gjson2VRT()

# # # # Lanzar proceso en Windows
#start_time = time.time()
#ProcesoControlCalidad.JSON_comprobacion = 'scripts\\mapeo\\2Proceso-ValidacionGeojson\\lib\\comprobacion.json'
#ProcesoControlCalidad.procesoControlCalidad()

# # # # Lanzar proceso en Linux

ProcesoControlCalidad.JSON_comprobacion = './lib/comprobacion.json'
ProcesoControlCalidad.procesoControlCalidad()

print("--- {} min de ejecución ---".format( (time.time() - start_time) /60 ) )
