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

start_time = time()

warnings.filterwarnings("ignore")

f = open("./config.json")

var_dict = json.load(f)

# Definimos las comunidades que se van a ejecutar
cod_comunidades = var_dict["codigo_comunidades"]

lib_path = var_dict["lib_path"]

# archivo de la matriz de elementos
elementos_file = var_dict["elementos_file"]

comunidades_file=var_dict["comunidades_file"]


niveles = ['regional', 'nacional']

matriz_niveles = pd.read_excel(
    f"{lib_path}{elementos_file}", engine='openpyxl')

lista_clases = matriz_niveles["elementos"]

lista_clases_short = matriz_niveles["elementos_short"]

comunidades = pd.read_excel(f"{lib_path}{comunidades_file}", engine='openpyxl')


if var_dict["regenerar_comunidades_pol_file"]:
    print("Generando capa poligonal de comunidades")
    generar_voronoi(var_dict['comunidades_pol_file'], modo="comunidades")

mascara_comunidades = gpd.read_file(var_dict["comunidades_pol_file"])

sheets = {}


def update_proceso4_config_file(path, key, value):
    jsonFile = open(path, "r")  # Open the JSON file for reading
    data = json.load(jsonFile)  # Read the JSON into the buffer
    jsonFile.close()  # Close the JSON file

    # Working with buffered content
    data[key] = value

    # Save our changes to JSON file
    jsonFile = open(path, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

process_4_config_file = var_dict["config_proceso_4"]

if(len(sys.argv) == 2 and sys.argv[1] == "update"):
    print(
        f"Actualizando comunidades en la carpeta: {var_dict['path_productores_comunidades']}")

    lista_comunidades = [int(mun) for mun in os.listdir(
        var_dict['path_productores_comunidades'])]
    comunidades = comunidades.loc[comunidades['codigo_ine_mun'].isin(
        lista_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]

    update_proceso4_config_file(
        process_4_config_file, "lista_comunidades", lista_comunidades)

    print(f"Lista de comunidades que hay que actualizar: {keys}")

elif(len(sys.argv) == 2 and sys.argv[1] == "update-missing"):
    print(
        f"Actualizando comunidades que faltan en la carpeta: {var_dict['path_generados_comunidades_recorte']}")

    lista_comunidades = [int(mun) for mun in os.listdir(
        var_dict['path_generados_comunidades_recorte'])]
    comunidades = comunidades.loc[~comunidades['codigo_ine_mun'].isin(
        lista_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]

    update_proceso4_config_file(
        process_4_config_file, "lista_comunidades", lista_comunidades)

    print(f"Lista de comunidades que hay que actualizar: {keys}")


elif cod_comunidades:
    comunidades = comunidades.loc[comunidades['cod_com_aut'].isin(
        cod_comunidades)].reset_index()
    comunidades = comunidades.groupby(by="cod_com_aut")
   
    update_proceso4_config_file(
        process_4_config_file, "lista_comunidades", cod_comunidades)


for clase in lista_clases:
    sheets[clase] = pd.DataFrame(columns=["cod_mun", "nivel"])


def generarComunidad(index, row):

    cod_com = str(int(row["cod_com_aut"])).zfill(2)
    
    # misma ruta o cambia
    pathlib.Path(f"{var_dict['path_generados_comunidades_recorte']}{cod_com}").mkdir(
        parents=True, exist_ok=True)

    warnings.filterwarnings("ignore")

    print(
        f"generando comunidades:  {index} / \t\t({cod_com})")
    sys.stdout.flush()

    comunidad = str(row["cod_com_aut"]).zfill(2)
    mascara_comunidad = mascara_comunidades[mascara_comunidades["codigo"].str[2:4] == comunidad]
    mascara_comunidad.to_file(f"{var_dict['path_generados_comunidades_recorte']}{comunidad}/{comunidad}.fgb", driver='FlatGeobuf' ,crs="EPSG:4258")
    coordinates = mascara_comunidad["geometry"].apply(lambda x: wkt.dumps(x))
    #mascara_comunidad = generarLimite(cod=comunidad, modo="comunidades")
   
    for clase in lista_clases:
        i = 0
        index_level = i
        nivel = niveles[0]
        nivel_encontrado = False
        while (not nivel_encontrado) and (i < len(niveles)):
            nivel = niveles[i]
            if i == 0:
                cod = comunidad              
            else:
                cod = "00"
            nivel_encontrado = check_nivel(nivel, cod, clase)
            i += 1
        
        if nivel_encontrado:
            print("encontrado ", i, nivel, comunidad, cod)
          
            if i == 1:
                path_to_vrt = nivel_encontrado[0]
                path_to_fgb = path_to_vrt.split(".vrt")[0]+".fgb"

                shutil.copy(
                    path_to_vrt, f"{var_dict['path_generados_comunidades_recorte']}{cod}")
                shutil.copy(
                    path_to_fgb, f"{var_dict['path_generados_comunidades_recorte']}{cod}")

            else:
                cod = str(int(row["cod_com_aut"])).zfill(2)

                # Hacemos el clip
                vrt_text = do_clip(niveles[i-1], nivel_encontrado[0], coordinates, clase)

                # Generamos vrt de recorte
                write_vrt(vrt_text, cod, clase, is_recorte=True,
                          carpeta="path_generados_comunidades_recorte")

                # Repensar el log
                sheets[clase] = sheets[clase].append({'cod_mun': cod,
                                                      'nivel': niveles[i-1]},
                                                     ignore_index=True)

                if "_pto" in clase:
                    cmd = f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}_recorte.vrt >{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt 2>&1"

                
                else:
                    cmd = f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc {var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.fgb  {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}_recorte.vrt >{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt 2>&1"


                # Ejecutamos el comando ogr2ogr para generar el flatgeobuf

                os.system(cmd)

                hay_error = search_str(
                    f"{var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.txt", 'ERROR')
                
                # comprobar error y si es así lanzar el comando con MakeValid

                if hay_error:
                    cmd = f"ogr2ogr -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc {var_dict['path_generados_comunidades_recorte']}{cod}/{cod}.fgb -dialect sqlite -sql \"select distinct ST_MakeValid(geometry),* from {clase}\"  {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}.fgb  {var_dict['path_generados_comunidades_recorte']}{cod}/{clase}_recorte.vrt -skipfailure >/dev/null 2>&1"

                    # cmd = f"ogr2ogr -gt 5000000 -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc {minx} {miny} {maxx} {maxy} -dialect sqlite -sql \"select distinct ST_MakeValid(geometry),* from {clase}\"  /var/MVT_MapaBaseXYZ/DatosProcesados/generados/comunidades/com_aut/{cod}/{clase}.fgb /var/MVT_MapaBaseXYZ/DatosProcesados/productores/nacional/00/{clase}.vrt -skipfailure >/dev/null 2>&1"


                    # print(cmd)

                    os.system(cmd)

                # escribimos el vrt que hace referencia al flatgeobuf comunidad
                vrt_text = f"""
                    <OGRVRTDataSource>
                        <OGRVRTUnionLayer name="{clase}">
                            <OGRVRTLayer name="{clase}">
                                <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
                            </OGRVRTLayer>                     
                        </OGRVRTUnionLayer>
                    </OGRVRTDataSource>
                    """

                write_vrt(vrt_text, cod, clase,
                          carpeta="path_generados_comunidades_recorte")

        else:
            cod = comunidad

            sheets[clase] = sheets[clase].append({'cod_com_aut': cod,
                                                  'nivel': 'None'},
                                                 ignore_index=True)


# Paralelización, el -1 indica que coge el máximo número de procesos. Utilizamos memoria compartida con el parámetro sharedmem, para poder escribir los logs
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(
    delayed(lambda group: [generarComunidad(index, row) for index, row in group[1].iterrows()])(group) for group in comunidades)


# Escribimos en un excel las distintas clases como hojas, con 2 columnas, el código de comunidad y el nivel que ha cogido para la extracción.
now = datetime.now()

dt_string = now.strftime("%Y-%m-%d_%H:%M:%S")
log_path = f"{var_dict['logs_path']}{dt_string}_comunidades.xlsx"
print(f"Tiempo total = {time() - start_time}")
with pd.ExcelWriter(log_path) as writer:
    for clase, clase_short in zip(lista_clases, lista_clases_short):
        sheets[clase].to_excel(writer,
                               sheet_name=str(clase_short), index=False)
