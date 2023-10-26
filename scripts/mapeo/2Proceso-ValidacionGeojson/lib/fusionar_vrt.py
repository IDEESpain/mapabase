from logging import raiseExceptions
import  os, time, os, json, sys, codecs, gc
from datetime import datetime

import re

class fusionar_vrt:

    def __init__(self,path_carpetaEntrada):
        self.path_carpetaEntrada = path_carpetaEntrada
        self.verbose = False
                       
    def gjson2VRT(self):
        jsonElementos = {}
        listaGeojsonCreados = [x for x in os.listdir(self.path_carpetaEntrada) if "geojson" in x]

        # XML ejemplo unión
        """
        <OGRVRTDataSource>
            <OGRVRTUnionLayer name="unionLayer">
                <OGRVRTLayer name="source1">
                    <SrcDataSource>source1.shp</SrcDataSource>
                </OGRVRTLayer>
                <OGRVRTLayer name="source2">
                    <SrcDataSource>source2.shp</SrcDataSource>
                </OGRVRTLayer>
            </OGRVRTUnionLayer>
        </OGRVRTDataSource>


        <OGRVRTDataSource>
            <OGRVRTLayer name="source">
                <SrcDataSource>source.shp</SrcDataSource>
                <SrcRegion clip="true">POLYGON((0 40,10 40,10 50,0 50,0 40))</SrcRegion>
            </OGRVRTLayer>
        </OGRVRTDataSource>
        """
        xml = """
              <OGRVRTDataSource>
                <OGRVRTUnionLayer name="unionLayer">
              """

        gjsonAnterior = ''
        for e in sorted(listaGeojsonCreados):
            if e.split('.')[0] == gjsonAnterior:
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(e.split('.')[0],"./"+e )
            else:
                xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                            """
                xml = xml.replace("unionLayer",gjsonAnterior)
                print(xml)
                text_file = open(self.path_carpetaEntrada+gjsonAnterior+".vrt", "w")
                n = text_file.write(xml)
                text_file.close()
                print(e)
                xml = """
                         <OGRVRTDataSource>
                             <OGRVRTUnionLayer name="unionLayer">
                      """
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(e.split('.')[0],"./"+e )
                
            gjsonAnterior = e.split('.')[0]

        xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                    """
        xml = xml.replace("unionLayer",e.split('.')[0])
        print(xml)
        text_file = open(self.path_carpetaEntrada+gjsonAnterior+".vrt", "w")
        n = text_file.write(xml)
        text_file.close()
        print('--------------------')
        # exit()
        # command_line = "ogr2ogr -f GeoJSONSeq " + fichero_ndjson_zip + " " + fichero_geojson
        # print(command_line)
        # args = shlex.split(command_line)
        # subprocess.call(args)
        return 0

    def has_numbers(self,inputString):
        return bool(re.search(r'\d+$', inputString[:-4]))

    def fgb2VRT(self,path_carpeta_fgb=None):
        if path_carpeta_fgb is None:
            path_carpeta_fgb=self.path_carpetaEntrada
        jsonElementos = {}
        listaGeojsonCreados = [x for x in os.listdir(path_carpeta_fgb) if "fgb" in x and self.has_numbers(x) == False]

        xml = """
              <OGRVRTDataSource>
                <OGRVRTUnionLayer name="unionLayer">
              """

        gjsonAnterior = ''
        for e in sorted(listaGeojsonCreados):
            if e.split('.')[0] == gjsonAnterior:
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(e.split('.')[0],"./"+e )
            else:
                xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                            """
                xml = xml.replace("unionLayer",gjsonAnterior)
                print(xml)
                text_file = open(path_carpeta_fgb+gjsonAnterior+".vrt", "w")
                n = text_file.write(xml)
                text_file.close()
                print(e)
                xml = """
                         <OGRVRTDataSource>
                             <OGRVRTUnionLayer name="unionLayer">
                      """
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(e.split('.')[0],"./"+e )
                
            gjsonAnterior = e.split('.')[0]

        xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                    """
        xml = xml.replace("unionLayer",e.split('.')[0])
        print(xml)
        text_file = open(path_carpeta_fgb+gjsonAnterior+".vrt", "w")
        n = text_file.write(xml)
        text_file.close()
        print('--------------------')
        # exit()
        # command_line = "ogr2ogr -f GeoJSONSeq " + fichero_ndjson_zip + " " + fichero_geojson
        # print(command_line)
        # args = shlex.split(command_line)
        # subprocess.call(args)
        return 0

    def fgb_n_2VRT(self,path_carpeta_fgb=None):

        if path_carpeta_fgb is None:
            path_carpeta_fgb=self.path_carpetaEntrada
        jsonElementos = {}
        listaGeojsonCreados = [x for x in os.listdir(path_carpeta_fgb) if "fgb" in x and self.has_numbers(x) == True ]

        xml = """
              <OGRVRTDataSource>
                <OGRVRTUnionLayer name="unionLayer">
              """
        nombreCapa = ""
        gjsonAnterior = ''
        for e in sorted(listaGeojsonCreados):
            nombreCapa = '_'.join(e.split('.')[0].split('_')[0:-1])
            # print(nombreCapa)

            if self.has_numbers(e) == False:
                continue

            if nombreCapa  == gjsonAnterior:
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(nombreCapa ,"./"+e )
            else:
                xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                            """
                xml = xml.replace("unionLayer",gjsonAnterior)
                # print(xml)
                text_file = open(path_carpeta_fgb+gjsonAnterior+".vrt", "w")
                n = text_file.write(xml)
                text_file.close()
                print(e)
                xml = """
                         <OGRVRTDataSource>
                             <OGRVRTUnionLayer name="unionLayer">
                      """
                xml = xml + """
                                <OGRVRTLayer name="{}">
                                    <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
                                </OGRVRTLayer>
                            """.format(nombreCapa ,"./"+e )
                
            gjsonAnterior = nombreCapa

        xml = xml + """
                            </OGRVRTUnionLayer>
                        </OGRVRTDataSource>
                    """
        xml = xml.replace("unionLayer",nombreCapa )
        # print(xml)
        text_file = open(path_carpeta_fgb+gjsonAnterior+".vrt", "w")
        n = text_file.write(xml)
        text_file.close()
        print('--------------------')
        # exit()
        # command_line = "ogr2ogr -f GeoJSONSeq " + fichero_ndjson_zip + " " + fichero_geojson
        # print(command_line)
        # args = shlex.split(command_line)
        # subprocess.call(args)
        return 0

    def deleteTempFiles(self, path_carpetaTempFGB):
        command_line = "rm -rf " + path_carpetaTempFGB
        print(command_line)
        # args = shlex.split(command_line)
        os.system(command_line)

