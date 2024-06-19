
*run_crearJSONValidacion.py* -  Crea el archivo .json (/lib/comprobacion.json) desde la web (github mapabase) a partir del html (ver Nota). Si hay cambios en el modelo se tiene que actualizar el repositorio en local y volver a lanzar. Si no ha habido cambios en el modelo se puede utilizar el archivo (/lib/comprobacion.json) anterior.

Nota - En el código del script, la variable llamada ProcesoControlCalidad.git_carpeta_mapabase_gh_pages, definida en el archivo config.json, indica la ruta del repositorio mapabase que tengas en el ordenador desde el que se va a lanzar el script. Utiliza la rama en la que esté ese repositorio, no va a utilizar automáticamente gh_pages desde la web. Por ejemplo, si en ese repositorio indicado está la rama desarrollo utilizará desarrollo.

*config.json* - configuración de rutas y archivos
Para ejecutar el proceso, se necesitará configurar en primer lugar el archivo config.json dónde se van a parametrizar los valores necesarios para la ejecución del proceso. Parámetros obligatorios:


    "geojson_folder_path":"./salida_geojsons_andalucia/",  # Carpeta donde se encuentran los geojsons obtenidos en el proceso 1
    
    "fgb_folder_path": "./salida_geojsons_andalucia/fgb/",  #Carpeta para los fgb que se crearán
    
    "git_carpeta_mapabase_gh_pages" : "./mapabase", #git con el modelo de mapa base, desde el que se crea el json de validación.
    
    "JSON_comprobacion" : "./lib/comprobacion.json", #fichero de comprobación/validación creado a partir del gihubt de mapabase.    
    
    "fgb_temp_folder" : "./salida_geojsons_andalucia/fgb_temp/" #Carpeta temporal, que se borra al finalizar el proceso.
    

*run_completeProcess.py* - Ejecuta todos los procesos del proceso 2: validation + transformation. Se recomienda no utilizar este proceso la primera vez y utilizar por separado: run_validationProcess.py y una vez estén los datos sin errores ejecutar run_transformationProcess.py

*run_validationProcess.py* -  Pasa la validación del modelo. Recomendado para la primera ejecución para tener más control del proceso, en lugar de run_completeProcess.py.

*run_transformationProcess.py* - Pasa de json a fgb. Recomendado para la primera ejecución para tener más control del proceso, en lugar de run_completeProcess.py.

*run_2FGB.py* - incluido en transformation process. Se deja aqui por separado

*run_2VRT.py* - incluido en transformation process.  Se deja aqui por separado


**Fichero log de salida**

El log del proceso de validación se estructura de la siguiente manera:

    
    1. Cabecera con información general del proceso: fecha de inicio.
    
        I. Comprobación de ficheros geojson:
        
        II. Geojson existentes en el modelo de datos
        
        III. Geojson entregados
        
        IV. Geojson entregados que pertenecen al modelo de datos
        
        V. Geojson NO entregados del modelo de datos
        
        VI. Geojson entregados que NO son del modelo de datos
        
    2. Comprobación de atributos en cada geojson:
    
        I. Atributos en modelo de datos
        
        II. Atributos en Geojson
        
        III. Atributos NO encontrados en alguna entidad del Geojson
        
        IV. Atributos encontrados del modelo
        
        V. Atributos encontrados en alguna entidad que NO son del modelo
        
    3. Comprobación de dominio de los atributos:
    
        I. Muestra los valores no contemplados en el modelo de datos que existen en un atributo
        
    4. Final de fichero con fecha de finalización.
    


