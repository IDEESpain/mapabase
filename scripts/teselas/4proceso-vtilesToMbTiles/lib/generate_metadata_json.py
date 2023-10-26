import os
import pandas
import json


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

def check_different_elements(lst):

    if len(set(lst)) == 1:
        return lst[0]
    else:
        return list(set(lst))

def main():

    teselas_folder="/var/MVT_MapaBaseXYZ/tmp/"
    dest_folder = "/var/MVT_MapaBaseXYZ/teselas/"
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

            df = pandas.DataFrame.from_dict(pandas.json_normalize(json_dict), orient='columns')
            df_list.append(df)

    # DataFrame con todos los JSON 
    df_final = pandas.concat(df_list)

    #print(df_final["minzoom"])

    # Listas con las columnas de los dataframe

    # set_fields = set([x for x in df_final["fields"]])

    # set_fields = set([x for x in df_final["fields"]])

    lst_minzoom = [int(x) for x in df_final['minzoom'].to_list()]
    lst_maxzoom = [int(x) for x in df_final['maxzoom'].to_list()]

    lst_center = [(x) for x in df_final['center']]
    lst_bounds = [(x) for x in df_final['bounds'].to_list()]
    lst_json = [(y,json.loads(x)) for x,y in zip(df_final['json'].to_list(),df_final['minzoom'])]

    center_tuple_lst = []
    bounds_tuple_lst = []

    # Descompone las celdas de los DataFrame para obtener las coordenadas por separado
    for i in range(len(lst_center)):
        center_tuple_lst.append(tuple(lst_center[i].split(',')))

    for i in range(len(lst_bounds)):
        bounds_tuple_lst.append(tuple(lst_bounds[i].split(',')))

    # Diccionario para el JSON de salida
    dic_output_json = {}

    dic_output_json['id'] = "mapabase_cnig"#self.check_different_elements(df_final['name'].to_list())
    dic_output_json['name'] = "mapabase_cnig"
    dic_output_json['basename'] = "mapabase_cnig"
    dic_output_json['attribution'] = "url cnig"
    dic_output_json['description'] = 	"Mapa Base de Centro Nacional de Información Geográfica"#self.check_different_elements(df_final['description'].to_list())
    dic_output_json['version'] = 2 #self.check_different_elements(df_final['type'].to_list())
    dic_output_json['minzoom'] = min(lst_minzoom)
    dic_output_json['maxzoom'] = max(lst_maxzoom)
    dic_output_json['center'] = """{0},{1},{2}""".format(compute_max_min_avg(center_tuple_lst, 'avg', 0), compute_max_min_avg(center_tuple_lst, 'avg', 1), compute_max_min_avg(center_tuple_lst, 'min', 2))
    dic_output_json['bounds'] = """{0},{1},{2},{3}""".format(compute_max_min_avg(bounds_tuple_lst, 'avg', 0), compute_max_min_avg(bounds_tuple_lst, 'avg', 1), compute_max_min_avg(bounds_tuple_lst, 'avg', 2), compute_max_min_avg(bounds_tuple_lst, 'avg', 3))
    dic_output_json['type'] = "overlay" #self.check_different_elements(df_final['type'].to_list())
    dic_output_json['format'] = "pbf" #self.check_different_elements(df_final['format'].to_list())
    dic_output_json['fields'] = check_different_elements(df_final['generator'].to_list())

    dic_output_json['tiles'] = ["https://www.ign.es/web/resources/mapa-base-xyz/vt/{z}/{x}/{y}.pbf"]
    dic_output_json['generator'] = check_different_elements(df_final['generator'].to_list())

    capas_totales={}

    tilestats={}

    for zoom,element in lst_json:
        for vector_layer in element["vector_layers"]:
            if vector_layer["id"] not in capas_totales.keys():
                #añadir los atributos de la capa(solo 1 vez ya que son siempre los mismos?)
                elemento={"id":vector_layer['id'],"minzoom":vector_layer['minzoom'],"maxzoom":vector_layer['maxzoom'],"description":vector_layer['description'],"fields":vector_layer['fields']}
                capas_totales[vector_layer["id"]]=elemento
            else:
                if vector_layer["minzoom"] < capas_totales[vector_layer["id"]]["minzoom"]:
                    capas_totales[vector_layer["id"]]["minzoom"]=vector_layer["minzoom"]
                if vector_layer["maxzoom"] > capas_totales[vector_layer["id"]]["maxzoom"]:
                    capas_totales[vector_layer["id"]]["maxzoom"]=vector_layer["maxzoom"]
                lista_atributos_zoom=vector_layer["fields"]
                #print(lista_atributos_zoom)
                lista_atributos_completa=capas_totales[vector_layer["id"]]["fields"]
                capas_totales[vector_layer["id"]]["fields"]={**lista_atributos_completa, **lista_atributos_zoom}
                
        tilestats[zoom]=element["tilestats"]
        #print(element)

    #print(capas_totales)

    list_capas_totales=[]

    for key,value in capas_totales.items():
        list_capas_totales.append(value)

    dic_output_json['vector_layers'] =list_capas_totales

    dic_output_json['tilestats'] =tilestats


    with open(dest_folder+'metadata.json', 'w') as f:
        f.write(json.dumps(dic_output_json))




if __name__=="__main__":
    main()