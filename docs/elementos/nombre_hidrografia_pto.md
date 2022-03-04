## nombre_hidrografia_pto
<br />

El elemento «nombre_hidrografia_pto» contiene las referencias puntuales de los nombres geográficos de los distintos elementos de naturaleza hidrográfica continental y orográfica marítima y costera que se encuentran incluidos en el *Nomenclátor Geográfico Básico de España (NGBE)*, mantenido por el [*Instituto Geográfico Nacional (IGN)*](https://www.ign.es) y distribuido como Información Geográfica de Referencia por el [*Centro Nacional de Información Geográfica (CNIG)*](https://www.cnig.es), así como los nombres geográficos oficiales de similar naturaleza que se encuentran recogidos en la cartografía topográfica regional y nomenclátores geográficos editados por las Comunidades Autónomas.

#### Geometría:

Punto

#### Atributos y dominios de valores:

|Atributo|Tipo|Valor|Observaciones|
|---|---|---|---|
|`clase`|string| |Clase de objeto|
| | |curso_artificial_agua| |
| | |curso_natural_agua| |
| | |embalse| |
| | |entrante_costero_estrecho_maritimo| |
| | |glaciar| |
| | |hidronimo_puntual| |
| | |isla| |
| | |mar| |
| | |masa_agua| |
| | |otro_relieve_costero| |
| | |playa| |
| | |relieve_submarino| |
| | |saliente_costero| |
|`nombre`|string|[nombre]|Nombre|
|`nombre_alt`|string|[nombre_alternativo]|Nombre alternativo|
|`proveedor`|string|[codigo_proveedor]|Proveedor de la información (lista controlada)|

#### Asignación a capas:

|Filtro|[00](../../niveles/nivel_00)|[01](../../niveles/nivel_01)|[02](../../niveles/nivel_02)|[03](../../niveles/nivel_03)|[04](../../niveles/nivel_04)|[05](../../niveles/nivel_05)|[06](../../niveles/nivel_06)|[07](../../niveles/nivel_07)|[08](../../niveles/nivel_08)|[09](../../niveles/nivel_09)|[10](../../niveles/nivel_10)|[11](../../niveles/nivel_11)|[12](../../niveles/nivel_12)|[13](../../niveles/nivel_13)|[14](../../niveles/nivel_14)|[15](../../niveles/nivel_15)|[16](../../niveles/nivel_16)|[17](../../niveles/nivel_17)|[18](../../niveles/nivel_18)|[19](../../niveles/nivel_19)|[20](../../niveles/nivel_20)|[21](../../niveles/nivel_21)|[22](../../niveles/nivel_22)|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|`clase`=curso_artificial_agua| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=curso_natural_agua| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=embalse| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=entrante_costero_estrecho_maritimo| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=glaciares| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=hidronimo_puntual| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=isla| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=mar| | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=masa_agua| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=otro_relieve_costero| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`=playa| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`= relieve_submarino| | | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|
|`clase`= saliente_costero| | | | | | | | | | |x|x|x|x|x|x|x|x|x|x|x|x|x|
