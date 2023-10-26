import time
from lib.mapeo import mapeo_PG_GJSON

if __name__ == '__main__':
    # # # # parámetros del script
    path_jsonConex = '/var/proyectos/mapaBaseXYZ/input_geojson/0vt-procesos/1Proceso-PostGISToGeojson/lib/conex.json'
    path_hojaCalculoMApeo = '/var/proyectos/mapaBaseXYZ/input_geojson/1CNIG/CNIG_ToGeojoson.ods'
    path_carpetaSalida = '/var/proyectos/mapaBaseXYZ/input_geojson/1CNIG/1Geojson'
    proveedor = 'CNIG'
    
    # # # # Se llama a la clase con los parámetros de la ejecución
    ProcesoMapeo = mapeo_PG_GJSON(path_jsonConex,path_hojaCalculoMApeo,path_carpetaSalida,proveedor)
    ProcesoMapeo.verbose = True
    ProcesoMapeo.verboseRecorrido = 50000
    
    # # # # partir las entidades de entrada en bloques
    ProcesoMapeo.partirClaseEntidad = True
    ProcesoMapeo.tipoPartirClaseEntidad = 1
    ProcesoMapeo.partirClaseEntidadCantidad = 500000
    
    # # # # geojson de salida que quiero de salida
    # ProcesoMapeo.geojsonSalida = ['portal_pto', 'hidrografia_pol', 'altimetria_lin', 'autopista_lin']
    # ProcesoMapeo.geojsonSalida = ['altimetria_lin']
    
        
    # # # # Crear carperta de exportación de los geojson
    # ProcesoMapeo.crearCarpeta(sobrescribir = True)
    
    # # # # Sobreescribir Geojsons de salida
    ProcesoMapeo.sobreescribirGeojson = True
    
    # # # # Renombrar geojson si ha dado error el proceso
    ProcesoMapeo.renombrarSiError = True
    
    # # # # Paginar sentencia SQL
    ProcesoMapeo.paginarSentenciaSQL = True
    ProcesoMapeo.limiteCantidad = 500000
    
    # # # # Partir geojsons para luego fusionarlos al final
    ProcesoMapeo.partirGeojson = True
    
    # # # # Límite sentencia SQL. Modo PRUEBAS
    # ProcesoMapeo.limit = True
    # ProcesoMapeo.limiteCantidad = 100
    
    
    # # # # Proceso de mapeo
    start_time = time.time()
    ProcesoMapeo.procesoMapeo()
    print("--- {} horas de ejecución ---".format( (time.time() - start_time) /3600 ) )