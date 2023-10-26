import json, os, shutil, codecs, time, gc, sys
from logging import raiseExceptions
try:
    import psycopg2
except:
    import psycopg2cffi as psycopg2
import numpy as np
from pathlib import Path
from datetime import datetime
from pyexcel_ods3 import get_data
from .terminal_color import *


class mapeo_PG_GJSON:
    def __init__(self,path_jsonConex,path_hojaCalculoMApeo,path_carpetaSalida,proveedor):
        self.path_jsonConex = path_jsonConex
        self.path_hojaCalculoMApeo = path_hojaCalculoMApeo
        self.path_carpetaSalida = path_carpetaSalida
        self.proveedor = proveedor

        # Param predefinidos
        self.sobreescribirGeojson = False
        self.renombrarSiError = False
        self.verbose = False
        self.verboseRecorrido = 100
        self.EPSG_salida = 4258
        self.geojsonSalida = ['*']
        self.numeroDecimales = 7
        self.partirClaseEntidad = False
        self.partirClaseEntidadCantidad = 1000
        self.tipoPartirClaseEntidad = 1
        self.paginarSentenciaSQL = False
        self.limiteCantidad = 1000
        self.partirGeojson = False

        # Param parámetros pruebas (debe ir con paginarSentenciaSQL = False)
        self.limit = False
        
        # Param orden columas hoja de cálculo (comienza en 0)
        self.aliasBBDD = 0
        self.tablaOrigen = 1
        self.filtro = 2
        self.claseDeEntidad = 3
        self.atributoOrigen = 4
        self.valorOrigen = 5
        self.atributoDestino = 6
        self.valorDestino = 7
        self.crearCentroide = 8
        self.procesar = 9
        self.observaciones = 10

    def sizeof_fmt(self, num, suffix='B'):
            ''' by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified'''
            for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
                if abs(num) < 1024.0:
                    return "%3.1f %s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f %s%s" % (num, 'Yi', suffix)

    def tipoPartirClaseEntidadINFO(self):
        dictt ={
                '1':'por número de entidades',
                '2': 'por tamaño en bytes'
                }
        return dictt

    def EntidadA_GJSON(self, geojson, nombreSalida):
        listaGeojsonCreados = os.listdir(self.path_carpetaSalida)
        # print(listaGeojsonCreados)
        # print(nombreSalida+'.geojson')

        if self.partirGeojson == True:
            geojsonCount = str(len([x for x in listaGeojsonCreados if nombreSalida+'.geojson' in x])+1)
            archivoGeoJSON = codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson_' + geojsonCount, "w", "utf-8")
            archivoGeoJSON.write(json.dumps(geojson, ensure_ascii=False))
            archivoGeoJSON.close()

        elif not nombreSalida+'.geojson' in listaGeojsonCreados and self.partirGeojson == False:
            archivoGeoJSON = codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson', "w", "utf-8")
            archivoGeoJSON.write(json.dumps(geojson, ensure_ascii=False))
            archivoGeoJSON.close()

        else:
            print('- - -')
            print('leyendo archivo')
            # archivoGeoJSON = codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson', "r", "utf-8")
            print('- - -')
            print('cargando')
            # jsonGJSON = json.loads(archivoGeoJSON.read())
            jsonGJSON = json.load( codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson', "r", "utf-8") )
            # archivoGeoJSON.close()
            print('- - -')
            print('archivo cargado')
            jsonGJSON['features'].extend(geojson['features'])
            print('- - -')
            print('entidades metidas')
            # archivoGeoJSON.seek(0)
            # print('- - -')
            # print('seek0')

            # archivoGeoJSON = codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson', "r+", "utf-8")
            # dumpFile = json.dumps(jsonGJSON, ensure_ascii=False)
            # print('- - -')
            # print('dump')
            archivoGeoJSON = codecs.open(self.path_carpetaSalida+'/'+nombreSalida+'.geojson', "w", "utf-8")
            json.dump(jsonGJSON, archivoGeoJSON, ensure_ascii=False)
            archivoGeoJSON.close()
            print('- - -')
            print('archivo escrito')

            # for name, size in sorted(((name, sys.getsizeof(value)) for name, value in locals().items()),
            #                     key= lambda x: -x[1])[:10]:
            #     print("{:>30}: {:>8}".format(name, self.sizeof_fmt(size)))
            del jsonGJSON
            # del dumpFile
            

        del geojson
        del archivoGeoJSON
        del listaGeojsonCreados
        gc.collect()
        
        if self.verbose:
            print('')
            print('Geojson exportado en carpeta: ',nombreSalida)
        return 0
    
    def crearCarpeta(self, sobrescribir = False):
        if sobrescribir == False:
            Path(self.path_carpetaSalida).mkdir(parents=True, exist_ok=True)

        elif sobrescribir == True:
            try:
                listaGeojsonCreados = os.listdir(self.path_carpetaSalida)
                for i in listaGeojsonCreados:
                    # if '.geojson' in i:
                    #     os.remove(self.path_carpetaSalida+'/'+i) 
                    os.remove(self.path_carpetaSalida+'/'+i) 
            except FileNotFoundError:
                Path(self.path_carpetaSalida).mkdir(parents=True, exist_ok=True)

        else:
            pass
             
        return 0

    def procesoMapeo(self):
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
        archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
        archivoLOG.write(" ### --- Log del proceso de mapeo y transformación de PG a Geojson --- ### \n")
        archivoLOG.write(" # ----------------------------------------------------------------------- \n") 
        archivoLOG.write(" \n")
        archivoLOG.write(" # Inicio: {} \n".format( ahora.strftime("%m/%d/%Y, %H:%M:%S")) )
        archivoLOG.write(" \n")
        archivoLOG.close()

        # Coge los parámetros de conexión a PG
        jsonConString = open(self.path_jsonConex, "r")
        jsonCon = json.loads(jsonConString.read())
        jsonConString.close()

        #Coge para el proceso la primera hoja
        hojaCalMApeo = get_data(self.path_hojaCalculoMApeo)
        for i in hojaCalMApeo:
            hoja1 = i
            break

        ordenesMApeo = hojaCalMApeo[hoja1]
        ordenesMApeo = list(filter(None, ordenesMApeo))
        
        # obtener valores únicos del grupo Alias-Tabla-Filtro-GeojsonSalida
        ordenesMApeoUnicosSET =  set(tuple([row[self.aliasBBDD],row[self.tablaOrigen],row[self.filtro],row[self.claseDeEntidad]] ) for row in ordenesMApeo[1:])
        ordenesMApeoUnicosSET = list(filter(None, ordenesMApeoUnicosSET))

        ordenesMApeoUnicos = []
        for i in ordenesMApeoUnicosSET:
            for j in ordenesMApeo:
                if i[0] == j[self.aliasBBDD] and i[1] == j[self.tablaOrigen] and i[2] == j[self.filtro] and i[3] == j[self.claseDeEntidad]:
                    if j[self.procesar].replace(' ','') == 'F':
                        continue
                    if not j[self.claseDeEntidad] in self.geojsonSalida:
                        if '*' in self.geojsonSalida:
                            pass
                        else:
                            continue
                    ordenesMApeoUnicos.append(j)
                    break
        
        atributosOrdenesMapeoUnicos = []
        for i in ordenesMApeoUnicos:
            tmp_list = []
            for j in ordenesMApeo:
                if i[0] == j[self.aliasBBDD] and i[1] == j[self.tablaOrigen] and i[2] == j[self.filtro] and i[3] == j[self.claseDeEntidad]:
                    if j[self.procesar].replace(' ','') == 'F':
                        continue
                    if not j[self.claseDeEntidad] in self.geojsonSalida:
                        if '*' in self.geojsonSalida:
                            pass
                        else:
                            continue
                    
                    if j[self.atributoOrigen].replace(" ","")!= "":
                        if len(j[self.atributoOrigen].split(',')) > 1 :
                            for t in j[self.atributoOrigen].split(','):
                                tmp_list.append(t.replace(' ',''))
                        else:
                            tmp_list.append(j[self.atributoOrigen])

            atributosOrdenesMapeoUnicos.append(tmp_list)
            tmp_list = []
        
        
        if self.sobreescribirGeojson:
            listaGeojsonCreados = os.listdir(self.path_carpetaSalida)
            listaGeojsonCreados = [ archivo.split('.')[0] for archivo in listaGeojsonCreados if 'geojson' in archivo ]
            for j in ordenesMApeoUnicos:
                if j[self.claseDeEntidad] in listaGeojsonCreados:
                    try:
                        geojson2Delete = [x for x in os.listdir(self.path_carpetaSalida) if j[self.claseDeEntidad]+'.geojson' in x]
                        for archivoDelete in geojson2Delete:
                            os.remove(self.path_carpetaSalida+'/'+archivoDelete) 
                    except Exception as e:
                        pass

        archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
        archivoLOG.write(" # Órdenes de conexión únicas: {} \n".format(len(ordenesMApeoUnicos)) )
        archivoLOG.write(" - - - - - - - - - - - - - - - - -\n" )
        archivoLOG.write("  \n" )
        archivoLOG.write("  \n" )
        archivoLOG.close()

        if self.verbose:
            print("  \n" )
            print(" # Órdenes de conexión únicas: {} \n".format(len(ordenesMApeoUnicos)))
            print("  \n" )


        #lista de geojson que han dado error
        listaGeojsonError = []
        stringError = '0_error_'

        for id_ordenUnico,ordenUnico in enumerate(ordenesMApeoUnicos):
            try:
                start_time = time.time()
                # if not ordenUnico[self.claseDeEntidad] in self.geojsonSalida:
                #     if '*' in self.geojsonSalida:
                #         pass
                #     else:
                #         continue
                
                if self.verbose:
                    print(id_ordenUnico+1,'orden único ->',ordenUnico[self.aliasBBDD], ordenUnico[self.tablaOrigen], ordenUnico[self.filtro], ordenUnico[self.claseDeEntidad] )

                archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                archivoLOG.write(" ######## {} ######## \n".format(ordenUnico[self.claseDeEntidad]))
                archivoLOG.write(" {}º Orden de conexión: {} {} {} {} \n".format(id_ordenUnico+1, ordenUnico[self.aliasBBDD], ordenUnico[self.tablaOrigen], ordenUnico[self.filtro], ordenUnico[self.claseDeEntidad]) )
                archivoLOG.write(" \n")
                archivoLOG.close()

                jsonConn = jsonCon[ordenUnico[self.aliasBBDD]]
                conn = psycopg2.connect( database=jsonConn['bbdd'], user = jsonConn['usuario'], password = jsonConn['contrasena'], host = jsonConn['ip'], port = jsonConn['puerto'] )
                cur = conn.cursor()
            
                sentenciaSQL = """ SELECT column_name,data_type FROM information_schema.columns WHERE table_schema = '{}' AND table_name= '{}' """.format(jsonConn['esquema'],ordenUnico[self.tablaOrigen])
                cur.execute(sentenciaSQL)
                atributos_tipo = cur.fetchall()
                atributos = ''
                atributos_tipo_sentencia=[]
                atributos_array = []
                for i in atributos_tipo:
                    if i[1] == 'USER-DEFINED':
                        sentenciaSQL = """ SELECT ST_SRID({}) FROM "{}"."{}" limit 1 """.format(i[0],jsonConn['esquema'],ordenUnico[self.tablaOrigen])
                        cur.execute(sentenciaSQL)
                        EPSG_entrada = cur.fetchall()[0][0]
                        crearCentroide = ordenUnico[self.crearCentroide].replace(' ','')
                        
                        decimal = '0.'
                        
                        for d in range(self.numeroDecimales-1):
                          decimal += '0'
                        decimal += '1'
                        
                        # print('decimales entrada: ',self.numeroDecimales)
                        # print('decimales salida: ',decimal)
                                                
                        if crearCentroide == 'F':
                            # atributos = atributos + 'ST_AsGeoJSON( ST_Transform('+ i[0] + ',' + str(EPSG_entrada) + ',' + str(self.EPSG_salida)+ ')), '
                            atributos = atributos + 'ST_AsGeoJSON( ST_SnapToGrid ( ST_Force2D( ST_Transform('+ i[0] + ',' + str(self.EPSG_salida) + ') ), ' + decimal + ') ), '
                            atributos_array.append('geom')

                        elif crearCentroide == 'T':
                            atributos = atributos + 'ST_AsGeoJSON( ST_SnapToGrid ( ST_Force2D( ST_Centroid( ST_Transform('+ i[0] + ',' + str(self.EPSG_salida) + ') ) ), ' + decimal + ') ), '
                            atributos_array.append('geom')

                        else:
                            print(Base.FAIL," # ¡Error! Valor para crearCentroide no permitido {} \n".format(crearCentroide) , Base.END)
                            archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                            archivoLOG.write(" # ¡Error! Valor para crearCentroide no permitido {} \n".format(crearCentroide) )
                            archivoLOG.close()
                            # raise Exception('Valor para crearCentroide no permitido')
                        
                        atributos_tipo_sentencia.append(i)

                    else:
                        if i[0] in atributosOrdenesMapeoUnicos[id_ordenUnico]:
                            atributos = atributos + i[0] + ', '
                            atributos_tipo_sentencia.append(i)
                            atributos_array.append(i[0])
                atributos = atributos[:-2]             

                banderaCortarWhile = 0
                offset = 0
                while banderaCortarWhile == 0:
                    if self.paginarSentenciaSQL == False:
                        banderaCortarWhile = 1
                    elif self.paginarSentenciaSQL == True:
                        pass
                    else:
                        raise Exception('Valor para paginarSentenciaSQL no permitido')
        
                    if ordenUnico[self.filtro].replace(' ','') == '':
                        where = ordenUnico[self.filtro]
                        sentenciaSQL = """ SELECT {atributos} FROM "{esquema}"."{tabla}" """.format(atributos=atributos, esquema=jsonConn['esquema'], tabla=ordenUnico[self.tablaOrigen])

                    else:
                        where = ordenUnico[self.filtro].replace('”','"').replace("“",'"').replace("‘","'").replace("’","'").replace("\\","")
                        sentenciaSQL = """ SELECT {atributos} FROM "{esquema}"."{tabla}" WHERE {where}  """.format(atributos=atributos, esquema=jsonConn['esquema'], tabla=ordenUnico[self.tablaOrigen], where=where)
                    
                    if self.limit and not self.paginarSentenciaSQL:
                        sentenciaSQL = sentenciaSQL + " limit {}".format(self.limiteCantidad)
                    elif self.limit and self.paginarSentenciaSQL:
                        sentenciaSQL = sentenciaSQL + " limit {}  offset {}".format(self.limiteCantidad,offset)
                        offset += self.limiteCantidad
                        banderaCortarWhile = 1
                    elif not self.limit and self.paginarSentenciaSQL:
                        conn = psycopg2.connect( database=jsonConn['bbdd'], user = jsonConn['usuario'], password = jsonConn['contrasena'], host = jsonConn['ip'], port = jsonConn['puerto'] )
                        cur = conn.cursor()
                        sentenciaSQL = sentenciaSQL + " limit {}  offset {}".format(self.limiteCantidad,offset)
                        offset += self.limiteCantidad
                    else:
                        pass

                    if self.verbose:
                        print('Sentencia SQL: ',sentenciaSQL)

                    archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                    archivoLOG.write(" Sentencia SQL: {} \n".format(sentenciaSQL) )
                    archivoLOG.close()

                    cur.execute(sentenciaSQL)
                    valores = cur.fetchall()
                    conn.close()

                    gjson = {
                                "type": "FeatureCollection",
                                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::{}".format(self.EPSG_salida) } },
                                "features": []
                                }

                    longValores = len(valores)
                    if longValores == 0:
                        banderaCortarWhile = 1
                        break
                    elif longValores < self.limiteCantidad:
                        banderaCortarWhile = 1
                    
                    archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                    archivoLOG.write(" Número de entidades: {} \n".format(longValores) )
                    archivoLOG.write(" \n")
                    archivoLOG.close()

                    dicOrdenesCantidad= {}
                    listOrdenes = []

                    entidadesNoProcesadas = 0

                    # valores = np.array(valores)
                    # for id_fila,fila in enumerate(valores):
                    valores_iter = len(valores)
                    for id_fila in range(valores_iter):
                        fila = valores[id_fila]
                        ordenesPorRegistro = 0

                        if self.verbose and ( (id_fila+1) % self.verboseRecorrido == 0 or id_fila+1 == longValores ):
                            print('Recorrido de la tabla: ',id_fila+1,'/', longValores, '///  tiempo ejecución: ',int(time.time() - start_time),' seg', end ='\r')
                            if id_fila+1 == longValores :
                                print('Fin recorrido de la tabla: ',id_fila+1,'/', longValores, ' ///  tiempo ejecución: ',int(time.time() - start_time),' seg')

                        entidad =  {
                                "type": "Feature",
                                "properties": {},
                                "geometry": {}
                                }
                        # fila = np.array(fila)
                        # for idValor,valor in enumerate(fila):
                        fila_iter = len(fila)
                        for idValor in range(fila_iter):
                            valor = fila[idValor]

                            if atributos_tipo_sentencia[idValor][1] == 'USER-DEFINED':
                                valorJS = json.loads(valor)
                                entidad['geometry'] = valorJS

                                # pass

                                # if valor == None:
                                #     continue
                                # # Modificar los decimales del geojson
                                # valorJS = json.loads(valor)
                                # listaCoordenadas = valorJS['coordinates']
                                # # listaCoordenadas_iter = len(listaCoordenadas)
                                # for i_l,l in enumerate(listaCoordenadas):
                                #     # l = listaCoordenadas[i_l]
                                #     try:
                                #         np_array = np.array(l)
                                #         np_array_round = np.round( np_array ,self.numeroDecimales)
                                #         listaCoordenadas[i_l] = np_array_round.tolist()
                                #     except TypeError:
                                #         j_list=[]
                                #         for j in l:
                                #             j = np.round( j ,self.numeroDecimales)
                                #             j_list.append(j.tolist())
                                #         listaCoordenadas[i_l] = j_list
                                    

                                # valorJS['coordinates'] = listaCoordenadas
                                # entidad['geometry'] = valorJS
                                # # del np_array
                                # # del np_array_round
                                # # del valorJS
                                # # gc.collect()
                                

                            else:
                                atributoOrigenPG = atributos_tipo_sentencia[idValor][0]
                                if valor in  [None,'']:
                                    valorOrigenPG = ''
                                else:
                                    if str(type(valor)) == "<class 'decimal.Decimal'>":
                                        valor = float(valor)
                                    valorOrigenPG = valor

                                

                                ordenesMApeo_iter = len(ordenesMApeo)
                                for id_orden in range(ordenesMApeo_iter):
                                    orden = ordenesMApeo[id_orden]
                                    # Condicionales de optimización del proceso
                                    if orden[self.procesar].replace(' ','') == 'F':
                                        continue
                                    if not ordenUnico[self.aliasBBDD] == orden[self.aliasBBDD]:
                                        continue
                                    if not ordenUnico[self.tablaOrigen] == orden[self.tablaOrigen]:
                                        continue
                                    if not ordenUnico[self.filtro] == orden[self.filtro]:
                                        continue
                                    if not ordenUnico[self.claseDeEntidad] == orden[self.claseDeEntidad]:
                                        continue

                                    #Preparación de condicionales "especiales"
                                    concatenaAtributos = 0
                                    if len(orden[self.atributoOrigen].split(',')) > 1 :
                                        concatenaAtributos = 1
                                        listaAtributosConcatena = []
                                        listaValoresConcatena = []
                                        for t in orden[self.atributoOrigen].split(','):
                                            listaAtributosConcatena.append(t.replace(' ',''))

                                        for l in listaAtributosConcatena:
                                            for idValor2,valor2 in enumerate(fila):
                                                if l == atributos_array[idValor2].replace(' ',''):
                                                    listaValoresConcatena.append(valor2)
                                                    break

                                    #Condicionales de los mapeos de atributo y valor
                                    banderaLog = 1
                                    
                                    if atributoOrigenPG == orden[self.atributoOrigen] and str(type(valorOrigenPG)) == "<class 'str'>":
                                        orden[self.valorOrigen] = str(orden[self.valorOrigen])
                                        # print(atributoOrigenPG,' ',orden[self.atributoOrigen], ' ', valorOrigenPG,' ',str(type(valorOrigenPG)),' ', orden[self.valorOrigen],' ',str(type(orden[self.valorOrigen])))

                                    if atributoOrigenPG == orden[self.atributoOrigen] and valorOrigenPG == orden[self.valorOrigen]:
                                        entidad['properties'][ orden[self.atributoDestino] ] = orden[self.valorDestino]

                                    elif str(orden[self.atributoOrigen]).replace(" ","") == '' and  str(orden[self.valorOrigen]).replace(" ","") == '':
                                        entidad['properties'][ orden[self.atributoDestino] ] = orden[self.valorDestino]
                                    
                                    elif atributoOrigenPG == orden[self.atributoOrigen] and  str(orden[self.valorOrigen]).replace(" ","") == '*' and  str(orden[self.valorDestino]).replace(" ","") == '*':
                                        entidad['properties'][ orden[self.atributoDestino] ] = valorOrigenPG
                                    
                                    elif atributoOrigenPG == orden[self.atributoOrigen] and  str(orden[self.valorOrigen]).replace(" ","") == '*' and  str(orden[self.valorDestino]).replace(" ","") != '*' :
                                        if not orden[self.atributoDestino] in entidad['properties']:
                                            entidad['properties'][ orden[self.atributoDestino]] = orden[self.valorDestino]
                                    
                                    elif concatenaAtributos == 1:
                                        concatenaAtributos = 0   
                                        cadenaTexto = orden[self.valorDestino].replace('”',"'").replace("“","'").replace("‘","'").replace("’","'").replace("\\","")
                                        listaCadenaTexto = cadenaTexto.replace("'","").split('+')
                                        listaCadenaTexto = cadenaTexto.split('+')
                                        
                                        valorAtributoConcatenado = ''
                                        for m in listaCadenaTexto:    
                                            if m.replace("'","").isspace() == False:
                                                for i_n, n in enumerate(listaAtributosConcatena):
                                                    if m.replace(" ","") == n.replace(" ",""):
                                                        valorAtributoConcatenado = valorAtributoConcatenado + str(listaValoresConcatena[i_n]).replace(" ","")
                                            else:
                                                i_ori = 0
                                                i_final = 0
                                                for i_mm, mm in enumerate(m):
                                                    if mm == ' ' and i_ori == 0 and i_final == 0:
                                                        pass
                                                    elif mm == ' ' and i_ori != 0 and i_final == 0:
                                                        pass
                                                    elif mm == ' ' and i_ori != 0 and i_final != 0:
                                                        break
                                                    elif mm == "'" and i_ori == 0 and i_final == 0:
                                                        i_ori = i_mm
                                                    elif mm == "'" and i_ori != 0 and i_final == 0:
                                                        i_final = i_mm

                                                valorAtributoConcatenado = valorAtributoConcatenado + m[i_ori+1:i_final]
                                        
                                        entidad['properties'][ orden[self.atributoDestino] ] = valorAtributoConcatenado

                                    else:
                                        continue

                                    if banderaLog == 1:
                                        ordenesPorRegistro += 1
                                        banderaLog = 0
                                        if not orden[self.atributoDestino]+': '+str(orden[self.valorDestino])  in listOrdenes:
                                            listOrdenes.append(orden[self.atributoDestino]+': '+str(orden[self.valorDestino]) )
                                            dicOrdenesCantidad[orden[self.atributoDestino]+': '+str(orden[self.valorDestino]) ] = 1
                                        else:
                                            dicOrdenesCantidad[orden[self.atributoDestino]+': '+str(orden[self.valorDestino]) ] = dicOrdenesCantidad[orden[self.atributoDestino]+': '+str(orden[self.valorDestino]) ]+1

                                # entidad['properties'][ atributoOrigenPG ] = valorOrigenPG

                        gjson["features"].append(entidad)

                        if ordenesPorRegistro == 0:
                            entidadesNoProcesadas += 1
                        else:
                            entidadesNoProcesadas = 0

                        

                        if self.partirClaseEntidad == True:

                            if id_fila+1 == longValores:
                                del valores
                            
                            if int(self.tipoPartirClaseEntidad) == 1:
                                if (id_fila+1) % self.partirClaseEntidadCantidad == 0 or id_fila+1 == longValores:
                                    # del np_array
                                    # del np_array_round
                                    # del listaCoordenadas
                                    # del valorJS
                                    # gc.collect()
                                    
                                    self.EntidadA_GJSON(geojson=gjson, nombreSalida = ordenUnico[self.claseDeEntidad])
                                    gjson = {
                                        "type": "FeatureCollection",
                                        "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::{}".format(self.EPSG_salida) } },
                                        "features": []
                                    }

                            elif int(self.tipoPartirClaseEntidad) == 2:
                                tamannoGJSON = sys.getsizeof(gjson["features"])
                                if tamannoGJSON >= self.partirClaseEntidadCantidad or  id_fila+1 == longValores:
                                    # del np_array
                                    # del np_array_round
                                    # del listaCoordenadas
                                    # del valorJS
                                    # gc.collect()
                                    
                                    self.EntidadA_GJSON(geojson=gjson, nombreSalida = ordenUnico[self.claseDeEntidad])
                                    gjson = {
                                        "type": "FeatureCollection",
                                        "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::{}".format(self.EPSG_salida) } },
                                        "features": []
                                    }
                            else:
                                print(Base.FAIL,'ERROR: valor no permitido. Comprobar tipoPartirClaseEntidadINFO()', Base.END)
                                raise Exception('ERROR: valor no permitido. Comprobar tipoPartirClaseEntidadINFO()')
        
                    if self.verbose:
                        print()
                        print('Geojson creado en memoria')

                    archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                    archivoLOG.write(" listado de mapeos realizados: \n")
                    for j in dicOrdenesCantidad:
                        archivoLOG.write(" {} --> registros: {} \n".format(j, dicOrdenesCantidad[j] ))
                    archivoLOG.write(" \n")
                    
                    if self.verbose:
                        print('entidadesNoProcesadas: ',entidadesNoProcesadas)

                    archivoLOG.write(" Entidades no procesadas: {}\n".format(int(entidadesNoProcesadas)) )
                    archivoLOG.write(" tiempo de ejecución: {} seg\n".format( (time.time() - start_time) ))
                    archivoLOG.write(" --------------------------------------------------------------- \n")
                    archivoLOG.write(" \n")

                    archivoLOG.close()

                    if self.partirClaseEntidad == False:
                        # del np_array
                        # del np_array_round
                        # del valorJS
                        # del listaCoordenadas
                        del valores
                        gc.collect()

                        self.EntidadA_GJSON(geojson=gjson, nombreSalida = ordenUnico[self.claseDeEntidad])

                    del dicOrdenesCantidad
                    del listOrdenes
                    del gjson
                    gc.collect()

            except Exception as e:
                print(Base.FAIL,'ERRORRRRR: ',e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(Base.END)
                if not ordenUnico[self.claseDeEntidad] in listaGeojsonError:
                    listaGeojsonError.append(ordenUnico[self.claseDeEntidad])
                archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
                archivoLOG.write(" ¡¡¡¡ ERROR !!!!: {} \n".format( e ) )
                archivoLOG.write(" --------------------------------------------------------------- \n")
                archivoLOG.write(" \n")
                archivoLOG.close()


        listaGeojsonCreados = os.listdir(self.path_carpetaSalida)

        nGjson=0
        for gj in listaGeojsonCreados:
            if '.geojson' in gj:
                nGjson +=1

            if self.renombrarSiError:
                if gj.split('.')[0] in listaGeojsonError:
                    try:
                        os.rename(self.path_carpetaSalida+'/'+gj, self.path_carpetaSalida+'/'+stringError+gj)
                    except FileExistsError:
                        os.remove(self.path_carpetaSalida+'/'+stringError+gj)
                        os.rename(self.path_carpetaSalida+'/'+gj, self.path_carpetaSalida+'/'+stringError+gj)



        ahora = datetime.now()
        archivoLOG = codecs.open(self.path_carpetaSalida+'/'+subNombre +'_ToGeojson_'+self.proveedor+'.log', "a","utf-8")
        archivoLOG.write(" # Número de Geojsons creados: {} \n".format( nGjson ) )
        archivoLOG.write(" # Fin: {}  // tiempo de ejecución total: {} Horas \n".format( ahora.strftime("%m/%d/%Y, %H:%M:%S"), (time.time() - start_time_total)/3600) )
        archivoLOG.close()
        return 0


