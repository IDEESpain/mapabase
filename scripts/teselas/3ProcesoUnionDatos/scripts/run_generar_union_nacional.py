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

pathlib.Path(f"{var_dict['path_generados_nacional_com_aut']}00").mkdir(parents=True, exist_ok=True)


comunidades = municipios.groupby(by="cod_com_aut")
def generarClaseNacional(clase):
    lista_comunidades_presentes=[]
    lista_comunidades_no_presentes=[]
    print(f"Procesando lista de comunidades que contienen el elemento {clase}")

    for comunidad in comunidades.groups:
            
        cod_com = str(comunidad).zfill(2)
        #print(cod_com)

        ruta_vrt_mun = check_nivel("regional_generados",cod_com,clase)
            

        if ruta_vrt_mun:
                lista_comunidades_presentes.append((cod_com,ruta_vrt_mun[0]))
        else:
                lista_comunidades_no_presentes.append((cod_com,None))

    #print(lista_comunidades_presentes)
    if lista_comunidades_presentes:
        print(f"Generando vrt nacional para el elemento {clase}")
        vrt=vrt_nacional(clase,lista_comunidades_presentes)

        #escribimos el vrt de recorte
        write_vrt(vrt,"00",clase,is_recorte=True,carpeta="path_generados_nacional_com_aut")

        # PROBAR NUEVA FORMA DE GENERAR UNIÓN NACIONAL!!
        
        # Lista de archivos FGB que deseas unir
        archivos_fgb = []
        for c in lista_comunidades_presentes:
            cod = c[0]
            archivo = str(var_dict['path_generados_comunidades_com_aut']) + str(cod)+ "/"+clase +".fgb"
            archivos_fgb.append(archivo)
            
        # Nombre del archivo de salida
        archivo_salida = f"{var_dict['path_generados_nacional_com_aut']}00/{clase}.fgb"
        gdf_total = gpd.GeoDataFrame()
        for archivo in archivos_fgb:
           print(f"Leyendo {archivo}")
           gdf_comunidad = gpd.read_file(archivo)
           gdf_total = gpd.GeoDataFrame( pd.concat( [gdf_total,gdf_comunidad], ignore_index=True) )
        print(f"Guardando fichero {archivo_salida}")
        gdf_total.to_file(archivo_salida , driver="FlatGeobuf",crs="EPSG:4258")   
        
        # ANTIGUO CÓDIGO POR SI FUNCIONA PEOR LO DE ARRIBA!!
        
        # cmd=f"ogr2ogr -skipfailures -f \"FlatGeobuf\" -nln {clase} -dialect sqlite -sql \"select distinct geometry,* from {clase}\" {var_dict['path_generados_nacional_com_aut']}00/{clase}.fgb {var_dict['path_generados_nacional_com_aut']}00/{clase}_recorte.vrt >/dev/null 2>&1"


        # #Ejecutamos el comando ogr2ogr para generar el geojson
        # try:
        #     os.system(cmd)
        # except Exception as e:
        #     print(f"Se produjo una excepción: {e}")
            

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
        
        write_vrt(vrt_text,"00",clase,carpeta="path_generados_nacional_com_aut")
        print(f"Elemento {clase} nacional generado")
    else:
        pass
Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(delayed(generarClaseNacional)(clase) for clase in lista_clases)


sheets={}