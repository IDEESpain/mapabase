from logging import raiseExceptions
import  os, time, os, json, sys, codecs, gc
from datetime import datetime
import html_to_json

from xml.etree import ElementTree as ET



class control_calidad_GJSON:

    def __init__(self,path_carpetaEntrada):
        self.path_carpetaEntrada = path_carpetaEntrada

        with open ("./config.json") as f:
            var_dict=json.load(f)

        self.verbose = False
        self.git_carpeta_mapabase_gh_pages = var_dict["git_carpeta_mapabase_gh_pages"]
        self.JSON_comprobacion = var_dict["JSON_comprobacion"]
        self.JSON_config_Tippecanoe = var_dict["JSON_config_Tippecanoe"]
                       

    def elementosAJSON(self):
        jsonElementos = {}
        elementos = os.listdir(self.git_carpeta_mapabase_gh_pages+'/elementos')

        for e in elementos:
            jsonElementos[e] = {}

            indexHTMLFile = codecs.open(self.git_carpeta_mapabase_gh_pages+'/elementos/'+e+'/index.html', "r", 'UTF-8')
            indexHTMLJSON = html_to_json.convert(indexHTMLFile.read())
            indexHTMLFile.close()

            for ind_line, line in enumerate(indexHTMLJSON['html'][0]['body'][0]['div']):
                if 'Atributos y dominios de valores' in json.dumps(line):
                    for line_n2 in line['div']:
                        if 'table' in json.dumps(line_n2):
                            for line_n3 in line_n2['table'][0]['tbody'][0]['tr']:
                                if 'code' in str(line_n3['td'][0]):
                                    if line_n3['td'][2] == {}:
                                        listaDominio = ['*']
                                    elif not '[' in str(line_n3['td'][2]['_value']):
                                        listaDominio = [line_n3['td'][2]['_value']]
                                    else:
                                        listaDominio = ['*']
                                    print(e,line_n3)
                                    atrNombre = line_n3['td'][0]['code'][0]['_value']
                                    jsonElementos[e][line_n3['td'][0]['code'][0]['_value']] = listaDominio
                                    
                                else:
                                    value = line_n3['td'][2]['_value']
                                    if atrNombre == 'jerarquia':
                                        value = int(value)
                                    if jsonElementos[e][atrNombre] == ['*']:
                                        jsonElementos[e][atrNombre] = []
                                    jsonElementos[e][atrNombre].append( value )

            if jsonElementos[e] == {}:
                del jsonElementos[e]

        archivoJSON =codecs.open(self.JSON_comprobacion, "w", "utf-8")
        archivoJSON.write(json.dumps(jsonElementos, ensure_ascii=False))
        archivoJSON.close()
        return 0

    def elementosAJSON_Tippecanoe(self,destination_layers_geojson,destination_mbtiles,temp_directory, project:dict, setup:dict):
        json_config= {
            "destination_layers_geojson": destination_layers_geojson,
            "destination_mbtiles": destination_mbtiles,
            "temp_directory": temp_directory,
            "project":project,
            "setup":setup,
            "zoom_levels":[]
            }
        niveles = os.listdir(self.git_carpeta_mapabase_gh_pages+'/niveles')
        for e in niveles:
            if e in ['no_disponible']:
                continue

            dicc_nivel = {
                            "level": e.split('_')[1],
                            "process": "yes",
                            "layers": [],
                            "layers_no_coalesce": [],
                            "layers_with_labels": [],
                            "filter": {}
                        }
            json_config['zoom_levels'].append(dicc_nivel)

            indexHTMLFile = codecs.open(self.git_carpeta_mapabase_gh_pages+'/niveles/'+e+'/index.html', "r", 'UTF-8')
            indexHTMLJSON = html_to_json.convert(indexHTMLFile.read())
            indexHTMLFile.close()
            for j in indexHTMLJSON:
                if j =='html':
                    for jj in indexHTMLJSON[j][0]['body'][0]['div'][1]['div'][1]['p']:
                        if 'a' in jj:
                            diccCapa = {
                                        "file": jj['a'][0]['strong'][0]['_value']+".geojson",
                                        "name": jj['a'][0]['strong'][0]['_value']
                                        }
                            json_config['zoom_levels'][-1]['layers'].append(diccCapa)

                            if 'code' in jj:
                                
                                if '_value' in jj:
                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']] = ["all"]
                                    listaFiltro= [
                                                "==",
                                                jj['code'][0]['_value'],
                                                jj['_value'].split('=')[1][1:]
                                                ]
                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']].append(listaFiltro)

                                elif '_values' in jj:
                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']] = ["any"]
                                    listaFiltroLista = []
                                    for i_v,v in enumerate(jj['_values']):
                                        listaFiltro= [
                                                    "==",
                                                    jj['code'][i_v]['_value'],
                                                    v.split('=')[1][1:]
                                                    ]

                                        listaFiltroLista.append(listaFiltro)
                                    

                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']].extend(listaFiltroLista)

                                else:
                                    raiseExceptions

        archivoJSON =codecs.open(self.JSON_config_Tippecanoe, "w", "utf-8")
        archivoJSON.write(json.dumps(json_config, ensure_ascii=False))
        archivoJSON.close()

    def procesoControlCalidad(self):
        #Crea log del proceso
        start_time_total = time.time()
        ahora = datetime.now()
        anno = ahora.strftime("%Y")
        mes = ahora.strftime("%m")
        dia = ahora.strftime("%d")
        hora = ahora.strftime("%H")
        min = ahora.strftime("%M")
        seg = ahora.strftime("%S")
        subNombre = anno+mes+dia+'_'+hora+min+seg
        pathlog = self.path_carpetaEntrada +'/'+subNombre +'_ControlCalidad'+'.log'
        archivoLOG = codecs.open(pathlog, "w","utf-8")
        archivoLOG.write(" ### --- Log del proceso de control de calidad del proceso PG a GeoJSON --- ### \n")
        archivoLOG.write(" # ---------------------------------------------------------------------------- \n") 
        archivoLOG.write(" \n")
        archivoLOG.write(" # Inicio: {} \n".format( ahora.strftime("%m/%d/%Y, %H:%M:%S")) )
        archivoLOG.write(" \n")
        archivoLOG.close()

        # Coge los dominios del JSON
        jsonComprobaciones = codecs.open(self.JSON_comprobacion , "r","utf-8")
        jsonC = json.loads(jsonComprobaciones.read())
        jsonComprobaciones.close()

        ### Comprobación Archivos Geojson
        if self.verbose:
            print("##### Comprobación ficheros Geojson #####")
        archivoLOG = codecs.open(pathlog, "a","utf-8")
        archivoLOG.write(" ##### Comprobación ficheros Geojson #####\n")
        archivoLOG.write(" \n")

        totalGJSONModelo = len(jsonC)
        GJSONNModelo = []
        GJSONEntregados = []
        GJSONNOEntregados = []
        GJSONEntregadosModelo = []
        GJSONEntregadosNoModelo = []
        GJSONEntregadosModelo_NombreCompleto = []
        listaModelosEntregados =[]
        listaGeojsonVrt = [x for x in os.listdir(self.path_carpetaEntrada) if x.endswith(".vrt")]
        totalGeojsonEntregados=len(listaGeojsonVrt)-1

        #print(listaGeojsonVrt)
        for g in listaGeojsonVrt:
            xml = ET.parse(self.path_carpetaEntrada+"/"+g)
            root = xml.getroot()


            geojsons= [x.text for x in (root.findall("OGRVRTUnionLayer/OGRVRTLayer/SrcDataSource"))]

            for geojson in geojsons:
                nombreArchivoCompleto = geojson
                nombreArchivo=geojson.split("/")[-1].split(".")[0]
                #print(nombreArchivo)
                GJSONEntregados.append(nombreArchivo)


                print(jsonC)
                for j in jsonC:
                    if nombreArchivo == j:
                        print("Clase de entidad: ",nombreArchivo," \t Archivo: ", nombreArchivoCompleto)
                        GJSONEntregadosModelo.append((nombreArchivo,nombreArchivoCompleto.split("/")[-1]))
                        GJSONEntregadosModelo_NombreCompleto.append(nombreArchivoCompleto.split("/")[-1])
                        listaModelosEntregados.append(nombreArchivo)
                        break
        
        for j in jsonC:
            GJSONNModelo.append(j)
            if not j in GJSONEntregados:
                GJSONNOEntregados.append(j)
        
        for g in GJSONEntregados:
            if not g in GJSONNModelo:
                GJSONEntregadosNoModelo.append(g)

        totalGJSONEntregadosModelo=len(set(listaModelosEntregados))

        totalGJSONEntregadosNoModelo=len(set(GJSONEntregadosNoModelo))
            
        archivoLOG.write(" Geojson en el modelo de datos: {} \n".format(totalGJSONModelo)  )
        archivoLOG.write(" Geojson entregados: {} \n".format(totalGeojsonEntregados)  )
        archivoLOG.write(" Geojson entregados del modelo de datos: {} \n".format(totalGJSONEntregadosModelo)  )
        archivoLOG.write("      {} \n".format( sorted(listaModelosEntregados) ) )
        archivoLOG.write(" Geojson NO entregados del modelo de datos: {} \n".format(len(GJSONNOEntregados))  )
        archivoLOG.write("      {} \n".format( sorted(GJSONNOEntregados) ) )
        archivoLOG.write(" Geojson entregados que NO son del modelo de datos: {} \n".format(totalGJSONEntregadosNoModelo)  )
        archivoLOG.write("      {} \n".format(sorted(GJSONEntregadosNoModelo) )  )
        archivoLOG.write(" ------------------------------------------------------------- \n" )
        archivoLOG.write(" \n")
        archivoLOG.close()

        ### Comprobación Dominios para cada clase de entidad
        ## TODO CAMBIAR ESTO
        if self.verbose:
            print("##### Comprobación Atributos #####")
        archivoLOG = codecs.open(pathlog, "a","utf-8")
        archivoLOG.write(" ##### Comprobación Atributos #####\n")
        archivoLOG.write(" \n")

        for geojsonEntregadoModelo,geojsonEntregaModelo_nombre in GJSONEntregadosModelo:
            print(self.path_carpetaEntrada+geojsonEntregaModelo_nombre)

            jsonGJSON = codecs.open(self.path_carpetaEntrada+geojsonEntregaModelo_nombre , "r","utf-8")
            jsGJSON = json.loads(jsonGJSON.read())
            jsonGJSON.close()

            atributosModelo = []
            atributosEntregados = []
            atributosNOEntregados = []
            atributosEntregadosModelo = []
            atributosEntregadosNOModelo = []
            print("---- "+ geojsonEntregaModelo_nombre+"")
            for entidad in jsGJSON['features']:

                for e in entidad['properties']:
                    if not e in atributosEntregados:
                        atributosEntregados.append(e)

                for j in jsonC[geojsonEntregadoModelo]:
                    if not j in atributosModelo:
                        atributosModelo.append(j)

                for e in entidad['properties']:
                    if not e in atributosModelo:
                        if not e in atributosEntregadosNOModelo:
                            atributosEntregadosNOModelo.append(e)
                    else:
                        if not e in atributosEntregadosModelo:
                            atributosEntregadosModelo.append(e)

                for j in jsonC[geojsonEntregadoModelo]:
                    if not j in atributosEntregados:
                        if not j in atributosNOEntregados:
                            atributosNOEntregados.append(j)
            
            try:
                del jsGJSON
                del jsonGJSON
            except:
                pass
            gc.collect() 
                
            archivoLOG.write(" ------   {}   -------\n".format(geojsonEntregaModelo_nombre))
            archivoLOG.write(" \n")
            archivoLOG.write(" Atributos en modelo de datos : {} \n".format( len(atributosModelo) ) )
            archivoLOG.write("     {} \n".format(atributosModelo) )
            archivoLOG.write(" Atributos en Geojson : {} \n".format( len(atributosEntregados) ) )
            archivoLOG.write("     {} \n".format(sorted(atributosEntregados) ) )
            archivoLOG.write(" Atributos NO encontrados en alguna entidad del Geojson : {} \n".format( len(atributosNOEntregados) ) )
            archivoLOG.write("     {} \n".format(sorted(atributosNOEntregados)) )
            archivoLOG.write(" Atributos encontrados del modelo : {} \n".format( len(atributosEntregadosModelo) ) )
            archivoLOG.write("     {} \n".format(sorted(atributosEntregadosModelo) ) )
            archivoLOG.write(" Atributos encontrados en alguna entidad que NO son del modelo : {} \n".format( len(atributosEntregadosNOModelo) ) )
            archivoLOG.write("     {} \n".format(sorted(atributosEntregadosNOModelo) ) )
            diferencia_atributos = len(atributosModelo) - len(atributosEntregados)
            archivoLOG.write(" Diferencia de atributos: {} ".format( diferencia_atributos) )
            if diferencia_atributos != 0:
                archivoLOG.write(" ERROR. Número de atributos diferente al esperado")


            archivoLOG.write(" \n")
        archivoLOG.close()


        try:
            del jsGJSON
            del jsonGJSON
            del atributosModelo
            del atributosEntregados 
            del atributosNOEntregados 
            del atributosEntregadosModelo 
            del atributosEntregadosNOModelo 
        except:
            pass
        gc.collect()  

        ### Comprobación Dominios de valores de los atributos
        if self.verbose:
            print("##### Comprobación Dominios #####")

        archivoLOG = codecs.open(pathlog, "a","utf-8")
        archivoLOG.write(" ##### Comprobación Dominios #####\n")
        archivoLOG.write(" \n")

        for geojsonEntregadoModelo,geojsonEntregaModelo_nombre in GJSONEntregadosModelo:
            jsonGJSON = codecs.open(self.path_carpetaEntrada+'/'+geojsonEntregaModelo_nombre, "r","utf-8")
            jsGJSON = json.loads(jsonGJSON.read())
            jsonGJSON.close()

            archivoLOG.write(" ------   {}   -------\n".format(geojsonEntregaModelo_nombre))
            archivoLOG.write(" \n")

            valoresNoDominio = {}
            for entidad in jsGJSON['features']:
                for atr, valor in entidad['properties'].items():
                    # Si el atributo no está en el modelo, lo ignoramos.
                    if atr not in jsonC[geojsonEntregadoModelo]:
                        continue

                    # Si el valor no está dentro de los valores permitidos y no es un comodín ('*'), lo registramos.
                    if valor not in jsonC[geojsonEntregadoModelo][atr] and jsonC[geojsonEntregadoModelo][atr] != ['*']:
                        if atr not in valoresNoDominio:
                            valoresNoDominio[atr] = []
                        if valor not in valoresNoDominio[atr]:
                            valoresNoDominio[atr].append(valor)

            # Liberar recursos de memoria
            try:
                del jsGJSON
                del jsonGJSON
            except:
                pass
            gc.collect()

            # Escritura de las discrepancias en el archivo de log
            for atr, valores in valoresNoDominio.items():
                archivoLOG.write(f" Atributo donde existen discrepancias : {atr} \n")
                archivoLOG.write(f"     {sorted(valores)} \n")
                archivoLOG.write(" \n")

            # Liberar recursos adicionales de memoria
            try:
                del valoresNoDominio
            except:
                pass
            gc.collect()

        return 0
        


