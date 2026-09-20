# ESTADO DEL PROYECTO — INFORME DE TRASPASO PARA OTRA IA

Fecha de este informe: **2026-09-19 14:00 (sábado)**.
Propósito: que un agente/IA distinto entienda **en qué consiste el proyecto**, **qué se ha revisado**, **qué está hecho**, **qué falta** y **con qué reglas debe continuar**, sin tener que reconstruir el contexto desde cero.

> **Actualización (2026-09-19, noche — Publicación en GitHub y DESPLIEGUE COMPLETADO en Streamlit Community Cloud):** el proyecto quedó **público** en `https://github.com/javmar71/dashboard-financiero-2020-2025` (rama `master`, HEAD `c0c5c5a`; la raíz del repo coincide con `AUTOMAT ANALISIS FIN\`). La app **está en producción y activa**: `https://dashboard-financiero-2020-2025.streamlit.app` (Main file path `salidas/dashboard/app.py`), **confirmada funcional por el usuario** (EVENTO 30). Durante el despliegue se detectó y corrigió el `ModuleNotFoundError: matplotlib` del dashboard (el `requirements.txt` publicado no incluía `matplotlib`/`fpdf2`); se sobrescribió con versiones fijas del venv (`streamlit==1.64.0`, `pandas==3.0.5`, `numpy==2.4.6`, `plotly==6.9.0`, `matplotlib==3.11.1`, `fpdf2==2.8.8`, `openpyxl`) y se hizo push (`c0c5c5a`). Pendientes cosméticos: publicar fix de caption de `app.py`, `.streamlit\config.toml`, `ENLACE.txt` y esta documentación en el repo.

> **Actualización (2026-09-19):** Informe actualizado para mantener la vigencia. El estado sigue en la Fase 5 (escalado 2022–2025) según lo registrado el 2026-09-18.

> **Actualización (2026-09-19, tarde — cierre Fases 5/6 del plan):** aprobadas por el usuario y **CERRADAS** dos fases posteriores del plan:
> - **Fase 5 (Screening de Red Flags / Alertas Tempranas):** `agente_financiero\fase5_diagnostico.py` (determinístico, umbrales documentados; `SEÑAL_ALERTA/OBSERVACION/OK/NO_ENCONTRADO/NO_APLICA_TIPO_ENTIDAD`; nunca emite juicios de fraude). Salidas: `salidas\diagnostico_red_flags.{json,csv,md}`.
> - **Fase 6 (Salidas en Excel e informe interactivo HTML):** `agente_financiero\fase6_salidas.py` → `salidas\REPORTE_FINAL_INDICADORES.xlsx` (5 hojas), `salidas\informe_financiero_interactivo.html` (plotly). Además se regeneró `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv` (eliminado el stub `1.0`; ahora 65 filas con nombres y valores reales).
> - Hallazgo central: opinión **con salvedad desde 2023**; calidad de resultados (FCO/UN < 0) y variación CxC (+2,1× en 2025) concentran las señales cuantitativas 2024-2025. Detalle: `salidas\diagnostico_red_flags.md`.

> **Actualización (2026-09-19, noche — EVENTO 27, reorganización del árbol):** toda la carpeta `salidas\` fue **trasladada de la raíz a `AUTOMAT ANALISIS FIN\salidas\`** (decisión explícita del usuario). Se actualizaron las constantes de ruta de las fases 5-10 (`parents[1]`/`..`) y del dashboard y el generador PDF (que conservan `parents[2]` al vivir dentro de `salidas`), el `iniciar_dashboard.bat`, y se regeneraron CSV/XLSX/HTML/matriz/PDF (17 págs). Dashboard verificado con AppTest (0 excepciones, 11 pestañas, 72 métricas) y en ejecución en `http://localhost:8501`. Detalle: `07_HISTORIAL_DE_CAMBIOS.md` → EVENTO 27.

> **Advertencia de vigencia:** el archivo `AUTOMAT ANALISIS FIN\DOCUMENTACION_PROYECTO\00_ESTADO_MAESTRO.md` está **desactualizado** respecto al trabajo real del chat. Allí dice que las Fases 3–12 están "diseñadas pero no implementadas" y que no hay archivos `.py`. En realidad existe un pipeline funcional en `src/`, una taxonomía de Fase 2 implementada y los Pasos 3.1–3.6 ejecutados; la **Fase 3 (2021) está CERRADA**. Este informe es la fuente de verdad más reciente; si hay contradicción, prevalece este informe + los reportes de paso citados.

> **Actualización (2026-09-18, tarde):** la **Fase 4 (extracción IA 2021, extensión)** y la **Fase 4.7 (variables calculadas 2021/2020, IA propone / Python verifica)** quedaron **CERRADAS** en el chat de trabajo. Nota de nomenclatura: en el chat, la extensión de la extracción 2021 (lote 29→37) se denominó "Fase 4" y la capa de cálculo de variables derivadas "Fase 4.7". Detalle en `PASO_F4_REPORTE.md` y `PASO_F4_CALC_REPORTE.md` (sección 6 más abajo).

> **Actualización (2026-09-18, noche) — RESTRUCTURACIÓN DEL MOTOR DE IA:** se retiró Gemini del rol de motor generativo y se adoptó **opencode** (motor) + **big pickle** (modelo/paquete responsable de verificación, auditoría y decisión) + subagentes `explore`/`general`, sin claves API dentro del repositorio. Creados: `AGENTS.md` (raíz), `GUIA_MOTOR_IA.md` e `INSTRUCCIONES_EXTRACCION.md` en `agente_financiero\`. Los reportes históricos (PASO3_1…PASO3_6, PASO_F4, PASO_F4_CALC) se anotaron con nota de vigencia (no se reescriben). Los runners Gemini en `%TEMP%\opencode\` son respaldo histórico y **no se invocan**; `google-genai` queda instalado pero no se importa. **Revisión de fórmulas (R2) CERRADA 2026-09-18:** WACC confirmado contra fuentes académicas (Brealey & Myers, OpenStax, CFA, Damodaran); decisiones aplicadas en `taxonomia_variable_madre.csv` (145→151 filas) y `03_INDICADORES.md`: WACC con **tasa estatutaria** del Art. 240 E.T. (`tasa_estatutaria_impuestos`, parámetro externo; corregido por verificación: 2020: 32 %, 2021: 31 %, 2022+: 35 %) y `flujo_operativo` corregido a **− variacion_CapTrabajo** (re-corrida Fase 4.7 hecha: `flujo_operativo` 2021 = 72.399 y `flujo_libre` 2021 = 76.615; verificada, dif rel 0.0). Pendiente: re-correr `flujo_operativo`/`flujo_libre` (Fase 4.7) con el motor opencode. Detalle: `PASO_REVISION_FORMULAS.md`.

---

## 1. QUÉ ES EL PROYECTO

**Nombre:** `mi_proyecto_finanzas` (carpeta de trabajo `C:\Users\Usuario\Desktop\mi_proyecto_finanzas`).

**Objetivo:** automatizar **análisis financiero y auditoría financiera** de una o varias empresas a partir de **información empresarial multifuente** (estados financieros, notas, informe de gestión, informe de auditoría, actas, Excel, XBRL), conservando trazabilidad total del dato, sin inventar ni interpolar valores.

**Idea central:** un "agente financiero" que lee un conjunto documental desordenado (`1 empresa = conjunto documental`, **no** `1 empresa = 1 PDF`), extrae variables contables **madre** (dato primario), las valida (consistencia `ACTIVO = PASIVO + PATRIMONIO`), calcula indicadores derivados con fórmulas documentadas y produce diagnóstico + evidencia.

**Distinción conceptual irrenunciable:**
- **variable_madre:** dato fuente primario extraíble (ej: `efectivo_y_equivalentes`, `utilidad_neta`, `activo_total`). No requiere fórmula.
- **indicador_derivado:** cálculo que combina variables madre (ej: `ROE`, `EBITDA`, `razon_corriente`).
- **prueba_auditoria_red_flag:** screening con umbrales, no fórmula única (ej: Beneish M-Score, Accruals Ratio). Se reporta como `RED_FLAG / SEÑAL DE ALERTA`, **nunca** como `FRAUDE CONFIRMADO`.

---

## 2. ESTRUCTURA REAL DEL REPOSITORIO

```
mi_proyecto_finanzas\
├── venv\                                  <-- ÚNICO entorno Python válido (3.12.10)
├── .venv\                                 <-- ROTO (apunta a cpython 3.14.7 inexistente). NO usar.
├── ESTADO_PROYECTO_HANDOFF.md             <-- este informe (fuente de verdad más reciente)
├── config.py                              <-- rutas centrales (pathlib)
├── src\
│   ├── lectura_pdfs.py                    <-- extracción PDF (pymupdf). NO modificar.
│   ├── taxonomia.py                       <-- 87 conceptos contables. NO modificar.
│   ├── estados_normalizados.py
│   ├── indicadores.py
│   ├── validaciones.py
│   ├── xbrl_fallback.py                   <-- NO tocar
│   └── generar_notebook.py
├── AUTOMAT ANALISIS FIN\                <-- CARPETA PRINCIPAL (salidas\ vive aquí desde EVENTO 27)
│   ├── salidas\                         <-- MOVIDO aquí desde la raíz (2026-09-19, EVENTO 27)
│   │   ├── datos_estados_financieros.csv      <-- 87 x 9, años 2020-2025
│   │   ├── indicadores.csv                    <-- 65 indicadores
│   │   ├── reporte_validaciones.txt           <-- 65 OK / 0 fallas
│   │   ├── reporte_cobertura.txt              <-- cobertura por año
│   │   ├── diagnostico_red_flags.{json,csv,md}  <-- Fase 5 plan: screening red flags (2026-09-19)
│   │   ├── REPORTE_FINAL_INDICADORES.xlsx    <-- Fase 6 plan: Excel final (5 hojas) (2026-09-19)
│   │   ├── informe_financiero_interactivo.html <-- Fase 6 plan: informe HTML plotly (2026-09-19)
│   │   ├── config_entidad.json               <-- nombre_entidad + nit (agnóstico si vacío)
│   │   ├── dashboard\app.py                  <-- Fase 10 plan: Streamlit/Plotly
│   │   ├── reportes\generar_informe_pdf.py   <-- PDF diagnóstico por familias + riesgos
│   │   └── power_bi\                         <-- Data Mart star schema (dim_* / fact_*)
│   └── agente_financiero\                    <-- entregables de datos + reportes de paso
    │   ├── taxonomia_variable_madre.csv   <-- ENTREGABLE Fase 2 (139 filas, ahora 10 columnas)
    │   ├── README_taxonomia.md            <-- doc Fase 2
    │   ├── esquema_extraccion_ia.json     <-- ENTREGABLE Paso 3.1 (response_schema)
    │   ├── esquema_utils.py               <-- sanitiza schema (skip type lista) para SDK
    │   ├── PASO3_1_REPORTE.md … PASO3_6_REPORTE.md  <-- reportes de paso 3.1–3.6
    │   ├── segmentador_pdf.py             <-- ENTREGABLE Paso 3.2 (solo pymupdf+stdlib)
    │   ├── segmentacion_2021.json         <-- salida segmentador (3 PDF)
    │   ├── mapeo_variables_secciones.py
    │   ├── mapeo_variables_secciones_2021.json  <-- mapeo variable→sección del año
    │   ├── CONTRATO_DATOS.md              <-- contrato entrada/salida
    │   ├── validador_json.py, validador_extraccion.py  <-- validación lote (esquema + determinístico)
    │   ├── auditor_lote_extraccion.py     <-- auditoría oficial del lote (reglas de diseño)
    │   ├── fase5_diagnostico.py           <-- Fase 5 plan: screening red flags (2026-09-19)
    │   ├── fase6_salidas.py               <-- Fase 6 plan: salidas Excel + HTML (2026-09-19)
    │   ├── REPORTE_FINAL_65_INDICADORES.csv  <-- 65 indicadores, valores reales (regenerado 2026-09-19)
    │   ├── detector_requerimiento.py, audit_step3.py, auditor_rapido.py
    │   ├── extraction_2021_estados_financieros.json (+ _tabular.json)
    │   ├── FASE1_FINAL.txt, FASE1_RESUMEN.txt, FASE2_5_REPORTE.md
    │   ├── agente.ipynb, contexto_contable.ipynb, evidencia.ipynb, pruebas.ipynb, puc.ipynb
    │   └── interprete_contexto.py.backup
    ├── DOCUMENTACION_PROYECTO\            <-- memoria persistente (NO reestructurar)
    │   ├── 00_ESTADO_MAESTRO.md   (desactualizado)
    │   ├── 01_ARQUITECTURA.md
    │   ├── 02_VARIABLES_MADRE.md  (112 variables madre, diseño)
    │   ├── 03_INDICADORES.md      (65 indicadores reconciliados; Fases 5/6 cerradas)
    │   ├── 04_FUENTES_DOCUMENTALES.md
    │   ├── 05_SALIDAS_Y_POWER_BI.md
    │   ├── 06_REGLAS_DEL_PROYECTO.md
    │   ├── 07_HISTORIAL_DE_CAMBIOS.md
    │   └── INSTRUCTIVO PARA DILIGENCIAR EL ARCHIVO APEL.docx
    └── Estados Financieros\
        ├── Analisis_Financiero.ipynb
        └── ESTADOS_FINANCIEROS_2021 ... _2025\
            ├── Estados Financieros_2021.pdf   (6 pp)
            ├── Informe de Gestion_2021.pdf    (109 pp; contiene las NOTAS)
            ├── Informe de Audtoria_2021.pdf   (9 pp; typo "Audtoria")
            └── Otros (Superfinanciera) 2021.xbrl
            (análogo para 2022, 2023, 2024, 2025)
```

**Documentos fuente disponibles:** 2–5 años (2021–2025), cada año con 3 PDF + 1 XBRL. Los PDF de 2021 tienen **texto nativo** (no requieren OCR). La carpeta histórica real es `AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_YYYY`.

---

## 3. REGLAS PERMANENTES CLAVE (resumen operativo)

Detalle completo en `DOCUMENTACION_PROYECTO\06_REGLAS_DEL_PROYECTO.md`. Las más relevantes para continuar:

1. **No inventar ni interpolar.** Si no hay evidencia → `NO_ENCONTRADO`. Prohibido usar `0`/placeholder (salvo negación explícita documentada con cita, ver reclasificaciones Fase 3).
2. **Trazabilidad irrenunciable:** `documento → entidad → período → dato → variable_madre → fuente → evidencia → validación → indicador`.
3. **No mezclar fuentes** automáticamente: cada dato conserva su procedencia (estados / notas / gestión / auditoría / actas / Excel / XBRL).
4. **Jerarquía de fuentes:** 1º Estados Financieros, 2º Informe de Gestión, 3º Auditoría, 4º otros oficiales, 5º XBRL **solo como recuperación/verificación** (nunca por comodidad). En la versión actual **no hay búsqueda automática en Internet**; si falta info → **requerimiento al usuario**.
5. **Notebooks: no modificarlos sin autorización explícita.** Los archivos `.py` quedaron **autorizados como entregables permanentes** dentro del proyecto (aclaración operativa 2026-09-19, ver §9.4). Cada paso debe aprobarse antes de avanzar al siguiente.
6. **Verificar antes de modificar**; no duplicar funciones/catálogos; no hardcodear parámetros (ventana 2–5 años, tolerancias).
7. **Ventana histórica:** mínimo 2, máximo 5 años para análisis estándar; conservar todo el inventario.
8. **Consistencia contable obligatoria:** `ACTIVO = PASIVO + PATRIMONIO` (con tolerancia); violación → `INCONSISTENTE`.
9. Estados de validación permitidos: `ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`. Además, en Fase 3 se incorporaron `cualitativo_enum`/`cualitativo_texto_libre` como `tipo_dato` y la noción de "confirmado por diseño" (regla en taxonomía).

**Restricciones de entorno:** usar exclusivamente `C:\Users\Usuario\Desktop\mi_proyecto_finanzas\venv\Scripts\python.exe`; librerías solo en `venv\Lib\site-packages`; no crear otro venv; no instalar en Python global. Los `.py` permanentes están autorizados con registro documental (aclaración 2026-09-19).

---

## 4. ARQUITECTURA (capas)

Convergencia única de todas las fuentes:

```
DOCUMENTO → TIPO_DOCUMENTO → PERÍODO → INFORMACIÓN EXTRAÍDA
→ VARIABLE MADRE / CONTEXTO → EVIDENCIA → VALIDACIÓN → INDICADOR → DIAGNÓSTICO
```

Capas del sistema (`01_ARQUITECTURA.md`):
1. **Entrada documental** — lectura multifuente; extracción híbrida: Python/Docling primario → IA multimodal fallback → normalización/validación Python.
2. **Clasificación y catálogo** — categoría, mapeo a variables madre, fuente primaria/secundaria.
3. **Variables madre** — 112 propuestas (diseño), distinción madre vs derivado.
4. **Indicadores** — fórmulas parametrizadas (32 diseñados).
5. **Diagnóstico** — consistencia, estados de validación, hallazgos.
6. **Salida/Presentación** — Excel/DataFrame → HTML → Power BI (declarativo, futuro; **no es motor de cálculo**).

Prioridad de fuente para variables contables: **Excel estructurado ↓ PDF estructurado ↓ Notas ↓ Gestión ↓ Otros** (las demás fuentes se usan para corroborar/contextualizar/desagregar).

---

## 5. ESTADO POR FASES

| Fase | Título | Estado real |
|---|---|---|
| 0 | Memoria persistente | **Completada** (documentación en `DOCUMENTACION_PROYECTO\`; parcialmente desactualizada) |
| 1 | Extracción/normalización + indicadores | **Completada** — pipeline `src/` funcional, `salidas/` generado |
| 2 | Taxonomía variable madre | **Completada y aprobada** — `taxonomia_variable_madre.csv` |
| 3.1 | Esquema de extracción IA + entorno + inventario | **Completado y aprobado (v2)** |
| 3.2 | Segmentador determinístico PDF | **Completado y aprobado** |
| 3.3 | Piloto IA sobre una sección | **Completado** (runner `paso35_extraccion.py` + respaldos) |
| 3.4 | Auditoría del JSON de extracción | **Completado** (`auditor_lote_extraccion.py`, reglas de diseño) |
| 3.5 | Cobertura del año | **Completado** — validación oficial `valido=true` |
| 3.6 | Fallback XBRL + consolidación | **Completado** — entidad XBRL confirmada, incertidumbre ACEPTADO vía XBRL |
| **3** | **Fase 3 (2021)** | **CERRADA** — lote final validado, revisión humana 9, reportes 3.1–3.6 en `agente_financiero\` |
| **4** | **Extracción IA 2021 (extensión)** | **CERRADA** (2026-09-18) — lote **37** registros, `PASO_F4_REPORTE.md`; auditoría valido=True |
| **4.7** | **Variables calculadas 2021/2020** | **CERRADA** (2026-09-18) — 58 entradas: **38 ACEPTADO / 18 NO_CALCULABLE / 2 PENDIENTE_PARAMETRO_EXTERNO** (Fichas F-04 a F-07); `PASO_F4_CALC_REPORTE.md` |
| **R** | **Restructuración del motor de IA (Gemini → opencode / big pickle)** | **CERRADA** (2026-09-18) — R0/R1 hechos; R2 (revisión de fórmulas) con decisiones aplicadas y re-corrida de `flujo_operativo`/`flujo_libre` ejecutada y verificada |
| **5** | **Arquitectura multifuente y escalado 2022–2025** | **CERRADA** (2026-09-18) — Extracción de variables cualitativas y clave completada para todos los años; validación de lotes exitosa. |
| **5b** | **Screening de Red Flags / Alertas Tempranas (Fase 5 del plan)** | **CERRADA** (2026-09-19) — `fase5_diagnostico.py`; `salidas\diagnostico_red_flags.{json,csv,md}` |
| **6** | **Salidas en Excel e informe interactivo HTML (Fase 6 del plan)** | **CERRADA** (2026-09-19) — `fase6_salidas.py`; `salidas\REPORTE_FINAL_INDICADORES.xlsx` + `informe_financiero_interactivo.html`; `REPORTE_FINAL_65_INDICADORES.csv` regenerado con valores reales |
| **7** | **WACC con Ke = ROI = ROIC (id 34)** | **CERRADA** (2026-09-19) — `fase7_wacc_roi.py`; `salidas\fase7_wacc_roi\wacc_roi_2020_2025.{json,csv}`; CAPM descartado |
| **8** | **Módulo de Evidencia Formal** | **CERRADA y aprobada** (2026-09-19) — `fase8_evidencia_formal.py`; **486 ACEPTADO / 36 NO_ENCONTRADO / 0 DUDOSO** |
| **9** | **Prueba de Validación Transversal** | **CERRADA** (2026-09-19) — `fase9_validacion_transversal.py`; **100 % integridad matemática** (74 ACEPTADO / 0 DESCUDRE / 11 DUDOSO metodológicos / 4 NO_ENCONTRADO esperados) |
| **10** | **Capa de Visualización e Inteligencia Financiera** | **CERRADA Y ENTREGADA 100 %** (2026-09-19) — **RECONFIGURADA: Power BI sustituido por Dashboard Streamlit/Plotly** (`salidas\dashboard\app.py`, gratuito/open source); Data Mart base en `salidas\power_bi\` (fase10_powerbi_data_mart.py); `REPORTE_INTELIGENCIA_FINANCIERA.md` + resumen ejecutivo; **+ Módulo Informe Diagnóstico PDF con agente IA** (`salidas\reportes\generar_informe_pdf.py`, botón de descarga en Pestaña 4) |

**Regla de avance:** Fase 3 se ejecutó **sub-paso por sub-paso**, cada uno con aprobación explícita del usuario. Fase 4 y Fase 4.7 se ejecutaron con el esquema "IA propone / Python verifica" aprobado. **Fase 5 (escalado 2022–2025) iniciada con OK explícito del usuario (2026-09-18). Fases 5b, 6, 7, 8 y 9 del plan aprobadas y cerradas 2026-09-19 (fase5_diagnostico.py, fase6_salidas.py, fase7_wacc_roi.py, fase8_evidencia_formal.py y fase9_validacion_transversal.py, todas determinísticas/semantizadas sobre el consolidado). Con la confirmación de Big Pickle, proceder a las capas finales: Tableros / Power BI / Reportes de Inteligencia Financiera.**

---

## 6. LO QUE YA ESTÁ HECHO (detalle)

### Fase 1 — Pipeline cuantitativo
- `config.py` define `RAIZ_PROYECTO`, `DIR_SRC`, `DIR_SALIDAS`, `DIR_DOCUMENTOS`, `DIR_FUENTES_ESTADOS_FINANCIEROS`.
- `src/lectura_pdfs.py` extrae con `pymupdf` (en `import pymupdf`; `fitz` deprecado); conectado a `config.py`.
- Pipeline (`estados_normalizados.py` → `indicadores.py` → `validaciones.py`) produce:
  - `salidas/datos_estados_financieros.csv` (87 × 9, años 2020–2025).
  - `salidas/indicadores.csv` (65 filas).
  - `salidas/reporte_validaciones.txt` (65 OK / 0 fallas).
  - `salidas/reporte_cobertura.txt` (2021: 27/27, 22/23, 36/37).
- Trazabilidad indicador→concepto en `indicator_concept_map.json`: 58/65 con dependencias; 7 sin uso (IDs 19,20,21,22,36,37,43 → N/A).
- Nota: `src/` extrae **lo estructurado**; la IA **no** lo toca.

### Fase 2 — Taxonomía variable madre (aprobada)
- Entregable: `agente_financiero\taxonomia_variable_madre.csv` (UTF-8 BOM), **139 filas = 87 conceptos de `src/taxonomia.py` + 52 filas "madre-solo"**; **85 madres distintas**.
- Columnas originales: `variable_madre_id`, `cuenta_puc`, `concepto_src`, `indicador(es)_que_la_usan`, `fuente_esperada`.
- En Fase 3 se **extendió** a **10 columnas**: se agregaron `tipo_variable`, `formula_calculo`, `tipo_dato`, `valores_posibles`, `regla_diseno`.
  - `tipo_dato` ∈ {`cuantitativo`, `cualitativo_enum`, `cualitativo_texto_libre`}.
  - Asignaciones: `tipo_opinion`→`cualitativo_enum` (enum `sin_salvedad, con_salvedad, adversa, abstencion`); `riesgos`, `hechos_relevantes`, `incertidumbre`, `salvedades`→`cualitativo_texto_libre`; el resto cuantitativo.
  - `regla_diseno` (ej. salvedades): `condicion:tipo_opinion=sin_salvedad` → si se cumple, `NO_ENCONTRADO` se marca "confirmado por diseño" (fuera de revisión humana; solo alarma si se viola).
- `variable_madre_id=pendiente`: 0. `subtotal_calculado`: 9 (totales que no requieren madre independiente).
- `fuente_esperada` ∈ {`estados`, `notas`, `informe_gestion`, `informe_auditoria`} (no se usó `xbrl`; actas y variables externas quedan fuera del enum autorizado).
- Fusiones aprobadas: `efectivo`→`efectivo_y_equivalentes`; `ventas`→`ingresos_operacionales`; `deuda_total`+`deuda_financiera`→`deuda_financiera_total`; `b_otros_pasivos_no_financieros`→`otros_pasivos`. `capital_social` agrupa `capital_suscrito`+`prima_colocacion`. `proveedores` se mantiene separado de `cuentas_por_pagar` (subconjunto, a propósito).
- Documentado en `README_taxonomia.md` (notas 1–9).

### Paso 3.1 — Esquema de extracción IA (v2 aprobado)
- Entregable: `agente_financiero\esquema_extraccion_ia.json` (`response_schema` compatible con `google-genai`).
- **12 campos `required`** (se quitó `metodo_extraccion` en la v2). Campos: `variable_madre_id`, `documento_origen`, `pagina`, `seccion`, `cuenta_original`, `valor`, `periodo`, `unidad`, `evidencia`, `confianza`, `estado`, `codigo_puc`.
- **En Fase 3 el campo `valor` se flexibilizó a doble tipo** (`"type": ["number", "string"]`, nullable) para soportar cualitativos; `esquema_utils.sanear_schema_para_sdk` omite la clave `type` cuando es lista (el SDK de genai solo acepta un type único).
- `codigo_puc`: string libre o `null`, **sin** restricción `{200,1000,2000}`. `unidad`: string libre o `null`, sin lista cerrada. Normalización a unidad base y homologación PUC las hace **Python**.
- Metadatos **del sistema** (los agrega Python, no el modelo): `metodo_extraccion`, `modelo`, `version_esquema`, `requerimiento_ref`.
- Cadena de trazabilidad objetivo: `indicador → requerimiento → variable_madre → fuente_esperada → documento/sección → dato`.
- Una entrada por `(variable_madre_id, periodo)`. `pagina` y `documento_origen` obligatorios. `estado=NO_ENCONTRADO` válido (con `valor`/`periodo`/`unidad`/`cuenta_original` en `null` y `evidencia` que describe la búsqueda).
- Reporte: `PASO3_1_REPORTE.md` (16 reglas de validación).

### Paso 3.2 — Segmentador determinístico PDF (aprobado)
- Entregable: `agente_financiero\segmentador_pdf.py` (solo `pymupdf` + stdlib; determinístico; `usa_ia: false`; sin imports de red).
- Salida: `agente_financiero\segmentacion_2021.json` (~718 KB, JSON válido). Reporte: `PASO3_2_REPORTE.md`.
- Resultados sobre los 3 PDF de 2021:

  | Documento | Páginas | Segmentos | Filas ruido | Texto retenido |
  |---|---|---|---|---|
  | Estados Financieros_2021.pdf | 6 | 6 | 18 | 76.6 % |
  | Informe de Gestion_2021.pdf | 109 | 76 | 217 | 93.1 % |
  | Informe de Audtoria_2021.pdf | 9 | 7 | 17 | 96.2 % |

- Campos por segmento: `orden_documento`, `documento_origen`, `tipo_segmento`, `nivel`, `titulo_seccion`, `titulo_resumen`, `pagina_inicio`, `pagina_fin`, `texto`, `bloques_por_pagina`, `num_filas`, `encabezado_origen`.
- Tipos de segmento: `titulo_patron`, `seccion_numerada`, `subseccion_numerada`, `titulo_mayusculas`, `titulo_heuristica`, `preambulo`.
- Reglas: fusión de filas por centro con tolerancia ≤ 2.5 px; ruido = texto ≤ 90 car. (dígitos→`#`) repetido en ≥ 50 % de páginas (≥ 4 págs) en banda superior < 13 % o inferior > 85 %; jerarquía de encabezados por prioridad; continuidad para no cortar tablas al cambiar de página.
- CLI: `--dir`, `--out`, `--sin-heuristica`, `--debug`.
- **No** clasifica fuente, **no** asigna `variable_madre_id`/indicadores/PUC/valores.

### Paso 3.3 — Extracción IA por sección (runner + respaldos)
- Entregable operativo (temporal, en `%TEMP%\opencode`): `paso35_extraccion.py` (runner con fallback de modelos) + `paso35_deuda_confirm.py` (corroboración de deuda) + `paso35_merge.py` (lote).
- Flujo: mapeo `mapeo_variables_secciones_2021.json` (variable → sección del año) → una llamada IA por sección (contexto acotado) → raw JSON por llamada → agregación → merge con estructurales → lote.
- **Fallback de modelos:** `MODELS = [gemini-3.6-flash, gemini-3.5-flash]`. `gemini-3.6-flash` free-tier se agotó (429 RESOURCE_EXHAUSTED, límite 20 req/día); los re-run usan `gemini-3.5-flash`. Se registra `MODEL_USADO` e `intentos` en las metas. Cuotas: ~20 req/día/modelo.
- Variables con reglas reforzadas en `system_instruction` (reglas 10–14): valores de uso, verificación de captura, especificidad de evidencias; regla 10 clave para saldos en cero (NIC 7) → ACEPTADO=0 solo si el texto lo respalda.
- **(Referencia de ubicación:** runner y respaldos viven en `C:\Users\Usuario\AppData\Local\Temp\opencode` — temporales del chat; si faltan, se regeneran con los PDF/segmentación.)

### Paso 3.4 — Auditoría del lote (`auditor_lote_extraccion.py`)
- Audita el lote contra taxonomía: objetivos esperados (variable × periodo), cobertura, distribución por estado/confianza, duplicados, valores fuera de enum, **reglas de diseño** (`cargar_reglas_diseno`).
- Si una variable `NO_ENCONTRADO` cumple su `regla_diseno` (ej. `salvedades` con `tipo_opinion=sin_salvedad`) → **confirmado_por_diseno** (fuera de revisión humana); solo se alarma si la condición documentada se viola.
- Reporte JSON y consola con `REQUIEREN REVISIÓN HUMANA`.

### Paso 3.5 — Cobertura del año (2021) — completado
- Lote final: **29 registros** (22 IA + 7 estructurales por diseño). Validación oficial **`valido=true`**, 0 errores de esquema, 0 determinísticos, 2 advertencias (DUDOSO).
- Resultados meta: cobertura **20/23** variables IA, 19/46 objetivos; ACEPTADO 19, DUDOSO 2, NO_ENCONTRADO 8; confirmado por diseño 1 (`salvedades`); **revisión humana 9** (2 DUDOSO partes_relacionadas + 7 estructurales); duplicados 0.
- Reclasificaciones documentadas (regla de negación explícita):
  - `deuda_financiera_corriente` y `no_corriente` → **ACEPTADO = 0** (2021/2020). Evidencia: §2.2.6 (p17-18) *"no cuenta con pasivos financieros provenientes de prestamistas"* + sección 46 (Nota 18 DERECHO DE USO PASIVO, p72) y sección 68 (Nota 34 RESULTADO FINANCIERO NETO, p99-100).
    - `pasivo_financiero_corriente` = 0/sin partida (no hay fila "Obligaciones financieras"; solo `b_derecho_uso_pasivo` no corriente 9.689 → 7.767).
  - `hechos_relevantes` → **ACEPTADO = "sin hechos posteriores relevantes reportados"** (§40 p107: *"no se presentaron eventos significativos que requieran ser revelados"*).
  - `tipo_opinion` → ACEPTADO **`sin_salvedad`** (enum); `salvedades` → NO_ENCONTRADO **confirmado por diseño**.
  - `riesgos` → ACEPTADO texto (VaR Regulatorio 2021 $5.579 / 2,34 %; 2020 $4.017 / 1,56 %; portafolio $242.899 / $225.836).
  - `incertidumbre` → ACEPTADO (ver Paso 3.6, fuente XBRL).
- Detalle en `PASO3_5_REPORTE.md`.

### Paso 3.6 — Fallback XBRL + consolidación — completado
- **Verificación de entidad XBRL 2021:** `Otros (Superfinanciera) 2021.xbrl` **SÍ corresponde a Fiduciaria La Previsora S.A.** (se corrige el diagnóstico inicial del proyecto, que era incorrecto):
  - Identificador único en todos los contextos: **NIT `830053105-3`** (scheme `rut`).
  - Razón social declarada en el XBRL: `DisclosureOfGeneralInformationAboutFinancialStatements` = "Fiduciaria La Previsora S.A. ... Resolución 2521 de 1985".
  - Validado contra fuentes oficiales (Rama Judicial, UNGRD, Gobernación de Arauca).
- **`incertidumbre` reclasificada a ACEPTADO** (valor `"sin incertidumbre material sobre negocio en marcha"`) con evidencia XBRL:
  - `<ifrs:DisclosureOfGoingConcernExplanatory>` = "No aplica" y `<ifrs:DescriptionOfUncertaintiesOfEntitysAbilityToContinueAsGoingConcern>` = "No aplica" (contexto TrimestreAcumuladoActual 2021).
  - No hay tag equivalente para 2020; la opinión limpia del dictamen cubre ambos periodos.
- **`partes_relacionadas` DUDOSO definitivo** (no se resuelve): el XBRL solo trae `CuentasCobrarPartesRelacionadasAsociadasCorrientes = 0` y `CuentasPagarEntidadesRelacionadas = 0` (sin total consolidado de transacciones; los 0 contradicen la nota 36 del EF, p100-102). 2 registros DUDOSO (2021/2020).
- **7 variables narrativas** (`crecimiento_adquisiciones`, `participacion_mercado`, `ventas_por_segmento`, `desempeno_por_segmento`, `eficiencia_operativa`, `numero_empleados`, `perspectivas`): **NO_ENCONTRADO estructural** — el XBRL (estándar estructurado) no aplica para contenido estratégico/cualitativo; no se buscaron allí.
- `composicion_deuda`, `tasas_interes`, `vencimientos` quedaron **sin resultado** (no localizables/NO_ENCONTRADO, falta de estructuras en las notas; forman parte de los 27 objetivos faltantes y las 3 variables sin resultado).
- Detalle en `PASO3_6_REPORTE.md`.

### Fase 4 — Extracción IA 2021 (extensión) — CERRADA (2026-09-18)
- Completaron las variables madre pendientes de 2021 con el esquema `esquema_extraccion_ia.json` v4 (`requerimiento_id` como campo de sistema, agregado por Python).
- 3 llamadas IA (`composicion_deuda`, `tasas_interes`, `vencimientos`) + 3 registros estructurales `no_aplica_tipo_entidad` (`composicion_inventarios`, `cuestiones_key`, `enfasis`).
- Resultado: lote **37 registros** (30 previos + 7 nuevos); estados 23 ACEPTADO / 4 DUDOSO / 10 NO_ENCONTRADO / 0 INCONSISTENTE; 0 duplicados.
  - `composicion_deuda` → ACEPTADO = 0 (2021/2020); `tasas_interes` → DUDOSO (varias candidatas); los 3 estructurales → NO_ENCONTRADO `no_aplica_tipo_entidad`.
  - **`vencimientos` retirada de la taxonomía por decisión del usuario (2026-09-18):** «vencimiento no es una variable». Su fila se eliminó de `taxonomia_variable_madre.csv`, del mapeo (`mapeo_variables_secciones_2021.json`, ahora 22 variables IA) y sus 2 registros ACEPTADO=0 del lote Fase 4 (vuelve a **37**). El perfil de vencimiento de deuda no aplica porque no hay pasivos financieros con prestamistas (corroboración 2.2.6, pág. 33); las «maduraciones» reveladas (pág. 62) son del portafolio de inversiones (`inversiones_detalle`).
- Reporte: `PASO_F4_REPORTE.md`. Lote: `paso35_lote.json` (37). Runner y respaldos en `%TEMP%\opencode`.

### Fase 4.7 — Variables calculadas 2021/2020 — CERRADA (2026-09-18)
- Capa de cálculo de las **30 variables `tipo_variable=calculada`** con esquema **"IA propone / Python verifica"** y `response_schema` `esquema_calculo_ia.json` (v1).
- Fuentes de insumo: `datos_estados_financieros.csv` (`concepto:`), agregados `ACTIVO_CORRIENTE`/`PASIVO_CORRIENTE` de `src/indicadores.py` (`agregado:`), y LOTE Fase 4 (`paso35_lote.json`).
- 1 llamada IA (`gemini-3.5-flash`; 3.6-flash agotado, HTTP 429) para las 60 entradas iniciales (2021 y 2020) → propuestas en `calculadas_ia_raw.json`. Python recalcula, compara (tol. rel. 0,5 %) y aplica cruces de control.
- Resultado (lote `calculadas_2021_2020.json`, **58 entradas**): **34 ACEPTADO / 22 NO_CALCULABLE / 2 PENDIENTE_PARAMETRO_EXTERNO**; 0 INCONSISTENTE; 7 cruces de control sin observaciones. **`compras` retirada por decisión del usuario (2026-09-18):** no es una variable de los EEFF (sin concepto en `src/taxonomia.py` ni en los PDF); sus 2 registros NO_CALCULABLE se eliminaron del lote y su fila, de la taxonomía.
- Decisiones del usuario aplicadas: convención canónica **B0.3 deuda=0** (⇒ `costo_deuda` NO_CALCULABLE por 0/0); `costo_patrimonio` **diferido** (PENDIENTE_PARAMETRO_EXTERNO); `wacc` NO_CALCULABLE; `opinion_*` derivadas determinísticamente de `tipo_opinion` (=`sin_salvedad` 2021).
- **Bug corregido:** desajuste `str`/`int` en claves de `STATES`/`LOTE` (marcaba todo NO_CALCULABLE).
- Reporte: `PASO_F4_CALC_REPORTE.md`. Scripts y respaldos en `%TEMP%\opencode` (`f4calc_insumos.py`, `f4calc_ia.py`, `f4calc_verificar.py`).

### Pipeline operativo del año (scripts temporales en `%TEMP%\opencode`)
- `paso35_extraccion.py` — runner principal (llama secciones mapeadas, respeta respaldo ya guardado, fallback de modelos, agrega raws → `paso35_extraccion_raw.json` + `paso35_resumen.json`). Flags: `PASO35_FORCE`, `PASO35_ORDENES`, `PASO35_MODEL`.
- `paso35_deuda_confirm.py` — runner de corroboración de deuda (secciones 46 y 68 → deuda_financiera_no_corriente/corriente).
- `paso35_merge.py` — arma el lote `paso35_lote.json` = extracción IA + 7 estructurales.
- `validador_extraccion.py` — validación oficial (esquema + determinística, con `tipos_dato`).
- `auditor_lote_extraccion.py` — auditoría oficial del lote (reglas de diseño).
- Raws por llamada: `paso35_call_{4,5,46,68,70,73,74}_raw.json` (+ `_meta.json`). El raw 74 está parcheado a ACEPTADO (hechos_relevantes) y el 5 a ACEPTADO (incertidumbre vía XBRL).

---

## 7. HALLAZGOS Y DECISIONES ABIERTAS

1. **`Informe de Gestion_2021.pdf` contiene las NOTAS** (p. 2: "NOTAS A LOS ESTADOS FINANCIEROS CONSOLIDADOS"), **sin** un encabezado literal "INFORME DE GESTIÓN". El segmentador conserva nombre de archivo y contenido como hechos independientes y **no** lo traduce a `fuente_esperada=informe_gestion`. En Fase 3 se extrajo de ese PDF (por sección) sin necesidad de resolver ese mapeo para el año 2021; **sigue pendiente formalizarlo como `fuente_esperada`.**
2. **No existe `requerimiento_id`** en la taxonomía. `variable_madre_id` **no es único** (24 de 85 madres en >1 fila). La pareja `(variable_madre_id, concepto_src)` identifica las 139 filas. `indicador(es)_que_la_usan` está **incompleto** (73/139 vacías). **Decisión:** no inventar id; amarre resuelto por Python; recomendar `requerimiento_id` en un paso futuro aprobado.
3. **XBRL Superfinanciera:** el diagnóstico inicial que decía que el XBRL no correspondía a la entidad era **incorrecto**; el identificador `830053105-3` sí es Fuprevisora. Los XBRL 2022–2025 **no han sido verificados** aún (pendiente para esa extracción). *(Nota 2026-09-19: confirmado luego por Ficha F-08; 2024 y 2025 descartados por `no_corresponde_a_entidad`.)*
4. **Cuotas IA:** `gemini-3.6-flash` free-tier agotada diariamente (20 req/día); usar `PASO35_MODEL=gemini-3.5-flash` como fallback. Algunas respuestas de 3.5-flash → 503 UNAVAILABLE intermitente (reintentar).
5. **Duplicados solo reportados, NO fusionados:** `pasivo_financiero_total ≈ deuda_financiera_total`; `pasivo_financiero_corriente ≈ deuda_financiera_corriente`; `deuda_financiera_no_corriente` (notas) sin contraparte en estados. **Pendiente de decisión del usuario.**
6. **`i_utilidad_bruta` en `src/taxonomia.py` en realidad es `ingresos_operacionales`** (nombre heredado, no corregido para no alterar el pipeline).
7. **Falsos positivos de la heurística del segmentador:** encabezados de tabla sin cifras detectados como `titulo_heuristica` (ej. `Nombre Consorcio Objeto` p.57–61; `Tipo Técnica de valuación` p.40–41). Mitigable con `--sin-heuristica`.
8. **Erratas del PDF 2021:** `ESTADODE CAMBIOS EN EL PATRIMONIO` (p.3), `PATRIMONO` (p.4), `POR LOS AÑOS TERMINARON` (p.4): la continuidad por título normalizado no une esas variantes.
9. **Informe de auditoría multientidad:** dictamen de la entidad en p.1–2 (opinión limpia, **sin salvedad**); el resto son dictámenes por fondo/patrimonio. La Fase 3 usó solo el dictamen de la entidad.
10. **Excel originales desaparecidos:** `MATRIZ_INDICADORES_VARIABLES.xlsx`, `CATALOGO_INDICADORES.xlsx`, `MATRIZ_...FASE3_VALIDADA.xlsx`, `VARIABLES_MADRE_EXTRAIDAS_FASE6*.xlsx`, `INDICADORES_CALCULADOS_FASE7.xlsx` ya no existen; la trazabilidad se reconstruyó desde `03_INDICADORES.md` y el código.
11. **112 variables madre sin IDs formalizados** en el repo (hallazgo confirmado).
12. **Entorno (2026-09-18, motor opencode):** `pymupdf` 1.28.2 disponible en `venv\Scripts\python.exe` (3.12.10). `google-genai` quedó instalado pero **no se importa**; `GEMINI_API_KEY` y `GOOGLE_API_KEY` quedan **fuera del flujo** (no usar; nunca imprimir). `.venv` roto. Referencia de roles: `agente_financiero\GUIA_MOTOR_IA.md`.
13. **OCR descartado** para 2021: todos los PDF tienen texto nativo.
14. **`vencimientos` retirada de la taxonomía (decisión del usuario, 2026-09-18):** «vencimiento no es una variable». Fila eliminada de `taxonomia_variable_madre.csv` (150 filas), del mapeo (`mapeo_variables_secciones.py` + `_2021.json`, ahora **22 variables IA**) y de `paso35_lote.json` (los 2 registros ACEPTADO=0; lote vuelve a **37**). El perfil de vencimiento de deuda no aplica porque no hay pasivos financieros con prestamistas (corroboración 2.2.6, pág. 33); las «maduraciones» reveladas (pág. 62) corresponden al portafolio de inversiones (`inversiones_detalle`). Reportes históricos (Fases 3–4) conservan sus menciones y no se reescriben.
15. **Regla condicional por tipo de entidad y Capa 4 de Razonamiento IA (2026-09-18):** las cuentas/indicadores **no se eliminan** por ser una empresa de servicios; se **condicionan** por `tipo_entidad` (`servicios_financieros`, fiduciaria). Indicadores que requieren `inventarios`/`costo_ventas`/`compras` → **NO APLICA (condicional)**: `prueba_acida`, `rotacion_inventarios`, `dias_inventario`, `rotacion_proveedores`, `dias_proveedores`, `ciclo_operativo`, `ciclo_conversion_efectivo`, `variacion_inventarios`. `costo_ventas` renombrado a `costo_operacional` (`no_aplica_tipo_entidad`). `compras` retirada (CSV **149 filas**). Decisiones formales registradas en **`agente_financiero\RAZONAMIENTO_DECISIONES.md`** (Fichas F-01 a F-07) bajo el esquema **`esquema_razonamiento_ia.json`**.
16. **Prueba ácida = Razon corriente (2026-09-19):** el usuario confirmó que la coincidencia de los ids 2 y 1 es **correcta** (empresa de servicios sin inventarios → AC/PC = (AC−Inv)/PC). No se recalcula nada; en el screening Fase 5 el id 2 se marca `NO_APLICA_TIPO_ENTIDAD`.
17. **Señal de auditoría (Fase 5, 2026-09-19):** opinión **limpia 2021-2022** y **con salvedad 2023-2025** (lotes revisados/validados). En 2024 la utilidad neta cayó **−70 %**; en 2025 la calidad de resultados (FCO/UN) fue **−0,48** y la variación de CxC **+2,11×** con ingresos +15 %. Hallazgos listos para revisión humana.

---

## 8. QUÉ FALTA (próximos pasos)

**Fase 5 avanzada (2026-09-18) — Escalado a otros años (2022–2025):**
- **Segmentación determinística 2022–2025** — **COMPLETADA** (`segmentacion_2022.json`, `segmentacion_2023.json`, `segmentacion_2024.json`, `segmentacion_2025.json`).
- **Verificación XBRL 2022–2025 (Ficha F-08)** — **COMPLETADA**: 2022 y 2023 corresponden a Fuprevisora (NIT 830053105-3); 2024 (NIT 900251864-8) y 2025 (NIT 901870663-3) pertenecen a otras entidades/fondos y se descartan (`no_corresponde_a_entidad`), siguiendo el precedente del diagnóstico XBRL 2021.
- **Consolidación de extracción cualitativa IA para 2022–2025** — **COMPLETADA** (lotes revisados; 2022 aprobado; 2023-2025 validados).
- **Fase 5 plan (Screening de Red Flags / Alertas Tempranas)** — **CERRADA** (2026-09-19): `agente_financiero\fase5_diagnostico.py` + `salidas\diagnostico_red_flags.{json,csv,md}`.
- **Fase 6 plan (Salidas en Excel e informe interactivo HTML)** — **CERRADA** (2026-09-19): `agente_financiero\fase6_salidas.py` → `salidas\REPORTE_FINAL_INDICADORES.xlsx`, `salidas\informe_financiero_interactivo.html`, y `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv` regenerado con valores reales.
- **Pendiente de revisión humana (Paso C), señalado por el screening:** opiniones con salvedad 2023-2025 (analizar impacto en estados), calidad de resultados FCO/UN < 0 en 2024-2025, y desfase CxC (+2,11×) vs ingresos (+15 %) en 2025.
- ~~Completar `costo_patrimonio` (parámetro externo manual, CAPM) para cerrar `wacc`.~~ -> **RESUELTO (2026-09-19): modificación metodológica WACC/CAPM, Ke = ROI = ROIC (id 34); CAPM y parámetros externos descartados.** Ejecutada la **Fase 7** (`agente_financiero\fase7_wacc_roi.py` → `salidas\fase7_wacc_roi\wacc_roi_2020_2025.{json,csv}`): WACC 2021=0.750317, 2022=0.682552, 2023=0.331181, 2024=0.220066, 2025=0.360281; 2020 NO_CALCULABLE (ROIC requiere t y t−1). Documentado en `03_INDICADORES.md` §2.9/§3/§5/§6 y `07_HISTORIAL_DE_CAMBIOS.md` (Evento 14). Fila `costo_patrimonio` de la taxonomía señalada para revisión (protegida, requiere autorización explícita).
- **Fase 8 — Módulo de Evidencia Formal CERRADA (2026-09-19):** `agente_financiero\fase8_evidencia_formal.py` cruza el consolidado (87 conceptos × 6 años = 522 observaciones) contra la segmentación de los estados financieros; resultado **486 ACEPTADO / 36 NO_ENCONTRADO / 0 DUDOSO**. Salidas: `salidas\fase8_evidencia_formal\evidencia_formal_conceptos.csv` y `resumen_evidencia_formal.json`.
- **Fase 9 — Prueba de Validación Transversal CERRADA (2026-09-19):** `agente_financiero\fase9_validacion_transversal.py` valida sobre la matriz consolidada la ecuación patrimonial, la conciliación de efectivo, la continuidad temporal, la descomposición del efectivo, la consistencia del resultado y la reproducibilidad EBIT/ROIC/WACC. **100 % de integridad matemática/sintáctica** (74 ACEPTADO / 0 DESCUDRE / 11 DUDOSO metodológicos / 4 NO_ENCONTRADO esperados 2020). Salidas: `salidas\fase9_validacion_transversal\matriz_consistencia_transversal.csv` y `resumen_validacion_transversal.json`.
- **Resoluciones metodológicas (decisión Big Pickle 2026-09-19):** tasa 2022 = 35 % confirmada (Ley 2155 de 2021, Art. 240 E.T.), se mantiene en la taxonomía; ROIC/NOPAT (id 34) usa tasa efectiva para el desempeño operativo real con la tasa estatutaria como parámetro de comparación (metadato en `03_INDICADORES.md`); RONA (id 35) ajustada en `src\indicadores.py` al denominador Capital Empleado (deuda_financiera_total + patrimonio_total) conforme al canon §2.4, con `salidas\indicadores.csv` regenerado.
- **Hallazgo formal (Protocolo Pasos B/C):** `i_ori_inmuebles` **2022 = $2.465** en consolidado vs **$11.751** en Nota 25; registrado en `salidas\bitacora_revisiones_humanas.md` para revisión cualitativa humana.

**Fases posteriores (diseñadas, no implementadas):** integración Power BI, Tableros y Reportes de Inteligencia Financiera (capas finales del proyecto). **Módulo de evidencia formal (Fase 8) y pruebas/validación transversal (Fase 9) del consolidado 65 × 6 años ya CERRADAS (2026-09-19).**
- **Capas Finales — Paso 1 INICIADO (2026-09-19):** Data Mart Power BI (Star Schema) generado por `agente_financiero\fase10_powerbi_data_mart.py` en `salidas\power_bi\` (dim_fecha, dim_indicador, dim_concepto, fact_indicadores, fact_estados, fact_wacc, fact_evidencia + data_mart_resumen.json). Librería de medidas DAX (3 carpetas: Efectivo & Liquidez / Rentabilidad & EVA / Estructura & Riesgo) y maquetación de 4 páginas documentadas en `salidas\power_bi\GUIA_IMPLEMENTACION_POWER_BI.md`. Z-Score: NO_APLICA (sin capitalización de mercado ni manufactura, Regla 1). Evento 16 en `07_HISTORIAL_DE_CAMBIOS.md`.
- **Capas Finales — Reporte de Inteligencia Financiera EMITIDO (2026-09-19):** `salidas\REPORTE_INTELIGENCIA_FINANCIERA.md` + `salidas\RESUMEN_EJECUTIVO_INTELIGENCIA_FINANCIERA.md`. Paso 1 aprobado y cerrado por Big Pickle. Evento 17 en `07_HISTORIAL_DE_CAMBIOS.md`. Pendiente: pronunciamiento humano de i_ori_inmuebles 2022 y observaciones cualitativas de la bitácora.
- **FASE 10 (Capa de Visualización e Inteligencia Financiera) CERRADA Y ENTREGADA 100 % — RECONFIGURADA A STREAMLIT/PLOTLY (2026-09-19):** instrucción operativa Big Pickle sustituyó **Power BI (propietario) por un dashboard gratuito/open source Streamlit + Plotly**. Aplicación `salidas\dashboard\app.py` (Streamlit 1.64.0, Plotly 6.9.0) consumiendo directamente el Data Mart de `salidas\power_bi\`; 4 pestañas (Creación de Valor, Efectivo y Liquidez, Estructura y Riesgo, Evidencia y Bitácora); verificada con AppTest (0 excepciones) y por HTTP (health ok). **Servidor activo en `http://localhost:8501`** (comando: `venv\Scripts\python.exe -m streamlit run "salidas\dashboard\app.py" --server.port 8501`). Data Mart, guía DAX y Reporte de Inteligencia Financiera permanecen como insumos. Evento 19 en `07_HISTORIAL_DE_CAMBIOS.md`. **Encargo CONCLUIDO.**
- **Despliegue en Streamlit Community Cloud — EN PRODUCCIÓN (2026-09-19, noche):** repo público `javmar71/dashboard-financiero-2020-2025` (rama `master`, HEAD `c0c5c5a`). **App activa en `https://dashboard-financiero-2020-2025.streamlit.app`** (Main file path `salidas/dashboard/app.py`), **confirmada funcional**. Fix aplicado: `requirements.txt` con `streamlit==1.64.0, pandas==3.0.5, numpy==2.4.6, plotly==6.9.0, matplotlib==3.11.1, fpdf2==2.8.8, openpyxl` (resuelve `ModuleNotFoundError: matplotlib`); push `c0c5c5a`. Pendientes cosméticos en el repo: fix de caption de `app.py`, `.streamlit\config.toml`, `ENLACE.txt` (modo dual público/local) y esta documentación. Detalle: `07_HISTORIAL_DE_CAMBIOS.md` → EVENTO 30.

---

## 9. CÓMO CONTINUAR (guía para la próxima IA)

1. **Leer primero:** este informe → `agente_financiero\GUIA_MOTOR_IA.md` → `agente_financiero\INSTRUCCIONES_EXTRACCION.md` → `PASO3_1_REPORTE.md` … `PASO3_6_REPORTE.md` → `README_taxonomia.md` → `CONTRATO_DATOS.md` → `06_REGLAS_DEL_PROYECTO.md`. Usar `DOCUMENTACION_PROYECTO\00_ESTADO_MAESTRO.md` con cautela (desactualizado).
2. **No avanzar de sub-paso sin aprobación explícita.** El usuario exige confirmación antes de cada paso; **Fase 4 y otros años requieren OK explícito.**
3. **No tocar:** `src/taxonomia.py`, `src/xbrl_fallback.py`, Fase 2 (`taxonomia_variable_madre.csv`) salvo instrucción (está extendida a 10 columnas; no revertir), `esquema_extraccion_ia.json` salvo instrucción, notebooks existentes, y la estructura de `DOCUMENTACION_PROYECTO\`.
4. **Aclaración operativa (2026-09-19, big pickle):** la prohibición de `.py` obedece a la Regla 2 (uso estándar de notebooks `.ipynb` y `.md` para auditoría). Queda **autorizado** crear y ejecutar archivos `.py` estructurados **permanentes** dentro del proyecto, con registro documental. Los artefactos deben ser **persistentes y trazables en el entorno oficial**; no existe regla que exija archivos temporales por seguridad (no dejar resultados solo en `%TEMP%`). Ejemplo en uso: `fase5_diagnostico.py` y `fase6_salidas.py` en `agente_financiero\`.
5. **Ejecutar Python solo con** `venv\Scripts\python.exe`; verificar con `py_compile` antes de dar por bueno un script.
6. **Mantener la trazabilidad** en cada dato y **no inventar** valores ni equivalencias; usar `NO_ENCONTRADO`/`DUDOSO` cuando corresponda. `ACEPTADO=0` o texto requiere **cita textual de negación explícita** en la evidencia.
7. **Registrar toda decisión** en la documentación (`07_HISTORIAL_DE_CAMBIOS.md` o el archivo de especificación pertinente) cuando el usuario lo autorice. Actualizar `ESTADO_PROYECTO_HANDOFF.md` al final de cada fase.
8. Estado esperado al retomar: **Fases 5b, 6, 7, 8 y 9 del plan CERRADAS (2026-09-19)** sobre el consolidado de los 65 indicadores (2020-2025): screening de red flags (`fase5_diagnostico.py`), salidas Excel/HTML (`fase6_salidas.py`), WACC con Ke=ROI (`fase7_wacc_roi.py`), evidencia formal (`fase8_evidencia_formal.py`, 0 DUDOSO) y validación transversal (`fase9_validacion_transversal.py`, 100 % integridad). RONA (id 35) ajustada a Capital Empleado y `salidas\indicadores.csv` regenerado; `salidas\bitacora_revisiones_humanas.md` consolida los puntos atípicos (i_ori_inmuebles 2022, divergencias de tasa). **Capas Finales — CERRADAS Y ENTREGADAS (2026-09-19):** Data Mart Star Schema en `salidas\power_bi\` + librería DAX + maquetación 4 páginas (`GUIA_IMPLEMENTACION_POWER_BI.md`) aprobados; **Reporte de Inteligencia Financiera EMITIDO** (`salidas\REPORTE_INTELIGENCIA_FINANCIERA.md` + resumen); **Fase 10 CERRADA Y ENTREGADA 100 % y RECONFIGURADA** a Dashboard **Streamlit/Plotly** (`salidas\dashboard\app.py`, servidor verificable en `http://localhost:8501`), sustituyendo a Power BI; **+ Módulo Informe Diagnóstico PDF con agente IA** (`salidas\reportes\generar_informe_pdf.py`, PDF de 6 páginas con gráficos, descargable desde Pestaña 4). **Encargo CONCLUIDO; quedan pendientes únicamente pronunciamientos humanos de la bitácora (i_ori_inmuebles 2022, observaciones cualitativas).**

---

## 10. COMANDOS DE REFERENCIA

Segmentador (ya ejecutado, Paso 3.2):
```
venv\Scripts\python.exe "AUTOMAT ANALISIS FIN\agente_financiero\segmentador_pdf.py" --out "AUTOMAT ANALISIS FIN\agente_financiero\segmentacion_2021.json"
```

Runner de extracción por sección (Paso 3.3/3.5, scripts temporales en `%TEMP%\opencode`):
```
& "C:\Users\Usuario\Desktop\mi_proyecto_finanzas\venv\Scripts\python.exe" "$env:TEMP\opencode\paso35_extraccion.py"   # respeta respaldos; re-llama solo PASO35_ORDENES si FORCE=1
$env:PASO35_MODEL="gemini-3.5-flash"
```
> **Nota (2026-09-18):** los comandos y flags `PASO35_*` corresponden al runner histórico Gemini
> (respaldo en `%TEMP%\opencode\`, **no se invocan**). Con el motor opencode la extracción la hace
> opencode siguiendo `INSTRUCCIONES_EXTRACCION.md`; la validación/auditoría determinística con
> `validador_extraccion.py` / `auditor_lote_extraccion.py` se mantiene igual.

Merge → lote (Paso 3.5):
```
venv\Scripts\python.exe "$env:TEMP\opencode\paso35_merge.py"
```

Validación y auditoría oficiales (Paso 3.5/3.6):
```
venv\Scripts\python.exe "AUTOMAT ANALISIS FIN\agente_financiero\validador_extraccion.py" "$env:TEMP\opencode\paso35_lote.json"
venv\Scripts\python.exe "AUTOMAT ANALISIS FIN\agente_financiero\auditor_lote_extraccion.py" "$env:TEMP\opencode\paso35_lote.json" --json "$env:TEMP\opencode\paso35_reporte_auditoria.json"
```

Flags runner: `PASO35_FORCE`, `PASO35_ORDENES`, `PASO35_MODEL`. Procesa por defecto los 3 PDF de `... \ESTADOS_FINANCIEROS_2021\`.