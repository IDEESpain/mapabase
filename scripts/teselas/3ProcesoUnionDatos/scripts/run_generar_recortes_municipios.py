from time import sleep
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


warnings.filterwarnings("ignore")

f = open ("./config.json")

var_dict=json.load(f)

#Definimos las comunidades que se van a ejecutar
cod_comunidades=var_dict["codigo_comunidades"]

lib_path=var_dict["lib_path"]

#archivo de la matriz de elementos
elementos_file=var_dict["elementos_file"]

#archivo de listado de municipios
municipios_file=var_dict["municipios_file"]


niveles=["local",'regional','nacional']

matriz_niveles= pd.read_excel(f"{lib_path}{elementos_file}",engine='openpyxl')

lista_clases = matriz_niveles["elementos"]

lista_clases_short = matriz_niveles["elementos_short"]

municipios = pd.read_excel(f"{lib_path}{municipios_file}",engine='openpyxl')

if var_dict["regenerar_municipios_pol_file"]:
    print("Generando capa poligonal de municipios")
    generar_voronoi(var_dict['municipios_pol_file'], modo="municipios")


mascara_municipios = geopandas.read_file(f"{var_dict['municipios_pol_file']}")

sheets={}

def update_proceso4_config_file(path,key,value):
    jsonFile = open(path, "r") # Open the JSON file for reading
    data = json.load(jsonFile) # Read the JSON into the buffer
    jsonFile.close() # Close the JSON file

    ## Working with buffered content
    data[key] = value
    
    ## Save our changes to JSON file
    jsonFile = open(path, "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

process_4_config_file=var_dict["config_proceso_4"]

if(len(sys.argv)==2 and sys.argv[1]=="update"):
    print(f"Actualizando municipios en la carpeta: {var_dict['path_productores_municipios']}")

    lista_municipios= [int(mun) for mun in os.listdir(var_dict['path_productores_municipios'])]
    municipios= municipios.loc[municipios['codigo_ine_mun'].isin(lista_municipios)].reset_index()
    comunidades = municipios.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]

    update_proceso4_config_file(process_4_config_file,"lista_municipios",lista_municipios)

    print(f"Lista de comunidades que hay que actualizar: {keys}")

elif(len(sys.argv)==2 and sys.argv[1]=="update-missing"):
    print(f"Actualizando municipios que faltan en la carpeta: {var_dict['path_generados_municipios']}")

    lista_municipios= [int(mun) for mun in os.listdir(var_dict['path_generados_municipios'])]
    municipios= municipios.loc[~municipios['codigo_ine_mun'].isin(lista_municipios)].reset_index()
    comunidades = municipios.groupby(by="cod_com_aut")
    keys = [key for key, _ in comunidades]

    update_proceso4_config_file(process_4_config_file,"lista_municipios",lista_municipios)


    print(f"Lista de comunidades que hay que actualizar: {keys}")

    # print(municipios)

    # exit()

elif cod_comunidades:
    municipios= municipios.loc[municipios['cod_com_aut'].isin(cod_comunidades)].reset_index()
    comunidades = municipios.groupby(by="cod_com_aut")

    update_proceso4_config_file(process_4_config_file,"lista_comunidades",cod_comunidades)



for clase in lista_clases:
    sheets[clase]=pd.DataFrame(columns=["cod_mun","nivel"])


def generarMunicipio(index,row):
    cod_mun=str(int(row["codigo_ine_mun"])).zfill(5)

    pathlib.Path(f"{var_dict['path_generados_municipios']}{cod_mun}").mkdir(parents=True, exist_ok=True)

    warnings.filterwarnings("ignore")

    print(f"generando municipios:  {index} / {municipios.shape[0]}\t\t({cod_mun})")
    sys.stdout.flush()
    #mascara_municipio=generarLimite(spain = municipios_pol, modo = "municipios", cod=str(int(row["codigo_ine_mun"])).zfill(5),cod_comunidad=str(row["cod_com_aut"]).zfill(2))
    #mascara_municipio=generarLimite(cod=str(int(row["codigo_ine_mun"])).zfill(5),cod_comunidad=str(row["cod_com_aut"]).zfill(2))

    mascara_municipio = mascara_municipios[mascara_municipios["codigo"].str[6:] == cod_mun]
    mascara_municipio['geometry'] = mascara_municipio['geometry'].buffer(var_dict["buffer"])
    mascara_municipio.to_file(f"{var_dict['path_generados_municipios']}{cod_mun}/{cod_mun}.fgb", driver='FlatGeobuf' ,crs="EPSG:4258")
    mascara_municipio=mascara_municipio.explode(index_parts=False)
    coordinates=mascara_municipio["geometry"].apply(lambda x: wkt.dumps(x))

    for clase in lista_clases:
        i=0
        index_level=i
        nivel=niveles[0]
        nivel_encontrado=False
        while (not nivel_encontrado) and (i<len(niveles)):
            nivel=niveles[i]
            if i==0:
                cod=str(int(row["codigo_ine_mun"])).zfill(5)
            elif i==1:
                cod=str(row["cod_com_aut"]).zfill(2)
            else:
                cod="00"
            nivel_encontrado=check_nivel(nivel,cod,clase)
            i+=1

        if nivel_encontrado:
            if i==1:
                path_to_vrt=nivel_encontrado[0]
                path_to_fgb=path_to_vrt.split(".vrt")[0]+".fgb"

                shutil.copy(path_to_vrt, f"{var_dict['path_generados_municipios']}{cod}")
                shutil.copy(path_to_fgb, f"{var_dict['path_generados_municipios']}{cod}")

            else:
                #hacemos el clip del vrt encontrado
                                            
                cod=str(int(row["codigo_ine_mun"])).zfill(5)

                #Hacemos el clip
                vrt_text=do_clip(niveles[i-1],nivel_encontrado[0],coordinates,clase)
             
                #Generamos vrt de recorte
                write_vrt(vrt_text,cod,clase,is_recorte=True,carpeta="path_generados_municipios")

                #Repensar el log
                sheets[clase] = sheets[clase].append({'cod_mun' : cod,
                    'nivel' : niveles[i-1]} , 
                    ignore_index=True)

                if "_pto" in clase:
                    cmd=f"ogr2ogr -gt 5000000 -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI {var_dict['path_generados_municipios']}{cod}/{clase}.fgb {var_dict['path_generados_municipios']}{cod}/{clase}_recorte.vrt -skipfailure >/dev/null 2>&1"
            
                else:  
                    cmd=f"ogr2ogr -gt 5000000 -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc {var_dict['path_generados_municipios']}{cod}/{cod}.fgb  {var_dict['path_generados_municipios']}{cod}/{clase}.fgb {var_dict['path_generados_municipios']}{cod}/{clase}_recorte.vrt >{var_dict['path_generados_municipios']}{cod}/{cod}.txt 2>&1"

                #Ejecutamos el comando ogr2ogr para generar el flatgeobuf
                os.system(cmd)
                
                hay_error=search_str(f"{var_dict['path_generados_municipios']}{cod}/{cod}.txt", 'ERROR')

                #comprobar error y si es así lanzar el comando con MakeValid

                if hay_error:
            
                    cmd=f"ogr2ogr -gt 5000000 -nln {clase} -f \"FlatGeobuf\" -nlt PROMOTE_TO_MULTI -clipsrc {var_dict['path_generados_municipios']}{cod}/{cod}.fgb -dialect sqlite -sql \"select distinct ST_MakeValid(geometry),* from {clase}\"  {var_dict['path_generados_municipios']}{cod}/{clase}.fgb  {var_dict['path_generados_municipios']}{cod}/{clase}_recorte.vrt -skipfailure >/dev/null 2>&1"
                    
                    # print(cmd)

                    os.system(cmd)

                #escribimos el vrt que hace referencia al flatgeobuf municipal
                vrt_text=f"""
                    <OGRVRTDataSource>
                        <OGRVRTUnionLayer name="{clase}">
                            <OGRVRTLayer name="{clase}">
                                <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
                            </OGRVRTLayer>                     
                        </OGRVRTUnionLayer>
                    </OGRVRTDataSource>
                    """
                
                write_vrt(vrt_text,cod,clase,carpeta="path_generados_municipios")    


        else:
            cod=str(row["codigo_ine_mun"]).zfill(5)

            sheets[clase] = sheets[clase].append({'cod_mun' : cod,
                    'nivel' : 'None'} , 
                    ignore_index=True)

#Paralelización, el -1 indica que coge el máximo número de procesos. Utilizamos memoria compartida con el parámetro sharedmem, para poder escribir los logs
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(delayed(generarMunicipio)(index,row) for index, row in municipios.iterrows())

#Escribimos en un excel las distintas clases como hojas, con 2 columnas, el código de municipio y el nivel que ha cogido para la extracción.
now = datetime.now()

dt_string = now.strftime("%Y-%m-%d_%H:%M:%S")
log_path=f"{var_dict['logs_path']}{dt_string}_municipios.xlsx"

with pd.ExcelWriter(log_path) as writer:
    for clase,clase_short in zip(lista_clases,lista_clases_short):
        sheets[clase].to_excel(writer,
             sheet_name=str(clase_short),index=False)