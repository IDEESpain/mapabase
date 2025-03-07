from time import sleep, time
import pandas as pd
import sys
from funciones_generales import *
import os
from shapely import wkt
import warnings
from joblib import Parallel, delayed
import json
import shutil
from datetime import datetime
import pathlib
import geopandas as gpd

start_time = time()

warnings.filterwarnings("ignore")

with open("./config.json") as f:
    var_dict = json.load(f)

# Definimos las comunidades que se van a ejecutar
cod_comunidades = var_dict["codigo_comunidades"]

lib_path = var_dict["lib_path"]

# archivo de la matriz de elementos
elementos_file = var_dict["elementos_file"]
comunidades_file = var_dict["comunidades_file"]

niveles = ['regional', 'nacional']

matriz_niveles = pd.read_excel(f"{lib_path}{elementos_file}", engine='openpyxl')

lista_clases = matriz_niveles["elementos"]
lista_clases_short = matriz_niveles["elementos_short"]

update_layers = var_dict.get("capas_actualizar", [])
if update_layers:
    df_layers = pd.DataFrame({"clase": lista_clases, "clase_short": lista_clases_short})
    df_layers = df_layers[df_layers["clase"].isin(update_layers)]
    lista_clases = df_layers["clase"].tolist()
    lista_clases_short = df_layers["clase_short"].tolist()

comunidades = pd.read_excel(f"{lib_path}{comunidades_file}", engine='openpyxl')

if var_dict["regenerar_comunidades_pol_file"]:
    print("Generando capa poligonal de comunidades")
    generar_voronoi(var_dict['comunidades_pol_file'], modo="comunidades")

mascara_comunidades = gpd.read_file(var_dict["comunidades_pol_file"])

sheets = {}

def update_proceso4_config_file(path, key, value):
    jsonFile = open(path, "r")  # Abrir el fichero JSON para lectura
    data = json.load(jsonFile)  # Leer el JSON
    jsonFile.close()  # Cerrar el fichero
    data[key] = value
    jsonFile = open(path, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

process_4_config_file = var_dict["config_proceso_4"]

if len(sys.argv) == 2 and sys.argv[1] == "update":
    print(f"Actualizando comunidades en la carpeta: {var_dict['path_productores_comunidades']}")
    lista_comunidades = [int(mun) for mun in os.listdir(var_dict['path_productores_comunidades'])]
    comunidades = comunidades.loc[comunidades['codigo_ine_mun'].isin(lista_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]
    update_proceso4_config_file(process_4_config_file, "lista_comunidades", lista_comunidades)
    print(f"Lista de comunidades que hay que actualizar: {keys}")

elif len(sys.argv) == 2 and sys.argv[1] == "update-missing":
    print(f"Actualizando comunidades que faltan en la carpeta: {var_dict['path_generados_comunidades_recorte']}")
    lista_comunidades = [int(mun) for mun in os.listdir(var_dict['path_generados_comunidades_recorte'])]
    comunidades = comunidades.loc[~comunidades['codigo_ine_mun'].isin(lista_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]
    update_proceso4_config_file(process_4_config_file, "lista_comunidades", lista_comunidades)
    print(f"Lista de comunidades que hay que actualizar: {keys}")

elif cod_comunidades:
    comunidades = comunidades.loc[comunidades['cod_com_aut'].isin(cod_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
    update_proceso4_config_file(process_4_config_file, "lista_comunidades", cod_comunidades)

# Inicializamos el diccionario para los logs de cada capa (solo para las capas que se van a procesar)
for clase in lista_clases:
    sheets[clase] = pd.DataFrame(columns=["cod_mun", "nivel"])

def generarComunidad(index, row):
    cod_com = str(int(row["cod_com_aut"])).zfill(2)
    pathlib.Path(f"{var_dict['path_generados_comunidades_recorte']}{cod_com}").mkdir(parents=True, exist_ok=True)
    warnings.filterwarnings("ignore")
    print(f"generando comunidades:  {index} / \t\t({cod_com})")
    sys.stdout.flush()
    comunidad = str(row["cod_com_aut"]).zfill(2)
    mascara_comunidad = mascara_comunidades[mascara_comunidades["codigo"].str[2:4] == comunidad]
    mascara_comunidad['geometry'] = mascara_comunidad['geometry'].buffer(var_dict["buffer"])
    mascara_comunidad = mascara_comunidad.explode(index_parts=False)
    mascara_comunidad.to_file(f"{var_dict['path_generados_comunidades_recorte']}{comunidad}/{comunidad}.fgb", driver='FlatGeobuf', crs="EPSG:4258")
    coordinates = mascara_comunidad["geometry"].apply(lambda x: wkt.dumps(x))
    
    for clase in lista_clases:
        i = 0
        nivel_encontrado = False
        while (not nivel_encontrado) and (i < len(niveles)):
            nivel = niveles[i]
            cod = comunidad if i == 0 else "00"
            nivel_encontrado = check_nivel(nivel, cod, clase)
            i += 1
        
        if nivel_encontrado:
            print(f"Encontrada la clase {clase} a nivel {nivel} para la comunidad {comunidad}")
            if i == 1:
                path_to_vrt = nivel_encontrado[0]
                path_to_fgb = path_to_vrt.split(".vrt")[0] + ".fgb"
                shutil.copy(path_to_vrt, f"{var_dict['path_generados_comunidades_recorte']}{cod}")
                shutil.copy(path_to_fgb, f"{var_dict['path_generados_comunidades_recorte']}{cod}")
            else:
                cod = str(int(row["cod_com_aut"])).zfill(2)
                vrt_text = do_clip(niveles[i-1], nivel_encontrado[0], coordinates, clase)
                write_vrt(vrt_text, cod, clase, is_recorte=True, carpeta="path_generados_comunidades_recorte")
                sheets[clase] = sheets[clase].append({'cod_mun': cod, 'nivel': niveles[i-1]}, ignore_index=True)
                if "_pto" in clase:
                    cmd = (
                        f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{clase}_recorte.vrt "
                        f">{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt 2>&1"
                    )
                else:
                    cmd = (
                        f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.fgb  "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb "
                        f"{var_dict['path_productores_nacional']}00/{clase}.fgb "
                        f">{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt 2>&1"
                    )
                os.system(cmd)
                hay_error = search_str(f"{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt", 'ERROR')
                if hay_error:
                    cmd = (
                        f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.fgb -dialect sqlite "
                        f"-sql \"select distinct ST_MakeValid(geometry),* from {clase}\"  "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb  "
                        f"{var_dict['path_generados_comunidades_recorte']}{cod}/{clase}_recorte.vrt -skipfailure "
                        f">/dev/null 2>&1"
                    )
                    os.system(cmd)
                vrt_text = f"""
                    <OGRVRTDataSource>
                        <OGRVRTUnionLayer name="{clase}">
                            <OGRVRTLayer name="{clase}">
                                <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
                            </OGRVRTLayer>                     
                        </OGRVRTUnionLayer>
                    </OGRVRTDataSource>
                    """
                write_vrt(vrt_text, cod, clase, carpeta="path_generados_comunidades_recorte")
        else:
            cod = comunidad
            sheets[clase] = sheets[clase].append({'cod_com_aut': cod, 'nivel': 'None'}, ignore_index=True)

# Paralelización: el -1 indica que se usa el máximo número de procesos. Se utiliza memoria compartida para escribir los logs.
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(
    delayed(lambda group: [generarComunidad(index, row) for index, row in group[1].iterrows()])(group) for group in comunidades
)

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H:%M:%S")
log_path = f"{var_dict['logs_path']}{dt_string}_comunidades.xlsx"
print(f"Tiempo total = {time() - start_time}")

with pd.ExcelWriter(log_path) as writer:
    # Se generan hojas de Excel solo para las capas procesadas (filtradas)
    for clase, clase_short in zip(lista_clases, lista_clases_short):
        sheets[clase].to_excel(writer, sheet_name=str(clase_short), index=False)
