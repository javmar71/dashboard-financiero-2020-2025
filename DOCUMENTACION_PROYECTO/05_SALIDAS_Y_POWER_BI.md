# 05_SALIDAS_Y_POWER_BI.md — SALIDAS Y POWER BI

## 1. MOTOR ANALÍTICO

El agente financiero realiza las siguientes funciones en el motor analítico:

| Capa | Función |
|------|---------|
| extracción | Lectura multifuente (PDF, XLSX, XLS, CSV, DOCX, TXT) |
| normalización | Conversión a estructura común (variable_canonica, período, valor, unidad, confianza, estado) |
| clasificación | Asignación a categoría y subcategoría del catálogo de variables madre |
| mapeo | Relación variable fuente → variable canónica del catálogo |
| cálculo | Cálculo de indicadores a partir de variables madre |
| validación | Consistencia contable, detección de anomalías, estados ACEPTADO/DUDOSO/NO_ENCONTRADO/INCONSISTENTE |
| diagnóstico | Generación de hallazgos, razones, ratios y observaciones |
| evidencia | Rastreo completo de origen de cada dato |

---

## 2. CAPAS DE PRESENTACIÓN

### 2.1 Excel

- **Salida:** Datos estructurados y auditable
- **Contenido:** DataFrame con variables canónicas, valores, metadatos (fuente, período, confianza, estado)
- **Formato:** `.xlsx` con hojas organizadas por categoría (liquidez, rentabilidad, endeudamiento, etc.)
- **Propósito:** Consumo por usuarios que requieren datos estructurados para análisis posterior o carga en otros sistemas
- **Características:** 
  - Fórmulas conservadas donde aplica
  - Formato monetario consistente
  - Filtrado y tabulado para auditoría
  - Sin fórmulas de cálculo volatiles que dependan de la ejecución del agente

### 2.2 HTML

- **Salida:** Presentación interactiva de resultados
- **Contenido:** Reportes HTML con indicadores clave, diagnóstico y evidencia
- **Formato:** `.html` con tablas, gráficos simples, resúmenes ejecutivos
- **Propósito:** Visualización rápida, reportes enviados por correo, visualización en navegador
- **Características:**
  - Diseño responsivo
  - Resaltado de valores DUDOSO/NO_ENCONTRADO/INCONSISTENTE
  - Enlaces a evidencia de origen
  - Resumen ejecutivo y detalle técnico

### 2.3 Power BI

- **Salida:** Dashboard de auditoría y análisis histórico
- **Relación con el motor:** Power BI **NO** debe convertirse en el motor de cálculo financiero principal. Debe **consumir** un modelo de datos estructurado generado por el sistema.
- **Formato:** `.pbix` o servicio Power BI Service
- **Propósito:** Paneles de control ejecutivo, seguimiento de indicadores temporales, visualización de diagnósticos
- **Capacidades a estudiar posteriormente:**
  - Automatizar Power BI Desktop mediante capacidades disponibles en el entorno
  - Conectar directamente con DataFrames de pandas generados por el agente
  - Programar actualizaciones programadas de datos
  - Crear visualizaciones de series históricas (2-5 años)

**No realizar todavía ninguna integración Power BI.** Esta definición es declarativa para futura autorización.

---

## 3. ARQUITECTURA DE SALIDA COMPLETA

```
AGENTE FINANCIERO
│
├── extracción multifuente
│   ├── PDF
│   ├── XLSX / XLS
│   ├── DOCX
│   ├── TXT
│   └── CSV
│
├── normalización a estructura común
│   ├── variable_canonica
│   ├── período
│   ├── valor (float o None)
│   ├── unidad
│   ├── confianza (0.0 a 1.0)
│   └── estado (ACEPTADO / DUDOSO / NO_ENCONTRADO / INCONSISTENTE)
│
├── clasificación y catálogo
│   ├── categoria (liquidez, rentabilidad, etc.)
│   ├── subcategoria
│   ├── fuente_preferente
│   └── documento_origen
│
├── cálculo de indicadores
│   ├── variables_madre_requeridas
│   ├── fórmulas_parametrizadas
│   ├── requiere_promedio
│   ├── requiere_series_historicas
│   └── requiere_externos
│
├── validación y diagnóstico
│   ├── consistencia_contable (ACTIVO = PASIVO + PATRIMONIO)
│   ├── estados_validacion
│   ├── hallazgos
│   └── observaciones
│
└── presentación de salida
    ├── Excel (datos estructurados)
    ├── HTML (presentación interactiva)
    └── Power BI (dashboard — futuro, consumir modelo estructurado)
```

---

## 4. ESPECIFICACIÓN TÉCNICA DE SALIDA

### 4.1 Estructura de diccionario por variable

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| variable_canonica | str | Nombre canonical estandarizado | `"Utilidad_neta"` |
| cuenta_original | str | Como apareció en el documento | `"Utilidad del Ejercicio"` |
| codigo_puc | str o None | Código PUC si aplica | `"200"` |
| valor_periodo_actual | float o None | Valor periodo actual | `30947.0` |
| valor_periodo_anterior | float o None | Valor periodo anterior | `28562.0` |
| periodo_actual | str | Etiqueta período actual | `"2025"` |
| periodo_anterior | str | Etiqueta período anterior | `"2024"` |
| unidad | str | Unidad de medida | `"Millones"` |
| pagina | int | Página/hoja de origen | `5` |
| metodo_extraccion | str | Método utilizado | `"pdfminer_texto"` |
| evidencia | str | Cadena de rastreo | `"Página 5: texto='...' | metodo='pdfminer_texto'"` |
| confianza | float | Puntuación 0.0 a 1.0 | `0.95` |
| estado | str | Estado de validación | `"ACEPTADO"` |
| variable_madre | str o None | Variable madre asociada | `"Utilidad_neta"` |
| tipo_documento | str | Tipo de documento origen | `"ESTADO_RESULTADOS"` |
| empresa | str | Empresa proveedora | `"Empresa X"` |

### 4.2 Convertir a DataFrame de pandas

```python
import pandas as pd

# Diccionario de salida por variable
datos_variable = {
    "variable_canonica": "Utilidad_neta",
    "cuenta_original": "Utilidad del Ejercicio",
    "codigo_puc": "300",
    "valor_periodo_actual": 30947.0,
    "valor_periodo_anterior": 28562.0,
    "periodo_actual": "2025",
    "periodo_anterior": "2024",
    "unidad": "Millones",
    "pagina": 5,
    "metodo_extraccion": "pdfminer_texto",
    "evidencia": "Página 5: texto='Utilidad del Ejercicio' | metodo='pdfminer_texto' | similitud=0.97",
    "confianza": 0.95,
    "estado": "ACEPTADO",
    "variable_madre": "Utilidad_neta",
    "tipo_documento": "ESTADO_RESULTADOS",
    "empresa": "Empresa X"
}

# Conversión a DataFrame (una fila por variable)
df = pd.DataFrame([datos_variable])

# Para un conjunto de variables, se concatenan filas
df_total = pd.concat([df1, df2, df3], ignore_index=True)
```

**Compatibilidad:** Esta estructura permite que el output del agente sea consumido directamente por el motor de indicadores del notebook `Analisis_Financiero.ipynb` sin transformaciones adicionales complejas.

### 4.3 Estructura de lote de variables

```python
# Múltiples variables en una sola estructura
datos_financieros = [
    {"variable_canonica": "Activo_Total", "valor_periodo_actual": 348129, "estado": "ACEPTADO", "variable_madre": "Activo_total", "tipo_documento": "BALANCE", "empresa": "Empresa X", ...},
    {"variable_canonica": "Resultado_Ejercicio", "valor_periodo_actual": 30947, "estado": "ACEPTADO", "variable_madre": "utilidad_neta", "tipo_documento": "ESTADO_RESULTADOS", "empresa": "Empresa X", ...},
    {"variable_canonica": "Pasivo_Total", "valor_periodo_actual": 60295, "estado": "ACEPTADO", "variable_madre": "pasivo_total", "tipo_documento": "BALANCE", "empresa": "Empresa X", ...}
]

df_financieros = pd.DataFrame(datos_financieros)
```

---

## 5. POWER BI: CAPA DE PRESENTACIÓN FUTURA

### 5.1 Rol definido

Power BI consume un modelo de datos estructurado generado por el agente financiero. No es el motor de cálculo.

### 5.2 Posibilidades futuras (por estudiar, no implementar ahora)

- Conectar Power BI Desktop con outputs pandas del agente
- Automatizar actualizaciones de datos en Dashboards
- Crear visualizaciones de series históricas (2-5 años)
- KPIs ejecutivos con indicadores de diagnóstico
- Filtrado por período, empresa, tipo_documento

### 5.3 Restricciones actuales

- No integrar Power BI en esta fase (FASE 0)
- No establecer conectividades técnicas
- No diseñar modelos de datos para Power BI
- Registrar como posible futura expansión

### 5.4 Decisión documentada

> **Power BI NO debe convertirse en el motor de cálculo financiero principal.**
> Debe consumir un modelo de datos estructurado generado por el sistema.
> 
> Las capacidades de automatización de Power BI Desktop se estudiarán posteriormente
> mediante las capacidades disponibles en el entorno, cuando haya autorización
> explícita para la Fase 11 (Power BI).

---

## 6. FORMATOS DE ARCHIVO DE SALIDA

| Formato | Contenido | Cuando usarse |
|---------|-----------|---------------|
| `.xlsx` | Datos estructurados, DataFrame, indicadores en hojas organizadas | Análisis posterior, carga en sistemas, auditoría detallada |
| `.html` | Reportes interactivos, resúmenes, evidencia enlazada | Reportes enviados, visualización en navegador, presentación ejecutiva |
| `.pbix` (futuro) | Dashboards, paneles ejecutivos, series temporales | Decision making ejecutivo, seguimiento continuo (por definir) |
| `.csv` (derivado) | Datos pujos, compatibilidad con Excel u otros tools | Intercambio rápido, backup simple |

---

## 7. ORDEN DE PRECEDENCIA DE SALIDA

1. **Datos estructurados** (Excel/DataFrame) — siempre generado, es la base
2. **HTML** — cuando se requiere presentación visual
3. **Power BI** — cuando esté autorizado y definido el modelo de datos estructurado
4. **CSV** — cuando se necesita simplicidad o compatibilidad rápida

**Ninguna salida se genera sin antes haber generado la estructura de datos estructurados (Excel/DataFrame).**