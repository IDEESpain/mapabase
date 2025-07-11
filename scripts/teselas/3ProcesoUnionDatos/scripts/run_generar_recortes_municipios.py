import time
import pandas as pd
import sys
import os
import geopandas
from shapely import wkt
import warnings
from joblib import Parallel, delayed
import json
import shutil
from datetime import datetime
import pathlib
import yaml

# --- INICIO DE LA EJECUCIÓN ---

# Se intenta importar el módulo de funciones generales.
# Si falla, se muestra un error crítico y el script se detiene.
try:
    from funciones_generales import *
except ImportError:
    print("ERROR CRÍTICO: 'funciones_generales.py' no encontrado. Asegúrate de que está accesible.")
    sys.exit(1)

# Se inicia el contador de tiempo para medir la duración total del script.
start_time = time.time()
# Se ignoran las advertencias para mantener la salida limpia.
warnings.filterwarnings("ignore")

# --- CARGA DE CONFIGURACIÓN ---

# Se carga el archivo de configuración principal 'config.json'.
try:
    with open("./config.json") as f:
        var_dict = json.load(f)
except FileNotFoundError:
    print("ERROR: config.json no encontrado.")
    sys.exit(1)
except json.JSONDecodeError:
    print("ERROR: config.json no es un JSON válido.")
    sys.exit(1)

# Se leen las variables del archivo de configuración.
cod_comunidades = var_dict.get("codigo_comunidades", [])
lib_path = var_dict.get("lib_path", "./")
elementos_file = var_dict.get("elementos_file", "elementos.xlsx")
municipios_file = var_dict.get("municipios_file", "municipios.xlsx")
process_4_config_file = var_dict.get("config_proceso_4", "proceso4_config.json")
yaml_estrategia_union_file = var_dict.get("yaml_estrategia_union_file", "estrategia_union_por_ccaa.yaml")

# Se define la jerarquía de niveles a comprobar.
niveles = ["local", 'regional', 'nacional']

# --- CARGAR Y FILTRAR DATOS ---

# Se cargan los dataframes desde los archivos Excel.
try:
    matriz_niveles = pd.read_excel(f"{lib_path}{elementos_file}", engine='openpyxl')
    # Se obtienen todas las clases y sus nombres cortos.
    full_lista_clases = matriz_niveles["elementos"].tolist()
    full_lista_clases_short = matriz_niveles["elementos_short"].tolist()
    
    municipios_df_full = pd.read_excel(f"{lib_path}{municipios_file}", engine='openpyxl')
except FileNotFoundError as e:
    print(f"ERROR: Archivo Excel requerido no encontrado: {e.filename}")
    sys.exit(1)

# --- INICIO DE LA LÓGICA DE FILTRADO DE CAPAS ---
# Se comprueba si en el config se ha especificado una lista de capas para actualizar.
update_layers = var_dict.get("capas_actualizar", [])
if update_layers:
    print(f"INFO: Se ha detectado la clave 'capas_actualizar'. Se procesarán únicamente {len(update_layers)} capas.")
    df_layers = pd.DataFrame({"elementos": full_lista_clases, "elementos_short": full_lista_clases_short})
    # Se filtra el DataFrame para mantener solo las capas especificadas.
    df_layers_filtrado = df_layers[df_layers["elementos"].isin(update_layers)]
    
    # Se actualizan las listas de clases a procesar.
    lista_clases = df_layers_filtrado["elementos"].tolist()
    lista_clases_short = df_layers_filtrado["elementos_short"].tolist()
    print(f"-> Capas a procesar: {lista_clases}")
else:
    # Si no se especifica 'capas_actualizar', se procesan todas.
    print("INFO: No se ha especificado 'capas_actualizar' en config.json. Se procesarán todas las capas.")
    lista_clases = full_lista_clases
    lista_clases_short = full_lista_clases_short
# --- FIN DE LA LÓGICA DE FILTRADO DE CAPAS ---


# --- CONFIGURACIÓN INICIAL Y CARGA DE MÁSCARAS ---

# Si se especifica en la configuración, se regenera la capa de polígonos de municipios (Voronoi).
if var_dict.get("regenerar_municipios_pol_file", False):
    print("Generando capa poligonal de municipios (Voronoi)...")
    try:
        generar_voronoi(var_dict['municipios_pol_file'], modo="municipios")
    except Exception as e:
        print(f"Error durante la generación de Voronoi: {e}")

# Se carga la máscara poligonal de todos los municipios.
try:
    mascara_municipios_global = geopandas.read_file(f"{var_dict['municipios_pol_file']}")
except Exception as e:
    print(f"ERROR: No se pudo leer el archivo de polígonos de municipios: {var_dict.get('municipios_pol_file', 'No especificado')}. Detalles: {e}")
    sys.exit(1)

# Se inicializa un diccionario para almacenar los dataframes de logs para las capas que se van a procesar.
sheets = {clase: pd.DataFrame(columns=["cod_mun", "nivel_origen_datos_final"]) for clase in lista_clases}

def update_proceso4_config_file(path, key, value):
    """Actualiza un archivo de configuración JSON con un par clave-valor."""
    try:
        with open(path, "r") as jsonFile: data = json.load(jsonFile)
    except (FileNotFoundError, json.JSONDecodeError): data = {}
    data[key] = value
    try:
        with open(path, "w+") as jsonFile: json.dump(data, jsonFile, indent=4)
    except IOError: print(f"Advertencia: No se pudo escribir en {path}")

# --- FILTRADO DE MUNICIPIOS A PROCESAR ---

# Se copia el dataframe completo para su posterior filtrado.
municipios_to_process = municipios_df_full.copy()

# Se manejan los argumentos de la línea de comandos para filtrar los municipios a procesar.
if len(sys.argv) == 2 and sys.argv[1] == "update":
    print(f"Actualizando municipios en la carpeta: {var_dict.get('path_productores_municipios', 'N/A')}")
    try:
        lista_municipios_arg = [int(mun) for mun in os.listdir(var_dict['path_productores_municipios'])]
        municipios_to_process = municipios_df_full[municipios_df_full['codigo_ine_mun'].isin(lista_municipios_arg)].reset_index(drop=True)
        comunidades_arg = municipios_to_process['cod_com_aut'].unique().tolist()
        update_proceso4_config_file(process_4_config_file, "lista_municipios", lista_municipios_arg)
        print(f"Lista de comunidades que hay que actualizar (basado en 'update'): {comunidades_arg}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Advertencia en modo 'update': {e}")
elif len(sys.argv) == 2 and sys.argv[1] == "update-missing":
    print(f"Actualizando municipios que faltan en la carpeta: {var_dict.get('path_generados_municipios', 'N/A')}")
    try:
        lista_municipios_generados_arg = [int(mun) for mun in os.listdir(var_dict['path_generados_municipios'])]
        municipios_to_process = municipios_df_full[~municipios_df_full['codigo_ine_mun'].isin(lista_municipios_generados_arg)].reset_index(drop=True)
        comunidades_arg = municipios_to_process['cod_com_aut'].unique().tolist()
        update_proceso4_config_file(process_4_config_file, "lista_comunidades_for_missing_update", comunidades_arg)
        print(f"Lista de comunidades que hay que actualizar (basado en 'update-missing'): {comunidades_arg}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Advertencia en modo 'update-missing': {e}")
elif cod_comunidades:
    municipios_to_process = municipios_df_full[municipios_df_full['cod_com_aut'].isin(cod_comunidades)].reset_index(drop=True)
    update_proceso4_config_file(process_4_config_file, "lista_comunidades", cod_comunidades)
    print(f"Procesando comunidades desde config: {cod_comunidades}")
else:
    print("Procesando todas las comunidades del archivo de municipios.")
    update_proceso4_config_file(process_4_config_file, "lista_comunidades", municipios_df_full['cod_com_aut'].unique().tolist())


def generarMunicipio(index, row, capas_a_procesar):
    """
    Función para el procesamiento detallado de un municipio.
    Realiza recorte o copia individual de datos.
    """
    cod_mun_str = str(int(row["codigo_ine_mun"])).zfill(5)
    cod_com_aut_str = str(int(row["cod_com_aut"])).zfill(2)

    path_generado_municipio = pathlib.Path(f"{var_dict['path_generados_municipios']}{cod_mun_str}")
    path_generado_municipio.mkdir(parents=True, exist_ok=True)

    print(f"  Procesando municipio (recorte detallado): {index + 1} / {df_municipios_in_ccaa_a_procesar_detalle.shape[0]}\t({cod_mun_str}) CCAA: {cod_com_aut_str}")
    sys.stdout.flush()

    mascara_municipio_gdf = mascara_municipios_global[mascara_municipios_global["codigo"].str.endswith(cod_mun_str)]
    if mascara_municipio_gdf.empty:
        print(f"    Advertencia: No se encontró máscara para el municipio {cod_mun_str}.")
    else:
        mascara_municipio_gdf = mascara_municipio_gdf.copy()
        try:
            mascara_municipio_gdf['geometry'] = mascara_municipio_gdf['geometry'].buffer(var_dict.get("buffer", 0.0))
            mascara_municipio_gdf.to_file(path_generado_municipio / f"{cod_mun_str}.fgb", driver='FlatGeobuf', crs="EPSG:4258")
        except Exception as e:
            print(f"    Error aplicando buffer o guardando máscara para {cod_mun_str}: {e}")

    coordinates_wkt_list = []
    if not mascara_municipio_gdf.empty and 'geometry' in mascara_municipio_gdf.columns:
        try:
            exploded_gdf = mascara_municipio_gdf.explode(index_parts=False)
            coordinates_wkt_list = exploded_gdf["geometry"].apply(lambda x: wkt.dumps(x)).tolist()
        except Exception as e:
            print(f"    Error explotando geometría para {cod_mun_str}: {e}.")
            if not mascara_municipio_gdf.empty:
                coordinates_wkt_list = mascara_municipio_gdf["geometry"].apply(lambda x: wkt.dumps(x)).tolist()

    for clase in capas_a_procesar:
        nivel_encontrado_flag = False
        path_data_source_vrt = None
        nivel_data_source_name = "None"
        
        for i_loop in range(len(niveles)):
            current_search_level = niveles[i_loop]
            code_to_check = ""
            if current_search_level == "local": code_to_check = cod_mun_str
            elif current_search_level == "regional": code_to_check = cod_com_aut_str
            elif current_search_level == "nacional": code_to_check = "00"
            
            check_result = check_nivel(current_search_level, code_to_check, clase)

            if check_result:
                path_data_source_vrt = check_result[0] if isinstance(check_result, list) and len(check_result) > 0 else (check_result if isinstance(check_result, str) else None)
                if path_data_source_vrt:
                    nivel_data_source_name = current_search_level
                    nivel_encontrado_flag = True
                    break

        if nivel_encontrado_flag:
            dest_clase_fgb = path_generado_municipio / f"{clase}.fgb"
            if nivel_data_source_name == "local":
                path_data_source_fgb = path_data_source_vrt.replace(".vrt", ".fgb")
                dest_clase_vrt = path_generado_municipio / f"{clase}.vrt"
                if os.path.exists(path_data_source_vrt) and os.path.exists(path_data_source_fgb):
                    shutil.copy(path_data_source_vrt, dest_clase_vrt)
                    shutil.copy(path_data_source_fgb, dest_clase_fgb)
                else:
                    nivel_data_source_name = "None_Productor_Local_Faltante"
            else:
                if not coordinates_wkt_list:
                    nivel_data_source_name = "None_Sin_Mascara_Valida"
                else:
                    vrt_clip_text = do_clip(nivel_data_source_name, path_data_source_vrt, coordinates_wkt_list, clase)
                    write_vrt(vrt_clip_text, cod_mun_str, clase, is_recorte=True, carpeta="path_generados_municipios")
                    path_recorte_vrt = path_generado_municipio / f"{clase}_recorte.vrt"
                    ogr_log_file = path_generado_municipio / f"{cod_mun_str}_{clase}.txt"
                    cmd_base = f'ogr2ogr -nln "{clase}" -f "FlatGeobuf" -nlt PROMOTE_TO_MULTI'
                    
                    if "_pto" in clase:
                        cmd = f'{cmd_base} "{dest_clase_fgb}" "{path_recorte_vrt}" -skipfailure > "{ogr_log_file}" 2>&1'
                    else:
                        cmd = f'{cmd_base} -clipsrc "{path_generado_municipio / f"{cod_mun_str}.fgb"}" "{dest_clase_fgb}" "{path_recorte_vrt}" > "{ogr_log_file}" 2>&1'
                    
                    os.system(cmd)
                    
                    if not "_pto" in clase and search_str(str(ogr_log_file), 'ERROR'):
                        print(f"      Reintentando con ST_MakeValid para {clase}.")
                        cmd = f'{cmd_base} -clipsrc "{path_generado_municipio / f"{cod_mun_str}.fgb"}" -dialect sqlite -sql "select distinct ST_MakeValid(geometry) as geometry, * from \\"{clase}\\"" "{dest_clase_fgb}" "{path_recorte_vrt}" -skipfailure > "{ogr_log_file}" 2>&1'
                        os.system(cmd)
                    
                    final_vrt_text = f"""<OGRVRTDataSource><OGRVRTUnionLayer name="{clase}"><OGRVRTLayer name="{clase}"><SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource></OGRVRTLayer></OGRVRTUnionLayer></OGRVRTDataSource>"""
                    write_vrt(final_vrt_text, cod_mun_str, clase, is_recorte=False, carpeta="path_generados_municipios")
        else:
            nivel_data_source_name = "None_No_Productor_Superior"
        
        new_row = pd.DataFrame([{'cod_mun': cod_mun_str, 'nivel_origen_datos_final': nivel_data_source_name}])
        sheets[clase] = pd.concat([sheets[clase], new_row], ignore_index=True)


# --- BUCLE PRINCIPAL CON ESTRATEGIA DUAL POR CCAA ---
estrategia_union_final = {}
grouped_by_ccaa = municipios_to_process.groupby('cod_com_aut')
lista_municipios_para_procesamiento_detalle = []

for cod_ccaa_key, df_municipios_in_ccaa in grouped_by_ccaa:
    cod_ccaa_str_loop = str(cod_ccaa_key).zfill(2)
    print(f"\n--- Evaluando CCAA: {cod_ccaa_str_loop} ---")

    ccaa_has_municipal_producer = False
    for _, mun_row_check in df_municipios_in_ccaa.iterrows():
        cod_mun_check_str = str(int(mun_row_check["codigo_ine_mun"])).zfill(5)
        # Se comprueba solo sobre las capas que se van a procesar.
        for clase_check in lista_clases:
            if check_nivel('local', cod_mun_check_str, clase_check):
                ccaa_has_municipal_producer = True
                print(f"  INFO: Productor municipal encontrado para {cod_mun_check_str} (clase {clase_check}). La CCAA {cod_ccaa_str_loop} requiere procesamiento detallado.")
                break
        if ccaa_has_municipal_producer:
            break

    if not ccaa_has_municipal_producer:
        print(f"  ESTRATEGIA para CCAA {cod_ccaa_str_loop}: UNIÓN DIRECTA DESDE CCAA. No se copian archivos.")
        estrategia_union_final[cod_ccaa_str_loop] = {
            "action": "use_ccaa_source_for_union",
            "reason": "No se encontraron productores a nivel municipal en esta CCAA."
        }
        for _, mun_row in df_municipios_in_ccaa.iterrows():
            cod_mun_str_log = str(int(mun_row["codigo_ine_mun"])).zfill(5)
            # El log se rellena solo para las capas filtradas.
            for clase in lista_clases:
                new_row = pd.DataFrame([{'cod_mun': cod_mun_str_log, 'nivel_origen_datos_final': 'regional_directo_para_union'}])
                sheets[clase] = pd.concat([sheets[clase], new_row], ignore_index=True)
    else:
        print(f"  ESTRATEGIA para CCAA {cod_ccaa_str_loop}: PROCESAMIENTO MUNICIPAL. Se encontraron productores.")
        estrategia_union_final[cod_ccaa_str_loop] = {
            "action": "individual_municipal_processing",
            "reason": "Se encontraron uno o más productores a nivel municipal en esta CCAA."
        }
        lista_municipios_para_procesamiento_detalle.extend(df_municipios_in_ccaa.to_dict('records'))


# --- PROCESAMIENTO DETALLADO EN PARALELO ---
if lista_municipios_para_procesamiento_detalle:
    df_municipios_in_ccaa_a_procesar_detalle = pd.DataFrame(lista_municipios_para_procesamiento_detalle).reset_index(drop=True)
    print(f"\n--- Iniciando procesamiento detallado en paralelo para {df_municipios_in_ccaa_a_procesar_detalle.shape[0]} municipios ---")
    num_threads = var_dict.get("num_threads", -1)
    
    Parallel(n_jobs=num_threads, require='sharedmem')(
        delayed(generarMunicipio)(idx, row_data, lista_clases) for idx, row_data in df_municipios_in_ccaa_a_procesar_detalle.iterrows()
    )
else:
    print("\n--- No hay municipios que requieran procesamiento detallado. Solo se definió la estrategia de unión. ---")

# --- LOGGING FINAL ---
try:
    with open(yaml_estrategia_union_file, 'w', encoding='utf-8') as f_yaml:
        yaml.dump(estrategia_union_final, f_yaml, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"\nResumen de la estrategia de unión guardado en: {yaml_estrategia_union_file}")
except IOError:
    print(f"Advertencia: No se pudo escribir el resumen YAML en {yaml_estrategia_union_file}")

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
log_path = pathlib.Path(var_dict.get("logs_path", "./logs/")) / f"{dt_string}_municipios_log.xlsx"
log_path.parent.mkdir(parents=True, exist_ok=True)

try:
    with pd.ExcelWriter(log_path) as writer:
        # El log se escribe solo para las capas procesadas.
        for clase, clase_short in zip(lista_clases, lista_clases_short):
            valid_sheet_name = "".join(c for c in clase_short if c.isalnum() or c in (' ', '_')).strip()[:31]
            if not valid_sheet_name: valid_sheet_name = clase[:31]
            sheets[clase].to_excel(writer, sheet_name=valid_sheet_name, index=False)
    print(f"Log Excel guardado en: {log_path}")
except Exception as e:
    print(f"Error escribiendo el log Excel: {e}")

print(f"\nEjecución finalizada. Tiempo total: {time.time() - start_time:.2f} segundos")
