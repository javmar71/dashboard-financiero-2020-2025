# 01_ARQUITECTURA.md — ARQUITECTURA DEL SISTEMA

## 1. ARQUITECTURA GENERAL

```
CARPETA_EMPRESA
│
├── PDF                    # Estados financieros, notas, informes
├── XLSX / XLS             # Excel financiero estructurado
├── DOCX                   # Informes de gestión
├── TXT                    # Textos, actos, documentación
└── OTROS                  # Formatos adicionales futuros
```

**Regla:** Las empresas NO entregan información organizada obligatoriamente por año (2021/, 2022/, etc.). El agente acepta la estructura que encuentre.

---

## 2. CONVERGENCIA DE FUENTES

Estructura común por la que deben pasar todos los datos:

```
DOCUMENTO
↓
TIPO_DOCUMENTO
↓
PERÍODO
↓
INFORMACIÓN EXTRAÍDA
↓
VARIABLE MADRE / CONTEXTO
↓
EVIDENCIA
↓
VALIDACIÓN
↓
INDICADOR
↓
DIAGNÓSTICO FINAL
```

**Cada dato conserva obligatoriamente:**
- fuente
- tipo_documento
- archivo
- período
- página/hoja
- sección/celda cuando corresponda
- valor
- unidad
- confianza
- estado

---

## 3. CAPAS DEL SISTEMA

### CAPA 1 — ENTRADA DOCUMENTAL
- Lectura multifuente (PDF, XLSX, XLS, CSV, DOCX, TXT)
- Detección automática de tipo de documento
- Detección de períodos reales (no asumir por nombre archivo)
- **EXTRACTIÓN HÍBRIDA:**
  - **PASO 1:** Python / Docling — extracción primaria de texto y tablas
  - **PASO 2:** opencode (motor generativo, sin claves API en el repo) — fallback cuando Docling no recupere correctamente estructura documental; también propone valores/extracciones por sección siguiendo `INSTRUCCIONES_EXTRACCION.md`
  - **PASO 3:** Python — normalización, estructuración, trazabilidad y validación posterior
  - **VERIFICACIÓN:** big pickle (modelo/paquete de opencode) audita el OCR, la extracción, las herramientas y el código antes de aceptar (ver `GUIA_MOTOR_IA.md`)
- Extracción preservando naturaleza original (no convertir automáticamente a PDF)

### CAPA 2 — CLASIFICACIÓN Y CATÁLOGO
- Clasificación automática por categoría (liquidez, actividad, márgenes, etc.)
- Mapeo a variables madre del catálogo maestro
- Identificación de fuente primaria y secundaria
- Clasificación como contable, de gestión, externa, etc.

### CAPA 3 — VARIABLES MADRE
- Conjunto de 112 variables madre propuestas
- Cada una con: canonical name, categoría, naturaleza, unidad, tipo dato, fuente preferente, requerimientos temporales
- Distinción clara: variable madre VS indicador derivado

### CAPA 4 — INDICADORES
- Cálculo a partir de variables madre
- Fórmulas documentadas y parametrizadas
- Control de períodos requeridos (1, 2 promedios, series históricas)
- Variables externas cuando sea necesario (beta, prima riesgo, TRM, etc.)

### CAPA 5 — DIAGNÓSTICO
- Validación de consistencia contable (ACTIVO = PASIVO + PATRIMONIO)
- Detección de inconsistencias documentales
- Estados de validación: ACEPTADO, DUDOSO, NO_ENCONTRADO, INCONSISTENTE
- Generación de hallazgos y observaciones

### CAPA 6 — SALIDA / PRESENTACIÓN
- Excel: datos estructurados y auditable
- HTML: presentación interactiva
- Power BI: Dashboard de auditoría y análisis histórico (consumir modelo estructurado, no ser motor de cálculo)

---

## 4. REGLAS DE SEPARACIÓN

### DATO CONTABLE vs. CONTEXTO GERENCIAL

El agente debe distinguir estrictamente:

- **DATO CONTABLE:** Información que aparece como cuenta contable en estados financieros o notas (ej: "utilidad operacional", "cuentas por cobrar"). Fuente: estados financieros, notas.
- **CONTEXTO GERENCIAL:** Información del informe de gestión, actas, auditoría que provee contexto pero NO es cuenta contable (ej: "participación de mercado", "perspectivas", "hechos relevantes", "crecimiento"). Fuente: informe gestión, actas, auditoría. **Estas variables NO deben mezclarse con cuentas contables.**

### ESTADOS FINANCIEROS vs. NOTAS vs. GESTIÓN vs. AUDITORÍA vs. ACTAS

Cada fuente conserva su identidad y no se mezcla automáticamente:

- **ESTADOS FINANCIEROS:** Fuentes primarias de variables contables (balanes, resultados)
- **NOTAS:** Variables fuente que requieren desagregación adicional (deuda, vencimientos, tasas, partes relacionadas)
- **GESTIÓN:** Contexto gerencial, estrategia, evolución del negocio, mercado
- **AUDITORÍA:** Opinión del auditor, salvedades, cuestiones clave, incertidumbres
- **ACTAS:** Decisiones societarias, dividendos, capitalizaciones, aprobaciones

**Ninguna fuente debe mezclarse automáticamente con otra.** Cada dato conserva su procedencia.

---

## 5. VENTANA HISTÓRICA EN ARQUITECTURA

La arquitectura debe diseñarse para trabajar con:

- **MÍNIMO:** 2 años
- **MÁXIMO:** 5 años

**Comportamiento del agente:**

1. Identificar todo lo disponible en la carpeta documental (años anteriores y posteriores)
2. Conservar el inventario completo (no descartar información >5 años)
3. Seleccionar automáticamente hasta 5 años para el análisis estándar (fórmulas, indicadores)
4. Utilizar información anterior a 5 años como contexto cuando sea relevante para diagnóstico
5. Nunca interpolar datos faltantes — si no hay evidencia, devolver NO_ENCONTRADO

---

## 6. EXCEL VS. PDF: PRIORIDAD Y PROCESAMIENTO

**Cuando exista información financiera estructurada en Excel del mismo período, empresa y alcance que una información presentada en PDF:**

**PREFERENTE:** Excel estructurado ↓ Estado financiero estructurado en PDF ↓ Notas ↓ Informe de gestión ↓ Otros documentos

**Significado:** No significa que las demás fuentes se ignoren. Significa que, para **variables contables específicas**, se dará prioridad a la fuente estructurada.

**Las demás fuentes se utilizan para:**
- Corroboración
- Contexto
- Desagregación
- Evidencia
- Explicación de variaciones
- Detección de inconsistencias

**Nunca convertir automáticamente todo a PDF.** Cada formato se procesa utilizando su naturaleza original.

---

## 7. DISTINCIÓN: VARIABLE MADRE vs. INDICADOR DERIVADO vs. PRUEBA/AUDITORÍA/RED_FLAG

**Variable madre:** Dato fuente primario. Puede ser extraído, identificado, reportado, confirmado, localizado documentalmente. **No requiere fórmula matemática.**

**Indicador derivado:** Cálculo que combina una o más variables madre. **Requiere fórmula matemática.**

**Ejemplos definitivos:**

| Variable madre | Es derivado? | Razón |
|---------------|-------------|-------|
| efectivo_y_equivalentes | NO | Valor fuente extraíble directamente |
| utilidad_neta | NO | Valor fuente extraíble directamente |
| razon_corriente | SÍ | Requiere: activo_corriente / pasivo_corriente |
| ROE | SÍ | Requiere: utilidad_neta / patrimonio |
| EBITDA | SÍ | Requiere: utilidad_operacional + depreciaciones + amortizaciones |
| margen_bruto | SÍ | Requiere: utilidad_bruta / ingresos |
| rotacion_activos | SÍ | Requiere: ingresos / activos_promedio |

**Prueba / Auditoría / Red Flag:** Análisis de screening que identifica patrones financieros que ameriten investigación o revisión. **No requiere una única fórmula matemática** sino la aplicación de criterios y umbrales sobre variables madre y datos documentales. **No constituye evidencia de fraude por sí sola.**

**Ejemplos de pruebas/auditoría/red flag:**

| Prueba | Tipo | Umbral/CRITERIO | Resultado |
|--------|------|-----------------|-----------|
| Beneish M-Score | Screening manipulación | M-Score > -1,78 | RED_FLAG (mayor probabilidad de manipulación) |
| Accruals Ratio | Screening calidad | |Accurrals Ratio| > 0,10 o creciente 2+ períodos | RED_FLAG_CALIDAD_GANANCIAS |
| Divergencia utilidad-caja | Detección anomalía | Utilidad ↑ pero CFO ↓/estancado | RED_FLAG (señal de alerta) |

**Regla de oro:** Si requiere una fórmula matemática para obtenerse → **NO es variable madre**, es **indicador derivado**. Si es un análisis de screening sobre variables madre → **es prueba/auditoría/red flag**.

---

## 8. ARCHIVOS DE DOCUMENTACIÓN RELACIONADOS

Esta arquitectura se complementa con los siguientes archivos de especificación (ubicados en `DOCUMENTACION_PROYECTO/`):

- `02_VARIABLES_MADRE.md` — Catálogo detallado de 112 variables madre
- `03_INDICADORES.md` — Fórmulas e requerimientos de cada indicador
- `04_FUENTES_DOCUMENTALES.md` — Arquitectura de extracción por formato
- `05_SALIDAS_Y_POWER_BI.md` — Capas de presentación
- `06_REGLAS_DEL_PROYECTO.md` — Reglas permanentes
- `07_HISTORIAL_DE_CAMBIOS.md` — Registro de eventos del proyecto

**Novedad Fase 2:** Se incorpora la categoría `PRUEBA_AUDITORIA_RED_FLAG` como clasificación independiente de variables madre e indicadores derivados.

---

---

## 8. ARCHIVOS DE DOCUMENTACIÓN RELACIONADOS

Esta arquitectura se complementa con los siguientes archivos de especificación (ubicados en `DOCUMENTACION_PROYECTO/`):

- `02_VARIABLES_MADRE.md` — Catálogo detallado de 112 variables madre
- `03_INDICADORES.md` — Fórmulas e requerimientos de cada indicador
- `04_FUENTES_DOCUMENTALES.md` — Arquitectura de extracción por formato
- `05_SALIDAS_Y_POWER_BI.md` — Capas de presentación
- `06_REGLAS_DEL_PROYECTO.md` — Reglas permanentes
- `07_HISTORIAL_DE_CAMBIOS.md` — Registro de eventos del proyecto