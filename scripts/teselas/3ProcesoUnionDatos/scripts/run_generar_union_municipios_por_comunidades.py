import pandas as pd
import sys
import os
from funciones_generales import *
from joblib import Parallel, delayed
import json

f = open ("./config.json")

var_dict=json.load(f)

#Definimos las comunidades que se van a ejecutar
lista_comunidades=var_dict["codigo_comunidades"]

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

municipios_por_comunidades = municipios.groupby(by="cod_com_aut")

#print(municipios_por_comunidades)

if not lista_comunidades:
    lista_comunidades=[comunidad for comunidad,municipios_com in municipios_por_comunidades.groups.items()]
    print("lista de comunidades: ",lista_comunidades)
    
def generarComunidad(comunidad,municipios_com):

    if comunidad in lista_comunidades:

        com=str(comunidad).zfill(2)

        pathlib.Path(f"{var_dict['path_generados_comunidades_municipios']}{com}").mkdir(parents=True, exist_ok=True)

        print("Número comunidad: ",comunidad)
        sys.stdout.flush()

        for clase in lista_clases:

            lista_municipios_presentes=[]
            lista_municipios_no_presentes=[]

            for index_mun in municipios_com:
                
                cod_mun = municipios.iloc[index_mun]["codigo_ine_mun"]
                cod_mun=str(cod_mun).zfill(5)

                ruta_vrt_mun = check_nivel("local_generados",cod_mun,clase)

                #print(ruta_vrt_mun)
                
                if ruta_vrt_mun:
                    lista_municipios_presentes.append((cod_mun,ruta_vrt_mun[0]))
                else:
                    lista_municipios_no_presentes.append((cod_mun,None))
       
            #print(lista_municipios_presentes)
            if lista_municipios_presentes:
                vrt=vrt_comunidad_autonoma(clase,lista_municipios_presentes)

                # #Escribimos el vrt de recorte
                write_vrt(vrt,com,clase,is_recorte=True,carpeta="path_generados_comunidades_municipios")

                cmd=f"ogr2ogr -f \"FlatGeobuf\" -nln {clase} -dialect sqlite -sql \"select distinct ST_MakeValid(geometry),* from {clase}\" {var_dict['path_generados_comunidades_municipios']}{com}/{clase}.fgb {var_dict['path_generados_comunidades_municipios']}{com}/{clase}_recorte.vrt >/dev/null 2>&1"
                
                #Ejecutamos el comando ogr2ogr para generar el fgb
                os.system(cmd)

                #escribimos el vrt que hace referencia al geojson municipal
                vrt_text=f"""
                    <OGRVRTDataSource>
                        <OGRVRTUnionLayer name="{clase}">
                            <OGRVRTLayer name="{clase}">
                                <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
                            </OGRVRTLayer>                     
                        </OGRVRTUnionLayer>
                    </OGRVRTDataSource>
                    """
                
                write_vrt(vrt_text,com,clase,carpeta="path_generados_comunidades_municipios")
                
            else:
                pass

#Paralelización, el -1 indica que coge el máximo número de procesos. Utilizamos memoria compartida con el parámetro sharedmem, para poder escribir los logs
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(delayed(generarComunidad)(comunidad,municipios_com) for comunidad,municipios_com in municipios_por_comunidades.groups.items())
                
sheets={}