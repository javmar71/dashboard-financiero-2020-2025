# Paso 3.1 — Preparación de la extracción IA (reporte)

Versión **v3** (v2: las 4 correcciones solicitadas tras la revisión; v3: validación `nullable`-aware y `pagina` required/sin `nullable`, documentadas en la sección 8). Fecha: 2026-09-17. Alcance de este documento: **solo preparatorio**. No se desarrolló el segmentador aquí (Paso 3.2). No se modificó Fase 2.

> **Nota de vigencia (2026-09-18):** reporte HISTÓRICO de cuando el motor generativo era Gemini
> (`google-genai`/`GEMINI_API_KEY`). Desde esa fecha el motor es **opencode** y el rol de verificación
> y auditoría lo ejerce **big pickle**; `INSTRUCCIONES_EXTRACCION.md` y `GUIA_MOTOR_IA.md` son las
> consignas vigentes. El esquema y sus 12 reglas siguen aplicando sin cambios.

## 1. Comprobaciones de entorno

| Comprobación | Método | Resultado |
|---|---|---|
| `google-genai` importable | `find_spec("google.genai")` en `venv\Scripts\python.exe` | **True** |
| `GEMINI_API_KEY` presente | `os.getenv("GEMINI_API_KEY")` (solo presencia; nunca el valor) | **True** |
| `GOOGLE_API_KEY` presente | `os.getenv("GOOGLE_API_KEY")` | **False** (no se usa) |
| Python autorizado | `venv\Scripts\python.exe` | 3.12.10 |
| Clave impresa/registrada | — | **No** |
| Llamadas a la API | — | **Ninguna** |

## 2. Esquema final propuesto

Archivo: `esquema_extraccion_ia.json` (response_schema compatible con `google-genai`). Deriva de `CONTRATO_DATOS.md`; **solo contiene campos que extrae la IA**. Los metadatos del sistema se agregan después con Python (sección 2.2).

### 2.1 Mapeo contrato → esquema (campos extraídos por IA)

| CONTRATO_DATOS.md | Campo del esquema | Nota |
|---|---|---|
| `variable_canonica` | `variable_madre_id` | Nombre de madre de `taxonomia_variable_madre.csv`. |
| entrada `pdf_original` | `documento_origen` | Obligatorio (nombre exacto). |
| `pagina` | `pagina` | Obligatorio; nunca 1 por defecto. |
| `evidencia.contexto_contable` | `seccion` | Título/sección documental. |
| `cuenta_original` | `cuenta_original` | Texto original. |
| `valor_periodo_actual` | `valor` | Numérico o `null`; jamás inferido. |
| `periodo_actual` | `periodo` | Ej. `"2021"`/`"2020"`; nunca inventado. |
| `unidad` | `unidad` | **Tal como se declara**, sin lista cerrada. |
| `evidencia` | `evidencia` | Obligatoria, nunca vacía. |
| `confianza` | `confianza` | Enum `ALTA/MEDIA/BAJA/NO_DETERMINADA`. |
| `estado` | `estado` | Enum `ACEPTADO/DUDOSO/NO_ENCONTRADO/INCONSISTENTE`. |
| `codigo_puc` | `codigo_puc` | **Sin restricción**; solo si es explícito y con evidencia. |

### 2.2 Metadatos del sistema (NO los genera el modelo; los agrega Python)

| Metadato | Origen | Descripción |
|---|---|---|
| `metodo_extraccion` | Python | Ej. `"gemini"`. Ya no es campo del `response_schema`. |
| `modelo` | Python | Identificador/versión del modelo usado. |
| `version_esquema` | Python | Versión/hash de `esquema_extraccion_ia.json`. |
| `requerimiento_ref` | Python | Amarre indicador → requerimiento → variable_madre (ver 2.3). |

### 2.3 Trazabilidad de requerimiento (corrección 1)

Cadena objetivo: **indicador → requerimiento → variable_madre → fuente_esperada → documento/sección → dato**.

Verificación hecha sobre `taxonomia_variable_madre.csv`:

- **No existe** columna de id de requerimiento/fila (columnas actuales: `variable_madre_id`, `cuenta_puc`, `concepto_src`, `indicador(es)_que_la_usan`, `fuente_esperada`).
- `variable_madre_id` **no es único**: 24 de 85 madres aparecen en más de una fila (`subtotal_calculado` 9, `impuestos` 6, `efectivo_y_equivalentes` 5, `impuestos_diferidos` 5, `arrendamientos` 4, `provisiones` 4, `ori_acumulado` 4, `ingresos_operacionales` 4, etc.). Por eso validar solo por `variable_madre_id` es insuficiente.
- La pareja `(variable_madre_id, concepto_src)` **sí identifica hoy** las 139 filas (0 duplicados), pero `concepto_src` es el concepto fuente, no el requerimiento.
- El único campo que expresa la relación indicador→madre es `indicador(es)_que_la_usan`, pero está **incompleto** (73/139 filas vacías) y en **formato mixto** (32 filas solo con IDs numéricos, 34 con nombres). Hoy no resuelve el requerimiento de forma determinística.
- **No se inventa un id.** Campo de la taxonomía que debe utilizarse para resolver la relación: **`indicador(es)_que_la_usan` (lado indicador) + `variable_madre_id`, con `concepto_src` como desambiguador de fila** cuando es distinto de `pendiente`. La matriz original de relaciones (`MATRIZ_INDICADORES_VARIABLES.xlsx`) ya no existe en el repo, así que un id de requerimiento no es reconstruible sin datos.
- **Recomendación (no ejecutada):** formalizar una columna `requerimiento_id` en la taxonomía en un paso aprobado. Mientras tanto, el amarre lo resuelve **Python** (no el modelo) con los campos existentes.

### 2.4 Decisiones del esquema

- **Una entrada por (variable_madre_id, periodo).** Dos periodos comparativos → dos entradas atómicas.
- **`pagina` y `documento_origen` obligatorios** en cada dato extraído.
- **`estado = NO_ENCONTRADO`** explícito: `valor`/`periodo`/`unidad`/`cuenta_original` pueden ser `null`, la `evidencia` describe la búsqueda; prohibido rellenar con `0`/placeholders o inferir.
- **Sin `metodo_extraccion`** en el schema (corrección 3): es metadato del sistema.
- **`codigo_puc` libre** (corrección 2) y **`unidad` libre** (corrección 4), sin listas cerradas.

## 3. Reglas de validación del esquema

1. Presentes los 12 campos `required` de cada entrada (aunque su valor sea `null` cuando aplique).
2. `documento_origen` string no vacío y perteneciente al inventario documental del año.
3. `pagina` entero ≥ 1 o `null`; nunca valor por defecto.
4. `variable_madre_id` debe existir en `taxonomia_variable_madre.csv`.
5. **Trazabilidad (no solo madre):** verificar el amarre `indicador → requerimiento → variable_madre → fuente_esperada` usando `indicador(es)_que_la_usan` + `variable_madre_id` (+ `concepto_src`); `fuente_esperada` debe coincidir con el tipo de documento de la sección (`notas`/`informe_gestion`/`informe_auditoria`); no se extrae por IA con fuente `estados`. La resolución la aplica Python.
6. `estado` ∈ {`ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`}.
7. `confianza` ∈ {`ALTA`, `MEDIA`, `BAJA`, `NO_DETERMINADA`}; sin score único combinado.
8. Si `estado = ACEPTADO`: `valor` numérico no nulo, `periodo` no nulo, `cuenta_original` no vacío y `evidencia` con documento + página.
9. Si `estado = NO_ENCONTRADO`: `valor`/`periodo`/`unidad`/`cuenta_original` pueden ser `null`; `evidencia` no vacía describiendo la búsqueda; no se completan valores.
10. `unidad`: string libre tal como se declara **o** `null`; **no** hay lista cerrada; nunca inferida por magnitud; la normalización a unidad base la hace Python.
11. `codigo_puc`: string libre **o** `null`; solo se informa si aparece explícitamente y con evidencia; **nunca se infiere**; no se restringe a `{200, 1000, 2000}`; la homologación PUC la hace Python.
12. `evidencia` no vacía en toda entrada y coherente con `documento_origen` + `pagina`.
13. Sin duplicados `(variable_madre_id, documento_origen, pagina, periodo)`; duplicado → `DUDOSO`.
14. Sin patrones `eval(`/`exec(`.
15. Si un dato contradice otro del documento o el balance → `estado = INCONSISTENTE`.
16. Los metadatos del sistema (`metodo_extraccion`, `modelo`, `version_esquema`, `requerimiento_ref`) **no** vienen del modelo: se validan/agregan en Python.

## 4. Inventario documental 2021

Directorio: `AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2021\`. Los 3 PDF tienen **texto nativo en todas las páginas** (sin OCR).

### 4.1 `Estados Financieros_2021.pdf` — 6 páginas (fuente estructurada, la maneja `src/`, NO la IA)

| Página | Contenido |
|---|---|
| 1 | Estado de Situación Financiera |
| 2 | Estado de Resultado Integral |
| 3–4 | Estado de Cambios en el Patrimonio |
| 5–6 | Estado de Flujo de Efectivo |

### 4.2 `Informe de Gestion_2021.pdf` — 109 páginas (texto nativo)

| Página | Sección |
|---|---|
| 2 | NOTAS A LOS ESTADOS FINANCIEROS CONSOLIDADOS / INFORMACIÓN GENERAL |
| 3–14 | Narrativa (mercados, riesgo, margen de solvencia) — **a confirmar** como informe de gestión |
| 15 | BASES DE PRESENTACIÓN |
| 19 | POLÍTICAS CONTABLES SIGNIFICATIVAS |
| 39 | USO DE ESTIMACIONES Y JUICIOS |
| 40 | NORMAS EMITIDAS NO EFECTIVAS / VALOR RAZONABLE |
| 42 | EFECTIVO |
| 45 | INVERSIONES, NETO |
| 47 | CUENTAS COMERCIALES POR COBRAR Y OTRAS, NETO |
| 54 | OPERACIONES CONJUNTAS |
| 61 | IMPUESTO A LAS GANANCIAS |
| 65 | OTROS ACTIVOS NO FINANCIEROS, NETO / PROPIEDADES Y EQUIPO, NETO |
| 67 | ACTIVOS INTANGIBLES, NETO |
| 68 | CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR |
| 70 | ACTIVOS POR DERECHO DE USO |
| 72 | DERECHO DE USO PASIVO / PASIVO POR BENEFICIO A EMPLEADOS |
| 73 | PROVISIONES POR BENEFICIOS A EMPLEADOS – POST EMPLEO |
| 75 | OTROS PASIVOS NO FINANCIEROS, NETO / PROVISIONES |
| 90 | CAPITAL SOCIAL |
| 91 | ORI |
| 92 | PRIMA EN COLOCACIÓN DE ACCIONES / RESERVAS |
| 93 | GANANCIAS O PÉRDIDAS NO REALIZADAS (ORI) / INGRESOS DE OPERACIONES |
| 95 | BENEFICIOS A EMPLEADOS |
| 96 | GASTOS DE ADMINISTRACIÓN |
| 97 | GASTOS DE ACTIVIDADES EN OPERACIONES CONJUNTAS |
| 98 | DETERIORO DE CUENTAS POR COBRAR, NETO / DEPRECIACIÓN / AMORTIZACIÓN |
| 99 | RESULTADO FINANCIERO, NETO |
| 100 | OTROS INGRESOS (EGRESOS), NETO / TRANSACCIONES CON PARTES RELACIONADAS |
| 102 | PATRIMONIO TÉCNICO Y RELACIÓN DE SOLVENCIA |
| 108 | APROBACIÓN DE LOS ESTADOS FINANCIEROS |
| 109 | CERTIFICACIÓN DE LOS ESTADOS FINANCIEROS |
| 44, 61, 64, 76–87, 101, 103–107 | Detalle/tablas intermedias (tasas, vencimientos, calificaciones, exposición) |

### 4.3 `Informe de Audtoria_2021.pdf` — 9 páginas (texto nativo)

| Página | Sección |
|---|---|
| 1 | INFORME DEL REVISOR FISCAL / **Opinión** / **Fundamento de la Opinión** |
| 2 | Párrafos de énfasis e incertidumbre material |
| 3 | INFORME SOBRE OTROS REQUERIMIENTOS LEGALES Y REGLAMENTARIOS + tabla “Tipo de dictamen” |
| 3–9 | Tablas de dictamen por fondo/patrimonio (`Sin salvedad` / `Con salvedad`) |
| 9 | Firma del Revisor Fiscal |

## 5. Hallazgos y observaciones

1. **Nombre de archivo ≠ contenido**: `Informe de Gestion_2021.pdf` contiene las **NOTAS** (p. 2) y no un encabezado literal “INFORME DE GESTIÓN” (la narrativa de gestión p. 3–14 está mezclada). Requiere tu confirmación para mapear `fuente_esperada=informe_gestion`.
2. **Ruido a excluir**: marca de agua `VERIFIED` y firmas repetidas (`ANDRÉS PABÓN SANABRIA`, `CLAUDIA PATRICIA CASTAÑEDA LADINO`, `FERNELY GARZÓN ARDILA`).
3. **Documento de auditoría multientidad**: dictamen de la entidad en p. 1–2; el resto son dictámenes por fondo.
4. **Convención de nombres**: archivo de auditoría llamado `Informe de Audtoria_2021.pdf` (typo).
5. **Trazabilidad incompleta en la taxonomía** (sección 2.3): sin `requerimiento_id`; `indicador(es)_que_la_usan` vacío en 73/139 filas.

## 6. Cambios exactos respecto a la v1

| # | Punto | Cambio aplicado |
|---|---|---|
| 1 | Trazabilidad | El `response_schema` ya no describe la validación como `variable_madre → fuente`; se documenta la cadena `indicador → requerimiento → variable_madre → fuente_esperada → documento/sección → dato`. Se verificó que la taxonomía **no** tiene id de requerimiento; se reporta que el campo para resolverla es `indicador(es)_que_la_usan` + `variable_madre_id` (+ `concepto_src`), resuelto por Python. No se inventó ningún id. |
| 2 | `codigo_puc` | Se eliminó la restricción a `{200, 1000, 2000}`. Ahora es string libre o `null`; solo si es explícito y respaldado con evidencia; nunca inferido; homologación PUC en Python. |
| 3 | `metodo_extraccion` | Se quitó del `response_schema` (pasó de 13 a 12 campos `required`). Se movió a “metadatos del sistema” (Python): `metodo_extraccion`, `modelo`, `version_esquema`. |
| 4 | `unidad` | Se eliminó la lista cerrada (`Miles/Millones/COP/$/Unidad base`). Ahora es string libre tal como se declara, o `null`; sin inferencia por magnitud; normalización a unidad base en Python. |

Se mantienen: una entrada por (variable/requerimiento, periodo), `NO_ENCONTRADO` válido, prohibición de inferir, evidencia obligatoria, documento+página como trazabilidad, y ninguna llamada a Gemini.

## 7. Archivos creados / modificados

| Acción | Archivo |
|---|---|
| Creado (v1) y **actualizado (v2)** | `AUTOMAT ANALISIS FIN\agente_financiero\esquema_extraccion_ia.json` |
| Creado (v1) y **actualizado (v2)** | `AUTOMAT ANALISIS FIN\agente_financiero\PASO3_1_REPORTE.md` |
| Modificado | Ninguno de Fase 2 (intacta) |

Scripts auxiliares temporales (fuera del proyecto): `inventario_2021.py`, `buscar_secciones_2021.py`. No se creó ningún módulo de segmentación.

## 8. Actualización v3 — validación `nullable`-aware

Motivo: al ejecutar el primer piloto real (Paso 3.3, sección 16) se detectó que `jsonschema` draft-07 puro rechazaba `codigo_puc: null` con `None is not of type 'string'`. Es un **falso positivo**: el esquema usa `nullable: true` (extensión de Google), que draft-07 no interpreta.

Decisiones aplicadas en la v3:

1. **La validación oficial del esquema usa una capa `nullable`-aware (extensión de Google), NO `jsonschema` draft-07 puro.** Se extiende `Draft7Validator` para aceptar `null` cuando el sub-esquema declara `nullable: true`, y se valida contra el esquema **original**. Documentado también en `CONTRATO_DATOS.md` §7.
2. **`pagina` pasa a `required` sin `nullable: true`.** Su tipo es entero ≥ 1 siempre; incluso con `estado = NO_ENCONTRADO` informa la página o el rango revisado.
3. **`sanear_schema_para_sdk()`** (módulo permanente `esquema_utils.py`) genera la copia que se pasa a `google-genai` como `response_schema`, quitando `$schema` y `additionalProperties` (no soportados por `types.Schema`). Solo aplica a la llamada; el archivo `esquema_extraccion_ia.json` no se altera.
4. **Regla de desambiguación** (total agregado vs desglose) y **`DUDOSO` ante ambigüedad genuina** incorporadas al prompt de sistema del extracción (ver `PASO3_3_REPORTE.md`).

Resultado de la validación oficial tras la v3: `nullable`-aware = **0 errores** tanto para el primer piloto (corregido manualmente) como para el piloto reforzado.
