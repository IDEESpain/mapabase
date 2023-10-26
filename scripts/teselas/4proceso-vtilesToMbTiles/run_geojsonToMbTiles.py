import json
import os
import signal
import shlex
import subprocess
import sys
import datetime
import time
import logging

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

#Núcleos
nucleos = 2

# Clase principal
class ProcessIGO:
    def __init__(self):
        self.config = None
        self.overpass_db = None

        if 'LD_LIBRARY_PATH' not in os.environ:
            os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib' + ':' + '/usr/local/boost/1.60.0/lib64'
            print("Updating... LD_LIBRARY_PATH")

        with open('config_vtiles.json') as data_file:
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

        input_directory = self.config["origin_layers_geojson"]
        output_directory = self.config["destination_layers_geojson"]

        for subdir, dirs, files in os.walk(input_directory):

            # for file_0 in files:
            def VRT2GZ(file_0):
                # print(BColors.OKGREEN +
                #       self.get_time() +
                #       "---> Exportando a GeoJSONSeq  [" + file_0 + "]..." +
                #       BColors.ENDC)
                # Cambiando geojson por vrt
                fichero_geojson = input_directory + file_0
                # fichero_ndjson_zip = output_directory + file.replace(".geojson", ".gz")
                fichero_ndjson_zip = output_directory + file_0.replace(".vrt", ".gz")

                # Export to GeoJSON - NDJSON
                # if os.path.isfile(fichero_ndjson_zip):
                #     # A^2: si es .log o .gz, que no haga nada
                #     if "log" in file or "geojson" in file or "vrt" in file:
                #         pass
                #     else:
                #         os.remove(fichero_ndjson_zip)
                # print(BColors.OKGREEN +
                #       self.get_time() +
                #       "---> Exportando a NDJSON (gzipped) [" + fichero_ndjson_zip + "]..." +
                #       BColors.ENDC)

				
				#Original
				#command_line = "ogr2ogr -f GeoJSONSeq /vsigzip/" + fichero_ndjson_zip + \
                #               " " + fichero_geojson
					  
                #Modifico 08/06/2021 // cambio por vrt
                #command_line = "ogr2ogr -f GeoJSONSeq " + fichero_ndjson_zip + " " + fichero_geojson
                # print(command_line)
                # args = shlex.split(command_line)
                # subprocess.call(args)
                if "vrt" in file_0 and not "recorte" in file_0:
                    print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Exportando a NDJSON (gzipped) [" + fichero_ndjson_zip + "]..." +
                      BColors.ENDC)
                    command_line = "ogr2ogr -f GeoJSONSeq " + fichero_ndjson_zip + " " + fichero_geojson
                    print(command_line)
                    args = shlex.split(command_line)
                    subprocess.call(args)

                # Borrado del GeoJSON original
                #if os.path.isfile(fichero_geojson):
                    #os.remove(fichero_geojson)

            Parallel(n_jobs=nucleos)(delayed(VRT2GZ)(file_0) for file_0 in files)  


    # Tippecanoe
    def tiling_pbf(self):
        print(BColors.OKGREEN +
              self.get_time() +
              "---> Ejecutando: tiling_layers" +
              BColors.ENDC)
        print(len(self.config["zoom_levels"]))
        for z in self.config["zoom_levels"]:
        # def teselacion(z):
            if z['process'] == 'no':
                continue
                # return

            input_layers = self.config["destination_layers_geojson"]
            output_mbtiles = self.config["destination_mbtiles"]
            destination_folder = self.config["destination_folder"]
            temp = self.config["temp_directory"]
            toFolder = self.config['setup']['toFolder']

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
                    layers_with_labels += " --named-layer='" + l["name"] + "':" + input_layers + l["file"]

                print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Tiling layers with labels, zoom " + zoom +
                      BColors.ENDC)
                command_line = "tippecanoe -P -o " + \
                               output_mbtiles + "CNIG_" + zoom + "_layers_with_labels.mbtiles " + \
                               layers_with_labels + \
                               " -j '" + filter_attr + "'" + \
                               " -z " + zoom + " -Z " + zoom + \
                               " --no-feature-limit" + \
                               " --no-tile-size-limit" + \
                               " --buffer=127" + \
                               " --convert-stringified-ids-to-numbers" + \
                               " --attribute-type=population:int" + \
                               " --attribute-type=sqkm:int" +\
                               " --no-tile-compression" +\
                               " -f -t " + temp

                # print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)

            # Layer que no tiene que unir (dissolve) EDIFICIOS
            if 'layers_no_coalesce' in z and len(z['layers_no_coalesce']) > 0:
                layers_no_coalesce = ''
                layers_to_join.append('layers_no_coalesce')
                for l in z["layers_no_coalesce"]:
                    layers_no_coalesce += " --named-layer='" + l["name"] + "':" + input_layers + l["file"]

                print(BColors.OKGREEN +
                      self.get_time() +
                      "---> Tiling layers with no coalesce, zoom " + zoom +
                      BColors.ENDC)
                command_line = "tippecanoe -P -o " + \
                               output_mbtiles + "CNIG_" + zoom + "_layers_no_coalesce.mbtiles " + \
                               layers_no_coalesce + \
                               " -j '" + filter_attr + "'" + \
                               " -z " + zoom + " -Z " + zoom + \
                               " --buffer=44" + \
                               " -f -t " + temp + \
                               " --reorder" + \
                               " --no-feature-limit" + \
                               " --no-tile-size-limit" + \
                               " --convert-stringified-ids-to-numbers" + \
                               " --attribute-type=population:int" + \
                               " --attribute-type=sqkm:int" +\
                               " --no-tile-compression"

                # print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)
            
            # Capas normales
            if 'layers' in z and len(z['layers']) > 0:
                layers = ''
                layers_to_join.append('layers')
                for l in z["layers"]:
                    layers += " --named-layer='" + l["name"] + "':" + input_layers + l["file"]

                if len(layers_to_join) == 1 and toFolder != 'yes':
                    # Tippecanoe command
                    print(BColors.OKGREEN +
                        self.get_time() +
                        "---> Tiling layers, zoom " + zoom +
                        BColors.ENDC)
                    command_line = "tippecanoe -P -o " + output_mbtiles + "CNIG_" + zoom + "_layers.mbtiles " + \
                                layers + \
                                " -j '" + filter_attr + "'" + \
                                " -z " + zoom + " -Z " + zoom + \
                                " --buffer=44" + \
                                " -f -t " + temp + \
                                " --coalesce" + \
                                " --reorder" + \
                                " --no-feature-limit" + \
                                " --no-tile-size-limit" + \
                                " --convert-stringified-ids-to-numbers" + \
                                " --attribute-type=population:int" + \
                                " --attribute-type=sqkm:int" +\
                                " --no-tile-compression"
                    print(command_line)
                    args = shlex.split(command_line)
                    subprocess.call(args)

                    os.rename(output_mbtiles + "CNIG_" + zoom + "_" + layers_to_join[0] + ".mbtiles",
                            output_mbtiles + "CNIG_" + zoom + ".mbtiles")

                
                if len(layers_to_join) == 1 and toFolder == 'yes':
                    
                    # Tippecanoe command
                    print(BColors.OKGREEN +
                        self.get_time() +
                        "---> Tiling layers, zoom " + zoom +
                        BColors.ENDC)
                    command_line = "tippecanoe -P -e " + \
                                destination_folder + \
                                layers + \
                                " -j '" + filter_attr + "'" + \
                                " -z " + zoom + " -Z " + zoom + \
                                " --buffer=44" + \
                                " -f -t " + temp + \
                                " --coalesce" + \
                                " --reorder" + \
                                " --no-feature-limit" + \
                                " --no-tile-size-limit" + \
                                " --convert-stringified-ids-to-numbers" + \
                                " --attribute-type=population:int" + \
                                " --attribute-type=sqkm:int" +\
                                " --no-tile-compression"
                    print(command_line)
                    args = shlex.split(command_line)
                    subprocess.call(args)
             
            #  Join de los MBTiles layers, layers_with_labels, layers_no_coalesce
            print(BColors.OKGREEN +
                  self.get_time() +
                  "---> Joining MBTiles, zoom " + zoom +
                  BColors.ENDC)

            if len(layers_to_join) <= 1:
                # return
                continue

            else:
                # Aure: comprobar si la salida es a mbtiles o a carpeta
                if toFolder == 'yes':
                    command_line = "tile-join -e " + \
                                destination_folder + \
                                "-pk " + \
                                "-f " +\
                                " --no-tile-compression"
                    for layer_type in layers_to_join:
                        command_line += output_mbtiles + "CNIG_" + zoom + "_" + layer_type + ".mbtiles "
                else:
                    command_line = "tile-join -o " + \
                                output_mbtiles + "CNIG_" + zoom + ".mbtiles " + \
                                "-pk " + \
                                "-f " +\
                                " --no-tile-compression"
                    for layer_type in layers_to_join:
                        command_line += output_mbtiles + "CNIG_" + zoom + "_" + layer_type + ".mbtiles "

                # print(command_line)
                args = shlex.split(command_line)
                subprocess.call(args)

                # Borramos archivos originales de capa
                #for layer_type in layers_to_join:
                    #os.remove(output_mbtiles + "CNIG_" + zoom + "_" + layer_type + ".mbtiles")


        # Parallel(n_jobs=nucleos)(delayed(teselacion)(z) for z in self.config["zoom_levels"])  


    # mb-util
    def MBtiles2Folder(self):
        output_mbtiles = self.config["destination_mbtiles"]
        destination_folder = self.config["destination_folder"]
        temp = self.config["temp_directory"]

        MBtilesFiles = [x for x in os.listdir(output_mbtiles)  if "mbtiles" in x]

        # for mbtile in MBtilesFiles:
        def MBtilesFiles2folder(mbtile):
            # Tippecanoe command
            print(BColors.OKGREEN +
                self.get_time() +
                "---> MBtile file  " + mbtile +
                BColors.ENDC)
            pathMBtile = output_mbtiles + mbtile +  " "
            pathFolder = temp + mbtile.split(".")[0] +  " "
            command_line = "mb-util " + \
                        " --image_format=pbf " + \
                        pathMBtile + \
                        pathFolder 
                        
            print(command_line)
            args = shlex.split(command_line)
            subprocess.call(args)
        
        Parallel(n_jobs=nucleos)(delayed(MBtilesFiles2folder)(mbtile) for mbtile in MBtilesFiles)  



'''
PROCESO DEL FICHERO IGO
'''

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
if setup['MBtilestoFolder'] == 'yes':
    log.info('--> MBtiles --> PBF folder')
    process.MBtiles2Folder()

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
