# CONTRATO DE DATOS DEL AGENTE FINANCIERO

> **Nota de vigencia (2026-09-18):** el motor generativo del proyecto es **opencode** y el rol de
> verificación/auditoría lo ejerce **big pickle** (ver `GUIA_MOTOR_IA.md`). Las referencias a
> `google-genai`/`GEMINI_API_KEY` de las secciones siguientes son **históricas**: el esquema, los
> estados y las reglas de evidencia siguen vigentes; la llamada al modelo ya no depende de una clave.

## 1. ENTRADA AL AGENTE

El agente recibe los siguientes datos de entrada, provenientes del notebook `Analisis_Financiero.ipynb` y/o del motor de extracción PDF:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pdf_original` | `bytes / ruta archivo` | El archivo PDF original de los estados financieros (`Estados-Financieros.pdf`). |
| `pagina` | `int` | Número de página dentro del PDF donde se encuentra la información. |
| `imagen_pagina` | `numpy array / None` | Imagen de la página cuando sea necesario (para casos de OCR o PDFs escaneados). |
| `texto_extraido` | `str` | Texto extraído de la página (mediante pdfminer, u otra librería de extracción de texto). |
| `tabla_extraida` | `dict / pandas.DataFrame o None` | Tabla extraída del PDF, estructurada con filas, columnas y valores (detectada por TableItem o similar). |
| `cuenta_candidata` | `str` | Nombre de la cuenta contable candidata detectada en el texto o tabla de la página. |
| `valores_detectados` | `dict` | Diccionario con los valores numéricos detectados por columna/periodo, ej: `{"2025": 46020, "2024": 47069}`. |
| `periodos` | `list[str]` | Lista de periodos identificados, ej: `["2025", "2024"]` o `["Actual", "Anterior"]`. |
| `unidad_monetaria` | `str` | Unidad monetaria detectada, ej: `"Millones"`, `"Miles"`, o el símbolo `"$"`. |
| `similitud_semantica` | `float` | Resultado de similitud coseno (0.0 a 1.0) entre el nombre de la cuenta candidata y la taxonomía de referencia. |

---

## 2. SALIDA DEL AGENTE

Para cada variable financiera procesada, el agente devuelve un diccionario con los siguientes campos como mínimo:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `variable_canonica` | `str` | Nombre canonical o estandarizado de la variable financiera (ej: `"Efectivo_y_equivalentes"`, `"Resultado_del_Ejercicio"`). |
| `cuenta_original` | `str` | Tal como apareció en el documento fuente (PDF o imagen). |
| `codigo_puc` | `str o None` | Código del Plan Úmero Contable (PUC) si puede determinirse, de lo contrario `None`. |
| `valor_periodo_actual` | `float o None` | Valor correspondiente al periodo actual (ej: 2025). |
| `valor_periodo_anterior` | `float o None` | Valor correspondiente al periodo anterior (ej: 2024). |
| `periodo_actual` | `str` | Etiqueta del periodo actual, ej: `"2025"`. |
| `periodo_anterior` | `str` | Etiqueta del periodo anterior, ej: `"2024"`. |
| `unidad` | `str` | Unidad de medida del valor, ej: `"Millones"`. |
| `pagina` | `int` | Número de página de donde proviene la información. |
| `metodo_extraccion` | `str` | Método utilizado para extraer el dato, ej: `"pdfminer_texto"`, `"pdfminer_tabla"`, `"tesseract_OCR"`, `"sentilembed_similitud"`. |
| `evidencia` | `str` | Documentación de dónde surgió el valor (ver sección 3). |
| `confianza` | `float` | Puntuación de confianza en el valor extraído, de 0.0 a 1.0. |
| `estado` | `str` | Estado de validación de la variable. Valores permitidos: `ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`. |

### Estados permitidos:

- `ACEPTADO`: El valor ha sido validado y es consistente con la taxonomía y contexto contable.
- `DUDOSO`: El valor es incierto, la similitud semántica fue borderline o hay ambigüedad en la cuenta.
- `NO_ENCONTRADO`: No se encontró evidencia suficiente para asignar un valor; el agente no debe inventar el valor.
- `INCONSISTENTE`: El valor contradice otros datos del documento o violaciones de principios contables (ej: activo ≠ pasivo + patrimonio).

---

## 3. EVIDENCIA

La salida debe incluir siempre una cadena de `evidencia` que documente de dónde proviene cada valor. La evidencia debe contener como mínimo:

- `pagina`: Número de página de donde se extrajo la información.
- `texto_o_referencia_a_imagen`: Fragmento de texto extraído o descripción de la región de la imagen donde apareció el valor.
- `cuenta_original`: El nombre de la cuenta tal como apareció en el documento fuente.
- `contexto_contable`: Contexto en que se encontró la cuenta (ej: "Balance General", "Estado de Resultados", "Nota 3.1").
- `metodo_utilizado`: El método o modelo que produjo el resultado (ej: `"sentence_transformers_all-MiniLM-L6-v2"` con similitud 0.92).

**Formato sugerido para evidencia:**

```
evidencia: "Página {pagina}: texto='{texto_extraido}' | cuenta='{cuenta_original}' | contexto='{contexto_contable}' | metodo='{metodo_extraccion}' | similitud={similitud_semantica}"
```

---

## 4. CONFIANZA

Se define una escala de confianza de 0.0 a 1.0 para cada salida. La confianza refleja el grado de certeza del agente sobre la correctitud del valor extraído.

### Niveles de confianza:

| Rango | Clasificación | Acción automática |
|-------|---------------|-------------------|
| `0.90 - 1.0` | `ALTA` | Aceptar valor automáticamente (`estado: ACEPTADO`). |
| `0.75 - 0.89` | `MEDIA` | Aceptar con revisión manual sugerida (`estado: ACEPTADO` o `DUDOSO` según validación posterior). |
| `0.50 - 0.74` | `BAJA` | Marcar como `DUDOSO`, requiere validación humana. |
| `0.0 - 0.49` | `MUY BAJA` | Devolver `NO_ENCONTRADO`; no asignar valor. |

### Condiciones para aceptar automáticamente un dato:

1. `similitud_semantica >= 0.90` Y `confianza >= 0.80`
2. La cuenta original coincide exactamente con una cuenta de la taxonomía (similitud = 1.0)
3. Los valores numéricos pasan validación de rango y consistencia (ver sección 8)
4. No hay contradicciones con datos de otros periodos o cuentas relacionadas

### Condiciones para devolver `DUDOSO`:

1. `0.50 <= similitud_semantica < 0.90` sin validación adicional
2. La cuenta tiene nombre similar pero no idéntico a la taxonomía
3. Los valores están fuera de rangos esperados pero no son absurdos
4. Contexto ambiguo o múltiples interpretaciones posibles

### Condiciones para devolver `NO_ENCONTRADO`:

1. `similitud_semantica < 0.50` (sin coincidencia significativa)
2. No hay texto ni tabla detectable en la página
3. La cuenta no aparece en la taxonomía y no hay forma de inferirla
4. Error en la extracción OCR o del PDF que impide leer el valor

### Condiciones para devolver `INCONSISTENTE`:

1. El valor contradice el balance contable (ej: activo ≠ pasivo + patrimonio)
2. El valor es negativo cuando no debería serlo (o viceversa según el contexto)
3. Los valores de los periodos no son coherentes con la tendencia esperada
4. Suma de partidas no concuerda con el total declarado

---

## 5. REGLA FUNDAMENTAL

**El agente NUNCA debe inventar un valor.**

- Si no existe evidencia suficiente para determinar un valor, el agente debe devolver `NO_ENCONTRADO` (o `DUDOSO` si hay duda fundada pero sin certeza absoluta).
- **Nunca** se debe asignar un valor numérico `0`, `None` o un placeholder como "No disponible" en lugar de `NO_ENCONTRADO`.
- Si la similitud semántica es baja o el contexto es ambiguo, la respuesta más segura es `NO_ENCONTRADO` o `DUDOSO`.
- El agente debe ser conservador: es mejor dejar un dato vacío (`NO_ENCONTRADO`) que inventar un valor incorrecto que contaminaría los indicadores financieros.

---

## 6. COMPATIBILIDAD CON DATAFrame DE PANDAS

El contrato debe asegurar que la salida del agente sea compatible con la conversión a `pandas.DataFrame` para alimentar el sistema actual de indicadores.

### Especificaciones de compatibilidad:

1. **Columnas consistentes:** Cada diccionario de salida debe tener las mismas claves para todas las variables financieras, permitiendo su directa conversión a DataFrame.

2. **Tipos de datos:** 
   - `valor_periodo_actual` y `valor_periodo_anterior`: `float` (o `None`/`NaN` si es `NO_ENCONTRADO`)
   - `confianza`: `float` entre 0.0 y 1.0
   - `estado`: `str` con valores de conjunto cerrado (`ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`)
   - `codigo_puc`: `str` o `None`

3. **Conversión a DataFrame:** Los diccionarios de salida se pueden transformar a un DataFrame de la siguiente manera:

```python
import pandas as pd

# Ejemplo de diccionario de salida por variable
datos_variable = {
    "variable_canonica": "Efectivo_y_equivalentes",
    "cuenta_original": "Efectivo y equivalentes de efectivo",
    "codigo_puc": "200",
    "valor_periodo_actual": 46020.0,
    "valor_periodo_anterior": 47069.0,
    "periodo_actual": "2025",
    "periodo_anterior": "2024",
    "unidad": "Millones",
    "pagina": 5,
    "metodo_extraccion": "pdfminer_texto",
    "evidencia": "Página 5: texto='Efectivo y equivalentes de efectivo' | metodo='pdfminer_texto' | similitud=1.0",
    "confianza": 1.0,
    "estado": "ACEPTADO"
}

# Conversión a DataFrame (una fila por variable)
df = pd.DataFrame([datos_variable])

# Para un conjunto de variables, se concatenan filas:
df_total = pd.concat([df1, df2, df3], ignore_index=True)
```

4. **Uso en el sistema actual:** Una vez convertido a DataFrame, las columnas pueden ser mapeadas al sistema existente de indicadores financieros mediante:
   - `variable_canonica` → nombre de la variable en el diccionario de indicadores
   - `valor_periodo_actual` / `valor_periodo_anterior` → datos de entrada para fórmulas de ratios
   - `estado` → filtrado o ponderación en los cálculos (ej: valores `DUDOSO` tienen peso reducido)

5. **Estructura recomendada para lote de variables:**

```python
# Múltiples variables en una sola estructura
datos_financieros = [
    {"variable_canonica": "Activo_Total", "valor_periodo_actual": 348129, "estado": "ACEPTADO", ...},
    {"variable_canonica": "Resultado_Ejercicio", "valor_periodo_actual": 30947, "estado": "ACEPTADO", ...},
    {"variable_canonica": "Pasivo_Total", "valor_periodo_actual": 60295, "estado": "ACEPTADO", ...},
    # ... más variables
]

df_financieros = pd.DataFrame(datos_financieros)
```

Esto permite que el output del agente pueda ser directamente consumido por el motor de indicadores del notebook `Analisis_Financiero.ipynb` sin requerir transformaciones adicionales complejas.

---

## 7. VALIDACIÓN DEL `response_schema` (nullable-aware)

El `response_schema` vigente es `esquema_extraccion_ia.json` (deriva de este contrato; ver `PASO3_1_REPORTE.md`). Usa la clave **`nullable`**, que es una **extensión de Google** ajena a JSON Schema draft-07.

### 7.1 Regla oficial

- La validación oficial del esquema **NO** es `jsonschema` draft-07 puro. Draft-07 no reconoce `nullable` y marcaría como inválido cualquier campo `nullable` que venga en `null` (p. ej. `codigo_puc: null`), produciendo un **falso positivo**.
- La capa oficial es **`nullable`-aware**: se extiende `Draft7Validator` para que un valor `null` sea válido cuando el sub-esquema declare `nullable: true`, y luego se aplica el esquema **original**, sin sanear.
- La copia que se pasa al modelo como `response_schema` (solo para la llamada) **no puede ser el archivo verbatim**: el SDK de llamada rechaza `$schema` y no soporta `additionalProperties`. Para eso existe `sanear_schema_para_sdk()` en `esquema_utils.py` (sanitizador JSON Schema genérico; copia saneada para la llamada; no altera el archivo).
- `pagina` es `required` y **no** es `nullable` desde la v3: siempre es un entero ≥ 1, incluso con `estado = NO_ENCONTRADO` (indica la página o el rango revisado).

### 7.2 Cómo se aplica

```python
import json
from jsonschema import validators, Draft7Validator

schema = json.load(open("esquema_extraccion_ia.json", encoding="utf-8"))

def nullable_type(v, types, instance, sch):
    if instance is None and sch.get("nullable") is True:
        return
    yield from Draft7Validator.VALIDATORS["type"](v, types, instance, sch)

ValidadorNullable = validators.extend(Draft7Validator, {"type": nullable_type})
ValidadorNullable(schema).validate(salida_ia)
```

---