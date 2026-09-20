# 07_HISTORIAL_DE_CAMBIOS.md — HISTORIAL DE CAMBIOS DEL PROYECTO

Crear un historial documental registrando como mínimo los siguientes eventos:

---

## EVENTO 1

**Proyecto inicialmente desarrollado con notebooks.**

- El proyecto `mi_proyecto_finanzas` fue concebido y desarrollado usando notebooks Jupyter `.ipynb` como modelo de ejecución principal.
- Se identificó la necesidad de automatizar análisis financieros y auditoría financiera mediante procesamiento multifuente.
- Los notebooks principales fueron ubicados en `agente_financiero/` y `Estados Financieros/`.

---

## EVENTO 2

**Se identificó que el PUC original contenía 21 cuentas.**

- El Plan Úmero Contable (PUC) inicial contenía 21 cuentas definidas.
- Estas 21 cuentas fueron la base inicial para la taxonomía y clasificación del proyecto.
- Se detectó la necesidad de consolidar y estandarizar las definiciones.

---

## EVENTO 3

**Se consolidaron las definiciones duplicadas de:**

- CLASES_VALIDAS;
- GRUPOS_VALIDOS;
- NATUREZAS_VALIDAS;
- CLASIFICACIONES_VALIDAS;
- validar_taxonomia().

**Detalle:**

- Se encontraron definiciones duplicadas o inconsistentes en estos enumeradores y funciones de validación.
- Se eliminaron duplicidades, quedando una única implementación de cada uno.
- `validar_taxonomia()` fue consolidada a una única definición en `agente_financiero/puc.ipynb`.
- **Impacto:** El PUC pasó de tener definiciones redundantes a tener 21 cuentas únicas y sin duplicidad.
- **Archivo modificado:** `agente_financiero/puc.ipynb` (modificación consolidación, no de contenido contable).

---

## EVENTO 4

**Se decidió NO basar la arquitectura futura exclusivamente en las 21 cuentas originales del PUC.**

- Una vez consolidadas las 21 cuentas, se determinó que la arquitectura futura no podía basarse exclusivamente en ellas.
- Las 21 cuentas eran insuficientes para cubrir el universo de indicadores financieros previstos para el proyecto.
- Se requirió ampliar el catálogo más allá del PUC actual.
- **Decisión documentada:** El diseño futuro debe incorporar variables nuevas, de notas, de gestión, externas, etc., más allá de las 21 cuentas del PUC.

---

## EVENTO 5

**Se definió un catálogo maestro ampliado de variables madre.**

- Durante la Fase 3, se diseñó un catálogo maestro de 112 variables madre propuestas.
- El catálogo cubre: liquidez, actividad/eficiencia, márgenes, rentabilidad, endeudamiento, apalancamiento, solidez, EBITDA, flujo de caja, capital de trabajo, WACC, estructura de capital.
- Además documenta variables provenientes de: notas contables, informes de gestión, auditoría, actas, fuentes externas.
- **Estados de clasificación:**
  - 18 variables reutilizables del PUC actual (85.7%)
  - ~94 variables nuevas por incorporar
  - 30 variables identificadas como derivadas (NO mother, solo referencia para matriz indicador → variable madre)
- **Archivo de diseño:** `DOCUMENTACION_PROYECTO/02_VARIABLES_MADRE.md`

---

## EVENTO 6

**Se estableció que los indicadores derivados NO son cuentas madre.**

- Se definió la regla fundamental: si una variable requiere una fórmula matemática para obtenerse, **NO es variable madre**, es **indicador derivado**.
- Ejemplos confirmados como derivados (no mother): EBITDA, ROA, ROE, WACC, márgenes, rotaciones, apalancamientos, flujo libre, razón corrente, prueba ácida.
- **Propósito:** Distinción clara entre datos fuente primarios y cálculos derivados.
- **Archivo de regla:** `DOCUMENTACION_PROYECTO/06_REGLAS_DEL_PROYECTO.md` (regla #11) y `02_VARIABLES_MADRE.md` (Catálogo 7: variables derivadas).

---

## EVENTO 7

**Se estableció arquitectura documental multifactoente.**

- El agente debe poder trabajar con múltiples documentos y formatos, no depender de un único PDF.
- Fuentes previstas: estados financieros, notas, informes de gestión, auditoría, actas, Excel, PDF.
- **Principio:** `1 empresa = conjunto documental`, no `1 empresa = 1 PDF`.
- **Ventana histórica:** 2-5 años mín/máx, identificando todo lo disponible y seleccionando hasta 5 años para análisis estándar.
- **Convergencia de fuentes:** Estructura común DOCUMENTO → TIPO_DOCUMENTO → PERÍODO → INFORMACIÓN EXTRAÍDA → VARIABLE MADRE / CONTEXTO → EVIDENCIA → VALIDACIÓN → INDICADOR → DIAGNÓSTICO.
- **Regla fundamental:** NO mezclar automáticamente información de fuentes diferentes cada una conserva: fuente, tipo_documento, archivo, período, página/hoja, sección/celda, valor, unidad, confianza, estado.
- **Archivo de diseño:** `DOCUMENTACION_PROYECTO/01_ARQUITECTURA.md` y `04_FUENTES_DOCUMENTALES.md`

---

## EVENTO 8

**Se estableció ventana histórica de 2 a 5 años.**

- **Regla formal:** La ventana de análisis histórico debe permitir mínimo 2 años y máximo 5 años.
- **Comportamiento del agente:**
  - Identificar todo lo disponible en la carpeta documental
  - Conservar el inventario completo (no descartar información >5 años)
  - Seleccionar automáticamente hasta 5 años para el análisis estándar
  - Utilizar información anterior a 5 años como contexto cuando sea relevante
  - No interpolar datos faltantes
- **Archivo de registro:** `DOCUMENTACION_PROYECTO/00_ESTADO_MAESTRO.md` (sección D) y `01_ARQUITECTURA.md` (sección 5)

---

## EVENTO 9

**Se estableció que el agente puede recibir carpetas con documentos de diferentes años y formatos.**

- **Nuevo paradigma de entrada:** El agente recibe `CARPETA_EMPRESA` que contiene documentos desorganizados por año y formato.
- **Formatos admitidos:** PDF, XLSX, XLS, CSV, DOCX, TXT (y futuros).
- **Tipos documentales:** INFORME_GESTION, ESTADO_SITUACION_FINANCIERA, ESTADO_RESULTADOS, ESTADO_CAMBIOS_PATRIMONIO, ESTADO_FLUJOS_EFECTIVO, NOTAS_ESTADOS_FINANCIEROS, INFORME_AUDITORIA, INFORME_ANUAL, ACTAS_ASAMBLEA, INFORMACION_FINANCIERA_EXCEL, OTRO_DOCUMENTO_FINANCIERO.
- **El agente no asume:** todos los documentos estarán presentes, o todos corresponderán a un mismo año.
- **Detección de períodos:** El agente debe detectar el período real contenido en cada documento, no asumir por el nombre del archivo.
- **Archivo de documentación:** `DOCUMENTACION_PROYECTO/04_FUENTES_DOCUMENTALES.md`

---

## EVENTO 10

**Se estableció Power BI como posible capa de presentación/auditoría.**

- **Definición:** Power BI debe consumir un modelo de datos estructurado generado por el sistema, no ser el motor de cálculo financiero principal.
- **Posibilidades futuras (por estudiar):** Automatizar Power BI Desktop, conectar con DataFrames pandas, visualización de dashboards ejecutivos, series temporales 2-5 años.
- **Restricciones actuales:** No integrar Power BI en esta fase. No establecer conectividades técnicas. Registrar como posible futura expansión (Fase 11).
- **Archivo de referencia:** `DOCUMENTACION_PROYECTO/05_SALIDAS_Y_POWER_BI.md` (sección 5 y 6)

---

## EVENTO 11

**Se identificó que anteriormente fueron creados accidentalmente archivos .py.**

**Hallazgo durante auditoría FASE 0:**

Durante la inspección de la estructura real del proyecto, se verificó lo siguiente respecto a archivos `.py`:

| Archivo mencionado en historial | Ubicación real | Estado |
|--------------------------------|----------------|--------|
| `test_fase1.py` | No encontrado en proyecto (fuera de venv o fue removido) | Verificar |
| `test_puc.py` | No encontrado en proyecto (fuera de venv o fue removido) | Verificar |
| `agente_financiero/puc.py` | No encontrado en proyecto (fuera de venv) | Verificar |

**Acción tomada:** Estos archivos fueron mencionados en el historial de conversación como creados "durante la sesión anterior", pero la auditoría física del proyecto no encontró archivos `.py` en la raíz del proyecto fuera del entorno virtual `venv`. 

**Registro:** Los nombres fueron anotados en el historial para transparencia, pero no existen como archivos .py del proyecto para eliminar. Se respetó la regla "NO eliminar archivos" y solo se documentó su (posible) existencia previa.

**Nota:** Si dichos archivos .py existen dentro del directorio `venv/` (entorno virtual), forman parte del entorno de dependencias y no del proyecto fuente, por lo que no deben ser eliminados ni considerados como parte del código del proyecto `mi_proyecto_finanzas`.

---

## EVENTO 12

**FASE 0 — Memoria persistente y estado maestro.**

- Se creó la carpeta `DOCUMENTACION_PROYECTO/` con la documentación necesaria para la continuidad del proyecto.
- Se generaron los archivos `00_ESTADO_MAESTRO.md` hasta `07_HISTORIAL_DE_CAMBIOS.md`.
- Se creó `AGENTS.md` en la raíz del proyecto (pending verificación y creación explícita).
- **Restricciones respetadas durante FASE 0:**
  - No se crearon archivos `.py` nuevos
  - No se crearon archivos `.ipynb` nuevos
  - No se modificaron notebooks existentes
  - No se ejecutó el proyecto (no se iniciaron agentes, notebooks, extracción, modelos)
  - No se eliminaron archivos
  - No se instalaron paquetes
- **Estado actual:** Documentación consolidada, proyecto en reposo listo para continuidad.

---

## EVENTO 13

**Estructura final de documentación creada:**

```
DOCUMENTACION_PROYECTO/
│
├── 00_ESTADO_MAESTRO.md          # Identidad, estado actual, fases, ventana histórica,
                                  # arquitectura multifactoente, variables madre, indicadores,
                                  # trazabilidad,validación, salidas, PUC comparación, limitaciones
│
├── 01_ARQUITECTURA.md            # Arquitectura general, capas, separación dato/contexto,
                                  # Excel/PDF prioridad, variable madre vs indicador, ventana histórica
│
├── 02_VARIABLES_MADRE.md         # Catálogo maestro de 112 variables madre, estructura por campo,
                                  # fuentes (A-G), estados financieros, notas, gestión, auditoría,
                                  # actas, Excel, WACC, flujo caja, EBITDA, apalancamiento,
                                  # dimensión temporal, PUC actual vs catálogo, resultado esperado,
                                  # control calidad, falso positivos comunes
│
├── 03_INDICADORES.md             # Lista completa de indicadores (32 definidos), fórmulas,
                                  # variables madre requeridas, fuentes esperadas, período,
                                  # promedio, externo, vacíos metodológicos, matrices
                                  # variable_madre→indicador e indicador→variable_madre
│
├── 04_FUENTES_DOCUMENTALES.md    # Arquitectura documental, tipos documento (1-11), formatos
                                  # (PDF,XLSX,XLS,CSV,DOCX,TXT), prioridad Excel, documento ≠ año,
                                  # nombre archivo ≠ sufiente, actas como contexto, auditoría,
                                  # notas contables, informe gestión, convergencia fuentes,
                                  # regla fundamental, ventana histórica
│
├── 05_SALIDAS_Y_POWER_BI.md      # Motor analítico, capas de presentación (Excel, HTML, Power BI),
                                  # arquitectura completa salida, diccionario variable, DataFrame
                                  # pandas, Power BI rol (consumir modelo, no calcular), formatos
                                  # salida, orden precedencia
│
├── 06_REGLAS_DEL_PROYECTO.md     # 27 reglas permanentes verificacion,No crear código,
                                  # no modificar notebooks, no eliminar archivos, no instalar,
                                  # no duplicar, no hardcodear, trazabilidad, separación capas,
                                  # madre vs derivado, ventana 2-5 años, múltiples documentos,
                                  # múltiples formatos, registrar incertidumbre, verificar antes,
                                  # no presentar como hecho sin verificar, contradicción instrucción,
                                  # no interpolar, consistencia ACTIVO=PASIVO+PATRIMONIO,
                                  # clasificación madre/derivado, documentación decisiones,
                                  # estructura documentación, agente con documentos incompletos
│
└── 07_HISTORIAL_DE_CAMBIOS.md    # Eventos 1-13 documentando historia proyecto:
                                  # desarrollo notebooks, PUC 21 cuentas, consolidación duplicados,
                                  # decisión no basarse solo en PUC, catálogo 112 variables,
                                  # indicadores no son madre, arquitectura multifactoente,
                                  # ventana 2-5 años, agente carpetas años/formatos, Power BI,
                                  # archivos .py identificados (auditoría), FASE 0 completada,
                                  # estructura documentación final
```

---

### CONFIRMACIÓN FINAL

```
FASE 0 — MEMORIA PERSISTENTE COMPLETADA

CONTEXTO DEL PROYECTO DOCUMENTADO

SIN MODIFICACIÓN DE NOTEBOOKS

SIN CREACIÓN DE ARCHIVOS .PY

SIN EJECUCIÓN DEL PROYECTO

LISTO PARA CAMBIO DE AGENTE
```

---

## EVENTO 14

**Modificación metodológica WACC/CAPM — Ke = ROI (instrucción ejecutiva 2026-09-19).**

- **Decisión:** queda **descartada la metodología CAPM** y la búsqueda/requerimiento de insumos externos de mercado (beta, tasa libre de riesgo, prima de riesgo). La tasa de costo del patrimonio (Ke) del WACC pasa a ser equivalente al **ROI / rentabilidad operativa interna**.
- **Fórmula en el motor:**

  `WACC = (Costo Deuda × (1 − Tasa Estatutaria Impuestos) × Deuda/(Deuda+Patrimonio)) + (ROI × Patrimonio/(Deuda+Patrimonio))`

- **Acuerdos de implementación (confirmados con decisión 2026-09-19):**
  - **Ke = ROI = ROIC (id 34)** del catálogo interno (Return on Invested Capital: UODI / capital invertido promedio). Para 2020 → **NO_CALCULABLE** (requiere promedio t y t−1; sin antecedente), sin interpolar.
  - **Costo Deuda = |intereses pagados| / deuda_financiera_total** (usa solo `c_intereses_pagados`, consistente con cobertura de intereses id 40; evita el doble conteo del artefacto `c_intereses_pagados + c_intereses_arrendamiento` que se anula en los datos normalizados).
  - **Tasa Estatutaria Impuestos**: tarifa general Art. 240 E.T. personas jurídicas régimen ordinario (2020: 32 %, 2021: 31 %, 2022+: 35 %). Único valor legal (regla universal), no insumo de mercado.
  - Ponderaciones según taxonomía: `proporcion_deuda = deuda_financiera_total/(deuda_financiera_total+patrimonio)`, `proporcion_patrimonio = patrimonio/(deuda_financiera_total+patrimonio)`. Deuda = proxy pasivo por derecho de uso (sin obligaciones financieras en la entidad).
- **Resultado ejecutado (Fase 7)** con `venv\Scripts\python.exe` → `agente_financiero\fase7_wacc_roi.py`, salidas en `salidas\fase7_wacc_roi\wacc_roi_2020_2025.{json,csv}`:
  - 2021: WACC = **0.750317** | 2022: **0.682552** | 2023: **0.331181** | 2024: **0.220066** | 2025: **0.360281** | 2020: NO_CALCULABLE (sin t−1 para promedio de ROIC).
- **Documentación actualizada:** `03_INDICADORES.md` (§2.9, §3, §5, §6) y este historial. La fila `costo_patrimonio` de `taxonomia_variable_madre.csv` queda señalada para revisión de definición (protegida: no modificar sin autorización explícita).
- **Siguiente acción:** continuar con el Módulo de Evidencia Formal o la Prueba de Validación Transversal.

## EVENTO 15

**Cierre Fases 8/9 y resolución de observaciones metodológicas (instrucción operativa Big Pickle 2026-09-19).**

- **Fase 8 (Módulo de Evidencia Formal) — CERRADA y aprobada:** `agente_financiero\fase8_evidencia_formal.py`. Cruce consolidado (87 conceptos × 6 años = 522 observaciones) vs segmentación de los estados financieros (matcher por restricción de segmento b_→SITUACION / i_→RESULTADO / c_→FLUJO, ALIAS, REQUERIDO, MIN_RECALL=0.55, ORDEN_FLUJO, fusionar). Resultado: **486 ACEPTADO / 36 NO_ENCONTRADO / 0 DUDOSO**. Salidas: `salidas\fase8_evidencia_formal\evidencia_formal_conceptos.csv` + `resumen_evidencia_formal.json`.
- **Fase 9 (Prueba de Validación Transversal) — CERRADA con 100 % de integridad matemática/sintáctica:** `agente_financiero\fase9_validacion_transversal.py`. Validadas sobre la matriz consolidada 2020–2025: ecuación patrimonial Activo=Pasivo+Patrimonio, conciliación de efectivo (cierre=inicio+aumento_neto), continuidad temporal (inicio(Y)=cierre(Y−1)), descomposición restringido+sin_restricción, aumento_neto=Op+Inv+Fin, cierre de flujo=b_efectivo, resultado del ejercicio, resultado integral, reproducibilidad EBIT/ROIC, recálculo WACC. Resultado: **74 ACEPTADO / 0 DESCUDRE / 11 DUDOSO / 4 NO_ENCONTRADO** (los DUDOSO = observaciones metodológicas; NO_ENCONTRADO 2020 sin t−1, esperados). Salidas: `salidas\fase9_validacion_transversal\matriz_consistencia_transversal.csv` + `resumen_validacion_transversal.json`.
- **Resolución de observaciones metodológicas (decisión Big Pickle):**
  - **Tasa 2022 = 35 %:** CONFIRMADA como correcta según **Ley 2155 de 2021** (Art. 240 E.T.). Se mantiene en la taxonomía (2020: 32 %, 2021: 31 %, 2022+: 35 %). No se revierte la tabla `T_ESTATUTARIA` de `fase7_wacc_roi.py`.
  - **ROIC/NOPAT (id 34):** se documenta en los metadatos del indicador (`03_INDICADORES.md` §1, §2.4) que **UODI usa la Tasa Efectiva** (impuesto corriente/EBIT) para el desempeño operativo real, y que la **Tasa Estatutaria Art. 240 E.T. queda registrada como parámetro de comparación**.
  - **RONA (id 35):** ajustada la fórmula en `src\indicadores.py` para usar el denominador **Capital Empleado** (`deuda_financiera_total + patrimonio_total`) conforme al canon `03_INDICADORES.md` §2.4 (antes usaba capital invertido). Regenerado `salidas\indicadores.csv` (RONA 2021–2025: 0.2092 / 0.1965 / 0.0925 / 0.0623 / 0.1025; 2020 NaN por promedio sin antecedente). ROIC y WACC intactos.
- **Hallazgo formal (Protocolo Pasos B/C):** `i_ori_inmuebles` **2022 = $2.465** en consolidado vs **$11.751** en Nota 25 del estado financiero. Registrado en `salidas\bitacora_revisiones_humanas.md` para revisión cualitativa humana; no interpola, no corrige sin intervención.
- **Bitácora de revisiones humanas creada:** `salidas\bitacora_revisiones_humanas.md` (consolida puntos atípicos: i_ori_inmuebles 2022, divergencia metodológica tasa efectiva vs estatutaria).
- **Documentación actualizada:** este historial, `ESTADO_PROYECTO_HANDOFF.md`, `03_INDICADORES.md` (id 34/35, §2.4, §2.9).
- **Siguiente acción:** con confirmación de Big Pickle, proceder a las capas finales del proyecto — Tableros / Power BI / Reportes de Inteligencia Financiera (ver `05_SALIDAS_Y_POWER_BI.md`).

## EVENTO 16

**Paso 1 Capas Finales — Data Mart, DAX y Maquetación Power BI (instrucción operativa Big Pickle 2026-09-19).**

- **Data Mart (Star Schema) generado:** `agente_financiero\fase10_powerbi_data_mart.py` consolida `salidas\indicadores.csv`, `salidas\fase7_wacc_roi\wacc_roi_2020_2025.csv`, `salidas\fase8_evidencia_formal\evidencia_formal_conceptos.csv` y `salidas\datos_estados_financieros.csv` en un modelo tabular optimizado para Power BI: `dim_fecha` (6), `dim_indicador` (65, catálogo completo), `dim_concepto` (87), `fact_indicadores` (390 = 65 × 6 años), `fact_estados` (522), `fact_wacc` (6, con `capital_empleado` derivado) y `fact_evidencia` (522). Salida: `salidas\power_bi\*.csv` + `data_mart_resumen.json`.
- **Librería de medidas DAX (3 carpetas cerradas):** [Efectivo & Liquidez] (razón corriente, prueba ácida, razón de efectivo, capital de trabajo neto, días de trabajo neto), [Rentabilidad & EVA] (ROIC id 34, RONA id 35, WACC Fase 7, Spread ROIC−WACC, EVA = NOPAT − WACC × Capital Empleado), [Estructura & Riesgo] (cobertura de intereses id 40/41, endeudamiento total id 6, deuda fin/EBITDA id 55/56, ICSD id 53). Z-Score documentado como **NO_APLICA** por ausencia de capitalización de mercado y de manufactura (Regla 1: sin evidencia → no inventar).
- **Maquetación de 4 páginas Power BI:** P1 Resultados (ROIC/WACC/Spread/EVA), P2 Efectivo y Liquidez, P3 Estructura y Riesgo, P4 Evidencia Formal y Trazabilidad. Con slicers de año, KPIs superiores, gráficos de líneas 2020–2025 y matrices de detalle. Especificación completa en `salidas\power_bi\GUIA_IMPLEMENTACION_POWER_BI.md`.
- **Siguiente acción (con OK de Big Pickle):** redactar el Reporte de Inteligencia Financiera (capa final).

## EVENTO 17

**Reporte de Inteligencia Financiera 2020–2025 (instrucción operativa Big Pickle 2026-09-19).**

- **Aprobación del Paso 1 (Data Mart/Power BI):** CERRADO y aprobado por Big Pickle (`fase10_powerbi_data_mart.py`, `salidas\power_bi\GUIA_IMPLEMENTACION_POWER_BI.md` + Data Mart).
- **Reporte redactado:** `salidas\REPORTE_INTELIGENCIA_FINANCIERA.md` (documento principal, 7 secciones) y `salidas\RESUMEN_EJECUTIVO_INTELIGENCIA_FINANCIERA.md` (versión consolidada/resumen, estándar Markdown del proyecto).
- **Contenido:** Resumen Ejecutivo, Creación de Valor (ROIC vs WACC, Spread, NOPAT, EVA), Liquidez/Efectivo/Capital de Trabajo (incl. Calidad de Utilidades FCO/UN), Estructura de Deuda y Solvencia, Matriz de Alertas Tempranas y Salvedades (i_ori_inmuebles 2022, divergencias tributarias), Dictamen de Sostenibilidad (hipótesis de negocio en marcha) y Consistencia de Cifras (mapeo completo a matrices auditadas).
- **Hallazgos críticos 2020–2025:** (1) Spread ROIC−WACC positivo pero delgado (+0,35…+1,88 pp) con EVA negativo sistemático (base capital empleado 260–300 M$); (2) FCO/UN negativo 2024–2025 (−0,35 / −0,48); (3) CxC +2,11× 2025 vs ingresos +15 %; (4) caída utilidad neta −70 % 2024 (rebote +47,4 % 2025); (5) salvedad de auditoría desde 2023; (6) hallazgo i_ori_inmuebles 2022 (2.465 vs 11.751) pendiente de pronunciamiento humano. Dictamen: negocio en marcha VÁLIDO sin duda material.
- **Trazabilidad:** cada cifra mapeada a `salidas\indicadores.csv`, `datos_estados_financieros.csv`, `fase7_wacc_roi\`, `fase8_evidencia_formal\`, `fase9_validacion_transversal\` y `bitacora_revisiones_humanas.md`. Tabla EVA verificada aritméticamente con `venv\Scripts\python.exe`.

## EVENTO 18

**CIERRE DEFINITIVO — Fase 10 (Capa de Visualización e Inteligencia Financiera) CERRADA Y ENTREGADA 100 % (instrucción operativa Big Pickle 2026-09-19).**

- **Power BI Desktop LANZADO:** `Start-Process "C:\Users\Public\Desktop\Power BI Desktop.lnk"` — proceso verificado en ejecución (PBIDesktop Id 9740 + msmdsrv Id 4848, 2026-09-19 15:41).
- **Data Mart listo para consumo en Power BI:** 7 artefactos en `salidas\power_bi\` — `dim_fecha.csv` (6), `dim_indicador.csv` (65), `dim_concepto.csv` (87), `fact_indicadores.csv` (390), `fact_estados.csv` (522), `fact_wacc.csv` (6, con capital_empleado) y `fact_evidencia.csv` (522), más `data_mart_resumen.json`. Nota de nomenclatura: los archivos se generan en minúsculas (`fact_indicadores.csv`, etc.) conforme al script `fase10_powerbi_data_mart.py`; se mantienen así para consumo directo del modelo.
- **Guía de implementación disponible:** `salidas\power_bi\GUIA_IMPLEMENTACION_POWER_BI.md` (Modelo Star Schema + relaciones + librería DAX en 3 carpetas + maquetación de 4 páginas + reglas de validación de carga).
- **Reporte de Inteligencia Financiera entregado:** `salidas\REPORTE_INTELIGENCIA_FINANCIERA.md` + `salidas\RESUMEN_EJECUTIVO_INTELIGENCIA_FINANCIERA.md`.
- **Estado del encargo: CONCLUIDO.** Pendientes NO bloqueantes para el cierre: pronunciamientos humanos de la bitácora (i_ori_inmuebles 2022; observaciones cualitativas Fase 5/6), que se resuelven en el entorno de auditoría fuera del pipeline.

## EVENTO 19

**Reconfiguración tecnológica de Fase 10 — Sustitución de Power BI por Dashboard gratuito Streamlit/Plotly (instrucción operativa Big Pickle 2026-09-19).**

- **Decisión:** Power BI (propietario) sustituido por **Streamlit + Plotly 100 % open source y gratuito** como capa de entrega de la Fase 10. El Data Mart en `salidas\power_bi\` permanece (modelo de datos base), ahora consumido por la app en lugar del `.pbix`.
- **Aplicación creada:** `salidas\dashboard\app.py` (Streamlit 1.64.0 + Plotly 6.9.0). Consume directamente las tablas del Data Mart (`dim_*`, `fact_*`), KPIs sensibles al selector de período y 4 pestañas:
  1. **Creación de Valor** — KPIs ROIC/WACC/Spread/EVA + líneas ROIC vs WACC vs Spread + barras EVA y NOPAT/EBITDA.
  2. **Efectivo y Liquidez** — razón corriente, prueba ácida, razón de efectivo, capital de trabajo neto, PDM y gráfico de **Calidad de Utilidades FCO/UN**.
  3. **Estructura y Riesgo** — endeudamiento, coberturas (id 40/41), deuda financiera/EBITDA, ICSD y **alertas tempranas (red flags)** filtradas por estado.
  4. **Evidencia y Bitácora** — matriz de trazabilidad (fact_evidencia, 522 registros, filtro por estado) y **hallazgo i_ori_inmuebles 2022 (2.465 vs 11.751, DUDOSO)**.
- **Entorno:** `pip install streamlit` en venv (plotly 6.9.0 ya presente). Verificado con `AppTest` (0 excepciones, 4 tabs renderizadas) y por HTTP (`GET /_stcore/health` → `ok`).
- **Lanzamiento local:** `venv\Scripts\python.exe -m streamlit run "salidas\dashboard\app.py" --server.port 8501` — servidor activo en `http://localhost:8501` (verify 2026-09-19).
- **Consistencia:** KPIs del dashboard coinciden con `REPORTE_INTELIGENCIA_FINANCIERA.md` (EVA 2021 = −152.545,8; FCO/UN 2025 = −0,48), trazados a `salidas\indicadores.csv` y `fase7_wacc_roi\`.

## EVENTO 20

**Módulo de generación de Informe Diagnóstico Financiero PDF con agente IA (instrucción operativa Big Pickle 2026-09-19).**

- **Módulo creado:** `salidas\reportes\generar_informe_pdf.py` (fpdf2 2.8.8 + matplotlib, instalados en venv; reportlab/weasyprint no usados).
  - `construir_contexto()` extrae directamente KPIs y series 2020-2025 del Data Mart `salidas\power_bi\` (fact_indicadores, fact_wacc, fact_evidencia, fact_estados): ROIC, WACC, Spread, NOPAT y EVA (NOPAT − WACC × Capital Empleado), FCO/UN, Endeudamiento, Cobertura, Deuda/EBITDA, ICSD, margen operativo, variación CxC, crecimientos, Evento 522 (486/36/0) y hallazgo `i_ori_inmuebles` 2022 (2.465 vs 11.751).
  - `construir_prompt()` / `redactar_analisis()` redactan la narrativa estructurada en markdown (5 secciones): Resumen Ejecutivo y Creación de Valor; Diagnóstico 2020-2025 (puntos fuertes vs débiles); Matriz de Alertas y Semáforo de Riesgo; Análisis Forense y Bitácora; Recomendaciones y Plan de Acción. Regla 1 (no inventar/interpolar): toda cifra proviene del Data Mart.
  - `generar_graficos()` genera PNG con matplotlib (ROIC vs WACC+Spread, FCO/UN) en `salidas\reportes\graficos\`.
  - `compilar_pdf()` (fpdf2, Arial TTF) produce `salidas\reportes\Informe_Diagnostico_Financiero_2020_2025.pdf` (6 páginas, portada + 5 secciones + 2 gráficos incrustados).
  - API pública: `generar_informe_pdf()` (devuelve ruta) y `generar_informe_bytes()` (bytes para descarga).
- **Integración dashboard:** `salidas\dashboard\app.py` — en Pestaña 4 (Evidencia y Bitácora) botón `st.button("Generar Informe PDF con IA")` + `st.download_button` con descarga en tiempo real (import `salidas\reportes\generar_informe_pdf.py`).
- **Verificación:** generación CLI OK (145 KB, header `%PDF-`, 6 páginas, 2 imágenes, todas las secciones y cifras presentes vía pypdf); **AppTest: 0 excepciones iniciales, 0 excepciones tras clic en el botón**, `st.success` confirmado. Servidor relanzado en `http://localhost:8501` (`/_stcore/health` → `ok`).
- **Consistencia:** EVA 2025 = −69.250 M$, FCO/UN 2025 = −0,482, Spread 2025 = 0,0053 (coinciden con Dashboard y Reporte de Inteligencia Financiera).

## EVENTO 21

**Inclusión de la matriz completa de indicadores (65) por familia y periodo en el Informe PDF (solicitud usuario 2026-09-19).**

- **Motivo:** el usuario reportó que el informe no mostraba todos los indicadores; solicitó un cuadro clasificado por familias y ordenado del año más antiguo al más reciente.
- **Alcance corregido:** el catálogo del Data Mart tiene **65 indicadores** (no 55): 58 con valores calculados y 7 sin base de cálculo (inventarios y ciclos, ids 19-22, 36, 37, 43), que se muestran como `n/d`.
- **Cambios en `salidas\reportes\generar_informe_pdf.py`:**
  - `_tabla_indicadores_completa()`: pivota los 65 indicadores del catálogo por periodo 2020-2025, ordenados por familia y año (parte de `dim_indicador` para garantizar las 65 filas, sin producto cartesiano).
  - `table_por_familia()` y `fmt_indicador()`: generan la Sección 6 en markdown agrupada por las 9 familias, con formateo por unidad (moneda, ratio, porcentaje, veces, días).
  - `redactar_analisis()`: añade la Sección 6 "Matriz consolidada de indicadores (65) por familia y periodo".
  - `compilar_pdf()` / `_escribir_matriz_landscape()`: renderiza la Sección 6 en **páginas A4 apaisadas** (7 columnas no caben en vertical).
- **Bugs corregidos:** `pdf.set_b_margin()` inexistente en fpdf2 2.8.8 (disparaba el `except` y volcaba todo el informe como texto plano, mostrando los `|` de markdown crudos); celdas con `<`/`>` sin escapar (`FCO/UN < 0`, `->`) que rompían `write_html`; acceso a columnas de periodo con `itertuples` (valores `n/d` indebidos).
- **Verificación:** PDF de 8 páginas (4 verticales + 4 apaisadas), sin tuberías markdown crudas, con los 65 ids (1-65) presentes por familia y valores reales (p. ej. Razón corriente 2020 = 8,685). AppTest del dashboard: 0 excepciones antes y después del clic; servidor en `http://localhost:8501`.

## EVENTO 22

**Propagación de la matriz de los 65 indicadores por familia y periodo al HTML interactivo y a los reportes MD (aprobación usuario 2026-09-19).**

- **HTML interactivo:** `AUTOMAT ANALISIS FIN\agente_financiero\fase6_salidas.py` — nueva sección 3 "Matriz consolidada de los 65 indicadores por familia y período (2020-2025)" (tabla por familia, del año más antiguo al más reciente; 7 indicadores sin base de cálculo como «—»); gráficos renumerados desde 4. Regenerado con `venv\Scripts\python.exe "AUTOMAT ANALISIS FIN\agente_financiero\fase6_salidas.py"` → `salidas\informe_financiero_interactivo.html` (65/65 indicadores, 9/9 familias). También se regeneraron `salidas\REPORTE_FINAL_INDICADORES.xlsx` y `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv` (mismos insumos: `indicadores.csv`, `diagnostico_red_flags.json`).
- **Reportes MD:** nueva Sección 8 en `salidas\REPORTE_INTELIGENCIA_FINANCIERA.md` y Sección 7 en `salidas\RESUMEN_EJECUTIVO_INTELIGENCIA_FINANCIERA.md` con la matriz completa (65 indicadores) por familia y periodo; fuente `salidas\indicadores.csv`.
- **Formato:** valores según unidad (moneda con miles; ratios/porcentaje 3 decimales; veces/días 2 decimales; coma decimal); sin base de cálculo → «—».
- **Verificación:** los tres informes contienen 65/65 indicadores y 9/9 familias. Sin cambios en cifras (Regla 1).

## EVENTO 23

**Corrección tipográfica, de codificación (Mojibake) y de formato monetario del dashboard Streamlit (orden de trabajo del usuario, 2026-09-19).**

- **Archivo:** `salidas\dashboard\app.py` reescrito íntegramente en UTF-8 (sin cambios funcionales en la lógica de datos/gráficos/PDF).
- **Codificación:** eliminada la secuencia Mojibake `â€”` (5 ocurrencias: líneas de títulos/encabezados/avisos) → reemplazada por el guion largo `—`; tildes y caracteres castellanos restaurados en títulos y etiquetas visibles (Creación de Valor, Prueba ácida, Razón corriente, Índice, Interpretación, Diagnóstico, Evolución, Semáforo, Bitácora, Pestaña, auditoría, Opinión).
- **Banner simplificado:** sustituido por `st.caption("Data Mart: `salidas\\power_bi\\` | Modelo financiero consolidado (Sin recalculación)")`.
- **Formato monetario (antirrecorte):** nuevo helper `fmt_pesos(valor, decimales)` — cifras grandes en M$ con separador de miles y signo previo (`EVA` 2025 = `-$69,249.8 M`; `Capital de trabajo neto` = `$268,659 M`), eliminando el truncamiento de tarjetas.
- **Unidades estandarizadas:** ROIC/WACC/Spread pasan a porcentaje real ×100 (`ROIC` 36.6%, `WACC` 36.0%, `Spread` 0.5%), coherentes con los ejes `.0%` de los gráficos (antes se mostraba `0.366%`).
- **CSS:** se inyecta estilo sobre `[data-testid="stMetricValue"]` (fuente, `white-space:normal`, `overflow:visible`, `text-overflow:clip`) para evitar el recorte de la métrica.
- **Limpieza:** eliminado código muerto en la pestaña de liquidez y la calculadora de la prueba ácida (ahora usa el indicador id 2).
- **Verificación:** `py_compile` OK; `AppTest` con 0 excepciones iniciales y tras el clic en «Generar Informe PDF con IA» (1 `st.success`); métricas renderizadas sin truncar: ROIC 36.6% / WACC 36.0% / Spread 0.5% / EVA -$69,249.8 M / Capital de trabajo neto $268,659 M / Cobertura 96.8x / Deuda/EBITDA 0.07x / ICSD 25.7x.

## EVENTO 24

**Corrección del CSS roto del informe HTML interactivo (la matriz de los 65 indicadores no se veía correctamente).**

- **Causa:** en `AUTOMAT ANALISIS FIN\agente_financiero\fase6_salidas.py` el bloque `<style>` se escribía con **dobles llaves** (`body{{...}}`, `.tbl th{{...}}`) sin aplicar `.format()`, por lo que el navegador descartaba todas las reglas; en particular se perdía `.resp{overflow:auto}`, dejando las columnas de años (2020-2025) fuera del área visible en pantallas estrechas.
- **Corrección:** llaves simples en todo el bloque CSS; `.resp` pasa a `overflow-x:auto` con scroll táctil; `.tbl` con `min-width`, celdas `white-space:nowrap` y encabezado `position:sticky`; añadido `<meta name="viewport">`.
- **Verificación:** regenerado `salidas\informe_financiero_interactivo.html`; sin `{{` en el CSS; 9 tablas de familia y **65/65 indicadores × 6 años (390 celdas de datos)**; sección 3 localizada al inicio del documento. Volcado del DOM con Chrome headless (`--dump-dom`): 9 tablas y 74 filas en la Sección 3 con los valores (p. ej. `8.6851`, `9.26008`) presentes en el render; conclusión: el archivo es correcto. También se regeneraron `salidas\REPORTE_FINAL_INDICADORES.xlsx` y `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv`.
- **Nuevo entregable ligero:** `escribir_matriz_html(df)` en `fase6_salidas.py` genera `salidas\MATRIZ_65_INDICADORES.html` (21 KB, una sola tabla de 65 filas × 2020-2025 con separador de miles, `«—»` para vacíos, sin plotly) para verificación rápida en cualquier navegador. Si el informe interactivo (5,8 MB con Plotly incrustado) no muestra la matriz, abrir este archivo o cerrar y reabrir la pestaña (no solo Ctrl+F5).

## EVENTO 25

**Reestructuración del informe PDF: un capítulo por familia (9) y capítulo de riesgos/alarmas.** (orden de trabajo del usuario 2026-09-19, opción "Ambos de una vez").

- **Archivo:** `salidas\reportes\generar_informe_pdf.py` ampliado por bloques (sin cambios en `cargar_mart`, `serie_indicador`, `construir_contexto`, `construir_prompt`, `_tabla_indicadores_completa`, `md_a_html`, `_b` ni en la API `generar_informe_pdf()` / `generar_informe_bytes()`).
- **Capítulos por familia (secciones 3-11):** nuevas funciones `capitulo_familia()` y `familia_analisis()` con narrativa determinística (n.º de indicadores con/sin base, representativos 2020→2025) y tabla completa de la familia; `_tabla_markdown()` unifica el formato de la tabla por unidad (`fmt_indicador`).
- **Capítulo de riesgos y alarmas (sección 12):** nueva función `capitulo_riesgos()` con semáforo (`_semaforo()`) de EVA, FCO/UN, var. CxC, spread, margen, crecimiento, endeudamiento, cobertura y deuda/EBITDA, más matriz priorizada por severidad y alertas de trazabilidad/cobertura del modelo (NO_ENCONTRADO y DUDOSO).
- **Gráficos por familia:** nueva `_grafico_familia()` (small-multiples 2×n de los indicadores con valores de cada familia); `generar_graficos()` devuelve `(ROIC/WACC, FCO/UN, {familia: ruta})`.
- **Compilación:** `informePDF(FPDF)` con pie de página y numeración; `_dividir_h2()` segmenta el HTML por capítulo e inserta el gráfico correspondiente (globales tras la sección 2 y el de familia tras su capítulo); `_write_html_seguro()` evita que una tabla problemática aborte el documento; `_insertar_grafico()` controla el salto de página con la altura real de la imagen (Pillow). Eliminada `_segmentar_html()` (obsoleta).
- **Verificación:** `py_compile` OK; PDF de **17 páginas**, **9 capítulos de familia**, capítulo **RIESGOS Y ALARMAS** con semáforo y alertas, **11 imágenes** (2 globales + 9 de familia), matriz consolidada apaisada presente y valores reales (`0,366` ROIC 2025; `i_ori_inmuebles`). `AppTest` del dashboard: **0 excepciones**, 11 pestañas, 72 métricas.
- **Ajuste posterior de la portada (solicitud del usuario):** eliminadas de la primera página las líneas "Generado por el agente IA (opencode + big pickle)" y "Data Mart: salidas/power_bi/ | Trazabilidad total sin interpolar (Regla 1)". La portada conserva título, "2020-2025", línea divisoria y resumen (pág. 1 con contenido, verificado por extracción de texto). PDF regenerado.

## EVENTO 26

**Identificación de entidad parametrizada en HTML y PDF (nombre y NIT) desde una única configuración.**

- **Configuración única:** nuevo archivo `salidas\config_entidad.json` con `nombre_entidad` y `nit`. Campos vacíos = modo agnóstico (`Entidad: reservada`); para **cualquier otra empresa** basta editar este JSON — los generadores no cambian (Regla de agnosticismo preservada: el código no contiene nombres/NIT de entidades).
- **HTML** (`AUTOMAT ANALISIS FIN\agente_financiero\fase6_salidas.py`): nueva función `cargar_entidad()`; el `informe_financiero_interactivo.html` muestra empresa + NIT en el `<title>` y bajo el `<h1>`, y `MATRIZ_65_INDICADORES.html` bajo su `<h1>`. Escape HTML con `html.escape` (import `html`); variable del documento renombrada a `html_doc` en `escribir_matriz_html()` para evitar colisión con el módulo `html`.
- **PDF** (`salidas\reportes\generar_informe_pdf.py`): `cargar_entidad()` (+ `import json`); portada muestra `Entidad: {nombre} | NIT {nit}` en el resumen y la narrativa añade `**Entidad:** {nombre} - NIT {nit}.` tras la línea de generación.
- **Verificación:** con valores de prueba ("EMPRESA PRUEBA S.A." / "000000000-0") aparecieron en título y encabezado HTML y en la pág. 1 y 2 del PDF; restaurada la config vacía y regenerados los entregables finales (HTML 65 indicadores, matriz HTML, XLSX, CSV y PDF).

## EVENTO 27

**Reorganización del árbol: `salidas\` trasladada al interior de `AUTOMAT ANALISIS FIN\salidas\`.** (orden de trabajo del usuario 2026-09-19: "Mover TODO a AUTOMAT ANALISIS FIN", opción elegida en el selector).

- **Movimiento:** `mi_proyecto_finanzas\salidas\` → `AUTOMAT ANALISIS FIN\salidas\`. Todo el contenido (reportes, dashboard, Data Mart `power_bi`, `config_entidad.json`, entregables HTML/XLSX/CSV) quedó reubicado sin pérdida. El dashboard quedó concentrado en la carpeta principal del proyecto.
- **Constantes de ruta actualizadas** (salidas pasa a ser hija de `AUTOMAT ANALISIS FIN`):
  - `agente_financiero\fase5_diagnostico.py`, `fase6_salidas.py`, `fase7_wacc_roi.py`, `fase8_evidencia_formal.py`, `fase9_validacion_transversal.py`: `parents[2]` → `parents[1]` (raíz = `AUTOMAT ANALISIS FIN`).
  - `fase10_powerbi_data_mart.py`: `"..", ".."` → `".."`.
  - `fase6_salidas.py`: `OUT_CSV_65` sin el segmento `"AUTOMAT ANALISIS FIN"` (ya incluido en la raíz).
  - `salidas\dashboard\app.py` y `salidas\reportes\generar_informe_pdf.py`: **se mantienen en `parents[2]`** (interpretación verificada: al estar dentro de `salidas`, la raíz de estos módulos es `AUTOMAT ANALISIS FIN`); `sys.path` del dashboard hacia `reportes` (parents[1]) sigue válido.
  - `iniciar_dashboard.bat`: ruta de la app actualizada a `"AUTOMAT ANALISIS FIN\salidas\dashboard\app.py"`.
- **Verificación:** `py_compile` OK en los 8 módulos; `fase6_salidas.py` regeneró CSV/XLSX/HTML/matriz (exit 0) en la nueva ubicación; PDF regenerado **17 páginas** (747 667 bytes) en `AUTOMAT ANALISIS FIN\salidas\reportes\`; `AppTest` del dashboard: **0 excepciones, 11 pestañas, 72 métricas**; servidor lanzado con `iniciar_dashboard.bat --silent` → health **200** en `http://localhost:8501`.
- **Nota:** el pipeline histórico de la raíz (`src\...`, config de la raíz) permanece como respaldo y no se tocó (Regla 2 / protección de `src`), por lo que puede referenciar la antigua `salidas\` de la raíz.

## EVENTO 28

**Identidad de la entidad configurada y mostrada en el dashboard (encabezado).**

- **Dashboard** (`AUTOMAT ANALISIS FIN\salidas\dashboard\app.py`): el encabezado muestra `**Entidad:** {nombre} — NIT {nit}` (o el nombre solo si falta el NIT), reutilizando `informe.cargar_entidad()` de `generar_informe_pdf.py`; se retiró del encabezado el texto informativo "Data Mart: salidas/power_bi\ | Modelo financiero consolidado". Se conserva `Modelo financiero consolidado (Sin recalculación)` como caption y, si la config está vacía, un texto neutro ("Entidad: reservada…") para no romper la UI.
- **Identidad cargada en `config_entidad.json`:** `FIDUCIARIA LA PREVISORA S.A.` (confirmada en fuente primaria: cabecera de Estados de Situación/Resultados 2021 y narrativa "1. INFORMACION GENERAL" del Informe de Gestión). **NIT no fijado:** no aparece en los estados financieros y los identificadores XBRL son inconsistentes entre años (830053105-3 en 2021-2023 vs 900251864-8/901870663-3 en 2024-2025, con 860525148-5/900251864-8 adicionales). Conforme a la Regla 1 y al Protocolo de Validación (Paso C), el NIT se deja pendiente de confirmación humana.
- **Verificación:** `AppTest` del dashboard 0 excepciones; servidor reiniciado y health 200 en `http://localhost:8501`.

## EVENTO 29

**Publicación en GitHub y preparación del despliegue en Streamlit Community Cloud.** (orden de trabajo del usuario, 2026-09-19: verificar estructura remota, desplegar y ejecutar correcciones UTF-8/visualización en el dashboard).

- **Repo público confirmado:** `https://github.com/javmar71/dashboard-financiero-2020-2025`, rama `master` (HEAD `45e178ba`). La raíz del repo corresponde al contenido de `AUTOMAT ANALISIS FIN\` (`DOCUMENTACION_PROYECTO\`, `Estados Financieros\` 2021-2025, `agente_financiero\`, `salidas\`); sin `src/`, `venv/` ni `config.py`.
- **Verificación de estructura remota:** presentes todos los artefactos de runtime del dashboard — `salidas\dashboard\app.py` (**idéntico al local**, 20 826 bytes; versión UTF-8/Mojibake corregida en EVENTO 23 ya publicada), Data Mart `salidas\power_bi\` (dim_fecha/indicador/concepto + fact_indicadores/estados/wacc/evidencia), `salidas\reportes\generar_informe_pdf.py` (importado por el dashboard), `config_entidad.json`, `diagnostico_red_flags.csv`, `bitacora_revisiones_humanas.md`, `REPORTE_INTELIGENCIA_FINANCIERA.md`, `fase7_wacc_roi\` y `fase8_evidencia_formal\`.
- **Corrección de visualización para despliegue:** en `salidas\dashboard\app.py` el fallback del caption de entidad apuntaba a `AUTOMAT ANALISIS FIN\salidas\config_entidad.json` (ruta local inexistente en el repo/cloud) → corregido a `salidas\config_entidad.json`. Sin otros cambios: las correcciones de codificación, formato monetario y CSS de EVENTO 23 ya estaban en el repo.
- **Archivos de despliegue creados en la raíz del repo** (`AUTOMAT ANALISIS FIN\`):
  - `requirements.txt`: `streamlit==1.64.0`, `plotly==6.9.0`, `pandas==3.0.5`, `numpy==2.4.6`, `matplotlib==3.11.1`, `fpdf2==2.8.8` (versiones fijas del venv probado).
  - `.streamlit\config.toml`: tema corporativo (primary `#1F4E79`) y `gatherUsageStats=false`.
- **Validación:** `py_compile` OK en `app.py` y `generar_informe_pdf.py`; `AppTest` del dashboard **0 excepciones, 72 métricas**, título OK y selector por defecto 2025 (SMOKE_OK).
- **Pendiente del usuario:** subir al repo los 3 archivos (`requirements.txt`, `.streamlit\config.toml`, `salidas\dashboard\app.py` actualizado) y crear la app en https://streamlit.io/cloud con **Main file path = `salidas/dashboard/app.py`** en rama `master`. URL esperada: `https://<alias>.streamlit.app`.

## EVENTO 30

**Despliegue en Streamlit Community Cloud COMPLETADO — app pública ACTIVA (2026-09-19, noche).**

- **App en producción:** `https://dashboard-financiero-2020-2025.streamlit.app` (repo público `javmar71/dashboard-financiero-2020-2025`, rama `master`, Main file path `salidas/dashboard/app.py`). **Confirmado funcional por el usuario.**
- **Error inicial detectado y resuelto:** el `requirements.txt` publicado junto a la subida contenía solo `streamlit / pandas / numpy / plotly / openpyxl` (sin versionar) → `ModuleNotFoundError: No module named 'matplotlib'` al importar `salidas\reportes\generar_informe_pdf.py` (importado por el dashboard en el arranque). Faltaban **`matplotlib` y `fpdf2`**.
- **Fix (dependencias):** `requirements.txt` sobrescrito en la raíz del repo con las versiones fijas probadas del venv: `streamlit==1.64.0`, `pandas==3.0.5`, `numpy==2.4.6`, `plotly==6.9.0`, `matplotlib==3.11.1`, `fpdf2==2.8.8`, `openpyxl`. Archivo sin BOM y con salto de línea final (pip-friendly). `matplotlib.use("Agg")` ya existía en `generar_informe_pdf.py` → headless sin pantalla; no se requirió `packages.txt`.
- **Git:** commit `c0c5c5a` en `master` ("fix: actualiza dependencias de matplotlib, fpdf2 y openpyxl para Streamlit Cloud"). Se requirió `git pull --rebase --autostash` para integrar el commit remoto `28b6de3` ("Added Dev Container Folder", `.devcontainer\devcontainer.json`) antes de empujar. Push verificado: `28b6de3..c0c5c5a master -> master`.
- **Verificación:** `git show origin/master:requirements.txt` = contenido exacto ejecutado; el rebuild de Streamlit Cloud re-instaló las dependencias y la app quedó **renderizando el dashboard**. Nota de método: `/_stcore/health` en Community Cloud devuelve el shell HTML incluso con la app corriendo (se comparó contra `data-profiler.streamlit.app`), por lo que **no es señal fiable**; la confirmación final fue humana y funcional.
- **Pendiente no crítico:** publicar en el repo los pendientes locales (fix de caption en `app.py` de EVENTO 29, `.streamlit\config.toml`, `ENLACE.txt` del modo dual y esta documentación). `salidas\dashboard\__pycache__\app.cpython-312.pyc` **NO debe versionarse**.

## EVENTO 31

**Arquitectura multi-tenant con aislamiento aprobada — PoC ejecutada e inmutabilidad de La Previsora verificada (2026-09-20).**

- **Decisión del usuario:** al detectarse que la arquitectura `almacen_empresas\<empresa>\` y el flag `--empresa` no existían, se solicitó y **aprobó** la opción "Aislamiento completo" (PoC).
- **Reestructuración del motor:** `agente_financiero\fase10_powerbi_data_mart.py` ahora acepta `--empresa <id>`. Con flag usa `almacen_empresas\<empresa>\salidas` (insumos y salidas), sin flag conserva la entidad ancla (raíz `salidas\`). Genera las **7 tablas del Data Mart** (`dim_fecha`, `dim_indicador`, `fact_indicadores`, `dim_concepto`, `fact_estados`, `fact_wacc`, `fact_evidencia`) + `data_mart_resumen.json`.
- **Generador sintético:** `agente_financiero\construir_empresa_prueba.py` crea el workspace de `empresa_prueba_2025` con datos **SINTÉTICOS** (semilla 2025, identidad contable `activo = pasivo + patrimonio` verificada por `assert`): 13 conceptos de estados × 6 periodos, 65 indicadores, 6 filas WACC, 78 registros de evidencia.
- **Resultado PoC:** `fase10 ... --empresa empresa_prueba_2025` escribió las 7 tablas + resumen **exclusivamente** en `almacen_empresas\empresa_prueba_2025\salidas\power_bi\` (`dim_indicador` 65, `fact_indicadores` 390, `dim_concepto` 13, `fact_estados` 78, `fact_evidencia` 78, `fact_wacc` 6, `dim_fecha` 6).
- **Inmutabilidad La Previsora:** snapshot MD5 de `salidas\` antes/después → **46/46 archivos idénticos** (0 cambios). Trazabilidad: `%TEMP%\opencode\snap_salidas_antes.txt`.
- **Dashboard multi-entidad:** `salidas\dashboard\app.py` descubre automáticamente los Data Marts (ancla + `almacen_empresas\*\salidas\power_bi\`) y expone **selector dinámico "Entidad"** en el sidebar; al conmutar se recargan tablas, métricas y gráficas Plotly.
- **Clarificación de "72 métricas":** corresponde al conteo de tarjetas `st.metric` de la UI (confirmado: 72 en cada entidad); el catálogo del Data Mart tiene **65 indicadores**.
- **Validación:** `py_compile` OK (constructor, fase10, app.py); AppTest del dashboard **0 excepciones**, opciones `['FIDUCIARIA LA PREVISORA S.A.', 'Empresa Prueba 2025']`, 72 métricas por entidad, 11 pestañas, conmutación dinámica sin errores; health local 200.
- **Pendientes del usuario (resueltos en este evento):** commit + push a `origin/master` y confirmación de `git status` limpio.