## ferrocarril_lin
<br />

El elemento «ferrocarril_lin» incluye los objetos geográficos lineales que conforman los tramos de la red de infraestructuras viarias del ferrocarril. La información puede proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuye el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.

#### Geometría:

Línea

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |cremallera| |
| | |funicular| |
| | |metro| |
| | |tranvia| |
| | |tren| |
| | |tren_ligero| |
|`nombre`|string|[denominacion_linea_ferrocarril]|Denominación|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|
|`puente`|string| |Puente (Sí/No)
| | |T|Sí|
| | |F|No|
|`tipo_tramo`|string|[referencia]|Tipo de tramo|
| | |otro| |
| | |playa_de_vias| |
| | |troncal| |
|`tunel`|string| |Puente (Sí/No)
| | |T|Sí|
| | |F|No|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=cremallera| | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|
|`clase`=funicular| | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|
|`clase`=metro| | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|
|`clase`=tren| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=tren_ligero| | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|
