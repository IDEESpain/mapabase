# Procesos de Validación y Transformación de GeoJSON

Esta carpeta incluye scripts para la validación y transformación de datos GeoJSON en el contexto de modelos de datos basados en el repositorio de [mapabase](https://github.com/IDEESpain/mapabase). A continuación, se describen los principales scripts, su funcionalidad y las configuraciones requeridas.

---

## **Scripts Principales**

### **1. `run_crearJSONValidacion.py`**
Genera el archivo `comprobacion.json` en la ruta `/lib/comprobacion.json` utilizando los datos del repositorio `mapabase`.  

#### **Uso:**
- Se debe ejecutar este script cada vez que haya cambios en el modelo de datos. Para ello:
  1. Actualiza el repositorio local de `mapabase`.
  2. Lanza el script.  
- Si no hay cambios en el modelo, se puede reutilizar el archivo `comprobacion.json` existente.

#### **Nota Importante:**
La variable `ProcesoControlCalidad.git_carpeta_mapabase_gh_pages` define la ruta local del repositorio `mapabase`, configurada en `config.json`.  
- Esta ruta debe apuntar a la rama que contiene el modelo (puede no ser `gh_pages`). Por ejemplo, si la rama activa es `desarrollo`, se utilizará `desarrollo`.

---

### **2. `run_completeProcess.py`**
Ejecuta todos los procesos del pipeline, combinando validación y transformación.  

#### **Recomendación:**
Para una primera ejecución, se sugiere ejecutar los scripts por separado:  
1. `run_validationProcess.py` para validar los datos.  
2. `run_transformationProcess.py` para transformar los datos una vez validados.

---

### **3. `run_validationProcess.py`**
Valida los datos GeoJSON según el modelo definido en `mapabase`.  
- Ideal para una primera ejecución, ya que permite mayor control sobre los errores y resultados.

---

### **4. `run_transformationProcess.py`**
Convierte los archivos GeoJSON validados a formato FGB.  
- Recomendado tras una validación exitosa.

---

### **5. Scripts Adicionales**
- **`run_2FGB.py`:** Realiza la transformación a FGB. Parte del proceso de transformación pero también puede ejecutarse de forma independiente.  
- **`run_2VRT.py`:** Crea archivos VRT. También es parte del proceso de transformación pero puede ejecutarse de forma separada.

---

## **Configuración (`config.json`)**

El archivo `config.json` define las rutas y parámetros necesarios para la ejecución de los scripts. Los campos obligatorios son:

```json
{
    "geojson_folder_path": "./salida_geojsons_andalucia/",
    "fgb_folder_path": "./salida_geojsons_andalucia/fgb/",
    "git_carpeta_mapabase_gh_pages": "./mapabase",
    "JSON_comprobacion": "./lib/comprobacion.json",
    "fgb_temp_folder": "./salida_geojsons_andalucia/fgb_temp/"
}
```

### **Descripción de Parámetros:**
- `geojson_folder_path`: Carpeta que contiene los archivos GeoJSON generados en el proceso anterior.  
- `fgb_folder_path`: Carpeta de salida para los archivos FGB.  
- `git_carpeta_mapabase_gh_pages`: Ruta local al repositorio `mapabase`.  
- `JSON_comprobacion`: Ruta del archivo de comprobación generado.  
- `fgb_temp_folder`: Carpeta temporal utilizada durante la transformación (se elimina al finalizar).  

---

## **Estructura del Log de Salida**

El log del proceso de validación proporciona un resumen detallado del estado de los datos. Su estructura es la siguiente:

1. **Cabecera:**  
   - Información general (fecha de inicio).  

2. **Comprobación de Archivos GeoJSON:**  
   - GeoJSON en el modelo de datos.  
   - GeoJSON entregados y su correspondencia con el modelo.  

3. **Comprobación de Atributos:**  
   - Atributos presentes en el modelo y en los GeoJSON.  
   - Discrepancias entre ambos.  

4. **Validación de Dominios:**  
   - Valores fuera del dominio esperado.  

5. **Finalización:**  
   - Fecha y hora de cierre del proceso.  

---

## **Recomendaciones**
- Asegúrate de mantener actualizadas las dependencias y el repositorio local de `mapabase` antes de ejecutar los scripts.  
- Valida los datos con `run_validationProcess.py` antes de proceder con la transformación.  
- Consulta el log de salida para identificar posibles errores o inconsistencias en los datos.


