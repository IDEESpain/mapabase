# Descripción General del Proceso

Para obtener las teselas vectoriales de los ficheros **FlatGeobuf** generados en el anterior proceso, estos se transformarán a un formato NDJson, comprimido en GZIP. Esto permitirá que sean procesados por la herramienta **Tippecanoe**, que creará tantas bases de datos locales (formato MBTile) como niveles de visualización haya. Cada nivel contendrá la información de las capas correspondientes.

Una vez organizada la información en estos niveles, las teselas vectoriales podrán obtenerse utilizando la herramienta **mb-util**, que extraerá las teselas de los archivos MBTiles y las distribuirá en una estructura de carpetas basada en coordenadas **Z/X/Y**, siendo **Y** el nombre de la tesela final, con extensión **PBF**.

---

## Variables de los Ficheros de Configuración

### Fichero `config.json`

- **`lib_path`**: Ruta a la carpeta `lib` con los archivos auxiliares definidos previamente. Valor por defecto: `"../lib/"`.
- **`num_threads`**: Número de hilos utilizados en la ejecución paralela de procesos.
- **`logs_path`**: Ruta a la carpeta `logs` para almacenar los logs del proceso. Valor por defecto: `"../logs/"`.
- **`aux_comunidades_file`**: Fichero FGB con las geometrías de las comunidades autónomas. Valor por defecto: `"./lib/voronoi_comunidades.fgb"`.
- **`aux_municipios_file`**: Fichero FGB con las geometrías de los municipios. Valor por defecto: `"./lib/voronoi_municipios.fgb"`.
- **`setup`**: Parámetro que contiene los cinco subprocesos del proceso general. Se indica qué subprocesos ejecutar con los valores `"yes"` o `"no"`. Los subprocesos son:
  - **`compress_geojson`**: Comprime los ficheros FGB a NDJson en formato GZ.
  - **`tiling_layers`**: Ejecuta los comandos **Tippecanoe** para generar las bases de datos locales MBTiles a partir de los archivos GZ.
  - **`to_folder`**: Extrae las teselas de las bases MBTiles y las organiza en carpetas temporales según coordenadas **Z/X/Y**.
  - **`move_to_final_folder`**: Mueve las teselas de las carpetas temporales a las carpetas definitivas.
  - **`join_json`**: Une los archivos de metadatos en formato JSON de cada nivel de visualización en un archivo global `metadata.json` que contiene la información de cada capa y nivel.
- **`input_vrt_IGN`**: Ruta a los ficheros FGB y VRT del proveedor nacional (IGN).
- **`input_vrt_comunidades`**: Ruta a los ficheros FGB y VRT autonómicos generados en la el proceso 3.
- **`input_vrt_municipios`**: Ruta a los ficheros FGB y VRT municipales generados en el proceso 3.
- **`gz_folder_IGN`**: Ruta de salida para los archivos GZ a partir de los FGB nacionales.
- **`gz_folder_comunidades`**: Ruta de salida para los archivos GZ a partir de los FGB autonómicos.
- **`gz_folder_municipios`**: Ruta de salida para los archivos GZ a partir de los FGB municipales.
- **`destination_mbtiles`**: Ruta donde se generarán los ficheros MBTiles. Será creada al inicio del proceso y eliminada al final.
- **`destination_folder`**: Ruta a la que se moverán las teselas vectoriales de forma definitiva.
- **`temp_directory`**: Ruta temporal donde se generarán las teselas vectoriales a partir de los MBTiles.
- **`lista_municipios`**: Lista de códigos INE de los municipios a actualizar, en caso de que el parámetro `update` tenga valor `municipios`.
- **`lista_comunidades`**: Lista de códigos de las comunidades a actualizar, en caso de que el parámetro `update` tenga valor `comunidades`.
- **`min_zoom_IGN`**: Zoom mínimo para la escala nacional. Valor por defecto: `0`.
- **`max_zoom_IGN`**: Zoom máximo para la escala nacional. Valor por defecto: `13`.
- **`min_zoom_comunidades`**: Zoom mínimo para la escala autonómica. Valor por defecto: `14`.
- **`max_zoom_comunidades`**: Zoom máximo para la escala autonómica. Valor por defecto: `16`.
- **`min_zoom_municipios`**: Zoom mínimo para la escala local. Valor por defecto: `17`.
- **`max_zoom_municipios`**: Zoom máximo para la escala local. Valor por defecto: `20`.
- **`min_zoom`**: Zoom mínimo para el Mapa Base. Valor por defecto: `0`.
- **`max_zoom`**: Zoom máximo para el Mapa Base. Valor por defecto: `20`.
- **`bbox`**: Coordenadas que definen el bbox de actualización regional. Ejemplo: `[-19.215480397527838, 26.62547835167641, 6.341170645348383, 44.792032154864046]`, que incluye todo el territorio de España.
- **`update`**: Modo de actualización regional de teselas. Los posibles valores son: `""`, `"comunidades"`, `"municipios"`, `"bbox"`, `"nacional"` y `"peninsular"`.

### Fichero `config_vtiles.json`

Este archivo puede autogenerarse con el script Python `run_crearJSONConfig.py` usando el JSON de validación del Proceso 2 (`comprobacion.json`). El parámetro relevante es:

- **`zoom_levels`**: Configuración para cada nivel de visualización:
  - **`level`**: Nivel de visualización.
  - **`process`**: Si el valor es `"yes"`, se generarán las teselas correspondientes a ese nivel de zoom.
  - **`layers`**: Listado de capas mostradas en el nivel de visualización. Se indica el fichero GZ y el nombre de la capa.
  - **`layers_no_coalesce`**: Capas donde se respetan los límites geométricos en caso de coincidencia entre elementos colindantes (útil para edificios).
  - **`layers_with_labels`**: Capas que contienen etiquetas (actualmente no se utiliza).

# Conversión de VRT a MBTiles

Una vez comprobado que los parámetros de configuración en los ficheros `config.json` y `config_vtiles.json` son correctos, se ejecutará el proceso **`run_vrtToMbTiles.py`**. Este script está disponible en el siguiente enlace: [run_vrtToMbTiles.py](https://github.com/IDEESpain/mapabase/blob/gh-pages/scripts/teselas/4proceso-vtilesToMbTiles/run_vrtToMbTiles.py)

Este proceso será responsable de llevar a cabo todos los subprocesos definidos previamente. A continuación, se detalla el flujo del proceso:

1. **Entrada de Datos**: Los archivos de entrada serán los ficheros **FGB** y **VRT** generados en la Fase IV.
2. **Compresión**: Estos archivos serán comprimidos en formato **NDJson** utilizando **GZip**.
3. **Conversión a MBTiles**: Los archivos NDJson comprimidos se convertirán a ficheros **MBTiles** usando la herramienta Tippecanoe, que contendrán la información vectorial necesaria.
4. **Extracción de Teselas**: A partir de los ficheros MBTiles, se extraerán las teselas vectoriales, que serán almacenadas en carpetas temporales.
5. **Movimiento a Carpeta Final**: Las teselas serán movidas desde las carpetas temporales a la carpeta final. La estructura de almacenamiento de las teselas seguirá el formato de directorios **Z/X/Y.pbf**, donde:
   - **Z**: Corresponde al nivel de visualización.
   - **X**: Coordenada X de la tesela.
   - **Y.pbf**: Coordenada Y de la tesela en formato PBF.

## Tipos de Generación de Teselas

La generación de teselas podrá realizarse para diferentes áreas geográficas, según lo definido en el parámetro de configuración `update`:
- **Global**: Cobertura de todo el territorio mundial (incluyendo capas de contexto con cobertura global).
- **Nacional**: Teselas generadas para todo el territorio de España.
- **Peninsular**: Teselas generadas para todo el territorio de la Península Ibérica.
- **Regional (comunidades o municipios)**: Generación específica para territorios autonómicos o municipales.
- **Personalizado**: Teselas generadas para un área específica definida por un **bbox** (cuadro delimitador).
