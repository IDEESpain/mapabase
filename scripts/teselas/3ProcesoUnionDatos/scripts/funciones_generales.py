import numpy as np
import glob
import json
import geopandas as gpd
import pandas as pd
import os
import pathlib
import geopandas
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.geometry import box
from shapely.validation import make_valid

f = open ("./config.json")

var_dict=json.load(f)

#CAMBIADO
def check_nivel(nivel,cod,elemento):

    if nivel=='local':
        carpeta_busqueda="path_productores_municipios"
    elif nivel=='regional':
        carpeta_busqueda="path_productores_com_aut"
    elif nivel=='local_generados':
        carpeta_busqueda="path_generados_municipios"
    elif nivel=='regional_generados':
        carpeta_busqueda="path_generados_comunidades_recorte"
    elif nivel=='regional_generados_union':
        carpeta_busqueda="path_generados_comunidades_municipios"
    else:
        carpeta_busqueda="path_productores_nacional"

    path_to_file=f"{var_dict[carpeta_busqueda]}{cod}/{elemento}.vrt"

    listaElementos=glob.glob(path_to_file)
    return listaElementos

#CAMBIADO
def generarLimite(cod,cod_comunidad="00"):

    carpeta_destino=var_dict["path_generados_municipios"]

    spain=geopandas.read_file(f"{var_dict['aux_municipios_file']}")

    path = f"{carpeta_destino}{cod}"
    #print(path)

    isExist = os.path.exists(path)

    if not isExist:
        os.makedirs(path)

    path = f"{carpeta_destino}{cod}/{cod}.fgb".format(carpeta_destino,cod,cod)

    spain[spain['codigo'].str.slice(-5)==cod].to_file(path, driver="FlatGeobuf",crs="EPSG:4258")


    mascara_comunidad=geopandas.read_file(path)

    mascara_comunidad=mascara_comunidad.buffer(var_dict["buffer"])

    mascara_comunidad.to_file(path, driver="FlatGeobuf",crs="EPSG:4258")

    mascara_comunidad=geopandas.read_file(path)

    return mascara_comunidad

#CAMBIADO
def do_clip(nivel,path,coordinates,clase):
    if nivel=='regional':
        carpeta_busqueda="path_productores_com_aut"
    else:
        carpeta_busqueda="path_productores_nacional"
    
    split_path=path.split("/")

    #si la ruta es relativa tendremos que cambiar desde la carpeta interna de generados a la carpeta de productores
    if not os.path.isabs(var_dict[carpeta_busqueda]):
            path_from_generadores_to_productores=var_dict["path_from_inside_generados_to_productores"]

            path_to_father_vrt=f"{path_from_generadores_to_productores}{split_path[-3]}/{split_path[-2]}/{split_path[-1]}"
    else:
            path_to_father_vrt=f"{var_dict[carpeta_busqueda]}{split_path[-2]}/{split_path[-1]}"

    #print(split_path)

    vrt="""
        <OGRVRTDataSource>
            <OGRVRTUnionLayer name="{}">
            {}
            </OGRVRTUnionLayer>
        </OGRVRTDataSource>
    """

    layer="""<OGRVRTLayer name="{}">
            <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
            <SrcRegion clip="true">{}</SrcRegion>
        </OGRVRTLayer>"""

    layers=""""""

    for polygon in coordinates:
        layers+=layer.format(clase,path_to_father_vrt,polygon)
    
    vrt=vrt.format(clase,layers)

    return vrt

#CAMBIADO
def vrt_comunidad_autonoma(clase,lista_municipios):

    vrt="""
        <OGRVRTDataSource>
            <OGRVRTUnionLayer name="{}">
            {}
            </OGRVRTUnionLayer>
        </OGRVRTDataSource>
    """

    layer="""<OGRVRTLayer name="{}">
            <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
        </OGRVRTLayer>"""

    layers=""""""

    for municipio,path in lista_municipios:

        split_path=path.split("/")

        #si la ruta es relativa tendremos que cambiar desde la carpeta interna de generados a la carpeta de productores
        if not os.path.isabs(path):
                path_from_generadores_to_productores=var_dict["path_from_inside_generados_com_aut_to_generados_municipios"]

                path_to_father_vrt=f"{path_from_generadores_to_productores}{split_path[-2]}/{split_path[-1]}"
        else:
                path_to_father_vrt=f"{path}"

        
        layers+=layer.format(clase,path_to_father_vrt)

    return vrt.format(clase,layers)

#CAMBIADO
def vrt_nacional(clase,lista_comunidades, comunidades=True):

    vrt="""
        <OGRVRTDataSource>
            <OGRVRTUnionLayer name="{}">
            {}
            </OGRVRTUnionLayer>
        </OGRVRTDataSource>
    """

    layer="""<OGRVRTLayer name="{}">
            <SrcDataSource relativeToVRT="1">{}</SrcDataSource>
        </OGRVRTLayer>"""

    layers=""""""

    for comunidad,path in lista_comunidades:
        split_path=path.split("/")


        #si la ruta es relativa tendremos que cambiar desde la carpeta interna de generados a la carpeta de productores
        if not os.path.isabs(path):
                if comunidades:
                    path_from_nacional_to_com_aut=var_dict["path_from_inside_generados_nacional_to_generados_com_aut"]
                    path_to_father_vrt=f"{path_from_nacional_to_com_aut}{split_path[-2]}/{split_path[-1]}"
                else:
                    path_from_nacional_to_com_aut=var_dict["path_from_inside_generados_nacional_to_generados_com_aut"]
                    path_to_father_vrt=f"{path_from_nacional_to_com_aut}{split_path[-2]}/{split_path[-1]}"
        else:
                path_to_father_vrt=f"{path}"
        layers+=layer.format(clase,path_to_father_vrt)

    return vrt.format(clase,layers)
     
#CAMBIADO
def write_vrt(vrt,cod,elemento,is_recorte=False,carpeta="path_generados_municipios"):

    recorte=""
    if is_recorte:
        recorte='_recorte'

    carpeta_destino=var_dict[carpeta]



    path_to_file=f"{carpeta_destino}{cod}/{elemento}{recorte}.vrt"

    # path="/".join(path_to_file.split("/")[:-1])
    # #print(path)
    # pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    text_file = open(path_to_file, "w+")
    n = text_file.write(vrt)

def search_str(file_path, word):
    with open(file_path, 'r') as file:
        # leer archivo
        content = file.read()
        # buscar string
        if word in content:
            return True
        else:
            return False
        
#NUEVO
def generar_puntos():
    modos = ["municipio", "comunidad_autonoma", "espana"]
    for modo in modos:
        # Cargar el GeoDataFrame con las geometrías de las comunidades
        poligono_gdf = gpd.read_file(f"../lib/aux_{modo}_pol.fgb")

        # Crear una lista para almacenar las filas modificadas
        new_rows = []

        # Iterar a través de los multipolígonos y obtener los puntos del borde
        for index, row in poligono_gdf.iterrows():
            boundary = row['geometry'].boundary
            border_points = []
            
            if boundary.type == 'MultiLineString':
                for line in boundary.geoms:
                    border_points.extend(line.coords)
            else:
                border_points.extend(boundary.coords)
            
            new_row = row.copy()
            new_row['geometry'] = MultiPoint(border_points)
            new_rows.append(new_row)

        border_gdf = gpd.GeoDataFrame(new_rows)
        individual_points_gdf = border_gdf.explode(index_parts=True)

        individual_points_gdf = individual_points_gdf.reset_index(drop=True)
        individual_points_gdf.to_file(f"../lib/aux_{modo}_puntos.fgb", driver="FlatGeobuf", crs="EPSG:4258")

#NUEVO
def generar_voronoi(ruta_salida, modo="municipios"):
    # Cargar los datos de las municipios autónomas y municipios en puntos
    if var_dict["generar_puntos_voronoi"]:
        generar_puntos()
    espana_point_df = gpd.read_file('../lib/aux_espana_puntos.fgb')
    espana_gdf = gpd.read_file('../lib/aux_espana_pol.fgb')
    
    if modo == "municipios":
        municipios_point_gdf = gpd.read_file('../lib/aux_municipio_puntos.fgb')
        poligonos_region_gdf = gpd.read_file("../lib/aux_municipio_pol.fgb")
        costa_points_gdf = municipios_point_gdf.overlay(espana_point_df,how="intersection")
        costa_points_gdf["codigo_municipio"] = costa_points_gdf["codigo_1"].str[6:]
    
    elif modo == "comunidades":
        comunidades_point_gdf = gpd.read_file('../lib/aux_comunidad_autonoma_puntos.fgb')
        poligonos_region_gdf = gpd.read_file("../lib/aux_comunidad_autonoma_pol.fgb")
        costa_points_gdf = comunidades_point_gdf.overlay(espana_point_df,how="intersection")
        costa_points_gdf["codigo_comunidad"] = costa_points_gdf["codigo_1"].str[2:4]


    coords = np.array(costa_points_gdf['geometry'].apply(lambda geom: (geom.x, geom.y)).tolist())

    vor = Voronoi(coords)
    polygons = [Polygon(vor.vertices[region]) for region in vor.regions if -1 not in region and len(region) > 0]
    voronoi_gdf = gpd.GeoDataFrame({'geometry': polygons}, crs=costa_points_gdf.crs)

    bbox = espana_gdf.total_bounds
    polygon = box(*bbox)
    data = {'geometry': [polygon]}
    gdf_polygon = gpd.GeoDataFrame(data, geometry='geometry')
    buffer_distance = 1  
    gdf_polygon = gdf_polygon.buffer(buffer_distance)
    gdf_polygon = gdf_polygon.reset_index()
    gdf_polygon = gpd.GeoDataFrame(gdf_polygon)
   
    voronoi_gdf['geometry'] = voronoi_gdf['geometry'].apply(make_valid)
    voronoi_join = voronoi_gdf.sjoin(costa_points_gdf)

    voronoi_join_clean = voronoi_join

    if modo == "municipios":    
        voronoi_join_clean["codigo_municipio"] = voronoi_join_clean["codigo_1"].str[6:]
        voronoi_join_clean['geometry'] = voronoi_join_clean['geometry'].apply(make_valid)
        dissolved_voronoi_gdf = voronoi_join_clean.dissolve(by='codigo_municipio', as_index=False)
        poligonos_region_gdf["codigo_municipio"] = poligonos_region_gdf["codigo"].str[6:]

    elif modo == "comunidades":
        voronoi_join_clean["codigo_comunidad"] = voronoi_join_clean["codigo_1"].str[2:4]
        voronoi_join_clean['geometry'] = voronoi_join_clean['geometry'].apply(make_valid)
        dissolved_voronoi_gdf = voronoi_join_clean.dissolve(by='codigo_comunidad', as_index=False)
        poligonos_region_gdf["codigo_comunidad"] = poligonos_region_gdf["codigo"].str[2:4]

    voronoi_gdf = dissolved_voronoi_gdf
    difference_gdf = gpd.overlay(voronoi_gdf, gdf_polygon, how='symmetric_difference')
    difference_gdf = difference_gdf.clip(gdf_polygon, keep_geom_type=True)
    difference_gdf = difference_gdf.explode(index_parts=False)

    def encontrar_municipio_mas_cercano(row):
        geometria_poligono = row['geometry']
        geometria_boundary = geometria_poligono.boundary
        municipio_pertinente = costa_points_gdf[costa_points_gdf['geometry'].intersects(geometria_boundary)]

        if not municipio_pertinente.empty:
            return municipio_pertinente.iloc[0]["codigo_municipio"]
        else:
            idx_municipio_mas_cercano = costa_points_gdf.distance(geometria_boundary).idxmin()
            municipio_mas_cercano =  costa_points_gdf.loc[idx_municipio_mas_cercano, 'codigo_municipio']
            return municipio_mas_cercano

    def encontrar_comunidad_mas_cercana(row):
        geometria_poligono = row['geometry']
        geometria_boundary = geometria_poligono.boundary
        ccaa_pertinente = costa_points_gdf[costa_points_gdf['geometry'].intersects(geometria_boundary)]

        if not ccaa_pertinente.empty:
            return ccaa_pertinente.iloc[0]["codigo_comunidad"]
        else:
            idx_ccaa_mas_cercana = costa_points_gdf.distance(geometria_boundary).idxmin()
            comunidad_mas_cercana =  costa_points_gdf.loc[idx_ccaa_mas_cercana, 'codigo_comunidad']
            return comunidad_mas_cercana

    if modo == "municipios":
        difference_gdf['codigo_municipio'] = difference_gdf.apply(encontrar_municipio_mas_cercano, axis=1)
        columnas_a_mantener = ['codigo_municipio']
    elif modo == "comunidades":
        difference_gdf['codigo_comunidad'] = difference_gdf.apply(encontrar_comunidad_mas_cercana, axis=1)
        columnas_a_mantener = ['codigo_comunidad']

    huecos_asignados = difference_gdf[columnas_a_mantener + ['geometry']]
    outer_spain = gdf_polygon.overlay(espana_gdf,how='difference')

    huecos_asignados = huecos_asignados.clip(outer_spain)
    voronoi_dissolve_clip = voronoi_gdf.clip(outer_spain)

    if modo == "municipios":
        huecos_asignados_dissolve = huecos_asignados.dissolve(by='codigo_municipio', as_index=False)
        voronoi_total = gpd.GeoDataFrame( pd.concat( [huecos_asignados_dissolve,voronoi_dissolve_clip], ignore_index=True) )
        voronoi_total= voronoi_total.dissolve(by='codigo_municipio', as_index=False)

    elif modo == "comunidades":
        huecos_asignados_dissolve = huecos_asignados.dissolve(by='codigo_comunidad', as_index=False)
        voronoi_total = gpd.GeoDataFrame( pd.concat( [huecos_asignados_dissolve,voronoi_dissolve_clip], ignore_index=True) )
        voronoi_total= voronoi_total.dissolve(by='codigo_comunidad', as_index=False)

    voronoi_total["codigo"] = voronoi_total["codigo_1"]
    voronoi_total_concat = gpd.GeoDataFrame( pd.concat( [voronoi_total,poligonos_region_gdf], ignore_index=True) )
    voronoi_total_concat = voronoi_total_concat.dissolve(by='codigo', as_index=False)
    voronoi_total_concat = voronoi_total_concat[poligonos_region_gdf.columns]
    voronoi_total_concat.to_file(f"{ruta_salida}", driver="FlatGeobuf",crs="EPSG:4258")


