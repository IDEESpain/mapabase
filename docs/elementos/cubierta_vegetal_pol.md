## cubierta_vegetal_pol
<br />

El elemento «cubierta_vegetal_pol» contiene los objetos geográficos poligonales de carácter natural que se extraen del *SIOSE (Sistema de Información de Ocupación del Suelo de España)* que distribuye el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), correspondientes a los siguientes códigos CODIIGE de cubierta terrestre:

- 150 Asentamiento agrícola y huerta
- 210 Cultivo herbáceo
- 231 Frutal cítrico
- 232 Frutal no cítrico
- 233 Viñedo
- 234 Olivar
- 235 Otros cultivos leñosos
- 236 Combinación de cultivos leñosos
- 240 Prado
- 250 Combinación de cultivos
- 260 Combinación de cultivos con vegetación
- 311 Bosque de frondosas
- 312 Bosque de coníferas
- 313 Bosque mixto
- 320 Pastizal o herbazal
- 330 Matorral
- 340 Combinación de vegetación
- 351 Playa, duna o arenal
- 352 Roquedo
- 353 Temporalmente desarbolado por incendios
- 354 Suelo desnudo
- 411 Zona húmeda y pantanosa
- 412 Turbera
- 413 Marisma
- 414 Salina
- 516 Glaciar y/o nieve perpetua

#### Geometría:

Polígono

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |asentamiento_agricola_y_huerta| |
| | |bosque_coniferas| |
| | |bosque_frondosas| |
| | |bosque_mixto| |
| | |combinacion_cultivos| |
| | |combinacion_cultivos_con_vegetacion| |
| | |combinacion_cultivos_leñosos| |
| | |combinacion_vegetacion| |
| | |cultivo_herbaceo| |
| | |frutal_citrico| |
| | |frutal_no_citrico| |
| | |glaciar_nieve_perpetua| |
| | |marisma| |
| | |matorral| |
| | |olivar| |
| | |otros_cultivos_leñosos| |
| | |pastizal_herbazal| |
| | |playa_duna_arenal| |
| | |prado| |
| | |roquedo| |
| | |salina| |
| | |suelo_desnudo| |
| | |temporalmente_desarbolado_por_incendios| |
| | |turbera| |
| | |viñedo| |
| | |zona_humeda_pantanosa| |
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=asentamiento_agricola_y_huerta| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=bosque_coniferas| | | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|
|`clase`=bosque_frondosas| | | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|
|`clase`=bosque_mixto| | | | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|
|`clase`=combinacion_cultivos| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=combinacion_cultivos_con_vegetacion| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=combinacion_cultivos_leñosos| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=combinacion_vegetacion| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=cultivo_herbaceo| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=frutal_citrico| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=frutal_no_citrico| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=glaciar_nieve_perpetua| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=marisma| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=matorral| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=olivar| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=otros_cultivos_leñosos| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=pastizal_herbazal| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=playa_duna_arenal| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=prado| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=roquedo| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=salina| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=suelo_desnudo| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=temporalmente_desarbolado_por_incendios| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=turbera| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=viñedo| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|`clase`=zona_humeda_pantanosa| | | | | | | | | | | | | | | |x|x|x|x|x|x|x|x|
|**Filtro**|[**00**](../../niveles/nivel_00)|[**01**](../../niveles/nivel_01)|[**02**](../../niveles/nivel_02)|[**03**](../../niveles/nivel_03)|[**04**](../../niveles/nivel_04)|[**05**](../../niveles/nivel_05)|[**06**](../../niveles/nivel_06)|[**07**](../../niveles/nivel_07)|[**08**](../../niveles/nivel_08)|[**09**](../../niveles/nivel_09)|[**10**](../../niveles/nivel_10)|[**11**](../../niveles/nivel_11)|[**12**](../../niveles/nivel_12)|[**13**](../../niveles/nivel_13)|[**14**](../../niveles/nivel_14)|[**15**](../../niveles/nivel_15)|[**16**](../../niveles/nivel_16)|[**17**](../../niveles/nivel_17)|[**18**](../../niveles/nivel_18)|[**19**](../../niveles/nivel_19)|[**20**](../../niveles/nivel_20)|[**21**](../../niveles/nivel_21)|[**22**](../../niveles/nivel_22)|

