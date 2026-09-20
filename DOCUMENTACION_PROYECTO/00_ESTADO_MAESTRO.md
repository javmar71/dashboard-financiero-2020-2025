# 00_ESTADO_MAESTRO.md — MEMORIA PERSISTENTE Y ESTADO MAESTRO DEL PROYECTO

## A. IDENTIDAD DEL PROYECTO

**Nombre:** `mi_proyecto_finanzas`

**Objetivo:** Automatizar análisis financiero y auditoría financiera utilizando información empresarial multifuente.

---

## B. ESTADO ACTUAL

### Qué está construido:
- 7 notebooks `.ipynb` en `agente_financiero/` y `Estados Financieros/`
- `CONTRATO_DATOS.md` con contrato de entrada/salida del agente
- PUC consolidado en `puc.ipynb` con 21 cuentas únicas (eliminadas duplicaciones de `CLASES_VALIDAS`, `GRUPOS_VALIDOS`, `NATUREZAS_VALIDAS`, `CLASIFICACIONES_VALIDAS` y única implementación de `validar_taxonomia()`)
- Arquitectura de extracción PDF con SentenceTransformer definida
- Pipeline completo en `Analisis_Financiero.ipynb` (extracción PDF, 25 indicadores, HTML/tools)
- **Fase 2 — Diseño de variables analíticas:** Matriz 26 capacidades analíticas con 25 necesidades de información definidas; 3 hojas de entrega: RESUMEN (10 ítems), INFORMACION_NECESARIA (28 filas capacidad-información), FUENTES_DOCUMENTALES (28 fuentes documentales); validador de requerimientos transversal al usuario

### Qué está incompleto:
- Catálogo maestro de variables madre (diseñado conceptual en Fase 3, no implementado)
- Arquitectura documental multiformato (diseñada en Fase 3, no implementada)
- Integración Power BI (planeada, no iniciada)
- Ningún archivo `.py` o `.ipynb` nuevo creado (respeto restricciones)

### Qué está diseñado pero no implementado:
- Fases 3-12 completas (catálogo variables madre, indicadores, diagnósticos, salidas)
- Arquitectura multifuente completa (estados, notas, gestión, auditoría, actas, Excel)
- Ventana histórica configurada (2-5 años definida conceptualmente)

---

## C. FASES

Registro de fases conocidas y su estado:

| Fase | Título | Estado |
|------|--------|--------|
| 0 | Memoria persistente | **EN PROGRESO** (esta documentación) |
| 1 | Consolidación/auditoría PUC | **COMPLETADA** — PUC consolidado, 21 cuentas únicas, validar_taxonomia() única |
| 2 | Diseño de variables madre | **DISEÑO COMPLETADO** — 112 variables madre propuestas + diseño de 26 capacidades analíticas con matriz de necesidades; 3 hojas de entrega: RESUMEN, INFORMACION_NECESARIA, FUENTES_DOCUMENTALES; mecanismo transversal de requerimientos al usuario implementado y probado en REQUERIMIENTOS_USUARIO.xlsx |
| 3 | Catálogo maestro | **DISEÑO COMPLETADO** — 112 variables, 18 reutilizables del PUC, ~94 nuevas, 30 descartadas |
| 4 | Arquitectura documental multifuente | **DISEÑO COMPLETADO** — Definida pero no implementada |
| 5 | Extracción y normalización | **COMPLETA_CON_LIMITACIONES** — Extracción híbrida definida: Python/Docling primario, IA multimodal fallback (no integrada externamente), Python normalización/validación. Documentado en 01_ARQUITECTURA.md, 04_FUENTES_DOCUMENTALES.md, 05_SALIDAS_Y_POWER_BI.md, 06_REGLAS_DEL_PROYECTO.md. PDF Estados-Financieros.pdf registrado como COMPLETA_CON_LIMITACIONES por extracción exitosa pero no perfecta. Todavía NO se ha implementado el puente EXTRACCIÓN → INFORMACIÓN ESTRUCTURADA → 112 VARIABLES MADRE → VALIDACIÓN. |
| 6 | Mapeo semántico | **PENDIENTE** — Por iniciar |
| 7 | Indicadores | **PENDIENTE** — Por iniciar |
| 8 | Diagnóstico y auditoría | **PENDIENTE** — Por iniciar |
| 9 | Evidencia y trazabilidad | **PENDIENTE** — Por iniciar |
| 10 | Salidas | **PENDIENTE** — Por iniciar |
| 11 | Power BI | **PENDIENTE** — Por iniciar |
| 12 | Pruebas y validación | **PENDIENTE** — Por iniciar |
| 13 | Memoria persistente (FASE 0) | **PENDIENTE** — Actualmente en ejecución |

**NO declarar una fase completada si no existe evidencia.** Las fases 1 y 2 tienen evidencia concreta (PUC consolidado, diseño de catálogo). Las fases 3-12 tienen diseño pero no implementación.

---

## D. VENTANA HISTÓRICA

**Regla del proyecto:**

La ventana de análisis histórico debe permitir:

- **mínimo:** 2 años
- **máximo:** 5 años

**Comportamiento del agente:**

- Determinar automáticamente qué períodos están disponibles dentro de esa ventana
- Identificar todo lo disponible en la carpeta documental
- Conservar el inventario completo
- Seleccionar hasta 5 años para el análisis estándar
- Utilizar información anterior a 5 años como contexto cuando sea relevante

**Aplicación:** No asumir que todos los documentos pertenecen al mismo año. Un documento puede contener un año, dos años comparativos, varios años, información histórica o prospectiva.

---

## E. ARQUITECTURA MULTIFUENTE

El agente debe poder trabajar con múltiples documentos y formatos.

**Fuentes previstas:**

1. **ESTADO DE SITUACIÓN FINANCIERA** — Activo, pasivo, fechas
2. **ESTADO DE RESULTADOS** — Ingresos, costos, utilidades
3. **ESTADO DE CAMBIOS EN EL PATRIMONIO** — Variaciones patrimoniales
4. **ESTADO DE FLUJOS DE EFECTIVO** — Operación, inversión, financiación
5. **NOTAS A LOS ESTADOS FINANCIEROS** — Déglose detallado, compromisos, contingencias
6. **INFORME DE GESTIÓN** — Contexto estratégico, evolución del negocio
7. **INFORME DE AUDITORÍA** — Opinión del auditor, salvedades, riesgos
8. **ACTAS DE ASAMBLEA** — Decisiones corporativas, dividendos, capitalizaciones
9. **archivos Excel** — Información estructurada, fórmulas, tablas
10. **archivos PDF** — Estados financieros, notas, documentos variados
11. **documentos adicionales relevantes** — TXT, DOCX, etc.

**Principio clave:** Los documentos pueden corresponder a **diferentes años**. El agente debe analizar el conjunto documental, no depender de un único PDF.

---

## F. ESTRUCTURA DE CARPETA DE FUENTES

**Concepto arquitectónico:**

Una empresa puede proporcionar una carpeta que contenga múltiples documentos correspondientes a varios períodos.

**El agente debe analizar el conjunto documental, no depender de un único PDF.**

**Ejemplo de estructura posible:**

```
EMPRESA
│
├── 2022
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
├── 2023
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
├── 2024
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
└── Excel / información regulatoria
```

**Lo que el agente debe identificar en cada documento:**

- año
- tipo documental
- empresa
- período
- formato
- contenido
- relevancia

---

## G. VARIABLES MADRE

**Regla fundamental:**

Una variable madre es un valor contable o financiero **primario** extraído de una fuente.

**No es una variable madre aquello que requiere una fórmula matemática para obtenerse.**

**Ejemplos de variables DERIVADAS (NO mother):**

- EBITDA
- ROA
- ROE
- WACC
- Margen EBITDA
- Razón corriente
- Prueba ácida
- Endeudamiento
- Deuda/EBITDA
- Flujo libre
- Cualquier ratio o cálculo

**Variables madre SÍ:**

- Efectivo y equivalentes
- Activo total
- Pasivo total
- Patrimonio
- Ingresos operacionales
- Costo de ventas
- Utilidad operacional
- Utilidad neta
- Depreciaciones
- Amortizaciones
- Cuentas por cobrar
- Inventarios
- Cuentas por pagar
- Pasivo financiero
- Y otras 18+ de catálogo

---

## H. INDICADORES

**Definición:**

Los indicadores se calculan a partir del catálogo de variables madre.

**Las fórmulas deben estar documentadas y parametrizadas.**

**Ejemplo:**

| Indicador | Fórmula (resumida) | Variables madre requeridas |
|-----------|-------------------|---------------------------|
| Razón corriente | Activo corriente / Pasivo corriente | activo_corriente, pasivo_corriente |
| ROE | Utilidad neta / Patrimonio | utilidad_neta, patrimonio |
| EBITDA | Utilidad operacional + Depreciaciones + Amortizaciones | utilidad_operacional, depreciaciones, amortizaciones |

---

## I. TRAZABILIDAD

**Cada dato relevante debe poder relacionarse con:**

- empresa
- período
- documento
- tipo de documento
- página/hoja cuando sea posible
- concepto original
- variable madre
- valor
- unidad
- fuente
- nivel de confianza
- estado de validación

**Formato de registro:**

Cada salida de variable debe incluir al menos: `evidencia` que documente página, texto/origen, cuenta original, contexto contable, método utilizado.

---

## J. ESTADOS DE VALIDACIÓN

Registros permitidos para el estado de cada variable:

- **ACEPTADO:** El valor ha sido validado y es consistente con la taxonomía y contexto contable
- **DUDOSO:** El valor es incierto, la similitud semántica fue borderline o hay ambigüedad en la cuenta
- **NO_ENCONTRADO:** No se encontró evidencia suficiente para asignar un valor; el agente no debe inventar el valor
- **INCONSISTENTE:** El valor contradice otros datos del documento o violaciones de principios contables

---

## K. CONSISTENCIA CONTABLE

**Validación obligatoria:**

```
ACTIVO = PASIVO + PATRIMONIO
```

con tolerancia configurable (por defecto, permitir pequeñas diferencias por redondeo o detección OCR).

Cualquier variable que viole esta relación debe marcarse como `INCONSISTENTE`.

---

## L. SALIDAS

**Se prevén los siguientes tipos de salida:**

- **datos estructurados:** Diccionarios o DataFrames con variables canónicas, valores, metadatos
- **indicadores:** Razones, ratios y KPIs calculados a partir de variables madre
- **diagnóstico:** Estado de consistencia, advertencias, hallazgos de auditoría
- **evidencia:** Rastreo completo de origen de cada dato (página, texto, método, confianza)
- **Excel:** Salida estructurada y auditable
- **HTML:** Presentación interactiva de resultados
- **Power BI:** Dashboard de auditoría y análisis histórico (posible capa de presentación futura, no motor de cálculo principal)

**Power BI:** No debe convertirse en el motor de cálculo financiero principal. Debe consumir un modelo de datos estructurado generado por el sistema.

---

## M. LIMITACIONES ACTUALES

1. **Sin archivos .py ni .ipynb nuevos:** Proyecto trabaja exclusivamente con notebooks existentes
2. **PUC consolidado de 21 cuentas:** Ampliar catálogo requiere diseño, no fuerza sobre PUC actual
3. **Un solo PDF de prueba:** `Estados-Financieros.pdf` — la arquitectura multifactorial debe diseñarse para escalar
4. **Sin Excel de prueba:** No hay archivos XLSX/XLS del proyecto para validar prioridad Excel sobre PDF
5. **Ventana histórica teórica:** 2-5 años definida pero no implementada sobre datos reales
6. **SentenceTransformer en Analisis_Financiero.ipynb:** Modelo cargado pero aún no validado en producción real

---

## N. PRÓXIMO PASO

Continuar con **FASE 0 completada** y pasar a ejecución de las fases subsiguientes cuando haya autorización explícita, respetando siempre las restricciones de no creación de .py/.ipynb y no modificación de notebooks existentes.

---

### FASE 0 — ESTADO MAESTRO CONSOLIDADO

### CONTEXTO DEL PROYECTO DOCUMENTADO

### SIN MODIFICACIÓN DE NOTEBOOKS EXISTENTES

### SIN CREACIÓN DE ARCHIVOS .PY

### SIN EJECUCIÓN DEL PROYECTO

### LISTO PARA CAMBIO DE AGENTE O CONTINUACIÓN FASES