import pandas as pd
import os
from joblib import Parallel, delayed
from funciones_generales import *
import json
import pathlib

# Abrimos y leemos la configuración
with open("./config.json") as f:
    var_dict = json.load(f)

lib_path = var_dict["lib_path"]

# Archivo de la matriz de elementos
elementos_file = var_dict["elementos_file"]

# Archivo de listado de municipios
municipios_file = var_dict["municipios_file"]

niveles = ["local", "regional", "nacional"]

matriz_niveles = pd.read_excel(f"{lib_path}{elementos_file}", engine='openpyxl')
lista_clases = matriz_niveles["elementos"]
lista_clases_short = matriz_niveles["elementos_short"]

municipios = pd.read_excel(f"{lib_path}{municipios_file}", engine='openpyxl')

# Creamos la carpeta de salida si no existe
pathlib.Path(f"{var_dict['path_generados_nacional_com_aut']}00").mkdir(parents=True, exist_ok=True)

comunidades = municipios.groupby(by="cod_com_aut")

def generarClaseNacional(clase):
    lista_comunidades_presentes = []
    lista_comunidades_no_presentes = []
    print(f"Procesando lista de comunidades que contienen el elemento {clase}")

    for comunidad in comunidades.groups:
        cod_com = str(comunidad).zfill(2)
        ruta_vrt_mun = check_nivel("regional_generados", cod_com, clase)
        if ruta_vrt_mun:
            lista_comunidades_presentes.append((cod_com, ruta_vrt_mun[0]))
        else:
            lista_comunidades_no_presentes.append((cod_com, None))

    if lista_comunidades_presentes:
        print(f"Generando vrt nacional para el elemento {clase}")
        vrt = vrt_nacional(clase, lista_comunidades_presentes)
        write_vrt(vrt, "00", clase, is_recorte=True, carpeta="path_generados_nacional_com_aut")
                
        cmd = (
            f"ogr2ogr -skipfailures -f \"FlatGeobuf\" -nln {clase} -dialect sqlite "
            f"-sql \"select ST_Multi(geometry),* from {clase}\" "
            f"{var_dict['path_generados_nacional_com_aut']}00/{clase}.fgb "
            f"{var_dict['path_generados_nacional_com_aut']}00/{clase}_recorte.vrt 2>> ../logs/union_comunidades_error.log"
        )

        try:
            os.system(cmd)
        except Exception as e:
            print(f"Se produjo una excepción: {e}")

        vrt_text = f"""
            <OGRVRTDataSource>
                <OGRVRTUnionLayer name="{clase}">
                    <OGRVRTLayer name="{clase}">
                        <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
                    </OGRVRTLayer>                     
                </OGRVRTUnionLayer>
            </OGRVRTDataSource>
            """
        
        write_vrt(vrt_text, "00", clase, carpeta="path_generados_nacional_com_aut")
        print(f"Elemento {clase} nacional generado")
    else:
        print(f"No se encontraron comunidades con el elemento {clase}")


update_layers = var_dict.get("capas_actualizar", [])
if update_layers:
    layers_to_update = [clase for clase in lista_clases if clase in update_layers]
    if not layers_to_update:
        print("No hay coincidencias entre las capas a actualizar y las existentes.")
else:
    layers_to_update = lista_clases

Parallel(n_jobs=var_dict["num_threads"], require='sharedmem')(
    delayed(generarClaseNacional)(clase) for clase in layers_to_update
)

print("Proceso de unión nacional de comunidades terminado")
sheets = {}
