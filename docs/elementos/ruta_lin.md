## ruta_lin
<br />

El elemento «ruta_lin» identifica los elementos lineales que representan los itinerarios correspondientes a las rutas, caminos y senderos de distinta naturaleza independientemente de la tipología del trazado físico sobre el que se apoyan. Dichos datos pueden proceder de la *Información Geográfica de Referencia de Redes de Transporte (IGR-RT)* que edita el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuye el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), que a su vez recoge los datos de la base de datos de direcciones «Cartociudad» gestionada por el IGN, de los proyectos de callejeros mantenidos por algunas administraciones regionales, y de los callejeros municipales.

#### Geometría:

Línea

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |camino_de_santiago| |
| | |ruta| |
| | |ruta_parque_nacional| |
| | |ruta_via_verde| |
| | |sendero_europeo| |
| | |sendero_gran_recorrido| |
| | |sendero_local| |
| | |sendero_pequeño_recorrido| |
| | |sendero_regional| |
| | |sendero_urbano| |
|`nombre`|string|[tipo_vial]+' '+[denominacion]|Denominación de la vía urbana|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|[todos los elementos]| | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|
