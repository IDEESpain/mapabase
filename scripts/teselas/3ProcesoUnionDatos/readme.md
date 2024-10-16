# Explicación General del Proceso

Los ficheros **FlatGeobuf** obtenidos del proceso 2 serán designados como datos productores, y se dividirán en tres tipos: **nacional**, **comunidades** y **municipios**. Además, habrá un nivel adicional de datos llamados **generados**, cuyo objetivo es garantizar la disponibilidad de información generada para todas las comunidades y municipios, incluso si no se cuenta con datos productores para algunas regiones.

### Mecanismo de Recorte y Jerarquía de Datos

Cuando no exista un productor para una unidad administrativa menor, se extraerá información de los niveles superiores de la jerarquía:

- Para las **comunidades autónomas** que no tengan productores, se recortará la sección correspondiente de los datos del nivel nacional.
- Para los **municipios**, se obtendrá la información de la comunidad autónoma correspondiente y, en caso de que no exista, se extraerá de la capa nacional.

### Unión de Datos

Una vez que se haya generado la información para todas las comunidades y municipios, se llevará a cabo un proceso de **unión**. En este proceso, se combinarán los datos de todas las comunidades para cada capa, formando el nivel de visualización **autonómico**. De manera similar, se unirán los datos de los municipios para generar el nivel de visualización **local**.

Este enfoque garantiza que cada unidad administrativa, desde el nivel nacional hasta el local, tenga una representación completa, extrayendo la información necesaria de los niveles superiores cuando sea necesario.

---
## Archivos Auxiliares Necesarios

A continuación se detallan los archivos auxiliares necesarios, disponibles en el siguiente enlace: [Repositorio GitHub](https://github.com/IDEESpain/mapabase/tree/gh-pages/scripts/teselas/3ProcesoUnionDatos/lib).

- **`comunidades_autonomas.xlsx`** y **`municipios.xlsx`**: Hojas de cálculo que contienen el listado de comunidades autónomas y municipios de España. Incluyen información útil como el código asignado a cada región y su nombre.
  
- **`matriz_elementos.xlsx`**: Este archivo define el listado de capas del modelo de datos del Mapa Base XYZ, indicando el ámbito de visualización al que pertenecen.

- **`aux_comunidad_autonoma_pol.fgb`**: Fichero que contiene las geometrías de las comunidades autónomas de España.

- **`aux_municipio_pol.fgb`**: Fichero que contiene las geometrías de los municipios de España.

- **`aux_espana_pol.fgb`**: Fichero que contiene la geometría de todo el territorio español.

- **`aux_espana_puntos.fgb`**, **`aux_comunidad_autonoma_puntos.fgb`**, **`aux_municipios_puntos.fgb`**: Estos archivos contienen los puntos extraídos de las fronteras de las geometrías de España, comunidades autónomas y municipios, respectivamente. Serán utilizados en el proceso de generación de los polígonos de Voronoi. En caso de que alguno de estos ficheros no esté disponible, la variable **`generar_puntos_voronoi`** deberá estar configurada en `true` en el archivo de configuración.

- **`voronoi_comunidades.fgb`** y **`voronoi_municipios.fgb`**: Ficheros que contienen las geometrías de las comunidades autónomas y municipios de España, adaptadas para formar un diagrama de Voronoi que cubre todo el territorio nacional. Si alguno de estos archivos no está presente, las variables **`regenerar_municipios_pol_file`** y/o **`regenerar_comunidades_pol_file`** deberán estar configuradas en `true` en el archivo de configuración.


---
# Configuración del Proceso

Fichero **config.json** - configuración de rutas y archivos
Para ejecutar el proceso, se necesitará configurar en primer lugar el archivo config.json dónde se van a parametrizar los valores necesarios para la ejecución del proceso. 

### Parámetros de configuración

- **`lib_path`**: Ruta a la carpeta ‘lib’ en la que se encuentran los archivos auxiliares que se definieron previamente, por defecto será `'../lib/'`.
  
- **`elementos_file`**: Nombre del fichero que contiene la hoja de cálculo con el listado de elementos, por defecto será `'matriz_elementos.xlsx'`.
  
- **`municipios_file`**: Nombre del fichero que contiene la hoja de cálculo con el listado de municipios, por defecto será `'municipios.xlsx'`.
  
- **`comunidades_file`**: Nombre del fichero que contiene la hoja de cálculo con el listado de comunidades autónomas, por defecto será `'comunidades_autonomas.xlsx'`.
  
- **`path_productores_municipios`**: Ruta a la carpeta en la que se encontrarán las carpetas de los proveedores de datos municipales. Cada carpeta tendrá el código INE correspondiente al municipio. Dentro de cada carpeta habrá ficheros FGB y VRT, por ejemplo: `tierra_firme_pol.fgb` y `tierra_firme_pol.vrt`.
  
- **`path_productores_com_aut`**: Ruta a la carpeta que contiene los datos de los proveedores autonómicos. Las carpetas estarán nombradas con los códigos correspondientes a las comunidades autónomas, como '01' para Andalucía.
  
- **`path_productores_nacional`**: Ruta a la carpeta con los datos del proveedor de ámbito nacional, que tendrá una única carpeta con el nombre '00'.
  
- **`path_generados_municipios`**: Ruta en la que se generarán las carpetas para cada municipio con los datos (FGB y VRT) de cada capa del modelo disponible.
  
- **`path_generados_comunidades_recorte`**: Ruta en la que se generarán las carpetas para cada comunidad autónoma, con los datos correspondientes a cada una.
  
- **`path_generados_comunidades_municipios`**: Ruta obsoleta que indicaba la carpeta para la unión de capas de municipios por comunidad autónoma. Ya no se utiliza.
  
- **`path_generados_nacional`**: Ruta para las capas nacionales generadas. Este parámetro ya no se utiliza para evitar duplicación de datos.
  
- **`path_generados_nacional_com_aut`**: Ruta donde se generará la carpeta nacional con el nombre '00', con los datos de todas las comunidades autónomas unidas en un único mapa nacional.
  
- **`path_generados_nacional_municipios`**: Ruta donde se generará la carpeta nacional con los datos de todos los municipios unidos.
  
- **`buffer`**: Parámetro auxiliar para definir la ampliación aplicada a las máscaras regionales en los procesos de recorte.
  
- **`path_from_inside_generados_to_productores`**: Ruta auxiliar para localizar la carpeta de productores desde la carpeta de generados, por defecto `'../../productores/'`.
  
- **`path_from_inside_generados_com_aut_to_generados_municipios`**: Ruta auxiliar para localizar la carpeta de municipios generados desde la carpeta de comunidades generadas.
  
- **`path_from_inside_generados_nacional_to_generados_com_aut`**: Ruta auxiliar para localizar la carpeta de comunidades generadas desde la carpeta del ámbito nacional.
  
- **`num_threads`**: Número de hilos que utilizará la máquina para procesos en paralelo.
  
- **`logs_path`**: Ruta para guardar los archivos de log, por defecto `'../logs/'`.
  
- **`generar_puntos_voronoi`**: Indica si deben generarse los archivos auxiliares de puntos Voronoi para comunidades autónomas y municipios. Si los archivos ya existen, este parámetro debe ser `false` para reducir tiempos de ejecución.
  
- **`municipios_pol_file`**: Fichero con el diagrama de Voronoi de los municipios, por defecto ubicado en `'../lib/voronoi_municipios.fgb'`.
  
- **`regenerar_municipios_pol_file`**: Si no existe el archivo anterior, este parámetro debe estar en `true`. Si existe y está actualizado, se recomienda `false` para reducir tiempos de ejecución.
  
- **`comunidades_pol_file`**: Fichero con el diagrama de Voronoi de las comunidades autónomas, por defecto en `'../lib/voronoi_comunidades.fgb'`.
  
- **`regenerar_comunidades_pol_file`**: Igual que el parámetro anterior, pero aplicado a comunidades autónomas.
  
- **`codigo_comunidades`**: Listado de códigos de dos dígitos de las comunidades autónomas que serán procesadas. Ejemplo: `[1,7]` para Andalucía y Castilla y León.
  
- **`config_proceso_4`**: Ruta del fichero de configuración de los procesos de la Fase V, por defecto `'../../4proceso-vtilesToMbTiles/config.json'`.


---
# Procesos de Recorte y Unión de Datos

### Scripts de Recorte

Los scripts **`run_generar_recortes_comunidades.py`** y **`run_generar_recortes_municipios.py`** se encargan de realizar los recortes geométricos de los datos según la escala de visualización.

Se definen tres escalas de visualización:

- **Escala nacional**: Niveles de visualización del 0 al 13.
- **Escala autonómica**: Niveles de visualización del 14 al 17.
- **Escala local**: Niveles de visualización del 18 al 20.

En la **escala nacional**, se utiliza la información del proveedor nacional, el Instituto Geográfico Nacional (IGN).

En la **escala autonómica**, se prioriza la información de los proveedores autonómicos. Si falta información de alguna comunidad, se recurre a los datos del proveedor nacional, recortando las capas con la geometría de la comunidad autónoma correspondiente.

Actualmente no se trabaja con la **escala local**, por lo que no hay información proporcionada por entidades locales. El objetivo futuro es usar información de proveedores municipales y, en caso de no encontrarla, utilizar los datos de la comunidad autónoma a la que pertenece el municipio. Si tampoco se encuentra información a nivel autonómico, se recurrirá a la del proveedor nacional, recortando siempre con la geometría del municipio.

### Ejemplo de Proceso: Recorte para Municipios en Extremadura

Para realizar el recorte de municipios en la comunidad autónoma de Extremadura, se deben seguir los siguientes pasos:

- En el archivo `config.json`, el parámetro **`codigo_comunidades`** debe estar configurado como `[11]`.
- Asignar las rutas de los parámetros **`path_productores_municipios`** y **`path_generados_municipios`** a las carpetas correspondientes:
  - `path_productores_municipios = carpeta_proyecto/productores/municipios`
  - `path_generados_municipios = carpeta_proyecto/generados/municipios`

El proceso leerá los ficheros auxiliares y obtendrá el listado de capas (por ejemplo, `hidrografia_pol`, `altimetria_lin`, etc.), junto con la geometría de los municipios.

#### Búsqueda y Copia de Capas

Para cada municipio, el script buscará las capas necesarias en las rutas indicadas:

- Si se encuentra la capa **`hidrografia_pol`** en la ruta del municipio, por ejemplo, `carpeta_proyecto/productores/municipios/10118/hidrografia_pol.fgb` y `hidrografia_pol.vrt`, los archivos serán copiados a `carpeta_proyecto/generados/municipios/10118/`.
- Si no se encuentra la capa en el ámbito municipal, el script buscará en el proveedor autonómico, en este caso, en `carpeta_proyecto/productores/comunidades/11/`.

#### Proceso de Recorte

Si se encuentra la capa a nivel autonómico, el proceso generará un archivo VRT auxiliar de recorte, llamado por ejemplo **`hidrografia_pol_recorte.vrt`**, que contendrá la geometría del municipio. Este VRT usará el archivo FGB de la comunidad como fuente y se aplicará el recorte directamente en el VRT.

El comando `ogr2ogr` de la librería GDAL se usará para transformar el VRT de recorte en un archivo FGB, generando también un VRT que apunte al nuevo FGB, almacenando ambos en la carpeta `carpeta_proyecto/generados/10118/`.

Si no se encuentra la capa en el proveedor autonómico, se buscará en el proveedor nacional (ruta: `carpeta_proyecto/productores/nacional/00/`) y se seguirá el mismo proceso de recorte.

Para las comunidades autónomas, el proceso será similar, pero sin tener que buscar en el ámbito local.

### Scripts de Unión

Una vez completados todos los recortes, las carpetas **`carpeta_proyecto/generados/comunidades`** y **`carpeta_proyecto/generados/municipios`** contendrán toda la información nacional dividida por comunidades autónomas y municipios, respectivamente.

#### Unión de Datos

Para generar las capas correspondientes al ámbito nacional, se deberá unir cada segmento regional de cada capa:

- Por ejemplo, para la capa **`hidrografia_pol`** a nivel autonómico, se unirán los segmentos de cada comunidad, ubicados en:
  - `carpeta_proyecto/generados/comunidades/01/hidrografia_pol.fgb`
  - `carpeta_proyecto/generados/comunidades/02/hidrografia_pol.fgb`
  - ...

La unión se localizará en la ruta especificada por el parámetro **`path_generados_nacional_com_aut`**, por ejemplo: `carpeta_proyecto/generados/nacional/comunidades/00/hidrografia_pol.fgb`.

Este proceso se repetirá para todas las capas y también para la escala local, utilizando un VRT que indique las rutas de los VRT regionales, y luego se ejecutará el comando `ogr2ogr` para generar el FGB nacional.

Habrá dos scripts para este proceso:

- **`run_generar_union_nacional.py`**: Para la unión de las comunidades autónomas.
- **`run_generar_union_nacional_municipios.py`**: Para la unión de los municipios.

---
