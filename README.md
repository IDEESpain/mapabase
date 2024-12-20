# mapabase
# Mapa Base XYZ del Sistema Cartográfico Nacional: Teselas vectoriales

Para realizar este proceso se integra la información de las distintas administraciones en dos fases: una de mapeo y otra de generación de teselas. Durante la primera fase del mapeo, los productores de información extraen de sus bases de datos la información (**proceso 1**) según el modelo definido desde el proyecto Mapa Base. A continuación, se pasa un proceso para asegurar la calidad y coherencia de la información proporcionada respecto al modelo (**proceso 2**). Una vez obtenida la información, se envía al O.A. Centro Nacional de Información Geográfica (O.A. CNIG), encargado de la implementación del proyecto Mapa Base, para continuar la transformación.

La segunda fase se desarrolla en la infraestructura del O.A. CNIG. Esta se subdivide en dos fases sucesivas, donde se integran los datos de todos los proveedores (**proceso 3**) y se exportan al formato final para su publicación (**proceso 4**). Una vez generadas las teselas, se ha previsto la actualización periódica de los datos en coordinación con los productores y las actualizaciones de su información.

El esquema general de funcionamiento es el recogido en el cuadro siguiente. Cada uno de los procesos puede tener variaciones y otros ficheros de configuración y complementarios.

Las versiones actualizadas de los scripts se encuentran en:  
[https://github.com/IDEESpain/mapabase/tree/gh-pages/scripts](https://github.com/IDEESpain/mapabase/tree/gh-pages/scripts)


Enlace a la página web del modelo
https://ideespain.github.io/mapabase/

Ramas del repositorio
- gh-pages. Producción
- Desarrollo. Pre-producción
- modelo_0001. Ramas de desarrollo. Para cambios, crear una nueva rama sobre la rama Desarrollo con un número consecutivo. Se pueden eliminar una vez acabado el commit.
