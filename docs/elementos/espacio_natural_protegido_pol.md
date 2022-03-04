## espacio_natural_protegido_pol
<br />

El elemento «espacio_natural_protegido_pol» incluye los objetos geográficos poligonales que definen los perímetros que definen los distintos tipos de Espacios Naturales Protegidos. Los datos pueden provenir de la información geográfica editada por el Instituto Geográfico Nacional (IGN) y distribuida por el Centro Nacional de Información Geográfica (CNIG), así como de la información geográfica de referencia o temática producida por las Comunidades Autónomas u otras administraciones públicas con competencias en la materia.

#### Geometría:

Polígono

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |arbol_singular| |
| | |area_marina_protegida
| | |area_natural_singular| |
| | |area_natural_recreativa
| | |area_privada_de_interes_ecologico
| | |biotopo_protegido| |
| | |corredor_ecologico_y_de_biodiversidad| |
| | |corredores_ecoculturales| |
| | |cuevas| |
| | |enclave_natural| |
| | |humedal_protegido| |
| | |lugar_de_interes_cientifico| |
| | |microrreserva| |
| | |monumento_natural| |
| | |monumento_natural_de_interes_nacional| |
| | |paisaje_protegido| |
| | |paraje_natural| |
| | |paraje_natural_de_interes_nacional| |
| | |paraje_natural_municipal| |
| | |paraje_pintoresco| |
| | |parque_nacional| |
| | |parque_natural| |
| | |parque_periurbano| |
| | |parque_periurbano_de_conservacion_y_ocio| |
| | |parque_regional| |
| | |parque_rural| |
| | |plan_especial_de_proteccion| |
| | |refugio_de_fauna| |
| | |reserva_de_la_biosfera| |
| | |reserva_fluvial| |
| | |reserva_natural| |
| | |reserva_natural_concertada| |
| | |reserva_natural_de_fauna_salvaje| |
| | |reserva_natural_dirigida| |
| | |reserva_natural_especial| |
| | |reserva_natural_integral| |
| | |reserva_natural_parcial| |
| | |sitio_de_interes_cientifico| |
| | |sitio_natural_de_interes_nacional| |
| | |zona_de_especial_conservacion_de_importancia_comunitaria| |
| | |zona_de_especial_proteccion_de_los_valores_naturales| |
| | |zona_de_importancia_comunitaria_lic| |
| | |zona_de_interes_regional| |
| | |zona_de_la_red_ecologica_europea_natura_2000| |
| | |zona_humeda| |
|`nombre`|string|[denominacion]|Denominación oficial|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=arbol_sigular| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=area_marina_protegida| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=area_natural_singular| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=area_natural_recreativa| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=area_privada_de_interes_ecologico| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=biotopo_protegido| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=corredor_ecologico_y_de_biodiversidad| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=corredores_ecoculturales| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=cuevas| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=enclave_natural| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=humedal_protegido| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=lugar_de_interes_cientifico| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=microrreserva| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=monumento_natural| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=monumento_natural_de_interes_nacional| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=paisaje_protegido| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=paraje_natural| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=paraje_natural_de_interes_nacional| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=paraje_natural_municipal| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=paraje_pintoresco| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_nacional| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_natural| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_periurbano| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_periurbano_de_conservacion _y_ocio| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_regional| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=parque_rural| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=plan_especial_de_proteccion| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=refugio_de_fauna| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_de_la_biosfera| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_fluvial| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_concertada| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_de_fauna_salvaje| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_dirigida| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_especial| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_integral| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=reserva_natural_parcial| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=sitio_de_interes_cientifico| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=sitio_natural_de_interes_nacional| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_de_especial_conservacion_de_importancia_comunitaria| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_de_especial_proteccion_de_los_valores_naturales| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_de_importancia_comunitaria_lic| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_de_interes_regional| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_de_la_red_ecologica_europea_natura_2000| | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=zona_humeda| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|**Filtro**|[**00**](../../niveles/nivel_00)|[**01**](../../niveles/nivel_01)|[**02**](../../niveles/nivel_02)|[**03**](../../niveles/nivel_03)|[**04**](../../niveles/nivel_04)|[**05**](../../niveles/nivel_05)|[**06**](../../niveles/nivel_06)|[**07**](../../niveles/nivel_07)|[**08**](../../niveles/nivel_08)|[**09**](../../niveles/nivel_09)|[**10**](../../niveles/nivel_10)|[**11**](../../niveles/nivel_11)|[**12**](../../niveles/nivel_12)|[**13**](../../niveles/nivel_13)|[**14**](../../niveles/nivel_14)|[**15**](../../niveles/nivel_15)|[**16**](../../niveles/nivel_16)|[**17**](../../niveles/nivel_17)|[**18**](../../niveles/nivel_18)|[**19**](../../niveles/nivel_19)|[**20**](../../niveles/nivel_20)|[**21**](../../niveles/nivel_21)|[**22**](../../niveles/nivel_22)|
