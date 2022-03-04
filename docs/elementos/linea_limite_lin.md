## linea_limite_lin
<br />

El elemento «linea_limite_lin» contiene la descripción geométrica de las Líneas Límite Municipales, Provinciales y Autonómicas, que responde a la interpretación de los títulos jurídicos de delimitación, inscritos en el *Registro Central de Cartografía (RCC)* (Real Decreto 1545/2007). Esta información es distribuida oficialmente por el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es).

#### Geometría:

Línea

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |limite_autonomico| |
| | |limite_provincial| |
| | |limite_municipal| |
|`nombre`|string|[NAME_BOUND]|Denominación|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|
|`ref`|string|[NATIONALCO]|Referencia|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=limite_autonomico| | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=limite_municipal| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=limite_provincial| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|