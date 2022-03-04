## hidrografia_lin
<br />

El elemento «hidrografia_lin» comprende los objetos geográficos lineales de carácter natural y artificial que forman la red hidrográfica de España. Los datos pueden provenir de la *Información Geográfica de Referencia de Hidrografía (IGR-HY)* que edita el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuye el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), así como de la cartografía topográfica de referencia y cartografía temática editada por las Comunidades Autónomas y otras instituciones competentes en la materia.

#### Geometría:

Línea

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |acequia| |
| | |canal| |
| | |curso_natural| |
| | |tuberia| |
|`nombre`|string|[denominacion]|Denominación oficial|
|`orden`|string| |Nivel jerárquico|
| | |primero| |
| | |quinto_sexto| |
| | |segundo| |
| | |tercero_cuarto| |
| | |otro| |
|`persistencia`|string| |Persistencia|
| | |estacional| |
| | |esporadico| |
| | |permanente| |
| | |otro| |
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`orden`=otro| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`orden`=primero| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`orden`=quinto_sexto| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`orden`=segundo| | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`orden`=tercero_cuarto| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
