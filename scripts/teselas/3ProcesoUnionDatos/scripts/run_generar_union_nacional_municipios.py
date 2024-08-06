import pandas as pd
import os
from joblib import Parallel, delayed
from funciones_generales import *
import json

f = open ("./config.json")

var_dict=json.load(f)

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

pathlib.Path(f"{var_dict['path_generados_nacional_municipios']}00").mkdir(parents=True, exist_ok=True)

def generarClaseNacional(clase):
    lista_comunidades_presentes=[]
    lista_comunidades_no_presentes=[]
    
    print(f"Procesando lista de municipios que contienen el elemento {clase}")
    for index,municipio in municipios.iterrows():

        cod_com = str(municipio["codigo_ine_mun"]).zfill(5)
        ruta_vrt_mun = check_nivel("local_generados",cod_com,clase)

        if ruta_vrt_mun:
                lista_comunidades_presentes.append((cod_com,ruta_vrt_mun[0]))
        else:
                lista_comunidades_no_presentes.append((cod_com,None))
        
    #print(lista_comunidades_presentes)
    if lista_comunidades_presentes:
        print(f"Generando vrt nacional para el elemento {clase}")
        vrt=vrt_nacional(clase,lista_comunidades_presentes, False)

        #escribimos el vrt de recorte
        write_vrt(vrt,"00",clase,is_recorte=True,carpeta="path_generados_nacional_municipios")

        cmd=f"ogr2ogr -skipfailures -f \"FlatGeobuf\" -nln {clase} -dialect sqlite -sql \"select ST_MakeValid(geometry),* from {clase}\" {var_dict['path_generados_nacional_municipios']}00/{clase}.fgb {var_dict['path_generados_nacional_municipios']}00/{clase}_recorte.vrt >/dev/null 2>&1"


        #Ejecutamos el comando ogr2ogr para generar el geojson
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
        
        write_vrt(vrt_text,"00",clase,carpeta="path_generados_nacional_municipios")
        print(f"Elemento {clase} nacional generado")
    else:
        pass
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(delayed(generarClaseNacional)(clase) for clase in lista_clases)

print("Proceso de unión nacional de municipios terminado")

sheets={}