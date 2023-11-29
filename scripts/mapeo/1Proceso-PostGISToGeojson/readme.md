# Datos de entrada proceso .ods Proveedores de datos

Los datos de entrada al proceso se indican en el fichero de entrada: CNIG_ToGeojson.ods

Cada nuevo proveedor tendrá que crear su propio archivo .ods (CNIG_ToGeojson.ods) con sus propias fuentes y campos. El fichero de ejemplo de CNIG se proporciona como muestra de como realizar las consultas que analizar y actualizar de las conexiones, clases de entidad y valores para poder generar una V1 del MapaBaseXYZ.

Este Excel es el fichero que se utilizó en la versión 0 del MapaBaseXYZ. Para el mapeado inicial se utilizaron diferentes bases de datos, en función de la facilidad de acceso, mapeado y disponibilidad en el momento de crear las teselas.

De forma alternativa, algunos proveedores pueden preferir realizar una transformación de BBDD para realizar el mapeo en lugar de utilizar el fichero .ods. Se ofrece un script _run_generar_sql.py_ (ver más adelante en esta página) para crear una BBDD vacía con la estructura del modelo. A partir de esa estructura del modelo se tendrá que realizar igualmente la correspondencia entre datos del proveedor y modelo XYZ.

***Hoja ProcesoToGeojson***

Mapeo de los datos de entrada al proceso de generación de los geojson de teselas vectoriales.

*Campos*

*Conexión*. Identificador de la conexión de base de datos. Las cadenas de conexión están en la hoja BBDD a modo de referencia del nombre de la conexión. El proceso utiliza el archivo ./lib/conex.json donde estarán las contraseñas y datos de conexión.

*TablaOrigen*. Tabla dentro de la BD desde la que se obtienen los datos.

*Filtro*. Claúsula where del SQL para obtener los datos concretos de ese elemento geográfico. Si está vacío se incluye todos los elementos de la tabla. Para mapeados valor a valor se pueden utilizar los campos ValorOrigen y ValorDestino sin tener que hacer filtros por cada valor.

*ClaseDeEntidad*. Clase de entidad de destino en el modelo de datos de Mapa Base

*AtributoOrigen*. Campo de la tabla origen con el valor para el atributo de destino.

*ValorOrigen*. Valores del atributo origen.

    * - Mapea todos los valores de entrada como atributo de salida. Ejemplo: nombre
    
    Vacío – No existe valor de entrada (o no está en la tabla) y sólo se crea atributo y valor de salida. Ejemplo: productor, se añade el atributo con un valor fijo (“IGN”) para toda la clase de entidad.
    
    Otro valor – Mapea valor a valor en un valor de destino indicado. Por ejemplo: tip_area 1 -> clase “aeródromo”. Sería una especie de reclasificación valor a valor.

*AtributoDestino*. Atributo del modelo en el que se van a almacenar los valores.

*ValorDestino*. Valor que se almacena en el json final.

*CrearCentroide*. Se utiliza capas de origen polígono o línea que en el modelo final se representan por un punto. Si se marca verdadero se incluye la función ST_CENTROID en la sentencia SQL
  
    F - Falso
  
    T - Verdadero

*Procesar*. Indica qué filas del excel se van a procesar al correr el proceso. Se utiliza para actualizaciones parciales o pruebas.

    F - Falso

    T - Verdadero
  
***Hoja BBDD***

Listado de las bases de datos utilizadas en el mapeo. Como referencia.

***Hoja Dataset***

Listado de todos los elementos geográficos y niveles del modelo. Como referencia.

Actualizada en: https://ideespain.github.io/mapabase/elementos/relacion_tematica/

# run_postGISToGeojson.py
Script que exporta los datos desde las fuentes originales a .json

En las primeras líneas se configuran los parámetros:

    path_jsonConex = '/lib/conex.json' #ruta al fichero con las conexiones a la BBDD
    
    path_hojaCalculoMApeo = '/1CNIG/CNIG_ToGeojoson.ods' #ruta al fichero con el mapeo del modelo
    
    path_carpetaSalida = '/1CNIG/1Geojson' #ruta a la carpeta para los datos de salida
    
    proveedor = 'cnig' 
    
Consultar el código de proveedor en https://ideespain.github.io/mapabase/datos/proveedores_de_datos/



# ./lib/conex.json
Identificar las fuentes de datos que se utilizan en el archivo .ods de entrada.

# run_generar_sql.py
Script que genera una base de datos vacía con la estructura del modelo a partir la página web del modelo. Al rodar el script, recorre la web y se genera, cada tabla y campos correspondientes. Se proporciona como alternativa al .ods para transformación de modelos. Puede ser útil a algunos productores que les resulte más sencillo exportar de su modelo de datos al modelo de datos XYZ a través de tabla en lugar del .ods de mapeo.


# requirements.txt
Listado de librerías necesarias para el funcionamiento de los scripts tanto del proceso 1 y 2, como 3 y 4.

