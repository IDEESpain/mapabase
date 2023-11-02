from logging import raiseExceptions
import  os, time, os, json, sys, codecs, gc
from datetime import datetime

import warnings

from joblib import Parallel, delayed

class transformar:

    def __init__(self,path_carpetaEntrada):
        self.path_carpetaEntrada = path_carpetaEntrada
        self.verbose = False
        self.nNucleos = 6

                       
    def transformarVRT(self,path_carpetaFGB_origen=None,path_carpetaFGB_destino=None):
        if path_carpetaFGB_origen==None:
          path_carpetaFGB_origen=self.path_carpetaEntrada

        if path_carpetaFGB_destino==None:
          path_carpetaFGB_destino=self.path_carpetaEntrada


        listaVRTCreados = [x for x in os.listdir(path_carpetaFGB_origen) if "vrt" in x]

        print(path_carpetaFGB_origen)
        
        # for vrt in listaVRTCreados:
        def VRT2FGB(vrt):
          print(vrt)
          command_line = "ogr2ogr -skipfailures -f FlatGeobuf -nlt PROMOTE_TO_MULTI " + path_carpetaFGB_destino +  vrt.split(".")[0] + ".fgb"+ " " + path_carpetaFGB_origen  + vrt
          print(command_line)
          # args = shlex.split(command_line)
          os.system(command_line)

        #Paralelización, el -1 indica que coge el máximo número de procesos.
        Parallel(n_jobs=self.nNucleos)(delayed(VRT2FGB)(vrt) for vrt in listaVRTCreados)

    def transformarGJSON(self,path_carpetaSalida=None):
        if path_carpetaSalida==None:
          path_carpetaSalida=self.path_carpetaEntrada
        listaGeojsonCreados = [x for x in os.listdir(self.path_carpetaEntrada) if "geojson" in x]
        
        # for gjson in listaGeojsonCreados:
        def gjson2FGB(gjson):
          print(gjson)
          command_line = "ogr2ogr -skipfailures -f FlatGeobuf -nlt PROMOTE_TO_MULTI " + path_carpetaSalida +  gjson.split(".")[0] + "_"+gjson.split("_")[-1] + ".fgb"+ " " + self.path_carpetaEntrada  + gjson
          print(command_line)
          # args = shlex.split(command_line)
          os.system(command_line)
        
        #Paralelización, el -1 indica que coge el máximo número de procesos.
        Parallel(n_jobs=self.nNucleos)(delayed(gjson2FGB)(gjson) for gjson in listaGeojsonCreados)
