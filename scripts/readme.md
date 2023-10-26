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
