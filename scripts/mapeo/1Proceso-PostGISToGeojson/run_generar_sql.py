from logging import raiseExceptions
import  os, time, os, json, sys, codecs, gc, random, copy
from datetime import datetime
import html_to_json

def parseTypeScnToSql(typeP):
    if typeP == 'string':
        return "character varying"
    elif typeP == 'int' or typeP == 'integer':
        return "integer"

    return ""

def parseGeomScnToSql(typeP):
    if '_pol' in typeP:
        return "Polygon"
    elif '_lin' in typeP:
        return "Linestring"
    elif '_pto' in typeP:
        return "Point"

    return ""

if __name__ == "__main__":
    
    verbose = False
    # Ruta al directorio en el que se encuentra el repositorio mapabase
    git_carpeta_mapabase_gh_pages = '../../../../mapabase'

    jsonElementos = {}
    elementos = os.listdir(git_carpeta_mapabase_gh_pages+'/elementos')

    print ("Empezamos")
    sqlElements = ""

    for elemento in elementos:
        if elemento != "relacion_alfabetica" and elemento != "no_disponible" and elemento != "relacion_tematica":
            indexHTMLFile = codecs.open(git_carpeta_mapabase_gh_pages+'/elementos/'+elemento+'/index.html', "r", 'UTF-8')
            indexHTMLJSON = html_to_json.convert(indexHTMLFile.read())
            indexHTMLFile.close()
            try:
                comentario_tabla = indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["_values"][0] +" "+ indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["em"][0]["_value"]+" "+indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["_values"][1] + " "+indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["a"][0]["em"][0]["_value"]+indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["_values"][2] +" "+ indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["a"][1]["em"][0]["_value"]+" "+indexHTMLJSON['html'][0]['body'][0]['div'][1]['div'][1]['p'][1]["_values"][3]
            except:
                comentario_tabla = ""


            sqlElements += "\n\nCREATE TABLE public."+elemento + " ("
            print(elemento)
            for ind_line, line in enumerate(indexHTMLJSON['html'][0]['body'][0]['div']):
                if 'Atributos y dominios de valores' in json.dumps(line):
                    for divParentElement in line['div']:
                        if 'table' in json.dumps(divParentElement):
                            comentarios = {}
                            previous_attr = None
                            is_attribute = True
                            sqlElements += "\n\tthe_geom public.geometry("+parseGeomScnToSql(elemento)+",25830),"
                            for tdElement in divParentElement['table'][0]['tbody'][0]['tr']:
                                check_flag = False

                                
                                if 'code' in str(tdElement['td'][0])  and tdElement['td'][0]['code'][0]:
                                    attr = tdElement['td'][0]['code'][0]['_value']
                                    if previous_attr != attr:
                                        comentarios[attr] = []
                                        previous_attr = attr
                                    
                                    #print(tdElement['td'][0])
                                    if not is_attribute:
                                        sqlElements =sqlElements[:-1]
                                        sqlElements += ')),'
                                        is_attribute = True
                                    if '_value' in tdElement['td'][0]['code'][0]: 
                                        type_data = parseTypeScnToSql(tdElement['td'][1]['_value'])
                                        sqlElements += "\n\t" + attr + " " + type_data
                                        # print(tdElement['td'][2])
                                        if tdElement['td'][2] == {}:
                                            sqlElements += " CHECK ("+attr+" in ("

                                            if elemento == 'altimetria_pto' and attr=='clase':
                                                sqlElements += "'punto_acotado','punto_elevado')),"
                                                is_attribute = True
                                        else:
                                            sqlElements += ","

                                else:
                                    
                                    is_attribute = False
                                    if type_data == 'integer':
                                        sqlElements += tdElement['td'][2]['_value']+ ','
                                    else:
                                        # print(tdElement['td'][2]['_value'])
                                        sqlElements += '\'' + tdElement['td'][2]['_value']+ '\','

                                try:
                                    comentarios[attr].append(""+tdElement['td'][2]['_value']+":"+tdElement['td'][-1]['_value'])
                                except:
                                    pass
                            if not is_attribute:
                                sqlElements =sqlElements[:-1]
                                sqlElements += '))'
                                is_attribute = True

                            if sqlElements[-1:]==",":
                                sqlElements = sqlElements[:-1]
                                


                            sqlElements += ');'

                            sqlElements += '\n'
                            sqlElements += 'ALTER TABLE public.'+elemento+' OWNER TO postgres;'
                            sqlElements += '\n'
                            sqlElements += "CREATE INDEX sidx_"+elemento+"_the_geom ON public."+elemento+" USING gist (the_geom);"
                            sqlElements += '\n'
                            sqlElements += "COMMENT ON TABLE "+elemento+ " IS '"+comentario_tabla+"';"
                            sqlElements += '\n'

                            for columna,comentario_list in comentarios.items():
                                comentario = "\t".join(comentario_list)
                                 

                                sqlElements += "COMMENT ON COLUMN "+elemento+"."+columna+ " IS '"+comentario+"';"
                                sqlElements += '\n'

                            # print(comentarios)

    archivoSQL =codecs.open("./salida.sql", "w", "utf-8")
    archivoSQL.write(sqlElements)
    archivoSQL.close()


