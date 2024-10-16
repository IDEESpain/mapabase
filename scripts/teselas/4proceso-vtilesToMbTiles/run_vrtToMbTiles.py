import json
import math
import os
import signal
import shlex
import subprocess
import sys
import datetime
import time
import logging
import pandas
import shutil
import geopandas as gpd
import mercantile as me
import pandas as pd
from shapely.geometry import box


import warnings

from joblib import Parallel, delayed

log = logging.getLogger("mylog")
log.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")

# Log to file
filehandler = logging.FileHandler("log-vtiles.txt", "w")
filehandler.setLevel(logging.INFO)
filehandler.setFormatter(formatter)
log.addHandler(filehandler)


# Log colors
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Núcleos
nucleos = 2

# Clase principal


class ProcessIGO:
    def __init__(self):
        self.config = None
        self.overpass_db = None

        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib' + \
                ':' + '/usr/local/boost/1.60.0/lib64'
            print("Updating... LD_LIBRARY_PATH")

        with open('config_vtiles.json') as data_file:
            self.config_vtiles = json.load(data_file)

        with open('config.json') as data_file:
            self.config = json.load(data_file)

        signal.signal(signal.SIGINT, self.signal_handler)

    @staticmethod
    def signal_handler(sig, frame):
        print(BColors.FAIL + '\nIGO process ABORTED!' + BColors.ENDC)
        sys.exit(0)

    @staticmethod
    def get_time():
        return "[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] "

    @staticmethod
    def sizeof_fmt(num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

    @staticmethod
    def chunks(l, n):
        return [l[i:i + n] for i in range(0, len(l), n)]

    def get_setup(self):
        return self.config['setup']

    # Convertimos con GDAL de VRT a GeoJSONSeq comprimido
    def compress_geojson(self):
        print(BColors.OKGREEN +
              self.get_time() +
              "---> Ejecutando: compress_geojson" +
              BColors.ENDC)

        input_directories = [self.config["input_vrt_IGN"],
                             self.config["input_vrt_comunidades"], self.config["input_vrt_municipios"]]
        output_directories = [self.config["gz_folder_IGN"],
                              self.config["gz_folder_comunidades"], self.config["gz_folder_municipios"]]

        for i in range(len(input_directories)):
            for subdir, dirs, files in os.walk(input_directories[i]):

                # for file_0 in files:
                def VRT2GZ(file_0):

                    # Cambiando geojson por vrt
                    fichero_geojson = input_directories[i] + file_0
                    # fichero_ndjson_zip = output_directory + file.replace(".geojson", ".gz")
                    fichero_ndjson_zip = output_directories[i] + \
                        file_0.replace(".vrt", ".gz")

                    # Modifico 08/06/2021 // cambio por vrt
                    if ".vrt" in file_0 and not "recorte" in file_0:
                        print(BColors.OKGREEN +
                              self.get_time() +
                              "---> Exportando a NDJSON (gzipped) [" + fichero_ndjson_zip + "]..." +
                              BColors.ENDC)
                        command_line = "ogr2ogr -f GeoJSONSeq " + \
                            fichero_ndjson_zip + " " + fichero_geojson
                        print(BColors.OKBLUE + command_line)
                        args = shlex.split(command_line)
                        subprocess.call(args)

                Parallel(n_jobs=nucleos)(delayed(VRT2GZ)(file_0)
                                         for file_0 in files)

    # Tippecanoe

    def tiling_pbf(self):
        print(BColors.OKGREEN +
              self.get_time() +
              "---> Ejecutando: tiling_layers" +
              BColors.ENDC)
        print(len(self.config_vtiles["zoom_levels"]))

        min_level_ign = config["min_zoom_IGN"]
        max_level_ign = config["max_zoom_IGN"]

        min_level_comunidades = config["min_zoom_comunidades"]
        max_level_comunidades = config["max_zoom_comunidades"]

        for z in self.config_vtiles["zoom_levels"]:
            # def teselacion(z):
            if z['process'] == 'no':
                continue
                # return

            if z['level'] >= min_level_ign and z['level'] <= max_level_ign:
                input_layers = self.config["gz_folder_IGN"]
            elif z['level'] >= min_level_comunidades and z['level'] <= max_level_comunidades:
                input_layers = self.config["gz_folder_comunidades"]
            else:
                input_layers = self.config["gz_folder_municipios"]

            output_mbtiles = self.config["destination_mbtiles"]
            temp = self.config["temp_directory"]
            if not os.path.exists(temp):
                os.makedirs(temp)
                print(f'Creada carpeta temp: {temp}')
            # Nivel de zoom
            zoom = str(z["level"])

            # Filter
            filter_attr = json.dumps(z["filter"])

            # Layers to Join
            layers_to_join = []

            # Etiquetas
            if 'layers_with_labels' in z and len(z['layers_with_labels']) > 0:
                layers_with_labels = ''
                layers_to_join.append('layers_with_labels')
                for l in z["layers_with_labels"]:
                    layers_with_labels += " --named-layer='" + \
                        l["name"] + "':" + input_layers + l["file"]

                print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Tiling layers with labels, zoom " + zoom +
                      BColors.ENDC)
                command_line = "tippecanoe -P -o " + \
                               output_mbtiles+"CNIG_" + zoom + "_layers_with_labels.mbtiles " + \
                               layers_with_labels + \
                               " -j '" + filter_attr + "'" + \
                               " -z" + zoom + " -Z" + zoom + \
                               " --no-feature-limit" + \
                               " --force" + \
                               " --no-tile-size-limit" + \
                               " --buffer=127" + \
                               " --convert-stringified-ids-to-numbers" + \
                               " --attribute-type=population:int" + \
                               " --attribute-type=sqkm:int -pC" +\
                               " -t " + temp

                print(BColors.OKBLUE + command_line + BColors.ENDC)
                args = shlex.split(command_line)
                subprocess.call(args)

            # Layer que no tiene que unir (dissolve) EDIFICIOS
            if 'layers_no_coalesce' in z and len(z['layers_no_coalesce']) > 0:
                layers_no_coalesce = ''
                layers_to_join.append('layers_no_coalesce')
                for l in z["layers_no_coalesce"]:
                    layers_no_coalesce += " --named-layer='" + \
                        l["name"] + "':" + input_layers + l["file"]

                print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Tiling layers with no coalesce, zoom " + zoom +
                      BColors.ENDC)
                command_line = "tippecanoe -P -o " + \
                               output_mbtiles+"CNIG_" + zoom + "_layers_no_coalesce.mbtiles " + \
                               layers_no_coalesce + \
                               " -j '" + filter_attr + "'" + \
                               " -z" + zoom + " -Z" + zoom + \
                               " --buffer=44" + \
                               " -t " + temp + \
                               " --reorder" + \
                               " --no-feature-limit" + \
                               " --force" + \
                               " --no-tile-size-limit" + \
                               " --convert-stringified-ids-to-numbers" + \
                               " --attribute-type=population:int" + \
                               " --attribute-type=sqkm:int -pC"

                print(BColors.OKBLUE + command_line + BColors.ENDC)

                # print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)

            # Capas normales
            if 'layers' in z and len(z['layers']) > 0:
                layers = ''
                layers_to_join.append('layers')
                for l in z["layers"]:
                    layers += " --named-layer='" + \
                        l["name"] + "':" + input_layers + l["file"]
                print(layers_to_join)

                # Tippecanoe command
                print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Tiling layers, zoom " + zoom +
                      BColors.ENDC)
                command_line = "tippecanoe -o " + output_mbtiles+"CNIG_" + zoom + "_layers.mbtiles " + \
                    layers + \
                    " -j '" + filter_attr + "'" + \
                    " -z" + zoom + " -Z" + zoom + \
                    " --buffer=44" + \
                    " -t " + temp + \
                    " --coalesce" + \
                    " --reorder" + \
                    " --no-feature-limit" + \
                    " --force" + \
                    " --no-tile-size-limit" + \
                    " --convert-stringified-ids-to-numbers" + \
                    " --attribute-type=population:int" + \
                    " --attribute-type=sqkm:int -pC"
                print(BColors.OKBLUE + command_line + BColors.ENDC)
                print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)

            #  Join de los MBTiles layers, layers_with_labels, layers_no_coalesce
            print(BColors.OKGREEN +
                  self.get_time() +
                  "---> Joining MBTiles, zoom " + zoom +
                  BColors.ENDC)

            if len(layers_to_join) <= 1:
                # Se cambia el nombre al archivo
                os.rename(output_mbtiles+"CNIG_" + zoom + "_layers.mbtiles",
                          output_mbtiles+"CNIG_" + zoom + ".mbtiles")

            else:
                command_line = "tile-join -pk -pC --force -o " + \
                    output_mbtiles+"CNIG_" + zoom + ".mbtiles "
                for layer_type in layers_to_join:
                    command_line += output_mbtiles+"CNIG_" + zoom + "_" + layer_type + ".mbtiles "

                print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)

                # Borramos archivos originales de capa
                for layer_type in layers_to_join:
                    os.remove(output_mbtiles + "CNIG_" + zoom +
                              "_" + layer_type + ".mbtiles")

        # Parallel(n_jobs=nucleos)(delayed(teselacion)(z) for z in self.config["zoom_levels"])

    # mb-util

    def MBtiles2Folder(self):
        output_mbtiles = self.config["destination_mbtiles"]
        temp = self.config["temp_directory"]

        MBtilesFiles = [x for x in os.listdir(
            output_mbtiles) if "mbtiles" in x]

        # for mbtile in MBtilesFiles:
        def MBtilesFiles2folder(mbtile):
            # Tippecanoe command
            print(BColors.OKGREEN +
                  self.get_time() +
                  "---> MBtile file  " + mbtile +
                  BColors.ENDC)
            pathMBtile = output_mbtiles + mbtile + " "
            pathFolder = temp + mbtile.split(".")[0] + " "
            command_line = "mb-util " + \
                " --image_format=pbf " + \
                pathMBtile + \
                pathFolder

            print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

        Parallel(n_jobs=nucleos)(delayed(MBtilesFiles2folder)(mbtile)
                                 for mbtile in MBtilesFiles)

    # Método para copiar carpetas del directorio temporal al final
    def move_temp_files(self):

        temp_path = self.config["temp_directory"]
        father_dest_path = self.config["destination_folder"]
        temp_path_children = os.listdir(temp_path)
        
        # def mover_nivel(i, temp_path, temp_path_children, father_dest_path):
        #     cnig_folder_path = temp_path+temp_path_children[i] + '/'
        #     shutil.copytree(cnig_folder_path, father_dest_path,
        #                     dirs_exist_ok=True)
        # Parallel(n_jobs=12, require='sharedmem')(delayed(mover_nivel)(
        #     i, temp_path, temp_path_children, father_dest_path) for i in range(len(temp_path_children)))


        def mover_archivos_pbf(origen, destino):
            for dirpath, dirnames, filenames in os.walk(origen):
                for file in filenames:
                        # Construir la ruta completa del archivo origen
                        origen_completo = os.path.join(dirpath, file)
                        
                        # Construir la ruta destino manteniendo la estructura
                        # Obtiene la subruta relativa desde el directorio base de origen
                        subruta_relativa = os.path.relpath(dirpath, origen)
                        subruta_relativa = "/".join(subruta_relativa.split("/")[1:])
                        if file.endswith('.json'):
                            print("dirpath: " + dirpath)
                            print("subruta" + subruta_relativa)
                            if "CNIG" in dirpath:
                                subruta_relativa= (dirpath.split("/")[-1].split("_")[1]+ "/"+ subruta_relativa)
                            else:
                                subruta_relativa= (dirpath.split("/")[-1]+ "/"+ subruta_relativa)
                        print("SUBRUTA FINAL: "+ subruta_relativa)
                        # Construir la ruta completa del destino
                        destino_completo = os.path.join(destino, subruta_relativa, file)
                    
                        # Crear los directorios destino si no existen
                        os.makedirs(os.path.dirname(destino_completo), exist_ok=True)
                        
                        # Mover el archivo al destino
                        shutil.move(origen_completo, destino_completo)
                        print(f'Movido: {origen_completo} -> {destino_completo}')
        
        mover_archivos_pbf(temp_path, father_dest_path)

        def limpiar_carpeta(ruta_carpeta):
            """
            Elimina todo el contenido (archivos y subdirectorios) de la carpeta especificada.
            
            Parámetros:
            - ruta_carpeta: Ruta absoluta o relativa de la carpeta a limpiar.
            """
            try:
                for nombre_archivo in os.listdir(ruta_carpeta):
                    ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
                    if os.path.isfile(ruta_completa):
                        os.remove(ruta_completa)
                    elif os.path.isdir(ruta_completa):
                        shutil.rmtree(ruta_completa)
                print(f"Contenido de '{ruta_carpeta}' eliminado correctamente.")
            except Exception as e:
                print(f"Error al limpiar '{ruta_carpeta}': {e}")

        def eliminar_carpetas_vacias(directorio):
            # Recorre el directorio desde las subcarpetas más profundas hacia arriba
            for dirpath, dirnames, filenames in os.walk(directorio, topdown=False):
                # Si una carpeta está vacía, se elimina
                if not dirnames and not filenames:
                    os.rmdir(dirpath)
                    print(f'Eliminada carpeta vacía: {dirpath}')
                try:
                    os.rmdir(dirpath)
                    print(f'Eliminada carpeta: {dirpath}')
                except OSError as e:
                    continue

        eliminar_carpetas_vacias(temp_path)
        limpiar_carpeta(config["destination_mbtiles"])
    # Método para combinar los JSON de metadatos

    def combine_json(self):
        teselas_folder = self.config["destination_folder"]
        dest_folder = self.config["destination_folder"]
        lst_json_files_paths = []

        for subdir in os.listdir(teselas_folder):
            subdir_path = os.path.join(teselas_folder, subdir)
            
            # Verificar si es un directorio
            if os.path.isdir(subdir_path):
                # Buscar archivos .json dentro de este subdirectorio
                for name in os.listdir(subdir_path):
                    if name.endswith('.json'):
                        lst_json_files_paths.append(os.path.join(subdir_path, name))


        # Crea un DataFrame con cada JSON para luego unirlos en un solo DataFrame
        df_list = []
        for json_file_path in lst_json_files_paths:
            with open(json_file_path) as f:
                json_dict = json.load(f)

                df = pandas.DataFrame.from_dict(
                    pandas.json_normalize(json_dict), orient='columns')
                df_list.append(df)

        # DataFrame con todos los JSON
        df_final = pandas.concat(df_list)
    
        # Listas con las columnas de los dataframe

        # set_fields = set([x for x in df_final["fields"]])

        # set_fields = set([x for x in df_final["fields"]])


        lst_center = [(x) for x in df_final['center']]
        lst_bounds = [(x) for x in df_final['bounds'].to_list()]
        lst_json = [
            (str(y), json.loads(x) if x and isinstance(x, str) else None)  # Verificamos que x no esté vacío y sea una cadena
            for x, y in zip(df_final['json'].to_list(), df_final['minzoom'])
            if x and isinstance(x, str)  # Filtramos valores nulos y no strings
        ]

        # Filtrar valores None que podrían haberse producido por errores de decodificación
        lst_json = [(y, j) for y, j in lst_json if j is not None]

        # Imprimir o gestionar errores encontrados
        errores_json = [
            (str(y), x) 
            for x, y in zip(df_final['json'].to_list(), df_final['minzoom'])
            if not x or not isinstance(x, str) or (isinstance(x, str) and not x.strip())  # Detecta entradas inválidas
        ]

        # Si quieres ver cuáles JSON fueron problemáticos
        for error in errores_json:
            print(f"Error procesando JSON con minzoom {error[0]}: {error[1]}")

        center_tuple_lst = []
        bounds_tuple_lst = []

        # # Descompone las celdas de los DataFrame para obtener las coordenadas por separado
        # for i in range(len(lst_center)):
        #     center_tuple_lst.append(tuple(lst_center[i].split(',')))

        # for i in range(len(lst_bounds)):
        #     bounds_tuple_lst.append(tuple(lst_bounds[i].split(',')))

        # Diccionario para el JSON de salida
        dic_output_json = {}

        # self.check_different_elements(df_final['name'].to_list())
        dic_output_json['tilejson'] = "3.0.0"
        dic_output_json['name'] = "Mapa Base XYZ del Sistema Cartográfico Nacional"
        dic_output_json['description'] = "Servicio de visualización (Servicio de Teselas Vectoriales, MVT) del Sistema Cartográfico Nacional. Base de datos multiescala con cobertura completa y continua para España, que combina diferentes fuentes de datos. Teselas desde nivel de zoom 0 hasta nivel de zoom 17"
        dic_output_json['type'] = "overlay"
        dic_output_json['scheme'] = "xyz"
        dic_output_json['format'] = "pbf"
        dic_output_json['version'] = "1.0.0"
        dic_output_json['tiles'] = ["https://vt-mapabase.idee.es/1.0.0/mapabase/{z}/{x}/{y}.pbf"]
        dic_output_json['attribution'] = "<a href='https://www.scne.es//'>CC BY 4.0 scne</a>"
        dic_output_json['bounds'] = [-180, 90, 180, 90]
        dic_output_json['center'] = [-11.5, 35.789, 5]
        dic_output_json['minzoom'] = 0
        dic_output_json['maxzoom'] = 17
        dic_output_json['MetadataUrl'] = "https://ideespain.github.io/mapabase/"
        


        capas_totales = {}

        tilestats = {}

        for zoom, element in lst_json:
            for vector_layer in element["vector_layers"]:
                if vector_layer["id"] not in capas_totales.keys():
                    # añadir los atributos de la capa(solo 1 vez ya que son siempre los mismos?)
                    elemento = {"id": vector_layer['id'], "minzoom": vector_layer['minzoom'], "maxzoom": vector_layer['maxzoom'],
                                "description": vector_layer['description'], "atributos": vector_layer['fields']}
                    capas_totales[vector_layer["id"]] = elemento
                else:
                    if vector_layer["minzoom"] < capas_totales[vector_layer["id"]]["minzoom"]:
                        capas_totales[vector_layer["id"]
                                      ]["minzoom"] = vector_layer["minzoom"]
                    if vector_layer["maxzoom"] > capas_totales[vector_layer["id"]]["maxzoom"]:
                        capas_totales[vector_layer["id"]
                                      ]["maxzoom"] = vector_layer["maxzoom"]
                lista_atributos_zoom = vector_layer["fields"]
                lista_atributos_completa = capas_totales[vector_layer["id"]]["atributos"]
                capas_totales[vector_layer["id"]]["atributos"] = {
                    **lista_atributos_completa, **lista_atributos_zoom}

            tilestats[zoom] = element["tilestats"]

        # print(capas_totales)

        list_capas_totales = []

        for key, value in capas_totales.items():
            list_capas_totales.append(value)

        dic_output_json['vector_layers'] = list_capas_totales

        dic_output_json['tilestats'] = dict(sorted(tilestats.items()))

        with open(dest_folder+'metadata.json', 'w',encoding='utf-8') as f:
            f.write(json.dumps(dic_output_json, ensure_ascii=False, indent=4))

    @staticmethod
    def compute_max_min_avg(list, op, coord):

        df = pandas.DataFrame(list)

        try:
            data = [int(n) for n in df[coord].to_list()]
        except:
            data = [float(n) for n in df[coord].to_list()]

        if op == 'max':
            res = max(data)
        elif op == 'min':
            res = min(data)
        elif op == 'avg':
            res = sum(data)/len(data)

        return res

    @staticmethod
    def check_different_elements(lst):

        if len(set(lst)) == 1:
            return lst[0]
        else:
            return list(set(lst))


'''
PROCESO DEL FICHERO IGO
'''

# TODO INCLUIR TIEMPOS EN EL PROCESO DE ACTUALIZACIÓN

f = open("./config_vtiles.json")

config_vtiles = json.load(f)

f_config = open("./config.json")

config = json.load(f_config)

if(config["update"] != ""):
    print(f"Actualizando teselas de territorios por ", config["update"])
    process = ProcessIGO()
    setup = process.get_setup()
    print(process.get_time())
    # Exporting Layers to GeoJSON
    if setup['compress_geojson'] == 'yes':
        print('--> Compress layers GeoJSON to NDJson.GZ')
        process.compress_geojson()
    lista_comunidades = config["lista_comunidades"]
    lista_municipios = config["lista_municipios"]

    territorio_cod = ""

    ruta_carpeta = ""

    is_comunidades = False
    is_bbox = False
    # python3 run_vrtToMbTiles.py update comunidades
    if(config["update"] == "comunidades"):
        is_comunidades = True

    # python3 run_vrtToMbTiles.py update bbox -10 40 -20 60
    elif (config["update"] == "bbox"):
        print(f"Actualizando teselas de territorios por ", config["update"])
        is_bbox = True
        left, bottom, right, top = config["bbox"][0], config["bbox"][1], config["bbox"][2], config["bbox"][3]
    
    elif (config["update"] == "nacional"):
        print(f"Actualizando teselas de territorios por ", config["update"])
        is_bbox = True
        left, bottom, right, top = -19.215480397527838, 26.62547835167641, 6.341170645348383, 44.792032154864046

    elif (config["update"] == "peninsula"):
        print(f"Actualizando teselas de territorios por ", config["update"])
        is_bbox = True
        left, bottom, right, top = -9.94,35.01,4.64,44.1

    if not is_bbox:
        if lista_comunidades and is_comunidades:
            is_comunidades = True
            lista_territorios = lista_comunidades
        else:
            # solo municipios
            lista_territorios = lista_municipios
        print(lista_territorios)

    def get_territorio(is_comunidades, var_dict, codigo):
        if is_comunidades:
            file = f"{var_dict['aux_comunidades_file']}"
            comunidades_file = gpd.read_file(file)
            territorio = comunidades_file[comunidades_file["codigo"].str.slice(
                2, 4) == str(codigo).zfill(2)]

        else:

            file = f"{var_dict['aux_municipios_file']}"
            municipios_file = gpd.read_file(file)
            territorio = municipios_file[municipios_file["codigo"].str.slice(
                -5) == str(codigo).zfill(5)]

        return territorio.reset_index(drop=True)

    def get_bbox(territorio):
        left, bottom, right, top = territorio.bounds.loc[0, :].to_list()

        print(left, bottom, right, top)

        return left, bottom, right, top

    def get_tiles(left, bottom, right, top, var_dict):
        # me.Bbox(left,bottom,right,top)
        # if is_comunidades:
        #     zooms = [x for x in range(var_dict["min_zoom_comunidades"],var_dict["max_zoom_comunidades"] + 1)]
        # else:
        #     zooms = [x for x in range(var_dict["min_zoom_municipios"],var_dict["max_zoom_municipios"] + 1)]
        zooms = []
        for z in config_vtiles["zoom_levels"]:
            if z['process'] == 'yes':
                zooms.append(z["level"])
        print("Zooms: ")
        print(zooms)
        tiles = me.tiles(left, bottom, right, top, zooms)
        tiles_matrix = [(t.x, t.y, t.z) for t in tiles]

        # las teselas contiguas se incluyen o no?

        neigbour_tiles = []

        for t in tiles:
            neigbour_tiles.append(me.neighbors(t))

        neigbour_tiles_matrix = [(t.x, t.y, t.z)
                                 for l in neigbour_tiles for t in l]

        # total_tiles_matrix=tiles_matrix+neigbour_tiles_matrix

        total_tiles_matrix = tiles_matrix

        total_tiles_matrix_set = set(total_tiles_matrix)
        
        total_tiles_matrix_set_sorted_by_zoom = sorted(
            total_tiles_matrix_set, key=lambda tup: tup[2])

        total_tiles_dict = {i: {"x": t[0], "y": t[1], "z": t[2]} for i, t in enumerate(
            total_tiles_matrix_set_sorted_by_zoom)}

        tiles_df = pd.DataFrame.from_dict(total_tiles_dict, orient="index")

        return tiles_df

    def parse_json_v_tiles():
        layers = ''

        layer_dict_by_zoom = {}

        # print(json_file["zoom_levels"])

        for l in config_vtiles["zoom_levels"]:
            # print(l)
            layers = [layer["file"] for layer in l["layers"]]
            layers_no_coalesce = [layer["file"]
                                  for layer in l["layers_no_coalesce"]]
            layers_with_labels = [layer["file"]
                                  for layer in l["layers_with_labels"]]
            filters = l["filter"]
            # print(layers)
            layer_dict_by_zoom[l["level"]] = {
                "layers": layers, "layers_no_coalesce": layers_no_coalesce, "layers_with_labels": layers_with_labels, "filter": filters}

        return layer_dict_by_zoom





    def latlon_to_tile(lat, lon, zoom):
        """
        Convierte coordenadas geográficas (latitud y longitud) a coordenadas de tesela (tile) en un nivel de zoom específico.
        """
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x_tile = int((lon + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (x_tile, y_tile)

    def tile_to_latlon(x_tile, y_tile, zoom):
        """
        Convierte coordenadas de tesela (tile) a coordenadas geográficas (latitud y longitud) en un nivel de zoom específico.
        """
        n = 2.0 ** zoom
        lon = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat = math.degrees(lat_rad)
        return (lat, lon)

    def expand_bbox_to_include_tiles(bbox, zoom):
        """
        Expande el bbox para incluir completamente las teselas que intersectan con él en un nivel de zoom específico.
        """
        # Convertir el bbox a coordenadas de tesela
        bminlon, bminlat, bmaxlon, bmaxlat = bbox
        min_tile = latlon_to_tile(bminlat, bminlon, zoom)
        max_tile = latlon_to_tile(bmaxlat, bmaxlon, zoom)

        # Calcular el nuevo bbox que incluye completamente las teselas
        min_lat, min_lon = tile_to_latlon(min_tile[0], min_tile[1] + 1, zoom)
        max_lat, max_lon = tile_to_latlon(max_tile[0] + 1, max_tile[1], zoom)

        # Asegurarse de que las coordenadas estén dentro de los límites válidos
        min_lat = max(min_lat, -85.05112878)  # Límite de latitud mínima en Web Mercator
        max_lat = min(max_lat, 85.05112878)   # Límite de latitud máxima en Web Mercator
        min_lon = max(min_lon, -180.0)        # Límite de longitud mínima
        max_lon = min(max_lon, 180.0)         # Límite de longitud máxima
        return min_lon,min_lat,max_lon,max_lat


        
    def expand_bbox_to_cover_tiles(bbox, zoom_level):
        # Función para calcular el tamaño de un tile en grados de latitud y longitud
        def tile_size(zoom):
            return 360.0 / (2 ** zoom)

        # Función para calcular las coordenadas de un tile a partir de su índice x, y
        def tile_to_coords(x, y, zoom):
            size = tile_size(zoom)
            min_lon = -180.0 + x * size
            max_lon = min_lon + size
            max_lat = 90.0 - y * size
            min_lat = max_lat - size
            return (min_lon, min_lat, max_lon, max_lat)

        # Función para obtener el índice x, y del tile que contiene una coordenada dada
        def coords_to_tile(lon, lat, zoom):
            size = tile_size(zoom)
            x = math.floor((lon + 180.0) / size)
            y = math.floor((90.0 - lat) / size)
            return (x, y)

        # Expandimos el bbox para asegurarnos de que contenga todos los tiles
        min_lon, min_lat, max_lon, max_lat = bbox
        start_tile_x, start_tile_y = coords_to_tile(min_lon, max_lat, zoom_level)
        end_tile_x, end_tile_y = coords_to_tile(max_lon, min_lat, zoom_level)

        # Obtenemos las coordenadas de los extremos de los tiles
        expanded_min_lon, expanded_min_lat, _, _ = tile_to_coords(start_tile_x, start_tile_y, zoom_level)
        _, _, expanded_max_lon, expanded_max_lat = tile_to_coords(end_tile_x, end_tile_y, zoom_level)

        expanded_bbox = (expanded_min_lon, expanded_min_lat, expanded_max_lon, expanded_max_lat)
        return expanded_bbox
    
    def apply_buffer(bbox, buffer):
        geom = box(*bbox)

        buffered_geom = geom.buffer(buffer, cap_style=3)

        return buffered_geom.bounds
    

    def generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom, bbox):

        # preconfigurar

        destination_mbtiles = config["destination_mbtiles"]
        tmp = config["temp_directory"]

        min_level_ign = config["min_zoom_IGN"]
        max_level_ign = config["max_zoom_IGN"]

        min_level_comunidades = config["min_zoom_comunidades"]
        max_level_comunidades = config["max_zoom_comunidades"]
        

        if not os.path.exists(tmp):
            os.makedirs(tmp)
            print(f'Creada carpeta temp: {tmp}')
        for z in config_vtiles["zoom_levels"]:

            # def teselacion(z):
            if z['process'] == 'no':
                continue
                # return
            minlon, minlat, maxlon, maxlat = apply_buffer(expand_bbox_to_include_tiles(bbox, z['level']),-0.75)

            if z['level'] >= min_level_ign and z['level'] <= max_level_ign:
                origen = config["gz_folder_IGN"]
            elif z['level'] >= min_level_comunidades and z['level'] <= max_level_comunidades:
                origen = config["gz_folder_comunidades"]
            else:
                origen = config["gz_folder_municipios"]

            zoom = z['level']
            layers = ["--named-layer="+layer[:-3]+":"+origen +
                      layer for layer in layer_dict_by_zoom[zoom]["layers"]]
            layers_no_coalesce = ["--named-layer="+layer[:-3]+":"+origen +
                                  layer for layer in layer_dict_by_zoom[zoom]["layers_no_coalesce"]]
            layers_with_labels = ["--named-layer="+layer[:-3]+":"+origen +
                                  layer for layer in layer_dict_by_zoom[zoom]["layers_with_labels"]]
            filter_attr = json.dumps(layer_dict_by_zoom[zoom]["filter"])
            
            layers = " ".join(layers)

            command_line = f"tippecanoe --force -o " + destination_mbtiles+"CNIG_" + str(zoom) + "_"+str(int(round(minlon, 3) * 1000))+"_"+str(int(round(minlat, 3) * 1000))+"_layers.mbtiles " + \
                layers + \
                " -z" + str(zoom) + " -Z" + str(zoom) + \
                " -j '" + str(filter_attr) + "'" + \
                " --buffer=1" + \
                " -t " + tmp + "" + \
                " --coalesce" + \
                " --reorder" + \
                " --no-feature-limit" + \
                " --no-tile-size-limit" + \
                " --convert-stringified-ids-to-numbers" + \
                " --attribute-type=population:int" + \
                " --attribute-type=sqkm:int -pC" +\
                " --clip-bounding-box="+str(minlon)+","+str(minlat)+","+ str(maxlon)+","+ str(maxlat)

            print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

            if len(layers_no_coalesce) > 0:
                layers_nc = " ".join(layers_no_coalesce)
                command_line = f"tippecanoe --force -o " + str(destination_mbtiles) +"CNIG_" + str(zoom) + "_"+str(int(round(minlon, 3) * 1000))+"_"+str(int(round(minlat, 3) * 1000))+"_layers_no_coalesce.mbtiles " + \
                    layers_nc + \
                    " -z" + str(zoom) + " -Z" + str(zoom) + \
                    " -j '" + str(filter_attr) + "'" + \
                    " --buffer=44" + \
                    " -t " + tmp + "" + \
                    " --reorder" + \
                    " --no-feature-limit" + \
                    " --no-tile-size-limit" + \
                    " --drop-densest-as-needed" + \
                    " --convert-stringified-ids-to-numbers" + \
                    " --attribute-type=population:int" + \
                    " --attribute-type=sqkm:int -pC" +\
                    " --clip-bounding-box="+str(minlon)+","+str(minlat)+","+ str(maxlon)+","+ str(maxlat)

                args = shlex.split(command_line)
                subprocess.call(args)

            if len(layers_with_labels) > 0:
                layers_wl = " ".join(layers_with_labels)
                command_line = f"tippecanoe --force  -o " + destination_mbtiles+"CNIG_" + str(zoom) + "_"+str(int(round(minlon, 3) * 1000))+"_"+str(int(round(minlat, 3) * 1000))+"_layers_with_labels.mbtiles " + \
                    layers_wl + \
                    " -z" + str(zoom) + " -Z" + str(zoom) + \
                    " -j '" + str(filter_attr) + "'" + \
                    " --buffer=127" + \
                    " -t " + tmp + "" + \
                    " --no-feature-limit" + \
                    " --no-tile-size-limit" + \
                    " --convert-stringified-ids-to-numbers" + \
                    " --attribute-type=population:int" + \
                    " --attribute-type=sqkm:int -pC" +\
                    " --clip-bounding-box="+str(minlon)+","+str(minlat)+","+ str(maxlon)+","+ str(maxlat)

                args = shlex.split(command_line)
                subprocess.call(args)

    def grouped_mbtiles_by_zoom(mbtiles_path):
        try:

            mbtiles_files_dict = {}
            for i, f in enumerate(os.listdir(mbtiles_path)):
                zoom = f.split("_")[1].replace(".mbtiles", "")
                if config_vtiles["zoom_levels"][int(zoom)]["process"] == "no":
                    continue
              
                try:
                    layer_type = "_".join(f.split("_")[4:]).replace(".mbtiles","")
                    mbtiles_files_dict[i] = {"CNIG": f.split("_")[0],
                                            "zoom": f.split("_")[1],
                                            "x": f.split("_")[2],
                                            "y": f.split("_")[3],
                                            "layer_type": layer_type,
                                            "file_type": ".mbtiles"} 
                                        
                except:
                    continue

            df_mbtiles_files = pd.DataFrame.from_dict(
                mbtiles_files_dict, orient="index").sort_values(["zoom", "x", "y"])

            grouped_by_zoom = df_mbtiles_files.groupby("zoom")
        except Exception as e:
            print(e)
            return ""
        return grouped_by_zoom

    def tile_join():
        print("Joining tiles")
        path_mbtiles = config["destination_mbtiles"]
        grouped = grouped_mbtiles_by_zoom(path_mbtiles)
        files_to_delete = []

        files_to_pbf = []
        for zoom, group in grouped:
            print("Joinin z "+ zoom)
            command_line = "tile-join -pk -pC --force -o " + \
                path_mbtiles+"CNIG_" + zoom + ".mbtiles "

            files_to_pbf.append(path_mbtiles+"CNIG_" + zoom + ".mbtiles")

            for file in group.itertuples():
                file_name = f"{path_mbtiles}CNIG_{zoom}_{file.x}_{file.y}_{file.layer_type}.mbtiles"
                command_line += f"{file_name} "
                files_to_delete.append(file_name)

            # print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

        return files_to_pbf

            # Borramos archivos originales de capa
            # for layer_type in layers_to_join:
            #     os.remove(output_mbtiles + "CNIG_" + zoom + "_" + layer_type + ".mbtiles")
            # print(group)

    def mb_util_tiles(files_to_pbf):

        dest_folder = config["temp_directory"]
        
        for file in files_to_pbf:
        
            print(dest_folder+file.split("/")[-1].replace("CNIG_","").split(".")[0]+"/")
            command_line = "mb-util " + \
                " --image_format=pbf " + \
                file + " " +\
                dest_folder+file.split("/")[-1].replace("CNIG_","").split(".")[0]+"/"

            print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

        # for file in files_to_delete:
        #     #print(file)
        #     os.remove(file)

    if is_bbox:

        tiles_df = get_tiles(left, bottom, right, top, config)

        layer_dict_by_zoom = parse_json_v_tiles()

        bbox = left, bottom, right, top
        if setup['tiling_layers'] == 'yes':
            log.info('--> Tiling layers with Tippecanoe')
            generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom, bbox)
            files_to_pbf = tile_join()

        # MBtiles --> PBF folder
        if setup['to_folder'] == 'yes':
            log.info('--> MBtiles --> PBF folder')
            mb_util_tiles(files_to_pbf)
        if setup['join_json'] == 'yes':
                log.info('Joining all json in 1')
                process.combine_json()
        if setup['move_to_final_folder'] == 'yes':
            print('Moving pbfs folder')
            process.move_temp_files()

        print("Proceso de actualización de teselas por bbox terminado")

    else:

        for codigo in lista_territorios:

            territorio = get_territorio(is_comunidades, config, codigo)

            left, bottom, right, top = get_bbox(territorio)
            print("BBOX:")
            print(left, bottom, right, top)
            tiles_df = get_tiles(left, bottom, right, top, config)

            layer_dict_by_zoom = parse_json_v_tiles()
            
            if setup['tiling_layers'] == 'yes':
                log.info('--> Tiling layers with Tippecanoe')
                generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom, get_bbox(territorio))
                files_to_pbf = tile_join()

            # MBtiles --> PBF folder
            if setup['to_folder'] == 'yes':
                log.info('--> MBtiles --> PBF folder')
                mb_util_tiles(files_to_pbf)
            if setup['join_json'] == 'yes':
                log.info('Joining all json in 1')
                process.combine_json()
            if setup['move_to_final_folder'] == 'yes':
                print('Moving pbfs folder')
                process.move_temp_files()

            print("Proceso de actualización de teselas por territorios terminado")


else:

    print(f"Generando teselas de territorios al completo ")

    tiempo_inicio = time.time()

    process = ProcessIGO()
    setup = process.get_setup()
    log.info(process.get_time())

    # Exporting Layers to GeoJSON
    if setup['compress_geojson'] == 'yes':
        log.info('--> Compress layers GeoJSON to NDJson.GZ')
        process.compress_geojson()

    # Tiling with Tippecanoe into PBF
    if setup['tiling_layers'] == 'yes':
        log.info('--> Tiling layers with Tippecanoe')
        process.tiling_pbf()

    # MBtiles --> PBF folder
    if setup['to_folder'] == 'yes':
        log.info('--> MBtiles --> PBF folder')
        process.MBtiles2Folder()

    # m jsons -> 1 json
    if setup['join_json'] == 'yes':
        log.info('Joining all json in 1')
        process.combine_json()

    # MBtiles --> PBF folder
    if setup['move_to_final_folder'] == 'yes':
        log.info('Moving pbfs folder')
        process.move_temp_files()

    print(BColors.OKGREEN +
          "[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] " +
          "Fecha inicio: " +
          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tiempo_inicio)) +
          BColors.ENDC)

    print(BColors.OKGREEN +
          "[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] " +
          "Tiempo total: " +
          time.strftime('%d:%H:%M:%S', time.localtime(time.time() - tiempo_inicio)) +
          BColors.ENDC)

    print(BColors.OKGREEN +
          "[" + datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + "] " +
          "END" +
          BColors.ENDC)
