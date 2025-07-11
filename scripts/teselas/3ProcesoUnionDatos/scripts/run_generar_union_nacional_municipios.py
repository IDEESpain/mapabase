import pandas as pd
import os
from joblib import Parallel, delayed
import json
import pathlib
import yaml
import sys

# Se importa de forma explícita para evitar 'wildcard imports' y asegurar
# que las funciones estén disponibles en el ámbito global para los workers de joblib.
try:
    from funciones_generales import check_nivel, vrt_nacional, write_vrt
except ImportError:
    print("ERROR CRÍTICO: 'funciones_generales.py' no encontrado. Asegúrate de que está accesible.")
    sys.exit(1)

def get_config():
    """Carga la configuración principal desde config.json."""
    try:
        with open("./config.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR CRÍTICO: config.json no encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR CRÍTICO: config.json no es un JSON válido.")
        sys.exit(1)

def generarClaseNacional(clase, config):
    """
    Genera la capa nacional unificada para una clase de elemento específica.
    ESTA FUNCIÓN SE EJECUTA EN UN PROCESO INDEPENDIENTE Y CARGA SUS PROPIOS DATOS.
    """
    print(f"\n--- [Worker] Iniciando proceso para la capa: {clase} ---")

    # --- Carga de datos específica del Worker ---
    try:
        lib_path = config.get("lib_path", "./")
        municipios_file = config.get("municipios_file", "municipios.xlsx")
        yaml_estrategia_union_file = config.get("yaml_estrategia_union_file", "estrategia_union_por_ccaa.yaml")
        
        municipios_df = pd.read_excel(f"{lib_path}{municipios_file}", engine='openpyxl')
        
        # El archivo de estrategia puede no existir si es la primera ejecución.
        estrategia_ccaa = {}
        if os.path.exists(yaml_estrategia_union_file):
            with open(yaml_estrategia_union_file, 'r') as f_yaml:
                estrategia_ccaa_raw = yaml.safe_load(f_yaml)
                if estrategia_ccaa_raw:
                    # NORMALIZACIÓN DE CLAVES: Clave para el éxito.
                    estrategia_ccaa = {str(k).zfill(2): v for k, v in estrategia_ccaa_raw.items()}
    except Exception as e:
        print(f"  [Worker] ERROR FATAL para '{clase}': No se pudo cargar la estrategia o los municipios. Causa: {e}")
        return # Detiene este worker específico.

    lista_fuentes_vrt = []
    
    # Se obtienen TODAS las comunidades del archivo de municipios para asegurar una unión completa.
    all_ccaa_codes = sorted(municipios_df['cod_com_aut'].unique())

    # Se itera sobre TODAS las CCAA de España.
    for cod_ccaa_int in all_ccaa_codes:
        cod_ccaa_str = str(cod_ccaa_int).zfill(2)
        
        # Se busca una estrategia para la CCAA actual en el archivo YAML.
        strategy = estrategia_ccaa.get(cod_ccaa_str)

        # --- CASO 1: LA CCAA FUE ACTUALIZADA (tiene estrategia en el YAML) ---
        if strategy and isinstance(strategy, dict):
            # ESTRATEGIA A: Usar datos de municipios individuales recién generados.
            if strategy.get("action") == "individual_municipal_processing":
                print(f"  -> CCAA {cod_ccaa_str}: Aplicando estrategia de actualización (municipal).")
                df_municipios_in_ccaa = municipios_df[municipios_df['cod_com_aut'] == cod_ccaa_int]
                for _, municipio in df_municipios_in_ccaa.iterrows():
                    cod_mun_str = str(int(municipio["codigo_ine_mun"])).zfill(5)
                    ruta_vrt_mun = check_nivel("local_generados", cod_mun_str, clase)
                    if ruta_vrt_mun:
                        abs_path = os.path.abspath(ruta_vrt_mun[0])
                        lista_fuentes_vrt.append((cod_mun_str, abs_path))

            # ESTRATEGIA B: Usar el dato de la CCAA completa recién generado.
            elif strategy.get("action") == "use_ccaa_source_for_union":
                print(f"  -> CCAA {cod_ccaa_str}: Aplicando estrategia de actualización (regional).")
                ruta_vrt_ccaa = check_nivel("regional_generados", cod_ccaa_str, clase)
                if ruta_vrt_ccaa:
                    abs_path = os.path.abspath(ruta_vrt_ccaa[0])
                    lista_fuentes_vrt.append((cod_ccaa_str, abs_path))
        
        # --- CASO 2: LA CCAA NO FUE ACTUALIZADA (no tiene estrategia en el YAML) ---
        else:
            print(f"  -> CCAA {cod_ccaa_str}: No actualizada. Buscando datos generados previamente...")
            # Se busca primero si existe una capa de CCAA ya generada.
            ruta_vrt_ccaa = check_nivel("regional_generados", cod_ccaa_str, clase)
            if ruta_vrt_ccaa:
                abs_path = os.path.abspath(ruta_vrt_ccaa[0])
                lista_fuentes_vrt.append((cod_ccaa_str, abs_path))
            else:
                # Si no, se buscan los municipios individuales generados en una ejecución anterior.
                df_municipios_in_ccaa = municipios_df[municipios_df['cod_com_aut'] == cod_ccaa_int]
                for _, municipio in df_municipios_in_ccaa.iterrows():
                    cod_mun_str = str(int(municipio["codigo_ine_mun"])).zfill(5)
                    ruta_vrt_mun = check_nivel("local_generados", cod_mun_str, clase)
                    if ruta_vrt_mun:
                        abs_path = os.path.abspath(ruta_vrt_mun[0])
                        lista_fuentes_vrt.append((cod_mun_str, abs_path))

    # --- GENERACIÓN DEL VRT Y UNIÓN CON OGR2OGR ---
    path_salida_nacional = pathlib.Path(config['path_generados_nacional_municipios']) / "00"

    if lista_fuentes_vrt:
        print(f"  -> Generando VRT nacional para la capa '{clase}' con {len(lista_fuentes_vrt)} fuentes.")
        
        vrt_union_content = vrt_nacional(clase, lista_fuentes_vrt, comunidades=False)
        write_vrt(vrt_union_content, "00", clase, is_recorte=True, carpeta="path_generados_nacional_municipios")

        cmd = (
            f"ogr2ogr -skipfailures -f \"FlatGeobuf\" -nln {clase} -dialect sqlite "
            f"-sql \"SELECT ST_MakeValid(geometry) AS geometry, * FROM {clase}\" "
            f"\"{path_salida_nacional}/{clase}.fgb\" "
            f"\"{path_salida_nacional}/{clase}_recorte.vrt\" 2>> ../logs/union_municipios_error.log"
        )
        os.system(cmd)

        vrt_final_text = f"""<OGRVRTDataSource>
    <OGRVRTUnionLayer name="{clase}">
        <OGRVRTLayer name="{clase}">
            <SrcDataSource relativeToVRT="1">./{clase}.fgb</SrcDataSource>
        </OGRVRTLayer>                  
    </OGRVRTUnionLayer>
</OGRVRTDataSource>
"""
        write_vrt(vrt_final_text, "00", clase, carpeta="path_generados_nacional_municipios")
        print(f"  -> ÉXITO: Capa nacional '{clase}' generada.")
    else:
        print(f"  -> INFO: No se encontraron fuentes de datos para la capa '{clase}'. No se generó capa nacional.")

def main():
    """Función principal que orquesta el proceso de unión."""
    # Se carga la configuración una sola vez en el proceso principal.
    config = get_config()
    
    # Carga la lista de clases a procesar.
    try:
        lib_path = config.get("lib_path", "./")
        elementos_file = config.get("elementos_file", "elementos.xlsx")
        matriz_niveles = pd.read_excel(f"{lib_path}{elementos_file}", engine='openpyxl')
        full_lista_clases = matriz_niveles["elementos"].tolist()
    except FileNotFoundError as e:
        print(f"ERROR CRÍTICO: Archivo de elementos no encontrado: {e.filename}")
        sys.exit(1)
    
    # Crea el directorio de salida si no existe.
    path_salida_nacional = pathlib.Path(config['path_generados_nacional_municipios']) / "00"
    path_salida_nacional.mkdir(parents=True, exist_ok=True)

    # --- LÓGICA DE FILTRADO DE CAPAS PARA LA UNIÓN ---
    update_layers = config.get("capas_actualizar", [])
    if update_layers:
        print(f"INFO: Se ha detectado la clave 'capas_actualizar'. Se procesarán únicamente {len(update_layers)} capas para la unión.")
        layers_to_process = [clase for clase in full_lista_clases if clase in update_layers]
        print(f"-> Capas a procesar: {layers_to_process}")
    else:
        print("INFO: No se ha especificado 'capas_actualizar' en config.json. Se procesarán todas las capas.")
        layers_to_process = full_lista_clases
    # --- FIN DEL FILTRADO ---

    if layers_to_process:
        print(f"\nSe procesarán las siguientes {len(layers_to_process)} capas en paralelo...")
        Parallel(n_jobs=config.get("num_threads", -1), require='sharedmem')(
            # Se pasa la configuración a cada worker.
            delayed(generarClaseNacional)(clase, config) for clase in layers_to_process
        )
        print("\nProceso de unión nacional de municipios terminado.")
    else:
        print("No hay capas configuradas para actualizar en 'capas_actualizar' o no coinciden con las existentes.")

if __name__ == "__main__":
    main()
