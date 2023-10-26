from logging import raiseExceptions
import  os, time, os, json, sys, codecs, gc, random, copy
from datetime import datetime
import html_to_json
from lxml import etree


class control_calidad_GJSON:

    def __init__(self,path_carpetaEntrada):
        self.path_carpetaEntrada = path_carpetaEntrada

        self.verbose = False
        self.git_carpeta_mapabase_gh_pages = './mapabase-gh-pages'
        self.JSON_comprobacion = './lib/comprobacion.json'
        self.JSON_config_Tippecanoe = "./lib/config_vtiles.json"
        self.JSON_MapboxGL = "./lib/estiloMapboxGL.json"
                       
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
                                    atrNombre = line_n3['td'][0]['code'][0]['_value']
                                    jsonElementos[e][line_n3['td'][0]['code'][0]['_value']] = listaDominio
                                else:
                                    if jsonElementos[e][atrNombre] == ['*']:
                                        jsonElementos[e][atrNombre] = []
                                    jsonElementos[e][atrNombre].append( line_n3['td'][2]['_value'] )

            if jsonElementos[e] == {}:
                del jsonElementos[e]

        archivoJSON =codecs.open(self.JSON_comprobacion, "w", "utf-8")
        archivoJSON.write(json.dumps(jsonElementos, ensure_ascii=False))
        archivoJSON.close()
        return 0

    def niveles_AJSON_Tippecanoe(self):
        git_carpeta_mapabase_gh_pages=self.git_carpeta_mapabase_gh_pages
        niveles = list(reversed(os.listdir(git_carpeta_mapabase_gh_pages+'/niveles')))

        json_config = {
            "zoom_levels": [],
        }


        for nivel in niveles:
            if nivel in ['no_disponible']:
                continue

            #print(nivel)

            dicc_nivel = {
                            "level": int(nivel.split('_')[1]),
                            "process": "yes",
                            "layers": [],
                            "layers_no_coalesce": [],
                            "layers_with_labels": [],
                            "filter": {}
                        }
            #print('dicc_nivel ',dicc_nivel)
            

            #indexHTMLFile = codecs.open(git_carpeta_mapabase_gh_pages+'/niveles/'+nivel+'/index.html', "r", 'UTF-8')
            index_file=codecs.open(git_carpeta_mapabase_gh_pages+'/niveles/'+nivel+'/index.html', 'r')
            html_text=index_file.read()
            index_file.close()
            
            tree=etree.HTML(html_text)
            layers=[{"file":''.join(x.itertext())+".gz","name":''.join(x.itertext())} for x in tree.xpath("//p/a[not(@no_coalesce)]/strong")]
            layers_no_coalesce=[{"file":''.join(x.itertext())+".gz","name":''.join(x.itertext())} for x in tree.xpath("//p/a[@no_coalesce]/strong")]
            #hacer algo parecido para las layers con atributos
            dicc_nivel["layers"]=layers
            dicc_nivel["layers_no_coalesce"]=layers_no_coalesce


            filtros=tree.xpath("//*[@parent]")
            for filtro in filtros:
                dicc_nivel["filter"][filtro.attrib['parent']]=[]

            for filtro in filtros:
                list_filter=["=="]+''.join(filtro.itertext()).split("==")

                #filtros con un and: acequia...
                if len(list_filter)>3:
                    continue

                #print(list_filter)
                dicc_nivel["filter"][filtro.attrib['parent']].append(list_filter)

            for key,value in dicc_nivel["filter"].items():
                if len(value)>1:
                    dicc_nivel["filter"][key].insert(0,"any")
                else:
                    dicc_nivel["filter"][key].insert(0,"all")

                #print(dicc_nivel)

            
            json_config['zoom_levels'].append(dicc_nivel)

        #print(json_config)
        ordered_levels_list = sorted(json_config['zoom_levels'], key=lambda level: level['level']) 

        json_config["zoom_levels"]=ordered_levels_list

        with open("config_vtiles.json", "w") as outfile:
            json.dump(json_config, outfile)

    def elementosAJSON_Tippecanoe(self, destination_layers_geojson, gz_folder,destination_mbtiles, temp_directory, project: dict, setup: dict,destination_folder):
        json_config = {
            "input_vrt": destination_layers_geojson,
            "gz_folder":gz_folder,
            "destination_mbtiles": destination_mbtiles,
            "final_folder": destination_folder,
            "temp_directory": temp_directory,
            "project": project,
            "setup": setup,
            "zoom_levels": [],
        }
        niveles = list(reversed(os.listdir(self.git_carpeta_mapabase_gh_pages+'/niveles')))

        for e in niveles:
            if e in ['no_disponible']:
                continue

            dicc_nivel = {
                            "level": int(e.split('_')[1]),
                            "process": "yes",
                            "layers": [],
                            "layers_no_coalesce": [],
                            "layers_with_labels": [],
                            "filter": {}
                        }
            print('dicc_nivel ',dicc_nivel)
            json_config['zoom_levels'].append(dicc_nivel)

            indexHTMLFile = codecs.open(self.git_carpeta_mapabase_gh_pages+'/niveles/'+e+'/index.html', "r", 'UTF-8')
            indexHTMLJSON = html_to_json.convert(indexHTMLFile.read())
            indexHTMLFile.close()
            for j in indexHTMLJSON:
                if j =='html':
                    for jj in indexHTMLJSON[j][0]['body'][0]['div'][1]['div'][1]['p']:
 
                        if 'a' in jj:
                            for kk in jj['a']:
                                diccCapa = {
                                            "file": kk['strong'][0]['_value']+".gz",
                                            "name": kk['strong'][0]['_value']
                                            }
                                print('diccCapa ',diccCapa)
                                json_config['zoom_levels'][-1]['layers'].append(diccCapa)

                            if 'code' in jj:
                                
                                if '_value' in jj:
                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']] = ["all"]
                                    listaFiltro= [
                                                "==",
                                                jj['code'][0]['_value'],
                                                jj['_value'].split('=')[1][1:]
                                                ]
                                    print('listaFiltro0 ',listaFiltro)
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
                                        print('listaFiltro1 ',listaFiltro)
                                        listaFiltroLista.append(listaFiltro)
                                    

                                    json_config['zoom_levels'][-1]['filter'][jj['a'][0]['strong'][0]['_value']].extend(listaFiltroLista)

                                else:
                                    raiseExceptions



        archivoJSON =codecs.open(self.JSON_config_Tippecanoe, "w", "utf-8")
        archivoJSON.write(json.dumps(json_config, ensure_ascii=False))
        archivoJSON.close()

    def crearJSON_MapboxGL_desdeComprobacionJSON(self, confDic:dict, metadata:dict, sources:dict):

        dicc_MB_GL = {  
                        "version":confDic["version"],
                        "name":confDic["name"],
                        "metadata":metadata,
                        "sources":sources,
                        "sprite":confDic["sprite"],
                        "glyphs":confDic["glyphs"],
                        "layers":[],
                        "id":confDic["id"],
                        "owner":confDic["owner"],
                    }
        jsonComprobaciones = codecs.open(self.JSON_comprobacion , "r","utf-8")
        jsonC = json.loads(jsonComprobaciones.read())
        jsonComprobaciones.close()

        

        def valorAleatorio(): 
                return str(random.randint(0,255))

        for e in jsonC:
            
            layer_id = {
                    "id":"",
                    "type":"",
                    "source-layer":"",
                    "source":"",
                    "paint"	:{}
            }
            if len(dicc_MB_GL["layers"]) == 0:
                layer_id["id"] = "fondo"
                layer_id["type"] = 	"background"
                layer_id["paint"] = {"background-color":"rgba(135, 186, 190, 1)"}

                del layer_id["source-layer"]
                del layer_id["source"]

                dicc_MB_GL["layers"].append(copy.copy(layer_id))
            
            if e.split("_")[-1] == 'pol':
                layer_id["id"] = e
                layer_id["type"] = 	"fill"
                layer_id["source-layer"] = e
                layer_id["source"] = list(sources.keys())[0]
                layer_id["paint"] = {"fill-color":"rgba("+valorAleatorio()+","+valorAleatorio()+","+valorAleatorio()+", 0.7)",
                                    "fill-outline-color":"rgba("+valorAleatorio()+","+valorAleatorio()+","+valorAleatorio()+", 0.7)"
                                    }

                dicc_MB_GL["layers"].append(layer_id)


        for e in jsonC:
            
            layer_id = {
                    "id":"",
                    "type":"",
                    "source-layer":"",
                    "source":"",
                    "paint"	:{}
            }

            if e.split("_")[-1] == 'lin':
                layer_id["id"] = e
                layer_id["type"] = 	"line"
                layer_id["source-layer"] = e
                layer_id["source"] = list(sources.keys())[0]
                layer_id["layout"] = {"visibility":"visible"}
                layer_id["paint"] = {"line-color":"rgba("+valorAleatorio()+","+valorAleatorio()+","+valorAleatorio()+", 1)",
                                    "line-width": 2,
                                    "line-opacity": 1
                                    }
                                    
                dicc_MB_GL["layers"].append(layer_id)


        for e in jsonC:
            
            layer_id = {
                    "id":"",
                    "type":"",
                    "source-layer":"",
                    "source":"",
                    "paint"	:{}
            }

            if e.split("_")[-1] == 'pto':
                layer_id["id"] = e
                layer_id["type"] = 	"circle"
                layer_id["source-layer"] = e
                layer_id["source"] = list(sources.keys())[0]
                layer_id["layout"] = {"visibility":"visible"}
                layer_id["paint"] = {"circle-color":"rgba("+valorAleatorio()+","+valorAleatorio()+","+valorAleatorio()+", 1)",
                                    "circle-stroke-color":"rgba("+valorAleatorio()+","+valorAleatorio()+","+valorAleatorio()+", 1)",
                                    "circle-stroke-width": 2,
                                    "circle-radius": 6,
                                    }
                                    
                dicc_MB_GL["layers"].append(layer_id)



        archivoJSON =codecs.open(self.JSON_MapboxGL, "w", "utf-8")
        archivoJSON.write(json.dumps(dicc_MB_GL, ensure_ascii=False))
        archivoJSON.close()
        return 0


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
        listaGeojsonCreados = os.listdir(self.path_carpetaEntrada)
        for g in listaGeojsonCreados:
            if not '.geojson' in g:
                continue
            nombreArchivo = g.split('.')[0]
            GJSONEntregados.append(nombreArchivo)

            for j in jsonC:
                if nombreArchivo == j:
                    GJSONEntregadosModelo.append(nombreArchivo)
                    break
        
        for j in jsonC:
            GJSONNModelo.append(j)
            if not j in GJSONEntregados:
                GJSONNOEntregados.append(j)
        
        for g in GJSONEntregados:
            if not g in GJSONNModelo:
                GJSONEntregadosNoModelo.append(g)
            
        archivoLOG.write(" Geojson en el modelo de datos: {} \n".format(totalGJSONModelo)  )
        archivoLOG.write(" Geojson entregados: {} \n".format(len(GJSONEntregados))  )
        archivoLOG.write(" Geojson entregados del modelo de datos: {} \n".format(len(GJSONEntregadosModelo))  )
        archivoLOG.write(" Geojson NO entregados del modelo de datos: {} \n".format(len(GJSONNOEntregados))  )
        archivoLOG.write("      {} \n".format( sorted(GJSONNOEntregados) ) )
        archivoLOG.write(" Geojson entregados que NO son del modelo de datos: {} \n".format(len(GJSONEntregadosNoModelo))  )
        archivoLOG.write("      {} \n".format(sorted(GJSONEntregadosNoModelo) )  )
        archivoLOG.write(" ------------------------------------------------------------- \n" )
        archivoLOG.write(" \n")
        archivoLOG.close()

        ### Comprobación Dominios para cada clase de entidad
        if self.verbose:
            print("##### Comprobación Atributos #####")
        archivoLOG = codecs.open(pathlog, "a","utf-8")
        archivoLOG.write(" ##### Comprobación Atributos #####\n")
        archivoLOG.write(" \n")

        for geojsonEntregadoModelo in GJSONEntregadosModelo:

            jsonGJSON = codecs.open(self.path_carpetaEntrada+'/'+geojsonEntregadoModelo+'.geojson' , "r","utf-8")
            jsGJSON = json.loads(jsonGJSON.read())
            jsonGJSON.close()

            atributosModelo = []
            atributosEntregados = []
            atributosNOEntregados = []
            atributosEntregadosModelo = []
            atributosEntregadosNOModelo = []
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
                    
            archivoLOG.write(" ------   {}   -------\n".format(geojsonEntregadoModelo))
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
            archivoLOG.write(" \n")
        archivoLOG.close()  

        del jsGJSON
        del jsonGJSON
        del atributosModelo
        del atributosEntregados 
        del atributosNOEntregados 
        del atributosEntregadosModelo 
        del atributosEntregadosNOModelo 
        gc.collect()  

        ### Comprobación Dominios de valores de los atributos
        if self.verbose:
            print("##### Comprobación Dominos #####")

        archivoLOG = codecs.open(pathlog, "a","utf-8")
        archivoLOG.write(" ##### Comprobación Dominos #####\n")
        archivoLOG.write(" \n")

        for geojsonEntregadoModelo in GJSONEntregadosModelo:
            jsonGJSON = codecs.open(self.path_carpetaEntrada+'/'+geojsonEntregadoModelo+'.geojson' , "r","utf-8")
            jsGJSON = json.loads(jsonGJSON.read())
            jsonGJSON.close()

            archivoLOG.write(" ------   {}   -------\n".format(geojsonEntregadoModelo))
            archivoLOG.write(" \n")

            valoresNoDominio = []
            atributosConValoresNoDominio = []
            for entidad in jsGJSON['features']:
                for atr in entidad['properties']:
                    if not atr in jsonC[geojsonEntregadoModelo]:
                        continue
                    if not entidad['properties'][atr] in jsonC[geojsonEntregadoModelo][atr]:
                        if not entidad['properties'][atr] in valoresNoDominio:
                            if jsonC[geojsonEntregadoModelo][atr] == ['*']:
                                continue
                            valoresNoDominio.append(entidad['properties'][atr])
                            atributosConValoresNoDominio.append(atr)

            atrNuevo = ''
            listaValores= []
            for i_n, n in enumerate(valoresNoDominio):
                if i_n == 0:
                    atrNuevo = atributosConValoresNoDominio[i_n]
                if i_n +1 == len(valoresNoDominio):
                    listaValores.append(valoresNoDominio[i_n])
                    archivoLOG.write(" Atributo donde existen discrepancias : {} \n".format( atrNuevo ) )
                    archivoLOG.write("     {} \n".format(sorted(listaValores) ) )
                    archivoLOG.write(" \n")
                if atrNuevo != atributosConValoresNoDominio[i_n] and i_n > 0:
                    archivoLOG.write(" Atributo donde existen discrepancias : {} \n".format( atrNuevo ) )
                    archivoLOG.write("     {} \n".format(sorted(listaValores) ) )
                    atrNuevo = atributosConValoresNoDominio[i_n]
                    listaValores= []
                else:
                    listaValores.append(valoresNoDominio[i_n])
        ahora = datetime.now()
        archivoLOG.write(" # Fin: {}  // tiempo de ejecución total: {} min \n".format( ahora.strftime("%m/%d/%Y, %H:%M:%S"), (time.time() - start_time_total)/60) )      
        archivoLOG.close() 
        
        del jsGJSON
        del valoresNoDominio
        del listaValores
        del atributosConValoresNoDominio
        gc.collect()  

        return 0


