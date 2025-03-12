import os
import json
import geopandas as gpd
from shapely.validation import make_valid
import gc

# Cargar configuración desde config.json
with open("./config.json") as f:
    config = json.load(f)

# Ruta de la carpeta con los archivos geoespaciales (definida en config.json)
input_folder = config["geometrias_corregir"]

# Archivo de salida para el listado de archivos corregidos (definido en config.json)
output_json = config["json_corregir_geometrias"]

def correct_invalid_geometries(file_path, corrected_files):
    """
    Corrige las geometrías inválidas en un archivo FGB o GeoJSON.
    Retorna True si se realizaron correcciones, False si no se necesitó.
    """
    try:
        gdf = gpd.read_file(file_path)
        invalid_count = (~gdf.is_valid).sum()

        if invalid_count > 0:
            print(f"🔄 {file_path} - Corrigiendo {invalid_count} geometrías inválidas...")
            gdf["geometry"] = gdf["geometry"].apply(make_valid)
            gdf.to_file(file_path, driver="FlatGeobuf")
            corrected_files.append(file_path)
            result = True
        else:
            print(f"✅ {file_path} - No requiere correcciones.")
            result = False

        # Liberar memoria
        del gdf
        gc.collect()

        return result

    except Exception as e:
        print(f"⚠️ Error al procesar {file_path}: {e}")
        return False

if __name__ == "__main__":
    corrected_files = []

    # Obtener la lista de archivos a procesar
    file_list = [
        os.path.join(root, file)
        for root, _, files in os.walk(input_folder)
        for file in files if file.endswith(".geojson") or file.endswith(".fgb")
    ]

    print(f"🔎 Encontrados {len(file_list)} archivos a procesar...")

    # Procesar archivo a archivo
    for file_path in file_list:
        correct_invalid_geometries(file_path, corrected_files)

    # Guardar el listado en un JSON solo con archivos corregidos
    with open(output_json, "w") as f:
        json.dump({"corrected_files": corrected_files}, f, indent=4)

    print(f"\n✅ Proceso completado. Se corrigieron geometrías en {len(corrected_files)} archivos.")
    print(f"📂 Resultados guardados en: {output_json}")
