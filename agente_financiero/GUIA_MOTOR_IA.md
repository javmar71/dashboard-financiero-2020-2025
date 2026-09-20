# GUIA_MOTOR_IA.md — Roles y capas del motor de IA (opencode / big pickle)

Fecha de vigencia: 2026-09-18. Sustituye la referencia previa de un motor generativo con clave API
(Gemini). Este documento define quién genera, quién audita y quién decide en cada fase del pipeline.

## 1. Por qué cambió el motor

El motor generativo anterior (Gemini, `google-genai` + `GEMINI_API_KEY`) usaba cuotas free-tier
(≈ 20 peticiones/día/modelo, agotamientos HTTP 429/503) y exigía una clave dentro de un entorno
Python. A partir de 2026-09-18 el motor es **opencode**, sin claves API dentro del repositorio.

- Los runners Gemini previos (en `%TEMP%\opencode\`) son **respaldo histórico**; no se invocan.
- El paquete `google-genai` permanece instalado en `venv\` pero **no se importa** en el flujo.
- Los reportes de pasos previos (PASO3_1…PASO3_6, PASO_F4, PASO_F4_CALC) conservan su contenido
  histórico con una nota de vigencia; no se reescriben (ver `ESTADO_PROYECTO_HANDOFF.md`).

## 2. Los tres roles

| Rol | Componente | Responsabilidad |
|---|---|---|
| **Generador** | opencode (CLI, herramienta Read, websearch/webfetch) | Leer PDF/segmentos, resumir, extraer valores propuestos, traer fórmulas académicas, proponer cálculos. |
| **Verificador / Auditor / Decisor** | big pickle (paquete/modelo de opencode) + subagentes (`explore`, `general`) | Verificar el resultado de la extracción y del OCR/tools; auditar el código; revisar herramientas; auditar el **razonamiento de aplicabilidad** (evalúa si una cuenta/indicador aplica al contexto de la entidad con evidencia citable); marcar `DUDOSO`/`INCONSISTENTE`; decidir antes de aceptar. |
| **Validador determinístico** | Python (`venv\Scripts\python.exe`: `validador_extraccion.py`, `auditor_lote_extraccion.py`, `f4calc_verificar.py`) | Recalcular, comparar con tolerancia, aplicar cruces de control y reglas de diseño. La IA propone; Python verifica. |

Cadena de decisión: **opencode propone → big pickle audita → Python verifica → el usuario aprueba**.
Ningún dato se da por bueno antes de pasar por big pickle y por la validación determinística.

## 3. Capas donde interviene el motor

1. **Extracción (Fase 3/4):** opencode lee los segmentos del PDF (o el PDF completo) usando la
   consigna `INSTRUCCIONES_EXTRACCION.md` y propone entradas conforme a `esquema_extraccion_ia.json`.
   big pickle revisa cada propuesta (estado, confianza, evidencia, no-invención).
2. **Cálculo de derivadas (Fase 4.7):** opencode propone las 60 entradas usando `esquema_calculo_ia.json`;
   big pickle audita; `f4calc_verificar.py` recalcula y compara (tol. rel. 0,5 %) y aplica cruces.
3. **Verificación OCR/tools:** si algún PDF no tuviera texto nativo, la extracción corre por OCR; big
   pickle revisa el texto OCR contra el PDF para detectar lecturas erróneas antes de extraer.
4. **Razonamiento de aplicabilidad (lógica del requerimiento):** dado el marco general de análisis y el contexto de la entidad (`tipo_entidad`, rama de actividad, estructura ERI/balance y notas), opencode propone la aplicabilidad de cuentas, indicadores y fórmulas mediante **fichas de razonamiento** con evidencia citable; big pickle audita la justificación y validez; Python materializa las reglas (JSON + `NA_MOTIVOS`).
5. **Indicadores y derivadas (Fase 4.7 y 7):** opencode completa fórmulas y reglas condicionales aplicando el mismo esquema (propone → audita → verifica → aprueba).

## 4. Sin claves API

- No existe `GEMINI_API_KEY` en el flujo ni en archivos del repositorio.
- opencode y sus herramientas (Read, websearch, webfetch, subagentes) funcionan sin clave del
  proyecto; si hiciera falta una configuración local, vive fuera del repo y no se documenta aquí.
- Nunca registrar ni imprimir valores de claves en código, logs ni documentación.

## 5. Marco de reglas para el motor

- Aplican las reglas de `AGENTS.md` (raíz) y `06_REGLAS_DEL_PROYECTO.md`: no inventar, no interpolar,
  no mezclar fuentes, estados `ACEPTADO/DUDOSO/NO_ENCONTRADO/INCONSISTENTE`, consistencia
  `ACTIVO = PASIVO + PATRIMONIO`, jerarquía de fuentes y trazabilidad completa.
- El motor no sustituye validación contable: cualquier valor nuevo exige `evidencia` con
  documento + página y revisión por big pickle antes de aceptarlo.

## 6. Entregables de esta reestructuración

| Archivo | Contenido |
|---|---|
| `AGENTS.md` (raíz) | Instrucciones persistentes para opencode. |
| `INSTRUCCIONES_EXTRACCION.md` | Consigna de las reglas de extracción que opencode lee. |
| `PASO_REVISION_FORMULAS.md` | Bitácora de la revisión de fórmulas contra fuentes académicas. |
| `esquema_razonamiento_ia.json` | Esquema formal de las fichas de razonamiento de aplicabilidad IA. |
| `RAZONAMIENTO_DECISIONES.md` | Bitácora de decisiones de aplicabilidad y fichas de razonamiento (F-01 a F-07+). |

Histórico de retiro: ver nota de vigencia en `CONTRATO_DATOS.md`, `PASO3_1_REPORTE.md`,
`PASO3_3_REPORTE.md`, `PASO3_5_REPORTE.md`, `PASO_F4_REPORTE.md`, `PASO_F4_CALC_REPORTE.md` y
`ESTADO_PROYECTO_HANDOFF.md`.