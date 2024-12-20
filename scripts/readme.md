| **Scripts**                              | **Descripción**                                                                                                                                                             |
|------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1 mapeo / 1Proceso-PostGISToGeojson**  |                                                                                                                                                                         |
| 1.1 `run_postGISToGeojson.py`            | Exporta de BBDD a geojson.                                                                                                                                              |
| 1.1 `run_generar_sql.py`                 | Genera una base de datos vacía con la estructura del modelo a partir de la página web del modelo. Puede usarse para transformar de BBDD a BBDD previamente.             |
| **2 mapeo / 2Proceso-ValidacionGeojson** |                                                                                                                                                                         |
| 2.1 `run_completeProcess.py`            | Crea el json de validación a seguir; valida los geojson según modelo de datos del proyecto, incluido en el json del script anterior; y transforma los geojson a flatgeobuf, para realizar los siguientes procesos de forma más rápida. |
| **3 teselas / 3ProcesoUnionDatos**       |                                                                                                                                                                         |
| 3.0 `run_fgb_aux_to_excel.py`           | Crea un excel que será usado en los siguientes procesos a partir del fgb de municipios. No hace falta lanzarlo cada vez.                                                |
| 3.1 `run_generar_recortes_municipios.py`| Hace recortes de municipios en aquellos municipios donde no tengamos datos. Puede lanzarse en modo actualización.                                                      |
| 3.2 `run_generar_recortes_comunidades.py`| Hace recortes de las comunidades autónomas en aquellas comunidades donde no tengamos datos. Puede lanzarse en modo actualización.                                       |
| 3.3 `run_generar_union_nacional_municipios.py` | Agrupa los municipios por comunidades autónomas.                                                                                                                       |
| 3.4 `run_generar_union_nacional.py`     | Agrupa las comunidades anteriormente generadas en archivos a nivel nacional.                                                                                           |
| **4 teselas / 4proceso-vtilesToMbTiles** |                                                                                                                                                                         |
| 4.0 `run_crearJSONConfig.py`            | Creamos un json a partir del modelo de datos, para el lanzamiento del proceso.                                                                                         |
| 4.2 `run_vrtToMbTiles.py`               | Convertimos los vrt a teselas sin comprimir en estructura de carpetas. Puede lanzarse en modo actualización.                                                           |



**Requisitos previos**

Para ejecutar cada uno de los procesos es necesario python3. Suponiendo que se usa un SO basado en GNU/Linux, y en el caso que no se tenga por defecto instalado python3, el proceso sería el siguiente:

    sudo apt install python3
    

Para la instalación (opcional) de pypy3 :

    sudo apt install pypy3
    

Para la instalación de las librerías externas necesarias para la ejecución de los procesos ( html-to-json ,numpy, psycopg2, pyexcel-ods3), se realizará de la siguiente manera en terminal:

    pip3 install “nombre de la librería”
    

Otra opción es instalar directamente las librerías desde el archivo scripts/mapeo/1Proceso-PostGISToGeojson/requirements.txt:

    pip3 install -r requirements.txt
    
Para la instalación de las librerías en pypy3, se utilizará el siguiente comando:

    pypy -mpip install “nombre de la librería”

**Ejecución de scripts**

En general para todos los scripts del proceso, para ejecutar un script utilizar el comando de python:

   python3 nombredelscript.py
