## nombre_poblacion_construccion_pto
<br />

El elemento «nombre_poblacion_construccion_pto» contiene las referencias puntuales de los nombres geográficos de poblaciones y construcciones incluidos en el *Nomenclátor Geográfico Básico de España (NGBE)*, mantenido por el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuido como Información Geográfica de Referencia por el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), así como los nombres geográficos oficiales de similar naturaleza que se encuentran recogidos en la cartografía topográfica regional y nomenclátores geográficos editados por las Comunidades Autónomas.

#### Geometría:

Punto

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |barrio| |
| | |capital_comunidad_autonoma_ciudad_autonoma| |
| | |capital_eatim| |
| | |capital_estado| |
| | |capital_municipio| |
| | |capital_provincia| |
| | |construccion_instalacion_abierta| |
| | |distrito_municipal| |
| | |eatim| |
| | |edificacion| |
| | |entidad_colectiva| |
| | |entidad_menor_poblacion| |
| | |entidad_singular| |
| | |entidad_singular_INE| |
| | |hito_demarcacion_territorial| |
| | |hito_via_comunicacion| |
| | |infraestructura_transporte_terrestre| |
| | |instalacion_portuaria| |
| | |nucleo_poblacion| |
| | |otra_entidad_menor_poblacion| |
| | |vertice_geodesico| |
|`nombre`|string|[nombre]|Nombre|
|`nombre_alt`|string|[nombre_alternativo]|Nombre alternativo|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=barrio| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=capital_comunidad_autonoma_ciudad_autonoma| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=capital_eatim| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=capital_estado| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=capital_municipio| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=capital_provincia| | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=construccion_instalacion_abierta| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=distrito_municipal| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=eatim| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=edificacion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=entidad_colectiva| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=entidad_menor_poblacion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=entidad_singular| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=entidad_singular_INE| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=hito_demarcacion_territorial| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=hito_via_comunicacion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=infraestructura_transporte_terrestre| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=instalacion_portuaria| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=nucleo_poblacion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=otra_entidad_menor_poblacion| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=vertice_geodesico| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|**Filtro**|[**00**](../../niveles/nivel_00)|[**01**](../../niveles/nivel_01)|[**02**](../../niveles/nivel_02)|[**03**](../../niveles/nivel_03)|[**04**](../../niveles/nivel_04)|[**05**](../../niveles/nivel_05)|[**06**](../../niveles/nivel_06)|[**07**](../../niveles/nivel_07)|[**08**](../../niveles/nivel_08)|[**09**](../../niveles/nivel_09)|[**10**](../../niveles/nivel_10)|[**11**](../../niveles/nivel_11)|[**12**](../../niveles/nivel_12)|[**13**](../../niveles/nivel_13)|[**14**](../../niveles/nivel_14)|[**15**](../../niveles/nivel_15)|[**16**](../../niveles/nivel_16)|[**17**](../../niveles/nivel_17)|[**18**](../../niveles/nivel_18)|[**19**](../../niveles/nivel_19)|[**20**](../../niveles/nivel_20)|[**21**](../../niveles/nivel_21)|[**22**](../../niveles/nivel_22)|
