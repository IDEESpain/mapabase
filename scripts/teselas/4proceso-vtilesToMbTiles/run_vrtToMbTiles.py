import json
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
                               " -z " + zoom + " -Z " + zoom + \
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
                               " -z " + zoom + " -Z " + zoom + \
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
                command_line = "tippecanoe -P -o " + output_mbtiles+"CNIG_" + zoom + "_layers.mbtiles " + \
                    layers + \
                    " -j '" + filter_attr + "'" + \
                    " -z " + zoom + " -Z " + zoom + \
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

        def mover_nivel(i, temp_path, temp_path_children, father_dest_path):
            cnig_folder_path = temp_path+temp_path_children[i] + '/'
            shutil.copytree(cnig_folder_path, father_dest_path,
                            dirs_exist_ok=True)

        # TODO PARAMETRIZAR Y TRATAR DE HACERLO POR LAS X
        Parallel(n_jobs=6, require='sharedmem')(delayed(mover_nivel)(
            i, temp_path, temp_path_children, father_dest_path) for i in range(len(temp_path_children)))

    # Método para combinar los JSON de metadatos

    def combine_json(self):
        teselas_folder = self.config["temp_directory"]
        dest_folder = self.config["destination_folder"]
        lst_json_files_paths = []

        for root, dirs, files in os.walk(teselas_folder, topdown=False):
            for name in files:
                if name[-5:] == '.json':
                    lst_json_files_paths.append(os.path.join(root, name))

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

        print(df_final)

        # Listas con las columnas de los dataframe

        # set_fields = set([x for x in df_final["fields"]])

        # set_fields = set([x for x in df_final["fields"]])

        lst_minzoom = [int(x) for x in df_final['minzoom'].to_list()]
        lst_maxzoom = [int(x) for x in df_final['maxzoom'].to_list()]

        lst_center = [(x) for x in df_final['center']]
        lst_bounds = [(x) for x in df_final['bounds'].to_list()]
        lst_json = [(y, json.loads(x)) for x, y in zip(
            df_final['json'].to_list(), df_final['minzoom'])]

        center_tuple_lst = []
        bounds_tuple_lst = []

        # Descompone las celdas de los DataFrame para obtener las coordenadas por separado
        for i in range(len(lst_center)):
            center_tuple_lst.append(tuple(lst_center[i].split(',')))

        for i in range(len(lst_bounds)):
            bounds_tuple_lst.append(tuple(lst_bounds[i].split(',')))

        # Diccionario para el JSON de salida
        dic_output_json = {}

        # self.check_different_elements(df_final['name'].to_list())
        dic_output_json['id'] = "mapabase_cnig"
        dic_output_json['name'] = "mapabase_cnig"
        dic_output_json['basename'] = "mapabase_cnig"
        dic_output_json['attribution'] = "url cnig"
        # self.check_different_elements(df_final['description'].to_list())
        dic_output_json['description'] = "Mapa Base de Centro Nacional de Información Geográfica"
        # self.check_different_elements(df_final['type'].to_list())
        dic_output_json['version'] = 2
        dic_output_json['minzoom'] = min(lst_minzoom)
        dic_output_json['maxzoom'] = max(lst_maxzoom)
        dic_output_json['center'] = """{0},{1},{2}""".format(self.compute_max_min_avg(center_tuple_lst, 'avg', 0), self.compute_max_min_avg(
            center_tuple_lst, 'avg', 1), self.compute_max_min_avg(center_tuple_lst, 'min', 2))
        dic_output_json['bounds'] = """{0},{1},{2},{3}""".format(self.compute_max_min_avg(bounds_tuple_lst, 'avg', 0), self.compute_max_min_avg(
            bounds_tuple_lst, 'avg', 1), self.compute_max_min_avg(bounds_tuple_lst, 'avg', 2), self.compute_max_min_avg(bounds_tuple_lst, 'avg', 3))
        # self.check_different_elements(df_final['type'].to_list())
        dic_output_json['type'] = "overlay"
        # self.check_different_elements(df_final['format'].to_list())
        dic_output_json['format'] = "pbf"
        dic_output_json['tiles'] = [
            "https://www.ign.es/web/resources/mapa-base-xyz/vt/{z}/{x}/{y}.pbf"]
        dic_output_json['generator'] = self.check_different_elements(
            df_final['generator'].to_list())

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

        with open(dest_folder+'metadata.json', 'w') as f:
            f.write(json.dumps(dic_output_json))

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

if(config["update"] == "municipios" or config["update"] == "comunidades" or config["update"] == "bbox"):
    print(f"Actualizando teselas de territorios por ", config["update"])
    
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

    def get_tiles(left, bottom, right, top):
        # me.Bbox(left,bottom,right,top)
        zooms = [x for x in range(17)]
    
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

    def generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom):

        # preconfigurar

        destination_mbtiles = config["destination_mbtiles"]
        tmp = config["temp_directory"]

        min_level_ign = config["min_zoom_IGN"]
        max_level_ign = config["max_zoom_IGN"]

        min_level_comunidades = config["min_zoom_comunidades"]
        max_level_comunidades = config["max_zoom_comunidades"]

        # print(layer_dict_by_zoom)

        for t in tiles_df.itertuples():

            if t.z >= min_level_ign and t.z <= max_level_ign:
                origen = config["gz_folder_IGN"]
            elif t.z >= min_level_comunidades and t.z <= max_level_comunidades:
                origen = config["gz_folder_comunidades"]
            else:
                origen = config["gz_folder_municipios"]

            layers = ["--named-layer="+layer[:-3]+":"+origen +
                      layer for layer in layer_dict_by_zoom[t.z]["layers"]]
            layers_no_coalesce = ["--named-layer="+layer[:-3]+":"+origen +
                                  layer for layer in layer_dict_by_zoom[t.z]["layers_no_coalesce"]]
            layers_with_labels = ["--named-layer="+layer[:-3]+":"+origen +
                                  layer for layer in layer_dict_by_zoom[t.z]["layers_with_labels"]]
            filter_attr = json.dumps(layer_dict_by_zoom[t.z]["filter"])
            
            layers = " ".join(layers)

            command_line = f"tippecanoe --force -P -o " + destination_mbtiles+"CNIG_" + str(t.z) + "_"+str(t.x)+"_"+str(t.y)+"_layers.mbtiles " + \
                layers + \
                " -z " + str(t.z) + " -Z " + str(t.z) + \
                " -j '" + str(filter_attr) + "'" + \
                " --buffer=44" + \
                " -t " + tmp + "" + \
                " --coalesce" + \
                " --reorder" + \
                " --no-feature-limit" + \
                " --no-tile-size-limit" + \
                " --convert-stringified-ids-to-numbers" + \
                " --attribute-type=population:int" + \
                " --attribute-type=sqkm:int -pC" +\
                " -R "+str(t.z)+"/"+str(t.x)+"/"+str(t.y)

            # print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

            if len(layers_no_coalesce) > 0:
                command_line = f"tippecanoe --force -P -o " + str(destination_mbtiles) +"CNIG_" + str(t.z) + "_"+str(t.x)+"_"+str(t.y)+"_layers_no_coalesce.mbtiles " + \
                    str(layers_no_coalesce) + \
                    " -z " + str(t.z) + " -Z " + str(t.z) + \
                    " -j '" + str(filter_attr) + "'" + \
                    " --buffer=44" + \
                    " -t " + tmp + "" + \
                    " --reorder" + \
                    " --no-feature-limit" + \
                    " --no-tile-size-limit" + \
                    " --convert-stringified-ids-to-numbers" + \
                    " --attribute-type=population:int" + \
                    " --attribute-type=sqkm:int -pC" +\
                    " -R "+str(t.z)+"/"+str(t.x)+"/"+str(t.y)

                args = shlex.split(command_line)
                subprocess.call(args)

            if len(layers_with_labels) > 0:

                command_line = f"tippecanoe --force -P -o " + destination_mbtiles+"CNIG_" + str(t.z) + "_"+str(t.x)+"_"+str(t.y)+"_layers_with_labels.mbtiles " + \
                    layers_with_labels + \
                    " -z " + str(t.z) + " -Z " + str(t.z) + \
                    " -j '" + str(filter_attr) + "'" + \
                    " --buffer=127" + \
                    " -t " + tmp + "" + \
                    " --no-feature-limit" + \
                    " --no-tile-size-limit" + \
                    " --convert-stringified-ids-to-numbers" + \
                    " --attribute-type=population:int" + \
                    " --attribute-type=sqkm:int -pC" +\
                    " -R "+str(t.z)+"/"+str(t.x)+"/"+str(t.y)

                args = shlex.split(command_line)
                subprocess.call(args)

    def grouped_mbtiles_by_zoom(mbtiles_path):
        try:
            mbtiles_files_dict = {i: {"CNIG": f.split("_")[0], "zoom": f.split("_")[1], "x": f.split("_")[2], "y": f.split("_")[3], "layer_type": f.split(
                "_")[4].split(".")[0], "file_type": "."+f.split("_")[4].split(".")[1]} for i, f in enumerate(os.listdir(mbtiles_path)) if f[-8:] == ".mbtiles"}
            print(mbtiles_files_dict)
            df_mbtiles_files = pd.DataFrame.from_dict(
                mbtiles_files_dict, orient="index").sort_values(["zoom", "x", "y"])

            grouped_by_zoom = df_mbtiles_files.groupby("zoom")
        except:
            return ""
        return grouped_by_zoom

    def tile_join():
        path_mbtiles = config["destination_mbtiles"]
        grouped = grouped_mbtiles_by_zoom(path_mbtiles)
        files_to_delete = []

        files_to_pbf = []

        for zoom, group in grouped:
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

        dest_folder = config["destination_folder"]

        for file in files_to_pbf:
            command_line = "mb-util " + \
                " --image_format=pbf " + \
                file + " " +\
                dest_folder+file.split("_")[1].split(".")[0]+"/"

            # print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)

        # for file in files_to_delete:
        #     #print(file)
        #     os.remove(file)

    if is_bbox:

        tiles_df = get_tiles(left, bottom, right, top)

        layer_dict_by_zoom = parse_json_v_tiles()

        files_to_pbf = generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom)

        files_to_pbf = tile_join()

    else:

        for codigo in lista_territorios:

            territorio = get_territorio(is_comunidades, config, codigo)

            left, bottom, right, top = get_bbox(territorio)

            tiles_df = get_tiles(left, bottom, right, top)

            layer_dict_by_zoom = parse_json_v_tiles()

            files_to_pbf = generate_tiles_tippecanoe(tiles_df, layer_dict_by_zoom)

            files_to_pbf = tile_join()

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

    # MBtiles --> PBF folder
    if setup['move_to_final_folder'] == 'yes':
        log.info('Moving pbfs folder')
        process.move_temp_files()

    # m jsons -> 1 json
    if setup['join_json'] == 'yes':
        log.info('Joining all json in 1')
        process.combine_json()

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
