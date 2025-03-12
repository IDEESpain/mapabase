# Generador de Archivos GeoJSON

Este script está diseñado para generar archivos GeoJSON a partir de datos almacenados en una base de datos PostgreSQL. Permite realizar consultas SQL y transformar los resultados en un formato geoespacial comúnmente utilizado, cumpliendo con las especificaciones del formato GeoJSON.


## Ejecución en Windows

Si deseas ejecutar los procesos en Windows, sigue la guía proporcionada en el siguiente enlace:  
[Guía de lanzamiento en Windows](https://github.com/IDEESpain/mapabase/tree/gh-pages/scripts/mapeo/1Proceso-PostGISToGeojson/MapaCiudadano_Documentacion_Lanzamiento_en_Windows.pdf)


## Datos de entrada proceso .ods Proveedores de datos

Los datos de entrada al proceso se indican en el fichero de entrada: CNIG_ToGeojson.ods

Cada nuevo proveedor tendrá que crear su propio archivo .ods (CNIG_ToGeojson.ods) con sus propias fuentes y campos. El fichero de ejemplo de CNIG se proporciona como muestra de como realizar las consultas que analizar y actualizar de las conexiones, clases de entidad y valores para poder generar una V1 del MapaBaseXYZ.

Este Excel es el fichero que se utilizó en la versión 0 del MapaBaseXYZ. Para el mapeado inicial se utilizaron diferentes bases de datos, en función de la facilidad de acceso, mapeado y disponibilidad en el momento de crear las teselas.

De forma alternativa, algunos proveedores pueden preferir realizar una transformación de BBDD para realizar el mapeo en lugar de utilizar el fichero .ods. Se ofrece un script _run_generar_sql.py_ (ver más adelante en esta página) para crear una BBDD vacía con la estructura del modelo. A partir de esa estructura del modelo se tendrá que realizar igualmente la correspondencia entre datos del proveedor y modelo XYZ.

**Hoja ProcesoToGeojson**

Mapeo de los datos de entrada al proceso de generación de los geojson de teselas vectoriales.

*Campos*

*Conexión*. Identificador de la conexión de base de datos. Las cadenas de conexión están en la hoja BBDD a modo de referencia del nombre de la conexión. El proceso utiliza el archivo ./lib/conex.json donde estarán las contraseñas y datos de conexión.

*TablaOrigen*. Tabla dentro de la BD desde la que se obtienen los datos. Este campo es sensible a las mayúsculas.

*Filtro*. Claúsula where del SQL para obtener los datos concretos de ese elemento geográfico. Si está vacío se incluye todos los elementos de la tabla. Para mapeados valor a valor se pueden utilizar los campos ValorOrigen y ValorDestino sin tener que hacer filtros por cada valor.

*ClaseDeEntidad*. Clase de entidad de destino en el modelo de datos de Mapa Ciudadano

*AtributoOrigen*. Campo de la tabla origen con el valor para el atributo de destino. Este campo es sensible a las mayúsculas.

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

## Script run_generar_sql.py
Script que genera una base de datos vacía con la estructura del modelo a partir la página web del modelo. Al ejecutar el script, recorre la web y se genera, cada tabla y campos correspondientes. Se proporciona como alternativa al .ods para transformación de modelos. Puede ser útil a algunos productores que les resulte más sencillo exportar de su modelo de datos al modelo de datos XYZ a través de tabla en lugar del .ods de mapeo.

**IMPORTANTE**: El repositorio local que contiene la carpeta elementos/ debe estar actualizada a la última versión del [repositorio remoto](https://github.com/IDEESpain/mapabase)

## Script run_postGISToGeojson.py
Script que exporta los datos desde las fuentes originales a .json

En las primeras líneas se configuran los parámetros:

    path_jsonConex = '/lib/conex.json' #ruta al fichero con las conexiones a la BBDD
    
    path_hojaCalculoMApeo = '/1CNIG/CNIG_ToGeojoson.ods' #ruta al fichero con el mapeo del modelo
    
    path_carpetaSalida = '/1CNIG/1Geojson' #ruta a la carpeta para los datos de salida
    
    proveedor = 'cnig' 
    
Consultar el código de proveedor en https://ideespain.github.io/mapabase/datos/proveedores_de_datos/

**Errores controlados**

_run_postGISToGeojson.py <class 'MemoryError'> mapeo.py 410_

- Si da error de memoria hay que bajar el número de elementos que se utilizan, de 500.000 (por defecto) a uno más bajo, por ejemplo: 50.000. Todo va a depender de la capacidad de la máquina desde la que se lanza.

En https://github.com/IDEESpain/mapabase/blob/gh-pages/scripts/mapeo/1Proceso-PostGISToGeojson/run_postGISToGeojson.py

Cambiar partirClaseEntidadCantidad a 50.000:

    ProcesoMapeo.partirClaseEntidadCantidad = 50000

Descomentar estas líneas y bajar a 50.000:


    # # Se comenta para evitar la pérdida de información.
    # # Paginar sentencia SQL
    # ProcesoMapeo.paginarSentenciaSQL = True
    # ProcesoMapeo.limiteCantidad = 500000


- Volver a lanzar sólo con las capas que han dado el error. Hasta ahora han dado el error: altimetria_lin, edificios_pol, cubierta_vegetal_pol . Es un error de memoria, por lo que depende de la máquina en la que se lance el proceso.

- Al terminar volver a poner el script a 500.000 y comentar las líneas de paginación para el siguiente proceso.

## Funcionalidad Principal

1. **Construcción de Consultas SQL**:
   - Se configura y ejecuta una consulta SQL personalizada, en función de los atributos y filtros definidos en la configuración. Se incluyen opciones para:
     - Paginación de resultados (`offset` y `limit`).
     - Filtrado dinámico en base a atributos y valores específicos.

2. **Generación de GeoJSON**:
   - Cada registro resultante de la consulta se convierte en una entidad ("Feature") del archivo GeoJSON, con propiedades (`properties`) y geometría (`geometry`).
   - La geometría es procesada a partir de datos en formato JSON almacenados en PostgreSQL.
   - Las propiedades se asignan de acuerdo a mapeos predefinidos, con opciones para concatenación de atributos y asignación condicional de valores.

3. **Gestión de Salida**:
   - El script permite la creación de archivos GeoJSON particionados según el tamaño o el número de entidades, configurable a través de la variable `tipoPartirClaseEntidad`.
   - Los logs de procesamiento se guardan en archivos `.log` para facilitar el seguimiento de errores y mapeos realizados.

4. **Control de Errores**:
   - El script gestiona errores de conexión y ejecución, registrándolos en un archivo log específico. También renombra archivos resultantes en caso de errores en el proceso.

## Requisitos

- Python 3.x
- Biblioteca `psycopg2` para la conexión a PostgreSQL.
- Biblioteca `json` para el manejo de datos en formato JSON.
- Opcionalmente, `gc` para el manejo de memoria en procesos de gran tamaño.

## Configuración

El script requiere un archivo de configuración JSON (`./lib/conex.json`) con la siguiente estructura.

```json
{
"NOMBRE_CONEXION": {
    "ip": "XXX.XXX.XXX.XXX",
    "puerto": "XXXX",
    "usuario": "nombre_usuario",
    "contrasena": "password",
    "bbdd": "nombre_base_de_datos",
    "esquema": "nombre_esquema" }
}

```
Identificar las fuentes de datos que se utilizan en el archivo .ods de entrada.


## Ejecución

Ejecutar el script en el entorno Python configurado:

```bash
    python run_postGISToGeojson.py
```

Los archivos GeoJSON generados estarán disponibles en el directorio de salida especificado (path_carpetaSalida).
