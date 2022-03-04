## nombre_division_administrativa_pto
<br />

El elemento «nombre_división_Administrativa_pto» contiene las referencias puntuales de los nombres geográficos relativos a divisiones administrativas que se encuentran recogidos en el *Nomenclátor Geográfico Básico de España (NGBE)*, mantenido por el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuido como Información Geográfica de Referencia por el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), así como los nombres geográficos oficiales producidos por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.

#### Geometría:

Punto

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |ambito_inferior_a_municipio| |
| | |ciudad_autonomia| |
| | |comarca_administrativa| |
| | |comunidad_autonoma| |
| | |isla_administrativa| |
| | |jurisdiccion| |
| | |municipio| |
| | |nacion| |
| | |provincia| |
|`nombre`|string|[nombre]|Nombre|
|`nombre_alt`|string|[nombre_alternativo]|Nombre alternativo|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=ambito_inferior_a_municipio| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=ciudad_autonoma| | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=comarca_administrativa| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=comunidad_autonoma| | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=isla_administrativa| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=jurisdiccion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=municipio| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=nacion| | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=provincia| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|

