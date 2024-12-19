

CREATE TABLE public.estacion_autobus_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.estacion_autobus_pto OWNER TO postgres;
CREATE INDEX sidx_estacion_autobus_pto_the_geom ON public.estacion_autobus_pto USING gist (the_geom);
COMMENT ON TABLE estacion_autobus_pto IS 'El elemento «estacion_autobus_pto» comprende los objetos geográficos puntuales que representan las estaciones de autobuses. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN estacion_autobus_pto.clase IS 'estacion_autobus:Clase de objeto';
COMMENT ON COLUMN estacion_autobus_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN estacion_autobus_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.autovia_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('autovia','autovia_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.autovia_lin OWNER TO postgres;
CREATE INDEX sidx_autovia_lin_the_geom ON public.autovia_lin USING gist (the_geom);
COMMENT ON TABLE autovia_lin IS 'El elemento «autovia_lin» recoge la información lineal de los tramos de carretera clasificados como
                «Autovía», así como sus enlaces. Los datos pueden provenir de la Información Geográfica de
                    Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN autovia_lin.clase IS '';
COMMENT ON COLUMN autovia_lin.nombre IS '[denominacion_autovia]:Denominación';
COMMENT ON COLUMN autovia_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN autovia_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN autovia_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN autovia_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN autovia_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio,
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.lamina_agua_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('abrevadero','balsa_alberca_estanque','embalse','piscina','lago','lamina_agua','marisma','vaso_salina','zona_humeda')),
	persistencia character varying CHECK (persistencia in ('estacional','esporadico','permanente','otro')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.lamina_agua_pol OWNER TO postgres;
CREATE INDEX sidx_lamina_agua_pol_the_geom ON public.lamina_agua_pol USING gist (the_geom);
COMMENT ON TABLE lamina_agua_pol IS 'El elemento «lamina_agua_pol» comprende los objetos geográficos que representan las superficies de agua
                de carácter natural o artificial. Los datos pueden provenir de la Información Geográfica de
                    Referencia de Hidrografía (IGR-HY) que edita el Instituto
                        Geográfico Nacional (IGN)y distribuye el Centro
                        Nacional de Información Geográfica (CNIG) , así como de la cartografía topográfica de
                referencia y cartografía temática editada por las Comunidades Autónomas y otras instituciones
                competentes en la materia.';
COMMENT ON COLUMN lamina_agua_pol.clase IS '';
COMMENT ON COLUMN lamina_agua_pol.persistencia IS 'otro:Este valor puede utilizarse en el caso de que no aplique indicar persistencia';
COMMENT ON COLUMN lamina_agua_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN lamina_agua_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.senda_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.senda_lin OWNER TO postgres;
CREATE INDEX sidx_senda_lin_the_geom ON public.senda_lin USING gist (the_geom);
COMMENT ON TABLE senda_lin IS 'El elemento «senda_lin» comprende los objetos geográficos lineales por los que puede circular ganado y personas, cuya anchura es inferior a la de un camino. Estos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN senda_lin.clase IS 'senda:Clase de objeto';
COMMENT ON COLUMN senda_lin.nombre IS '[denominacion_camino]:Denominación del camino';
COMMENT ON COLUMN senda_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.area_servicio_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('area_servicio','area_descanso')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.area_servicio_pto OWNER TO postgres;
CREATE INDEX sidx_area_servicio_pto_the_geom ON public.area_servicio_pto USING gist (the_geom);
COMMENT ON TABLE area_servicio_pto IS 'El elemento «area_servicio_pto» incluye los elementos geográficos puntuales que representan las áreas de
                servicio.. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de
                    Transporte (IGR-RT) que edita el Instituto Geográfico Nacional
                        (IGN)y distribuye el Centro Nacional de Información
                        Geográfica (CNIG) , así como de la información geográfica de referencia producida por
                las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN area_servicio_pto.clase IS '';
COMMENT ON COLUMN area_servicio_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN area_servicio_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.provincia_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	codigo character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.provincia_pol OWNER TO postgres;
CREATE INDEX sidx_provincia_pol_the_geom ON public.provincia_pol USING gist (the_geom);
COMMENT ON TABLE provincia_pol IS '';
COMMENT ON COLUMN provincia_pol.clase IS 'provincia:Clase de objeto';
COMMENT ON COLUMN provincia_pol.codigo IS '[codigo]:Nationalcode según las especificaciones de datos INSPIRE para unidades administrativas. Código del país + Código de la CC. AA. + Código de la provincia + 5 dígitos 00000
    Ejemplo: Provincia de Valencia/València: 34104600000. 34+10+46+00000';
COMMENT ON COLUMN provincia_pol.nombre IS '[denominación_provincia]:Denominación oficial de la provincia';
COMMENT ON COLUMN provincia_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.autopista_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('autopista','autopista_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.autopista_lin OWNER TO postgres;
CREATE INDEX sidx_autopista_lin_the_geom ON public.autopista_lin USING gist (the_geom);
COMMENT ON TABLE autopista_lin IS 'El elemento «autopista_lin» recoge la información lineal de los tramos de carretera clasificados como
                «Autopista», así como sus enlaces. Los datos pueden provenir de la Información Geográfica de
                    Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN autopista_lin.clase IS '';
COMMENT ON COLUMN autopista_lin.nombre IS '[denominacion_autopista]:Denominación';
COMMENT ON COLUMN autopista_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN autopista_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN autopista_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN autopista_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN autopista_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.estacion_ferrocarril_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying,
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.estacion_ferrocarril_pto OWNER TO postgres;
CREATE INDEX sidx_estacion_ferrocarril_pto_the_geom ON public.estacion_ferrocarril_pto USING gist (the_geom);
COMMENT ON TABLE estacion_ferrocarril_pto IS 'El elemento «estacion_ferrocarril_pto» comprende los objetos geográficos puntuales que representan las
                estaciones de ferrocarril. Los datos pueden provenir de la Información Geográfica de Referencia de
                    Redes de Transporte (IGR-RT) que edita el Instituto Geográfico
                        Nacional (IGN)y distribuye el Centro Nacional de
                        Información Geográfica (CNIG) , así como de la información geográfica de referencia
                producida por las Comunidades Autónomas u otras administraciones públicas con competencias
                cartográficas.';
COMMENT ON COLUMN estacion_ferrocarril_pto.clase IS 'estacion_ferrocarril:Clase de objeto';
COMMENT ON COLUMN estacion_ferrocarril_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN estacion_ferrocarril_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN estacion_ferrocarril_pto.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.instalacion_tratamiento_aguas_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_tratamiento_aguas_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_tratamiento_aguas_pol_the_geom ON public.instalacion_tratamiento_aguas_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_tratamiento_aguas_pol IS '';
COMMENT ON COLUMN instalacion_tratamiento_aguas_pol.clase IS 'instalacion_tratamiento_aguas:Clase de objeto';
COMMENT ON COLUMN instalacion_tratamiento_aguas_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_tratamiento_aguas_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.instalacion_deportiva_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('zona_deportiva','campo_futbol','instalacion_deportiva','pista_deportiva','campo_golf','circuito','estacion_invernal')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_deportiva_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_deportiva_pol_the_geom ON public.instalacion_deportiva_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_deportiva_pol IS '';
COMMENT ON COLUMN instalacion_deportiva_pol.clase IS '';
COMMENT ON COLUMN instalacion_deportiva_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_deportiva_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.peaje_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.peaje_pto OWNER TO postgres;
CREATE INDEX sidx_peaje_pto_the_geom ON public.peaje_pto USING gist (the_geom);
COMMENT ON TABLE peaje_pto IS 'El elemento «peaje_pto» incluye los elementos geográficos puntuales que representan los puntos de acceso a las vías de comunicación mediante peaje. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN peaje_pto.clase IS 'peaje:Clase de objeto';
COMMENT ON COLUMN peaje_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN peaje_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_territorios_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('linea_limite','linea_especial')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_territorios_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_territorios_lin_the_geom ON public.contexto_territorios_lin USING gist (the_geom);
COMMENT ON TABLE contexto_territorios_lin IS '';
COMMENT ON COLUMN contexto_territorios_lin.clase IS '';
COMMENT ON COLUMN contexto_territorios_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_territorios_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_territorios_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_nombre_orografia_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('sierra','otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_orografia_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_orografia_lin_the_geom ON public.contexto_nombre_orografia_lin USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_orografia_lin IS '';
COMMENT ON COLUMN contexto_nombre_orografia_lin.clase IS '';
COMMENT ON COLUMN contexto_nombre_orografia_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_orografia_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_orografia_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_territorios_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('tierra_firme','mar')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_territorios_pol OWNER TO postgres;
CREATE INDEX sidx_contexto_territorios_pol_the_geom ON public.contexto_territorios_pol USING gist (the_geom);
COMMENT ON TABLE contexto_territorios_pol IS '';
COMMENT ON COLUMN contexto_territorios_pol.clase IS '';
COMMENT ON COLUMN contexto_territorios_pol.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_territorios_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_territorios_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.ferrocarril_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('cremallera','funicular','metro','tranvia','tren','tren_ligero')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	tipo_tramo character varying CHECK (tipo_tramo in ('otro','playa_de_vias','troncal')),
	tunel character varying CHECK (tunel in ('T','F')));
ALTER TABLE public.ferrocarril_lin OWNER TO postgres;
CREATE INDEX sidx_ferrocarril_lin_the_geom ON public.ferrocarril_lin USING gist (the_geom);
COMMENT ON TABLE ferrocarril_lin IS '';
COMMENT ON COLUMN ferrocarril_lin.clase IS '';
COMMENT ON COLUMN ferrocarril_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';
COMMENT ON COLUMN ferrocarril_lin.nombre IS '[denominacion_linea_ferrocarril]:Denominación';
COMMENT ON COLUMN ferrocarril_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN ferrocarril_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN ferrocarril_lin.tipo_tramo IS '';
COMMENT ON COLUMN ferrocarril_lin.tunel IS 'T:Sí	F:No';


CREATE TABLE public.contexto_nombre_orografia_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('montaña','saliente_costero','otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_orografia_pto OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_orografia_pto_the_geom ON public.contexto_nombre_orografia_pto USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_orografia_pto IS '';
COMMENT ON COLUMN contexto_nombre_orografia_pto.clase IS '';
COMMENT ON COLUMN contexto_nombre_orografia_pto.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_orografia_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_orografia_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.ferrocarril_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('elemento_infraestructura','perimetro_infraestructura')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.ferrocarril_pol OWNER TO postgres;
CREATE INDEX sidx_ferrocarril_pol_the_geom ON public.ferrocarril_pol USING gist (the_geom);
COMMENT ON TABLE ferrocarril_pol IS 'El elemento «ferrocarril_pol» comprende los objetos geográficos poligonales relativos a las instalaciones e infraestructuras de ferrocarril. Elementos poligonales constructivos de un ferrocarril que no son estación de ferrocarril, que deben incluirse en la clase estacion_ferrocarril_pol. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN ferrocarril_pol.clase IS '';
COMMENT ON COLUMN ferrocarril_pol.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';
COMMENT ON COLUMN ferrocarril_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN ferrocarril_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_nombre_orografia_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('depresion','llanura','meseta','peninsula','desierto','isla','archipielago','otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_orografia_pol OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_orografia_pol_the_geom ON public.contexto_nombre_orografia_pol USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_orografia_pol IS '';
COMMENT ON COLUMN contexto_nombre_orografia_pol.clase IS '';
COMMENT ON COLUMN contexto_nombre_orografia_pol.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_orografia_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_orografia_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.aparcamiento_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('aparcamiento','aparcamiento_invernal','aparcamiento_seguro')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.aparcamiento_pol OWNER TO postgres;
CREATE INDEX sidx_aparcamiento_pol_the_geom ON public.aparcamiento_pol USING gist (the_geom);
COMMENT ON TABLE aparcamiento_pol IS 'El elemento «aparcamiento_pol» comprende los objetos geográficos superficiales que representan las
                instalaciones de aparcamiento de vehículos. Los datos pueden provenir de la Información Geográfica
                    de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN aparcamiento_pol.clase IS 'aparcamiento:Área en superficie destinada habitualmente a aparcar vehículos. No se consideran los aparcamientos en línea o batería en los laterales de las calles.	aparcamiento_invernal:Aparcamiento para almacenamiento de vehículos pesados cuando, debido a las condiciones climatológicas, no sea posible su circulación.	aparcamiento_seguro:Aparcamiento para camiones y vehículos comerciales provisto de instalaciones de protección y seguridad y acceso a través de la Red Transeuropea de Carreteras y la Red de Carreteras del Estado.';
COMMENT ON COLUMN aparcamiento_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN aparcamiento_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.instalacion_tratamiento_residuos_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_tratamiento_residuos_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_tratamiento_residuos_pol_the_geom ON public.instalacion_tratamiento_residuos_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_tratamiento_residuos_pol IS '';
COMMENT ON COLUMN instalacion_tratamiento_residuos_pol.clase IS 'instalacion_tratamiento_residuos:Clase de objeto';
COMMENT ON COLUMN instalacion_tratamiento_residuos_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_tratamiento_residuos_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.camino_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')));
ALTER TABLE public.camino_lin OWNER TO postgres;
CREATE INDEX sidx_camino_lin_the_geom ON public.camino_lin USING gist (the_geom);
COMMENT ON TABLE camino_lin IS 'El elemento «camino_lin» incluye el trazado lineal de los distintos tipos de caminos, así como sus enlaces. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN camino_lin.clase IS 'camino:Clase de objeto';
COMMENT ON COLUMN camino_lin.nombre IS '[denominacion_camino]:Denominación del camino';
COMMENT ON COLUMN camino_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN camino_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN camino_lin.ref IS '[referencia]:Referencia o código del camino. Si no se conoce o no es aplicable dejarlo en blanco';
COMMENT ON COLUMN camino_lin.tunel IS 'T:Sí	F:No';


CREATE TABLE public.nombre_transporte_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('aerodromo','aeropuerto','camino_via_pecuaria','carretera','ferrocarril','infraestructura_transporte_terrestre','instalacion_portuaria','pista_aviacion_helipuerto','puerto','via_maritima','via_urbana')),
	nombre character varying,
	nombre_alt character varying,
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	proveedor character varying);
ALTER TABLE public.nombre_transporte_pto OWNER TO postgres;
CREATE INDEX sidx_nombre_transporte_pto_the_geom ON public.nombre_transporte_pto USING gist (the_geom);
COMMENT ON TABLE nombre_transporte_pto IS 'El elemento «nombre_transporte_pto» contiene las referencias puntuales de los nombres geográficos relativos al transporte recogidos en el Nomenclátor Geográfico Básico de España (NGBE) , mantenido por el Instituto Geográfico Nacional (IGN)y distribuido como Información Geográfica de Referencia por el Centro Nacional de Información Geográfica (CNIG) , así como los nombres geográficos oficiales de similar naturaleza que se encuentran recogidos en la cartografía topográfica regional y nomenclátores geográficos editados por las Comunidades Autónomas.';
COMMENT ON COLUMN nombre_transporte_pto.clase IS '';
COMMENT ON COLUMN nombre_transporte_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_transporte_pto.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_transporte_pto.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_transporte_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.aerodromo_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('aerodromo','aerodromo_helipuerto','deportivo_recreativo','helipuerto','hidroaerodromo')),
	nombre character varying,
	proveedor character varying,
	ref character varying,
	tipo character varying CHECK (tipo in ('internacional','no_internacional')),
	uso character varying CHECK (uso in ('civil','militar','mixto','otro')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.aerodromo_pto OWNER TO postgres;
CREATE INDEX sidx_aerodromo_pto_the_geom ON public.aerodromo_pto USING gist (the_geom);
COMMENT ON TABLE aerodromo_pto IS 'El elemento «aerodromo_pto» comprende los objetos geográficos puntuales relativos a las instalaciones y
                los servicios de aviación civil, militar y recreativa. Los datos pueden provenir de la Información
                    Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN aerodromo_pto.clase IS '';
COMMENT ON COLUMN aerodromo_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN aerodromo_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN aerodromo_pto.ref IS '[designador]:Referencia o nombre abreviado. Si no se conoce o no es aplicable dejarlo en blanco';
COMMENT ON COLUMN aerodromo_pto.tipo IS '';
COMMENT ON COLUMN aerodromo_pto.uso IS 'otro:Este valor puede utilizarse en el caso de que no aplique indicar el uso, 
                            o que sea un uso diferente a los contemplados en el listado';
COMMENT ON COLUMN aerodromo_pto.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.conduccion_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('conduccion','conduccion_agua','conduccion_comunicacion','conduccion_energia','conduccion_gas','conduccion_combustible','conduccion_saneamiento')),
	proveedor character varying);
ALTER TABLE public.conduccion_lin OWNER TO postgres;
CREATE INDEX sidx_conduccion_lin_the_geom ON public.conduccion_lin USING gist (the_geom);
COMMENT ON TABLE conduccion_lin IS '';
COMMENT ON COLUMN conduccion_lin.clase IS '';
COMMENT ON COLUMN conduccion_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.construccion_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('acueducto','auxiliar_construido','auxiliar_construido_vial','cercado','compuerta','construccion','construccion_ligera','escollera','muelle','muralla','muro','muro_contención','pantalán','pasarela','presa','puente','transporte_suspendido','túnel')),
	proveedor character varying);
ALTER TABLE public.construccion_lin OWNER TO postgres;
CREATE INDEX sidx_construccion_lin_the_geom ON public.construccion_lin USING gist (the_geom);
COMMENT ON TABLE construccion_lin IS '';
COMMENT ON COLUMN construccion_lin.clase IS 'auxiliar_construido:Otros elementos construidos, que pueden formar parte de otras construcciones. Su objetivo es servir de relleno 
                            cartográfico para dar detalle a la cartografía. 
                            Ejemplos: bordillos, escaleras, obras de fábrica, 
                            límites de explanadas, toboganes y atracciones de 
                            grandes dimensiones, vado, transporte suspendido etc.	auxiliar_construido_vial:Otros elementos construidos de carácter viario que no pertenecen a 
                            la red de transporte. Su objetivo es servir de relleno cartográfico 
                            para dar detalle a la cartografía. Ejemplos: eje de pistas de competición 
                            en circuitos, caminos dentro de parques, cementerios y 
                            otras infraestructuras, etc.	compuerta:Puerta que se encuentra generalmente en corrientes artificiales empleada para regular el flujo del agua.	construccion:Construcción con entidad propia, por tanto no es un elemento de otra construcción. Clase para los objetos que no pueden incluirse en otro tipo de construcciones.	construccion_ligera:Construcciones ligeras con entidad propia, por tanto no es un elemento de otra construcción. Clase para los objetos que no pueden incluirse en otro tipo de construcciones lineales.	transporte_suspendido:Remontador mecánico en que los vehículos están suspendidos de uno o más cables';
COMMENT ON COLUMN construccion_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_nombre_hidrografia_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('mar','llanura_abisal','cuenca_submarina','golfo_bahia','monte_submarino','meseta_submarina','plataforma_continental','banco','playa','otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_hidrografia_pol OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_hidrografia_pol_the_geom ON public.contexto_nombre_hidrografia_pol USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_hidrografia_pol IS '';
COMMENT ON COLUMN contexto_nombre_hidrografia_pol.clase IS '';
COMMENT ON COLUMN contexto_nombre_hidrografia_pol.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_hidrografia_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_hidrografia_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.altimetria_pto (
	the_geom public.geometry(Point,25830),
	altitud integer,
	clase character varying CHECK (clase in ('punto_acotado','punto_elevado')),
	proveedor character varying);
ALTER TABLE public.altimetria_pto OWNER TO postgres;
CREATE INDEX sidx_altimetria_pto_the_geom ON public.altimetria_pto USING gist (the_geom);
COMMENT ON TABLE altimetria_pto IS 'El elemento «altimetria_pto» incluye la información puntual relativa a puntos acotados sobre el terreno. Los datos pueden provenir de la Base Topográfica Nacional 1:25.000 (BTN25) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información topográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN altimetria_pto.altitud IS '[altitud]:Altitud';
COMMENT ON COLUMN altimetria_pto.clase IS '';
COMMENT ON COLUMN altimetria_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_lamina_agua_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('rio','embalse','lago','salina','zona_pantanosa','albufera','glaciar_hielo','otros')),
	esp integer,
	nombre character varying,
	orden character varying,
	persistencia character varying,
	proveedor character varying);
ALTER TABLE public.contexto_lamina_agua_pol OWNER TO postgres;
CREATE INDEX sidx_contexto_lamina_agua_pol_the_geom ON public.contexto_lamina_agua_pol USING gist (the_geom);
COMMENT ON TABLE contexto_lamina_agua_pol IS '';
COMMENT ON COLUMN contexto_lamina_agua_pol.clase IS '';
COMMENT ON COLUMN contexto_lamina_agua_pol.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_lamina_agua_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_lamina_agua_pol.orden IS '';
COMMENT ON COLUMN contexto_lamina_agua_pol.persistencia IS '';
COMMENT ON COLUMN contexto_lamina_agua_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.instalacion_militar_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_militar_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_militar_pol_the_geom ON public.instalacion_militar_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_militar_pol IS '';
COMMENT ON COLUMN instalacion_militar_pol.clase IS 'instalacion_militar:Clase de objeto';
COMMENT ON COLUMN instalacion_militar_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_militar_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.manzana_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	proveedor character varying);
ALTER TABLE public.manzana_pol OWNER TO postgres;
CREATE INDEX sidx_manzana_pol_the_geom ON public.manzana_pol USING gist (the_geom);
COMMENT ON TABLE manzana_pol IS '';
COMMENT ON COLUMN manzana_pol.clase IS 'manzana:Clase de objeto';
COMMENT ON COLUMN manzana_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.estacion_autobus_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.estacion_autobus_pol OWNER TO postgres;
CREATE INDEX sidx_estacion_autobus_pol_the_geom ON public.estacion_autobus_pol USING gist (the_geom);
COMMENT ON TABLE estacion_autobus_pol IS 'El elemento «estacion_autobus_pol» comprende los objetos geográficos superficiales que representan las estaciones de autobuses. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN estacion_autobus_pol.clase IS 'estacion_autobus:Clase de objeto';
COMMENT ON COLUMN estacion_autobus_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN estacion_autobus_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.linea_limite_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('limite_nacional','limite_autonomico','limite_provincial','limite_municipal')),
	nombre character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.linea_limite_lin OWNER TO postgres;
CREATE INDEX sidx_linea_limite_lin_the_geom ON public.linea_limite_lin USING gist (the_geom);
COMMENT ON TABLE linea_limite_lin IS '';
COMMENT ON COLUMN linea_limite_lin.clase IS '';
COMMENT ON COLUMN linea_limite_lin.nombre IS '[NAME_BOUND]:Denominación';
COMMENT ON COLUMN linea_limite_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN linea_limite_lin.ref IS '[NATIONALCODE]:Atributo nationalcode de líneas límite';


CREATE TABLE public.construccion_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('construccion','construccion_ligera','deposito','escollera','muro','puente','presa','torre')),
	proveedor character varying);
ALTER TABLE public.construccion_pol OWNER TO postgres;
CREATE INDEX sidx_construccion_pol_the_geom ON public.construccion_pol USING gist (the_geom);
COMMENT ON TABLE construccion_pol IS '';
COMMENT ON COLUMN construccion_pol.clase IS 'construccion:Construcción con entidad propia, por tanto no es un elemento de otra construcción. Clase para los objetos que no pueden incluirse en otro tipo de construcciones.	construccion_ligera:Construcciones ligeras con entidad propia, por tanto no es un elemento de otra construcción. Clase para los objetos que no pueden incluirse en otro tipo de construcciones poligonales.	torre:Torre fortificada, torre defensiva, torreón, torre campanario. Estructura o armazón de cierta altura construido para instalar algún elemento elevado respecto al suelo o realizar algún tipo de actividad sobre él. Se incluyen aquí las torres y torreones históricos. No se incluyen en esta clase las estructuras o armazones donde se realizan labores de vigilancia cinegética, contra incendios u otras vigilancias.';
COMMENT ON COLUMN construccion_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_industrial_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('area_industrial','explotacion_minera','poligono_industrial','zona_industrial')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_industrial_pol OWNER TO postgres;
CREATE INDEX sidx_zona_industrial_pol_the_geom ON public.zona_industrial_pol USING gist (the_geom);
COMMENT ON TABLE zona_industrial_pol IS '';
COMMENT ON COLUMN zona_industrial_pol.clase IS '';
COMMENT ON COLUMN zona_industrial_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_industrial_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.carretera_general_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera','carretera_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.carretera_general_lin OWNER TO postgres;
CREATE INDEX sidx_carretera_general_lin_the_geom ON public.carretera_general_lin USING gist (the_geom);
COMMENT ON TABLE carretera_general_lin IS 'El elemento «carretera_general_lin» incluye la información geográfica lineal de los tramos que conforman
                las carreteras pertenecientes a la Red General de Carreteras. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_general_lin.clase IS '';
COMMENT ON COLUMN carretera_general_lin.nombre IS '[denominacion_carretera]:Denominación';
COMMENT ON COLUMN carretera_general_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_general_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_general_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN carretera_general_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_general_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.instalacion_energia_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('eolica','instalacion_energia','nuclear','solar','termica')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_energia_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_energia_pol_the_geom ON public.instalacion_energia_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_energia_pol IS '';
COMMENT ON COLUMN instalacion_energia_pol.clase IS 'instalacion_energia:Otras instalaciones de energía que no se pueden clasificar en el resto de clases';
COMMENT ON COLUMN instalacion_energia_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_energia_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.carretera_pk_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.carretera_pk_pto OWNER TO postgres;
CREATE INDEX sidx_carretera_pk_pto_the_geom ON public.carretera_pk_pto USING gist (the_geom);
COMMENT ON TABLE carretera_pk_pto IS 'El elemento «carretera_pk_pto» incluye los elementos geográficos puntuales que representan los puntos
                kilométricos de los distintos tipos de carretera. Los datos pueden provenir de la Información
                    Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_pk_pto.clase IS 'pk_carretera:Clase de objeto';
COMMENT ON COLUMN carretera_pk_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_pk_pto.ref IS '[referencia]:Identificador del PK. Si no se conoce o no es aplicable dejarlo en blanco';


CREATE TABLE public.espacio_natural_protegido_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('árbol_singular','área_marina_protegida','área_natural_de_especial_interés','área_natural_recreativa','área_natural_singular','área_privada_de_interés_ecológico','biotopo_protegido','corredor_ecológico_y_de_biodiversidad','corredores_ecoculturales','cuevas','enclave_natural','espacio_protegido_red_natura_2000','humedal_protegido','lugar_de_interés_científico','microrreserva','monumento_natural','monumento_natural_de_interés_nacional','paisaje_protegido','paraje_natural','paraje_natural_de_interés_nacional','paraje_natural_municipal','paraje_pintoresco','parque_nacional','parque_natural','parque_periurbano','parque_periurbano_de_conservación_y_ocio','parque_regional','parque_rural','plan_especial_de_protección','refugio_de_fauna','reserva_de_fauna','reserva_de_la_biosfera','reserva_fluvial','reserva_integral','reserva_natural','reserva_natural_concertada','reserva_natural_de_fauna_salvaje','reserva_natural_dirigida','reserva_natural_especial','reserva_natural_integral','reserva_natural_marina','reserva_natural_parcial','reservas_marinas','sitio_de_interés','sitio_de_interés_científico','sitio_natural_de_interés_nacional','zona_de_especial_conservación_de_importancia_comunitaria','zona_de_importancia_comunitaria_zic','zona_de_interes_regional','zona_de_la_red_ecológica_europea_natura_2000','zona_especial_de_conservación','zonas_húmedas','otros')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.espacio_natural_protegido_pol OWNER TO postgres;
CREATE INDEX sidx_espacio_natural_protegido_pol_the_geom ON public.espacio_natural_protegido_pol USING gist (the_geom);
COMMENT ON TABLE espacio_natural_protegido_pol IS '';
COMMENT ON COLUMN espacio_natural_protegido_pol.clase IS '';
COMMENT ON COLUMN espacio_natural_protegido_pol.nombre IS '[denominacion]:Denominación oficial';
COMMENT ON COLUMN espacio_natural_protegido_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.altimetria_lin (
	the_geom public.geometry(Linestring,25830),
	altitud integer,
	clase character varying CHECK (clase in ('curva_nivel','curva_nivel_depresion')),
	proveedor character varying);
ALTER TABLE public.altimetria_lin OWNER TO postgres;
CREATE INDEX sidx_altimetria_lin_the_geom ON public.altimetria_lin USING gist (the_geom);
COMMENT ON TABLE altimetria_lin IS 'El elemento «altimetria_lin» incluye la información lineal relativa a curvas de nivel. Los datos pueden provenir de la Base Topográfica Nacional 1:25.000 (BTN25) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información topográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN altimetria_lin.altitud IS '[altitud]:Altitud';
COMMENT ON COLUMN altimetria_lin.clase IS '';
COMMENT ON COLUMN altimetria_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_hidrografia_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('curso_natural','otros')),
	esp integer,
	nombre character varying,
	orden character varying CHECK (orden in ('primero','segundo','tercero_cuarto','quinto_sexto','otro')),
	persistencia character varying,
	proveedor character varying);
ALTER TABLE public.contexto_hidrografia_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_hidrografia_lin_the_geom ON public.contexto_hidrografia_lin USING gist (the_geom);
COMMENT ON TABLE contexto_hidrografia_lin IS '';
COMMENT ON COLUMN contexto_hidrografia_lin.clase IS '';
COMMENT ON COLUMN contexto_hidrografia_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_hidrografia_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_hidrografia_lin.orden IS '';
COMMENT ON COLUMN contexto_hidrografia_lin.persistencia IS '';
COMMENT ON COLUMN contexto_hidrografia_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.aerodromo_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('aerodromo','area_estacionamiento','calle_rodaje','helipuerto','pista_aterrizaje')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')),
	nombre character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.aerodromo_pol OWNER TO postgres;
CREATE INDEX sidx_aerodromo_pol_the_geom ON public.aerodromo_pol USING gist (the_geom);
COMMENT ON TABLE aerodromo_pol IS 'El elemento «aerodromo_pol» comprende los objetos geográficos poligonales relativos a las instalaciones y
                los servicios de aviación civil, militar y recreativa. Los datos pueden provenir de la Información
                    Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN aerodromo_pol.clase IS '';
COMMENT ON COLUMN aerodromo_pol.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';
COMMENT ON COLUMN aerodromo_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN aerodromo_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN aerodromo_pol.ref IS '[designador]:Referencia o nombre abreviado. Si no se conoce o no es aplicable dejarlo en blanco';


CREATE TABLE public.peaje_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.peaje_pol OWNER TO postgres;
CREATE INDEX sidx_peaje_pol_the_geom ON public.peaje_pol USING gist (the_geom);
COMMENT ON TABLE peaje_pol IS 'El elemento «peaje_pol» incluye los elementos geográficos superficiales relativos a las zonas de acceso a las vías de comunicación mediante peaje. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN peaje_pol.clase IS 'peaje:Clase de objeto';
COMMENT ON COLUMN peaje_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN peaje_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.puerto_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('astillero_naval','puerto','puerto_comercial','puerto_deportivo','puerto_industrial','puerto_militar','puerto_pesquero','puerto_turistico')),
	nombre character varying,
	proveedor character varying,
	ref character varying,
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.puerto_pto OWNER TO postgres;
CREATE INDEX sidx_puerto_pto_the_geom ON public.puerto_pto USING gist (the_geom);
COMMENT ON TABLE puerto_pto IS 'El elemento «puerto_pto» comprende los objetos geográficos puntuales de referencia relativos a las
                instalaciones y los servicios portuarios de cualquier naturaleza. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN puerto_pto.clase IS '';
COMMENT ON COLUMN puerto_pto.nombre IS '[denominación_puerto]:Denominación oficial del puerto';
COMMENT ON COLUMN puerto_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN puerto_pto.ref IS '[designador]:Referencia o nombre abreviado. Si no se conoce o no es aplicable dejarlo en blanco';
COMMENT ON COLUMN puerto_pto.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.instalacion_educativa_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_educativa_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_educativa_pol_the_geom ON public.instalacion_educativa_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_educativa_pol IS '';
COMMENT ON COLUMN instalacion_educativa_pol.clase IS 'instalacion_educativa:Clase de objeto';
COMMENT ON COLUMN instalacion_educativa_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_educativa_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.hidrografia_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('curso_artificial','curso_natural')),
	persistencia character varying CHECK (persistencia in ('estacional','esporadico','permanente','otro')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.hidrografia_pol OWNER TO postgres;
CREATE INDEX sidx_hidrografia_pol_the_geom ON public.hidrografia_pol USING gist (the_geom);
COMMENT ON TABLE hidrografia_pol IS 'El elemento «hidrografia_pol» comprende los objetos geográficos poligonales de carácter natural y
                artificial que forman la red hidrográfica de España Los datos pueden provenir de la Información
                    Geográfica de Referencia de Hidrografía (IGR-HY) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la cartografía topográfica de referencia y cartografía temática editada por las Comunidades Autónomas
                y otras instituciones competentes en la materia.';
COMMENT ON COLUMN hidrografia_pol.clase IS '';
COMMENT ON COLUMN hidrografia_pol.persistencia IS 'otro:Este valor puede utilizarse en el caso de que no aplique indicar persistencia';
COMMENT ON COLUMN hidrografia_pol.nombre IS '[denominacion]:Denominación oficial';
COMMENT ON COLUMN hidrografia_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_verde_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('parque_jardin','terreno_natural','zona_verde')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_verde_pol OWNER TO postgres;
CREATE INDEX sidx_zona_verde_pol_the_geom ON public.zona_verde_pol USING gist (the_geom);
COMMENT ON TABLE zona_verde_pol IS '';
COMMENT ON COLUMN zona_verde_pol.clase IS '';
COMMENT ON COLUMN zona_verde_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_verde_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.cubierta_vegetal_bosque_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('bosque_arbolado')),
	proveedor character varying);
ALTER TABLE public.cubierta_vegetal_bosque_pol OWNER TO postgres;
CREATE INDEX sidx_cubierta_vegetal_bosque_pol_the_geom ON public.cubierta_vegetal_bosque_pol USING gist (the_geom);
COMMENT ON TABLE cubierta_vegetal_bosque_pol IS '';
COMMENT ON COLUMN cubierta_vegetal_bosque_pol.clase IS '';
COMMENT ON COLUMN cubierta_vegetal_bosque_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_militar_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_militar_pol OWNER TO postgres;
CREATE INDEX sidx_zona_militar_pol_the_geom ON public.zona_militar_pol USING gist (the_geom);
COMMENT ON TABLE zona_militar_pol IS '';
COMMENT ON COLUMN zona_militar_pol.clase IS 'zona_militar:Clase de objeto';
COMMENT ON COLUMN zona_militar_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_militar_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.carretera_otros_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera','carretera_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.carretera_otros_lin OWNER TO postgres;
CREATE INDEX sidx_carretera_otros_lin_the_geom ON public.carretera_otros_lin USING gist (the_geom);
COMMENT ON TABLE carretera_otros_lin IS 'El elemento «carretera_otros_lin» comprende la información geográfica lineal de los trazados viarios que
                atendiendo a las características técnicas propias de una carretera, no tienen una clasificación oficial
                específica como tal, así como sus enlaces. Dichos datos pueden proceder de la Información Geográfica
                    de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_otros_lin.clase IS '';
COMMENT ON COLUMN carretera_otros_lin.nombre IS '[denominacion_carretera]:Denominación de la carretera';
COMMENT ON COLUMN carretera_otros_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_otros_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_otros_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN carretera_otros_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_otros_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.carretera_autonomica_1er_nivel_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera','carretera_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.carretera_autonomica_1er_nivel_lin OWNER TO postgres;
CREATE INDEX sidx_carretera_autonomica_1er_nivel_lin_the_geom ON public.carretera_autonomica_1er_nivel_lin USING gist (the_geom);
COMMENT ON TABLE carretera_autonomica_1er_nivel_lin IS 'El elemento «carretera_autonomica_1er_nivel_lin» incluye la información geográfica lineal de los tramos
                que componen la red autonómica de primer nivel, así como sus enlaces. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.clase IS '';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.nombre IS '[denominacion_carretera]:Denominación';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_1er_nivel_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.aparcamiento_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('aparcamiento','aparcamiento_invernal','aparcamiento_seguro')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.aparcamiento_pto OWNER TO postgres;
CREATE INDEX sidx_aparcamiento_pto_the_geom ON public.aparcamiento_pto USING gist (the_geom);
COMMENT ON TABLE aparcamiento_pto IS 'El elemento «aparcamiento_pto» comprende los objetos geográficos puntuales que representan las
                instalaciones de aparcamiento de vehículos. Los datos pueden provenir de la Información Geográfica
                    de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN aparcamiento_pto.clase IS 'aparcamiento:Área en superficie destinada habitualmente a aparcar vehículos. No se consideran los aparcamientos en línea o batería en los laterales de las calles.	aparcamiento_invernal:Aparcamiento para almacenamiento de vehículos pesados cuando, debido a las condiciones climatológicas, no sea posible su circulación.	aparcamiento_seguro:Aparcamiento para camiones y vehículos comerciales provisto de instalaciones de protección y seguridad y acceso a través de la Red Transeuropea de Carreteras y la Red de Carreteras del Estado.';
COMMENT ON COLUMN aparcamiento_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN aparcamiento_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.carretera_autonomica_3er_nivel_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera','carretera_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.carretera_autonomica_3er_nivel_lin OWNER TO postgres;
CREATE INDEX sidx_carretera_autonomica_3er_nivel_lin_the_geom ON public.carretera_autonomica_3er_nivel_lin USING gist (the_geom);
COMMENT ON TABLE carretera_autonomica_3er_nivel_lin IS 'El elemento «carretera_autonomica_3er_nivel_lin» incluye la información geográfica lineal de los tramos
                que componen la red autonómica de tercer nivel, así como sus enlaces. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.clase IS '';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.nombre IS '[denominacion_carretera]:Denominación';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_3er_nivel_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.contexto_nombre_poblacion_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('capital_estado','nucleo_poblacion')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_poblacion_pto OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_poblacion_pto_the_geom ON public.contexto_nombre_poblacion_pto USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_poblacion_pto IS '';
COMMENT ON COLUMN contexto_nombre_poblacion_pto.clase IS '';
COMMENT ON COLUMN contexto_nombre_poblacion_pto.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_poblacion_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_poblacion_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nombre_orografia_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('alineacion_montañosa','comarca_geografica','cueva','depresion','llanura','montaña','otros_nombre_orografia','paisaje','paraje','paso_montaña','vertiente')),
	nombre character varying,
	nombre_alt character varying,
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	proveedor character varying);
ALTER TABLE public.nombre_orografia_pto OWNER TO postgres;
CREATE INDEX sidx_nombre_orografia_pto_the_geom ON public.nombre_orografia_pto USING gist (the_geom);
COMMENT ON TABLE nombre_orografia_pto IS 'El elemento «nombre_orografia_pto» contiene las referencias puntuales de los nombres de las entidades orográficas continentales y áreas geográficas que se encuentran incluidas en el Nomenclátor Geográfico Básico de España (NGBE) , mantenido por el Instituto Geográfico Nacional (IGN)y distribuido como Información Geográfica de Referencia por el Centro Nacional de Información Geográfica (CNIG) , así como los nombres geográficos oficiales de similar naturaleza que se encuentran recogidos en la cartografía topográfica regional y nomenclátores geográficos editados por las Comunidades Autónomas.';
COMMENT ON COLUMN nombre_orografia_pto.clase IS 'otros_nombre_orografia:Atributo para nombres que no se pueden clasificar en otro.';
COMMENT ON COLUMN nombre_orografia_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_orografia_pto.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_orografia_pto.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_orografia_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_dotacional_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('camping','cementerio','centro_penitenciario','parque_tecnologico','parque_tematico_ocio','piscifactoría','recinto_ferial','zona_comercial','zona_dotacional','zona_recreativa')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_dotacional_pol OWNER TO postgres;
CREATE INDEX sidx_zona_dotacional_pol_the_geom ON public.zona_dotacional_pol USING gist (the_geom);
COMMENT ON TABLE zona_dotacional_pol IS '';
COMMENT ON COLUMN zona_dotacional_pol.clase IS 'zona_dotacional:Otras zonas dotacionales que no se pueden clasificar en el resto de clases';
COMMENT ON COLUMN zona_dotacional_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_dotacional_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nombre_division_administrativa_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('ambito_inferior_a_municipio','ciudad_autonoma','comarca_administrativa','comunidad_autonoma','isla_administrativa','jurisdiccion','municipio','nacion','provincia')),
	nombre character varying,
	nombre_alt character varying,
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	proveedor character varying);
ALTER TABLE public.nombre_division_administrativa_pto OWNER TO postgres;
CREATE INDEX sidx_nombre_division_administrativa_pto_the_geom ON public.nombre_division_administrativa_pto USING gist (the_geom);
COMMENT ON TABLE nombre_division_administrativa_pto IS 'El elemento «nombre_división_Administrativa_pto» contiene las referencias puntuales de los nombres
                geográficos relativos a divisiones administrativas que se encuentran recogidos en el Nomenclátor
                    Geográfico Básico de España (NGBE) , mantenido por el Instituto
                        Geográfico Nacional (IGN)y distribuido como Información Geográfica de Referencia por
                el Centro Nacional de Información Geográfica (CNIG) , así como
                los nombres geográficos oficiales producidos por las Comunidades Autónomas u otras administraciones
                públicas con competencias cartográficas.';
COMMENT ON COLUMN nombre_division_administrativa_pto.clase IS '';
COMMENT ON COLUMN nombre_division_administrativa_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_division_administrativa_pto.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_division_administrativa_pto.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_division_administrativa_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.portal_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.portal_pto OWNER TO postgres;
CREATE INDEX sidx_portal_pto_the_geom ON public.portal_pto USING gist (the_geom);
COMMENT ON TABLE portal_pto IS '';
COMMENT ON COLUMN portal_pto.clase IS 'portal:Clase de objeto';
COMMENT ON COLUMN portal_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN portal_pto.ref IS '[numero]+" "+[extension]:Número y extensión';


CREATE TABLE public.municipio_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	codigo character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.municipio_pol OWNER TO postgres;
CREATE INDEX sidx_municipio_pol_the_geom ON public.municipio_pol USING gist (the_geom);
COMMENT ON TABLE municipio_pol IS '';
COMMENT ON COLUMN municipio_pol.clase IS 'municipio:Clase de objeto';
COMMENT ON COLUMN municipio_pol.codigo IS '[codigo]:Nationalcode según las especificaciones de datos INSPIRE para unidades administrativas.
    Código del país + Código de la CC. AA. + Código de la provincia + Código del municipio formado por 5 dígitos
    Ejemplo: Alberite, en La Rioja: 34172626006. 34+17+26+26006';
COMMENT ON COLUMN municipio_pol.nombre IS '[denominación_municipio]:Denominación oficial del municipio';
COMMENT ON COLUMN municipio_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.cubierta_vegetal_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('asentamiento_agricola_y_huerta','bosque_coniferas','bosque_frondosas','bosque_mixto','combinacion_cultivos','combinacion_cultivos_con_vegetacion','combinacion_cultivos_leñosos','combinacion_vegetacion','cultivo_herbaceo','frutal_citrico','frutal_no_citrico','glaciar_nieve_perpetua','marisma','matorral','olivar','otros_cultivos_leñosos','pastizal_herbazal','playa_duna_arenal','prado','roquedo','salina','suelo_desnudo','temporalmente_desarbolado_por_incendios','turbera','viñedo','zona_humeda_pantanosa')),
	proveedor character varying);
ALTER TABLE public.cubierta_vegetal_pol OWNER TO postgres;
CREATE INDEX sidx_cubierta_vegetal_pol_the_geom ON public.cubierta_vegetal_pol USING gist (the_geom);
COMMENT ON TABLE cubierta_vegetal_pol IS '';
COMMENT ON COLUMN cubierta_vegetal_pol.clase IS '';
COMMENT ON COLUMN cubierta_vegetal_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.hidrografia_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('acequia','canal','curso_natural','tuberia')),
	nombre character varying,
	orden character varying CHECK (orden in ('primero','quinto_sexto','segundo','tercero_cuarto','otro')),
	persistencia character varying CHECK (persistencia in ('estacional','esporadico','permanente','otro')),
	situacion character varying CHECK (situacion in ('subterraneo','en_superficie','elevado')),
	proveedor character varying);
ALTER TABLE public.hidrografia_lin OWNER TO postgres;
CREATE INDEX sidx_hidrografia_lin_the_geom ON public.hidrografia_lin USING gist (the_geom);
COMMENT ON TABLE hidrografia_lin IS 'El elemento «hidrografia_lin» comprende los objetos geográficos lineales de carácter natural y artificial
                que forman la red hidrográfica de España. Los datos pueden provenir de la Información Geográfica de
                    Referencia de Hidrografía (IGR-HY) que edita el Instituto
                        Geográfico Nacional (IGN)y distribuye el Centro
                        Nacional de Información Geográfica (CNIG) , así como de la cartografía topográfica de
                referencia y cartografía temática editada por las Comunidades Autónomas y otras instituciones
                competentes en la materia.';
COMMENT ON COLUMN hidrografia_lin.clase IS '';
COMMENT ON COLUMN hidrografia_lin.nombre IS '[denominacion]:Denominación oficial';
COMMENT ON COLUMN hidrografia_lin.orden IS 'otro:Este valor puede utilizarse en el caso de que no aplique indicar el nivel jerárquico';
COMMENT ON COLUMN hidrografia_lin.persistencia IS 'otro:Este valor puede utilizarse en el caso de que no aplique indicar persistencia';
COMMENT ON COLUMN hidrografia_lin.situacion IS '';
COMMENT ON COLUMN hidrografia_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.via_servicio_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('via_servicio','via_servicio_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')));
ALTER TABLE public.via_servicio_lin OWNER TO postgres;
CREATE INDEX sidx_via_servicio_lin_the_geom ON public.via_servicio_lin USING gist (the_geom);
COMMENT ON TABLE via_servicio_lin IS 'El elemento «via_servicio_lin» identifica los elementos lineales que representan los viales de las vías
                de servicio. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de
                    Transporte (IGR-RT) que edita el Instituto Geográfico Nacional
                        (IGN)y distribuye el Centro Nacional de Información
                        Geográfica (CNIG) , así como de la información geográfica de referencia producida por
                las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN via_servicio_lin.clase IS '';
COMMENT ON COLUMN via_servicio_lin.nombre IS '[denominacion_carretera]:Denominación de la carretera';
COMMENT ON COLUMN via_servicio_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN via_servicio_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN via_servicio_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su
                            competencial, un guion y un número';
COMMENT ON COLUMN via_servicio_lin.tunel IS 'T:Sí	F:No';


CREATE TABLE public.via_urbana_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('via_urbana','via_urbana_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.via_urbana_lin OWNER TO postgres;
CREATE INDEX sidx_via_urbana_lin_the_geom ON public.via_urbana_lin USING gist (the_geom);
COMMENT ON TABLE via_urbana_lin IS 'El elemento «via_urbana_lin» identifica los elementos lineales que representan los ejes de los viales que
                existen en un entorno urbano y que suelen estar identificados por una tipología de vial y un nombre.
                Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte
                    (IGR-RT) que edita el Instituto Geográfico Nacional
                        (IGN)y distribuye el Centro Nacional de Información
                        Geográfica (CNIG) , que a su vez recoge los datos de la base de datos de direcciones
                «Cartociudad» gestionada por el IGN, de los proyectos de callejeros mantenidos por algunas
                administraciones regionales, y de los callejeros municipales.';
COMMENT ON COLUMN via_urbana_lin.clase IS '';
COMMENT ON COLUMN via_urbana_lin.nombre IS '[tipo_vial]+" "+[denominacion]:Denominación de la vía urbana';
COMMENT ON COLUMN via_urbana_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN via_urbana_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN via_urbana_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN via_urbana_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN via_urbana_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.puerto_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('acceso','muelle','puerto','transito_mercancias','transito_pasajeros')),
	nombre character varying,
	proveedor character varying,
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.puerto_pol OWNER TO postgres;
CREATE INDEX sidx_puerto_pol_the_geom ON public.puerto_pol USING gist (the_geom);
COMMENT ON TABLE puerto_pol IS 'El elemento «puerto_pol» comprende los objetos geográficos poligonales que configuran las instalaciones y
                las zonas de los servicios portuarios de cualquier tipo. Los datos pueden provenir de la Información
                    Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN puerto_pol.clase IS '';
COMMENT ON COLUMN puerto_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN puerto_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN puerto_pol.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.carretera_autonomica_2do_nivel_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera','carretera_enlace')),
	nombre character varying,
	proveedor character varying,
	puente character varying CHECK (puente in ('T','F')),
	ref character varying,
	tunel character varying CHECK (tunel in ('T','F')),
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.carretera_autonomica_2do_nivel_lin OWNER TO postgres;
CREATE INDEX sidx_carretera_autonomica_2do_nivel_lin_the_geom ON public.carretera_autonomica_2do_nivel_lin USING gist (the_geom);
COMMENT ON TABLE carretera_autonomica_2do_nivel_lin IS 'El elemento «carretera_autonomica_2do_nivel_lin» incluye la información geográfica lineal de los tramos
                que componen la red autonómica de segundo nivel, así como sus enlaces. Dichos datos pueden proceder de
                la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.clase IS '';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.nombre IS '[denominacion_carretera]:Denominación';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.puente IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.ref IS '[referencia]:Identificador de la carretera o vía compuesto por un primera parte de texto según su competencial, un guion y un número';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.tunel IS 'T:Sí	F:No';
COMMENT ON COLUMN carretera_autonomica_2do_nivel_lin.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.servicio_instalacion_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('aerogenerador','antena','ayuntamiento','campo_futbol','camping','campo_golf','captacion','castillo_fortaleza','catedral','cementerio','centro_interpretacion','centro_penitenciario','circuito','convento','emergencias','ermita','estacion_bombeo','estacion_invernal','explotacion_minera','faro','fuente_ornamental','iglesia','instalacion_deportiva','instalacion_educativa','instalacion_energia','instalacion_militar','instalacion_religiosa','instalacion_sanitaria','instalacion_telecomunicacion','instalacion_tratamiento_aguas','instalacion_tratamiento_residuos','jardin','mezquita','monumento','museo','orden_publico_seguridad','otros_servicios_instalaciones','parque','parque_tecnologico','parque_tematico_ocio','piscifactoría','pista_deportiva','poligono_industrial','recinto_ferial','sinagoga','teatro_auditorio','templo','terreno_natural','torre_electrica','torre_transporte','zona_dotacional','zona_comercial','zona_industrial','zona_recreativa','zona_verde')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.servicio_instalacion_pto OWNER TO postgres;
CREATE INDEX sidx_servicio_instalacion_pto_the_geom ON public.servicio_instalacion_pto USING gist (the_geom);
COMMENT ON TABLE servicio_instalacion_pto IS '';
COMMENT ON COLUMN servicio_instalacion_pto.clase IS 'captacion:Lugar donde se capta o extrae agua de forma artificial mediante diversos procedimientos para su posterior aprovechamiento.	circuito:Circuito deportivo.	estacion_bombeo:Estación elevadora generalmente empleada para extracción o impulsión de agua.	instalacion_religiosa:Otros elementos religiosos genéricos o instalaciones religiosas puntuales que no se pueden clasificar en el resto de clases	otros_servicios_instalaciones:Otras servicios o instalaciones puntuales que no se pueden clasificar en el resto de clases	pista_deportiva:Otro tipo de pista, diferente a la de fútbol, destinada a la práctica de cualquier deporte	torre_transporte:Estructura o armazón de cierta altura desde donde se suspenden los cables de los que penden los transportes suspendidos por cable (teleférico, telesilla).';
COMMENT ON COLUMN servicio_instalacion_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN servicio_instalacion_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nombre_hidrografia_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('cascada','embalse','entrante_costero_estrecho_maritimo','glaciar','hidronimo_puntual','isla','mar','masa_agua','otro_relieve_costero','playa','relieve_submarino','saliente_costero','sifon_sumidero','surgencia','zona_salina')),
	nombre character varying,
	nombre_alt character varying,
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	proveedor character varying);
ALTER TABLE public.nombre_hidrografia_pto OWNER TO postgres;
CREATE INDEX sidx_nombre_hidrografia_pto_the_geom ON public.nombre_hidrografia_pto USING gist (the_geom);
COMMENT ON TABLE nombre_hidrografia_pto IS 'El elemento «nombre_hidrografia_pto» contiene las referencias puntuales de los nombres geográficos de los
                distintos elementos de naturaleza hidrográfica continental y orográfica marítima y costera que se
                encuentran incluidos en el Nomenclátor Geográfico Básico de España (NGBE) , mantenido por el Instituto Geográfico Nacional (IGN)y distribuido como
                Información Geográfica de Referencia por el Centro Nacional de
                        Información Geográfica (CNIG) , así como los nombres geográficos oficiales de similar
                naturaleza que se encuentran recogidos en la cartografía topográfica regional y nomenclátores
                geográficos editados por las Comunidades Autónomas.';
COMMENT ON COLUMN nombre_hidrografia_pto.clase IS 'sifon_sumidero:Sifones, sumideros o bocas hidrográficas entre otros lugares característicos en el curso de una corriente natural de agua, en que se producen cambios en el discurrir de sus aguas debido a las variaciones de la pendiente de su cauce.	surgencia:Fuentes, termas, manantiales entre otros lugares donde brota agua del terreno, ya sea de forma natural o mediante la ayuda de algún sistema de conductos.';
COMMENT ON COLUMN nombre_hidrografia_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_hidrografia_pto.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_hidrografia_pto.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_hidrografia_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_protegida_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('patrimonio_historico_artistico','yacimiento_arqueologico','zona_protegida')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_protegida_pol OWNER TO postgres;
CREATE INDEX sidx_zona_protegida_pol_the_geom ON public.zona_protegida_pol USING gist (the_geom);
COMMENT ON TABLE zona_protegida_pol IS '';
COMMENT ON COLUMN zona_protegida_pol.clase IS 'zona_protegida:Otras zonas protegidas que no se pueden clasificar en el resto de clases';
COMMENT ON COLUMN zona_protegida_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_protegida_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.edificio_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	proveedor character varying,
	tipo character varying CHECK (tipo in ('administrativo','asistencial','educativo','generico','historico','refugio','religioso','sanitario')));
ALTER TABLE public.edificio_pol OWNER TO postgres;
CREATE INDEX sidx_edificio_pol_the_geom ON public.edificio_pol USING gist (the_geom);
COMMENT ON TABLE edificio_pol IS '';
COMMENT ON COLUMN edificio_pol.clase IS 'edificio:Clase de objeto';
COMMENT ON COLUMN edificio_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN edificio_pol.tipo IS 'generico:Clase para los elementos que no se pueden incluir en otro atributo de esta clase. Por ejemplo: comercial, cultural, deportivo, residencial...	refugio:Refugio de montaña';


CREATE TABLE public.area_servicio_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('area_servicio','area_descanso')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.area_servicio_pol OWNER TO postgres;
CREATE INDEX sidx_area_servicio_pol_the_geom ON public.area_servicio_pol USING gist (the_geom);
COMMENT ON TABLE area_servicio_pol IS 'El elemento «area_servicio_pol» incluye los elementos geográficos superficiales que representan las áreas
                de servicio.. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de
                    Transporte (IGR-RT) que edita el Instituto Geográfico Nacional
                        (IGN)y distribuye el Centro Nacional de Información
                        Geográfica (CNIG) , así como de la información geográfica de referencia producida por
                las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN area_servicio_pol.clase IS '';
COMMENT ON COLUMN area_servicio_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN area_servicio_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nombre_toponimo_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('Comarca','division_administrativa','hidrografia','orografia','Otros','Paraje','poblacion','Sierra','transporte')),
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	nombre character varying,
	nombre_alt character varying,
	proveedor character varying);
ALTER TABLE public.nombre_toponimo_lin OWNER TO postgres;
CREATE INDEX sidx_nombre_toponimo_lin_the_geom ON public.nombre_toponimo_lin USING gist (the_geom);
COMMENT ON TABLE nombre_toponimo_lin IS '';
COMMENT ON COLUMN nombre_toponimo_lin.clase IS 'Otros:Clase de objeto no contemplada en el listado de valores. 
                            También puede utilizarse si no aplica asignar una clasificación.';
COMMENT ON COLUMN nombre_toponimo_lin.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_toponimo_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_toponimo_lin.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_toponimo_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.instalacion_telecomunicacion_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_telecomunicacion_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_telecomunicacion_pol_the_geom ON public.instalacion_telecomunicacion_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_telecomunicacion_pol IS '';
COMMENT ON COLUMN instalacion_telecomunicacion_pol.clase IS 'instalacion_telecomunicacion:Clase de objeto';
COMMENT ON COLUMN instalacion_telecomunicacion_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_telecomunicacion_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nucleo_urbano_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	cod_ine character varying,
	municipio character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.nucleo_urbano_pol OWNER TO postgres;
CREATE INDEX sidx_nucleo_urbano_pol_the_geom ON public.nucleo_urbano_pol USING gist (the_geom);
COMMENT ON TABLE nucleo_urbano_pol IS '';
COMMENT ON COLUMN nucleo_urbano_pol.clase IS 'nucleo_urbano:Clase de objeto';
COMMENT ON COLUMN nucleo_urbano_pol.cod_ine IS '[codigo_ine]:Código INE del núcleo urbano';
COMMENT ON COLUMN nucleo_urbano_pol.municipio IS '[denominacion_municipio]:Denominación oficial del municipio';
COMMENT ON COLUMN nucleo_urbano_pol.nombre IS '[denominacion_nucleo_urbano]:Denominación oficial del núcleo urbano';
COMMENT ON COLUMN nucleo_urbano_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.instalacion_sanitaria_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.instalacion_sanitaria_pol OWNER TO postgres;
CREATE INDEX sidx_instalacion_sanitaria_pol_the_geom ON public.instalacion_sanitaria_pol USING gist (the_geom);
COMMENT ON TABLE instalacion_sanitaria_pol IS '';
COMMENT ON COLUMN instalacion_sanitaria_pol.clase IS 'instalacion_sanitaria:Clase de objeto';
COMMENT ON COLUMN instalacion_sanitaria_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN instalacion_sanitaria_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.tierra_firme_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	codigo character varying,
	nombre character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.tierra_firme_pol OWNER TO postgres;
CREATE INDEX sidx_tierra_firme_pol_the_geom ON public.tierra_firme_pol USING gist (the_geom);
COMMENT ON TABLE tierra_firme_pol IS '';
COMMENT ON COLUMN tierra_firme_pol.clase IS '[tierra_firme]:Clase de objeto';
COMMENT ON COLUMN tierra_firme_pol.codigo IS '[codigo]:Nationalcode según las especificaciones de datos INSPIRE para unidades administrativas.';
COMMENT ON COLUMN tierra_firme_pol.nombre IS 'España:Nombre';
COMMENT ON COLUMN tierra_firme_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN tierra_firme_pol.ref IS '[designador]:Atributo previsto por si hay que distinguir o etiquetar distintintos tipos de polígonos de tierra.';


CREATE TABLE public.comunidad_autonoma_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying,
	codigo character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.comunidad_autonoma_pol OWNER TO postgres;
CREATE INDEX sidx_comunidad_autonoma_pol_the_geom ON public.comunidad_autonoma_pol USING gist (the_geom);
COMMENT ON TABLE comunidad_autonoma_pol IS '';
COMMENT ON COLUMN comunidad_autonoma_pol.clase IS 'comunidad_autonoma:Clase de objeto';
COMMENT ON COLUMN comunidad_autonoma_pol.codigo IS '[codigo]:Nationalcode según las especificaciones de datos INSPIRE para unidades administrativas. Código del país + Código de la CC. AA. + 2 dígitos 00 + 5 dígitos 00000
    Ejemplo: Illes Balears: 34040000000. 34+04+00+00000';
COMMENT ON COLUMN comunidad_autonoma_pol.nombre IS '[denominación_comunidad_autonoma]:Denominación oficial de la comunidad autónoma';
COMMENT ON COLUMN comunidad_autonoma_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.ferrocarril_pk_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	proveedor character varying,
	ref character varying);
ALTER TABLE public.ferrocarril_pk_pto OWNER TO postgres;
CREATE INDEX sidx_ferrocarril_pk_pto_the_geom ON public.ferrocarril_pk_pto USING gist (the_geom);
COMMENT ON TABLE ferrocarril_pk_pto IS 'El elemento «ferrocarril_pk_pto» incluye los elementos geográficos puntuales que representan los puntos kilométricos de la red de ferrocarril. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN ferrocarril_pk_pto.clase IS 'pk_ferrocarril:Clase de objeto';
COMMENT ON COLUMN ferrocarril_pk_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN ferrocarril_pk_pto.ref IS '[referencia]:Identificador del PK. Si no se conoce o no es aplicable dejarlo en blanco';


CREATE TABLE public.ruta_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('camino_de_santiago','carril_bici','ruta','ruta_parque_nacional','ruta_via_verde','sendero_europeo','sendero_gran_recorrido','sendero_local','sendero_pequeño_recorrido','sendero_regional','sendero_urbano','via_pecuaria')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.ruta_lin OWNER TO postgres;
CREATE INDEX sidx_ruta_lin_the_geom ON public.ruta_lin USING gist (the_geom);
COMMENT ON TABLE ruta_lin IS 'El elemento «ruta_lin» identifica los elementos lineales que representan los itinerarios correspondientes a las rutas, caminos y senderos de distinta naturaleza independientemente de la tipología del trazado físico sobre el que se apoyan. Dichos datos pueden proceder de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , que a su vez recoge los datos de la base de datos de direcciones «Cartociudad» gestionada por el IGN, de los proyectos de callejeros mantenidos por algunas administraciones regionales, y de los callejeros municipales.';
COMMENT ON COLUMN ruta_lin.clase IS '';
COMMENT ON COLUMN ruta_lin.nombre IS '[tipo_vial]+" "+[denominacion]:Denominación de la vía urbana';
COMMENT ON COLUMN ruta_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.zona_protegida_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('patrimonio_historico_artistico','yacimiento_arqueologico','zona_protegida')),
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.zona_protegida_pto OWNER TO postgres;
CREATE INDEX sidx_zona_protegida_pto_the_geom ON public.zona_protegida_pto USING gist (the_geom);
COMMENT ON TABLE zona_protegida_pto IS '';
COMMENT ON COLUMN zona_protegida_pto.clase IS 'zona_protegida:Otras zonas protegidas que no se pueden clasificar en el resto de clases';
COMMENT ON COLUMN zona_protegida_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN zona_protegida_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_carreteras_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('carretera_1er_nivel','carretera_2do_nivel','carretera_otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_carreteras_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_carreteras_lin_the_geom ON public.contexto_carreteras_lin USING gist (the_geom);
COMMENT ON TABLE contexto_carreteras_lin IS '';
COMMENT ON COLUMN contexto_carreteras_lin.clase IS '';
COMMENT ON COLUMN contexto_carreteras_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_carreteras_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_carreteras_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.nombre_poblacion_construccion_pto (
	the_geom public.geometry(Point,25830),
	clase character varying CHECK (clase in ('barrio','capital_comunidad_autonoma_ciudad_autonoma','capital_eatim','capital_estado','capital_municipio','capital_provincia','construccion_instalacion_abierta','distrito_municipal','eatim','edificacion','entidad_colectiva','entidad_menor_poblacion','entidad_singular','entidad_singular_INE','hito_demarcacion_territorial','hito_via_comunicacion','infraestructura_transporte_terrestre','instalacion_portuaria','nucleo_poblacion','otra_entidad_menor_poblacion','vertice_geodesico')),
	nombre character varying,
	nombre_alt character varying,
	jerarquia integer CHECK (jerarquia in (1,2,3,4,5,6,7)),
	proveedor character varying);
ALTER TABLE public.nombre_poblacion_construccion_pto OWNER TO postgres;
CREATE INDEX sidx_nombre_poblacion_construccion_pto_the_geom ON public.nombre_poblacion_construccion_pto USING gist (the_geom);
COMMENT ON TABLE nombre_poblacion_construccion_pto IS 'El elemento «nombre_poblacion_construccion_pto» contiene las referencias puntuales de los nombres
                geográficos de poblaciones y construcciones incluidos en el Nomenclátor Geográfico Básico de España
                    (NGBE) , mantenido por el Instituto Geográfico Nacional
                        (IGN)y distribuido como Información Geográfica de Referencia por el Centro Nacional de Información Geográfica (CNIG) , así como
                los nombres geográficos oficiales de similar naturaleza que se encuentran recogidos en la cartografía
                topográfica regional y nomenclátores geográficos editados por las Comunidades Autónomas.';
COMMENT ON COLUMN nombre_poblacion_construccion_pto.clase IS '';
COMMENT ON COLUMN nombre_poblacion_construccion_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN nombre_poblacion_construccion_pto.nombre_alt IS '[nombre_alternativo]:Nombre alternativo';
COMMENT ON COLUMN nombre_poblacion_construccion_pto.jerarquia IS '1:Recomendado para visualizarse a partir del nivel 0	2:Recomendado para visualizarse a partir del nivel 5	3:Recomendado para visualizarse a partir del nivel 7	4:Recomendado para visualizarse a partir del nivel 11	5:Recomendado para visualizarse a partir del nivel 13	6:Recomendado para visualizarse a partir del nivel 15	7:Recomendado para visualizarse a partir del nivel 17';
COMMENT ON COLUMN nombre_poblacion_construccion_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_nombre_hidrografia_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('dorsal','fosa','zona_factura','ria','entrante_costero_estrecho_maritimo','otros')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_nombre_hidrografia_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_nombre_hidrografia_lin_the_geom ON public.contexto_nombre_hidrografia_lin USING gist (the_geom);
COMMENT ON TABLE contexto_nombre_hidrografia_lin IS '';
COMMENT ON COLUMN contexto_nombre_hidrografia_lin.clase IS '';
COMMENT ON COLUMN contexto_nombre_hidrografia_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_nombre_hidrografia_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_nombre_hidrografia_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.contexto_ferrocarril_lin (
	the_geom public.geometry(Linestring,25830),
	clase character varying CHECK (clase in ('ferrocarril')),
	esp integer,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.contexto_ferrocarril_lin OWNER TO postgres;
CREATE INDEX sidx_contexto_ferrocarril_lin_the_geom ON public.contexto_ferrocarril_lin USING gist (the_geom);
COMMENT ON TABLE contexto_ferrocarril_lin IS '';
COMMENT ON COLUMN contexto_ferrocarril_lin.clase IS '';
COMMENT ON COLUMN contexto_ferrocarril_lin.esp IS '[esp]:Indica si los datos se superponen con el territorio español o son exclusivamente del contexto con propósitos de representación y estilo.';
COMMENT ON COLUMN contexto_ferrocarril_lin.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN contexto_ferrocarril_lin.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';


CREATE TABLE public.estacion_ferrocarril_pol (
	the_geom public.geometry(Polygon,25830),
	clase character varying CHECK (clase in ('apartadero','apartadero-cargadero','apeadero','apeadero-cargadero','cambiador','cargadero','edificio_estacion','estacion_ferrocarril','paso_a_nivel')),
	nombre character varying,
	proveedor character varying,
	estado character varying CHECK (estado in ('en_construcción','en_uso','fuera_de_servicio')));
ALTER TABLE public.estacion_ferrocarril_pol OWNER TO postgres;
CREATE INDEX sidx_estacion_ferrocarril_pol_the_geom ON public.estacion_ferrocarril_pol USING gist (the_geom);
COMMENT ON TABLE estacion_ferrocarril_pol IS 'El elemento «estacion_ferrocarril_pol» comprende los objetos geográficos superficiales que representan
                los distintos espacios de las estaciones de ferrocarril. Los datos pueden provenir de la Información
                    Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como
                de la información geográfica de referencia producida por las Comunidades Autónomas u otras
                administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN estacion_ferrocarril_pol.clase IS '';
COMMENT ON COLUMN estacion_ferrocarril_pol.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN estacion_ferrocarril_pol.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
COMMENT ON COLUMN estacion_ferrocarril_pol.estado IS 'en_construcción:Se encuentra en obras para un posterior uso	en_uso:Se encuentra utilizable o en condiciones constructivas aparentes para ser utilizable	fuera_de_servicio:Para los casos en los que el objeto geográfico se encuentra fuera de servicio, 
                            o se ha destruido en parte, aunque hay restos visibles';


CREATE TABLE public.paso_a_nivel_pto (
	the_geom public.geometry(Point,25830),
	clase character varying,
	nombre character varying,
	proveedor character varying);
ALTER TABLE public.paso_a_nivel_pto OWNER TO postgres;
CREATE INDEX sidx_paso_a_nivel_pto_the_geom ON public.paso_a_nivel_pto USING gist (the_geom);
COMMENT ON TABLE paso_a_nivel_pto IS 'El elemento «paso_a_nivel_pto» incluye los elementos geográficos puntuales que representan los pasos a nivel existentes en la red de carreteras. Los datos pueden provenir de la Información Geográfica de Referencia de Redes de Transporte (IGR-RT) que edita el Instituto Geográfico Nacional (IGN)y distribuye el Centro Nacional de Información Geográfica (CNIG) , así como de la información geográfica de referencia producida por las Comunidades Autónomas u otras administraciones públicas con competencias cartográficas.';
COMMENT ON COLUMN paso_a_nivel_pto.clase IS 'paso_a_nivel:Clase de objeto';
COMMENT ON COLUMN paso_a_nivel_pto.nombre IS '[nombre]:Nombre';
COMMENT ON COLUMN paso_a_nivel_pto.proveedor IS '[codigo_proveedor]:Proveedor de la información (lista controlada)';
