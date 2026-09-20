# Paso 3.3 — Piloto de extracción IA sobre UNA sección (reporte)

Fecha: 2026-09-17. Alcance: **un solo piloto** sobre la sección 16 `CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR` (`Informe de Gestion_2021.pdf`, pp. 68-70), variable objetivo `variable_madre_id = proveedores`, periodos 2021 y 2020. **No** se probó `NO_ENCONTRADO`, **no** se avanzó a 3.4 ni a más secciones.

> **Nota de vigencia (2026-09-18):** reporte HISTÓRICO (motor generativo = Gemini, retirado).
> El motor de extracción vigente es **opencode** siguiendo `INSTRUCCIONES_EXTRACCION.md`, con
> auditoría de **big pickle**; ver `GUIA_MOTOR_IA.md`. Los hallazgos metodológicos (desambiguación
> total/desglose, `DUDOSO` ante ambigüedad) siguen vigentes como reglas reforzadas.

## 1. Configuración de la llamada

| Ítem | Valor |
|---|---|
| Modelo | `gemini-3.6-flash`. **`gemini-2.5-flash` (el configurado en `agente.ipynb`) está retirado**: la API devolvió `404 ... use models/gemini-3.6-flash`. El 404 no generó tokens. |
| Secciones enviadas | 1 (índice 43 de `segmentacion_2021.json`; 6.237 chars). No se envió el PDF completo. |
| `response_schema` | `esquema_extraccion_ia.json` v3, vía `sanear_schema_para_sdk()` (copia sin `$schema`/`additionalProperties`). |
| `response_mime_type` | `application/json` (nunca texto libre). |
| Temperatura | 0.0 |
| Llamadas de generación | 1 por corrida (2 en total: preliminar y reforzada). |

## 2. Primer piloto (preliminar) y hallazgo

Salida cruda (2 entradas, ambas con el **total de la nota**):

```json
{"datos":[
 {"variable_madre_id":"proveedores","documento_origen":"Informe de Gestion_2021.pdf","pagina":68,"seccion":"16. CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR","cuenta_original":"Proveedores y servicios por pagar","valor":13394,"periodo":"2021","unidad":"$","confianza":"ALTA","estado":"ACEPTADO","codigo_puc":null,"evidencia":"... Proveedores y servicios por pagar (2) 13.394 9.380"},
 {"variable_madre_id":"proveedores","documento_origen":"Informe de Gestion_2021.pdf","pagina":68,"seccion":"16. CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR","cuenta_original":"Proveedores y servicios por pagar","valor":9380,"periodo":"2020","unidad":"$","confianza":"ALTA","estado":"ACEPTADO","codigo_puc":null,"evidencia":"... Proveedores y servicios por pagar (2) 13.394 9.380"}]}
```

**Hallazgo de ambigüedad semántica.** La sección contiene dos cifras para "proveedores":

- Total agregado de la nota: `Proveedores y servicios por pagar (2)  13.394  9.380`.
- Desglose de esa nota (p. 68): `Gastos administrativos (a) 8.620 / 7.055` · **`Proveedores (b) 4.742 / 2.272`** · `Gastos administrativos por arrendamientos 32 / 52`, que suma `13.394 / 9.380`.

El modelo eligió el **total** con `confianza=ALTA`, sin marcar `DUDOSO`. La variable `proveedores` corresponde a la **línea específica del desglose** ("Proveedores (b)"), no al agregado (que incluye gastos administrativos y arrendamientos).

## 3. Corrección manual del primer piloto

Por indicación del usuario, **sin reprocesar con IA**, se corrigió el JSON del primer piloto:

- `proveedores` 2021: `13394` → **`4742`**.
- `proveedores` 2020: `9380` → **`2272`**.
- `cuenta_original`: `"Proveedores y servicios por pagar"` → `"Proveedores (b)"`.
- `evidencia`: pasa a citar la línea del desglose y a registrar que el total se descartó por desambiguación.

Razón de la corrección: el nombre de la variable objetivo coincide **más específicamente** con la línea `Proveedores` del desglose que con el total `Proveedores y servicios por pagar`; usar el agregado sesgaría el indicador al incluir gastos administrativos y de arrendamiento. El JSON corregido valida sin errores (sección 5).

## 4. Refuerzo del prompt de sistema

Se añadieron dos reglas (además de las ya existentes de no invención, evidencia obligatoria, `pagina`/`documento_origen` obligatorios y una entrada por `(variable_madre_id, periodo)`):

- **Regla 8 — total agregado vs desglose:** si la sección contiene un total agregado y un desglose con líneas etiquetadas, y el nombre de la variable coincide más específicamente con una línea del desglose, extraer **la línea específica, nunca el agregado**.
- **Regla 9 — ambigüedad genuina:** si persiste ambigüedad entre dos candidatos igualmente plausibles, devolver `estado=DUDOSO` (nunca `confianza=ALTA`) y enumerar los candidatos y sus valores en `evidencia`, sin elegir en silencio.

## 5. Segundo piloto (reforzado) y resultado

Entrada: 6.237 chars; system prompt con las reglas 8 y 9; `response_schema` v3. Salida cruda:

```json
{
  "datos": [
    {"variable_madre_id":"proveedores","documento_origen":"Informe de Gestion_2021.pdf","pagina":68,"seccion":"16. CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR","cuenta_original":"Proveedores (b)","valor":4742,"periodo":"2021","unidad":"$","confianza":"ALTA","estado":"ACEPTADO","codigo_puc":null,"evidencia":"Informe de Gestion_2021.pdf, pagina 68: en la nota (2) El siguiente es el detalle de los proveedores y servicios por pagar, se reporta la linea 'Proveedores (b)' con un valor de $ 4.742 para 2021."},
    {"variable_madre_id":"proveedores","documento_origen":"Informe de Gestion_2021.pdf","pagina":68,"seccion":"16. CUENTAS COMERCIALES POR PAGAR Y OTRAS CUENTAS POR PAGAR","cuenta_original":"Proveedores (b)","valor":2272,"periodo":"2020","unidad":"$","confianza":"ALTA","estado":"ACEPTADO","codigo_puc":null,"evidencia":"Informe de Gestion_2021.pdf, pagina 68: en la nota (2) El siguiente es el detalle de los proveedores y servicios por pagar, se reporta la linea 'Proveedores (b)' con un valor de $ 2.272 para 2020."}
  ]
}
```

- **Distinguió el desglose del total:** devolvió `4.742 / 2.272` (línea `Proveedores (b)`), no `13.394 / 9.380`. Coincide con la corrección manual.
- **No activó `DUDOSO`**: la regla 8 resolvió el caso sin ambigüedad genuina. `estado=ACEPTADO`, `confianza=ALTA`.
- `NO_ENCONTRADO` **no se probó** (fuera del alcance autorizado).

## 6. Validación

| Capa | Primer piloto (corregido) | Piloto reforzado |
|---|---|---|
| `jsonschema` draft-07 puro | `INVALIDO` (falso positivo: `None is not of type 'string'` en `codigo_puc`, por `nullable`) | `INVALIDO` (mismo falso positivo) |
| `nullable`-aware (oficial, esquema v3 original) | **0 errores** | **0 errores** |
| Capa determinística propia (no invención, evidencia no vacía, enums, `pagina`/`documento_origen` no nulos, unicidad `(variable_madre_id, periodo)`, `NO_ENCONTRADO` ⇒ nulls) | **0 errores** | **0 errores** |
| `validador_json.py` (esquema viejo) | `valido=False`, **fallo esperado** | `valido=False`, **fallo esperado** |

`validador_json.py` reclama, en cada entrada, campos que no existen en el esquema 3.1: `valor_original`, `unidad_original`, `valor_normalizado`, `unidad_normalizada`, `nombre_canonico`, `estado_puc` y los 5 `confianza_*`. Es el **desajuste esperado** (valida el esquema de `CONTRATO_DATOS.md`, no el de 3.1). No se modificó ningún validador de fases anteriores.

## 7. Tokens (el SDK no expone costo monetario)

| Corrida | prompt | candidates | thoughts | total |
|---|---|---|---|---|
| Preliminar | 2.466 | 300 | 1.751 | 4.517 |
| Reforzada | 2.691 | 456 | 1.633 | 4.780 |

## 8. Cambios de artefactos

| Acción | Archivo |
|---|---|
| **Actualizado a v3** | `esquema_extraccion_ia.json` (`pagina` required sin `nullable`; nota de validación) |
| **Creado (módulo permanente)** | `esquema_utils.py` → `sanear_schema_para_sdk()` |
| **Creado (validador oficial)** | `validador_extraccion.py` (jsonschema `nullable`-aware + capa determinística; CLI) |
| **Marcado OBSOLETO** | `validador_json.py` (solo comentario de cabecera; retirado del flujo activo) |
| Modificado | `CONTRATO_DATOS.md` (§7 validación `nullable`-aware) |
| Modificado | `PASO3_1_REPORTE.md` (v3 + §8) |
| Creado | `PASO3_3_REPORTE.md` (este documento) |

Scripts temporales (fuera del proyecto, en `…\Temp\opencode`): `paso33_piloto.py`, `paso33_piloto_raw.json` (corregido manualmente), `paso33b_piloto.py`, `paso33b_piloto_raw.json`, `paso33_validar.py`, `paso33_validar_nullable.py`, y sus `*_meta.json`/`paso33b_schema_sdk.json`.

## 9. Validador oficial

- `validador_json.py` queda **OBSOLETO y retirado del flujo activo** (solo se le agregó un comentario de cabecera; no se borró ni se modificó nada más). Valida el esquema antiguo de `CONTRATO_DATOS.md`, no la salida de 3.1.
- Se promovió el script de validación a **`validador_extraccion.py`** (módulo permanente, documentado igual que `esquema_utils.py`): capa jsonschema `nullable`-aware + capa determinística, con CLI (`--variable`, `--periodos`, `--esquema`).
- Regla de `DUDOSO`: la capa determinística **no exige** un `valor` numérico único cuando `estado=DUDOSO` (lo emite como advertencia, no como error), porque una ambigüedad genuina puede no tener un valor elegible; los candidatos deben quedar en `evidencia`.

## 10. Pilotos negativos

### 10.1 Caso `NO_ENCONTRADO` (mismatch deliberado)

- Sección: `Opinión` — `Informe de Audtoria_2021.pdf`, p. 1 (833 chars).
- Variable: `proveedores` (IA-searchable, fuente `notas`) — **no** aparece en esa sección.

Salida cruda:

```json
{"datos":[{"variable_madre_id":"proveedores","documento_origen":"Informe de Audtoria_2021.pdf","pagina":1,"seccion":"Opinión","cuenta_original":null,"valor":null,"periodo":null,"unidad":null,"confianza":"NO_DETERMINADA","estado":"NO_ENCONTRADO","codigo_puc":null,"evidencia":"Se busco el dato relativo a la variable 'proveedores' en la seccion 'Opinión' (pagina 1) del documento 'Informe de Audtoria_2021.pdf', pero solo corresponde al texto de opinion de auditoria sin cifras desglosadas."}]}
```

- **No inventó ni forzó un valor aproximado**: `valor`/`periodo`/`unidad`/`cuenta_original` en `null`, `estado=NO_ENCONTRADO`.
- `pagina=1` presente (regla v3: obligatoria incluso en `NO_ENCONTRADO`), `documento_origen` presente, `evidencia` describe **qué buscó y dónde**.
- Validación oficial: **válido** (0 errores de esquema, 0 determinísticos).

### 10.2 Caso `DUDOSO` (ambigüedad genuina)

- Sección: `36. TRANSACCIONES CON PARTES RELACIONADAS` — `Informe de Gestion_2021.pdf`, pp. 100-102 (2.137 chars).
- Variable: `partes_relacionadas` (IA-searchable, fuente `notas`).
- Ambigüedad **real**: la sección presenta 4 bloques con subtotales (Casa Matriz; Personal Clave de la Gerencia; Junta Directiva; Operaciones Conjuntas), **sin total general** y **sin línea llamada "partes relacionadas"**. Hay candidatos igualmente plausibles para 2021 y 2020.

Salida cruda (resumida):

```json
{"datos":[
 {"variable_madre_id":"partes_relacionadas","pagina":100,"cuenta_original":null,"valor":null,"periodo":"2021","unidad":"$","confianza":"MEDIA","estado":"DUDOSO","codigo_puc":null,"evidencia":"... multiples subtotales por contraparte y concepto para 2021: Casa Matriz (Activo $1.049, Ingresos $16, Gastos $1.936), Personal Clave (Pasivo $1, Gastos $15.310), Junta Directiva (Pasivo $79, Gastos $826) y Operaciones Conjuntas (Activo $144, Pasivo $65, Ingresos $1.848). No existe un total consolidado ... ni una linea especifica ..."},
 {"variable_madre_id":"partes_relacionadas","pagina":100,"cuenta_original":null,"valor":null,"periodo":"2020","unidad":"$","confianza":"MEDIA","estado":"DUDOSO","codigo_puc":null,"evidencia":"... Casa Matriz (Activo $611, Ingresos $12, Gastos $1.711), Personal Clave (Pasivo $2.119, Gastos $15.122), Junta Directiva (Pasivo $52, Gastos $641) y Operaciones Conjuntas (Activo $242, Pasivo $0, Ingresos $1.585) ..."}]}
```

- **No eligió en silencio**: `estado=DUDOSO`, `confianza=MEDIA` (no `ALTA`) y `evidencia` **enumera todos los candidatos** con sus valores y explica que no hay total ni línea específica.
- Entradas atómicas por periodo (2021 y 2020).
- Validación oficial: **válido**; 2 advertencias esperadas (`DUDOSO sin valor único`, candidatos detallados en evidencia).

### 10.3 Tokens (el SDK no expone costo monetario)

| Caso | prompt | candidates | thoughts | total |
|---|---|---|---|---|
| `NO_ENCONTRADO` | 807 | 150 | 402 | 1.359 |
| `DUDOSO` | 1.505 | 633 | 2.044 | 4.182 |

Nota: la primera corrida del caso `DUDOSO` falló con `503 UNAVAILABLE` (alta demanda del servidor, transitorio); se reintentó y completó. No es comportamiento del modelo.

## 11. Conclusión

El esquema v3 **aguantó las pruebas positivas y negativas**: JSON estricto vía `response_schema`, entradas atómicas por periodo, `pagina`/`documento_origen` no nulos, sin invención. El refuerzo de prompt (reglas 8 y 9) resolvió la ambigüedad total-vs-desglose (piloto positivo) y, ante ambigüedad genuina, produce `DUDOSO` con candidatos enumerados en lugar de elegir con `ALTA` (piloto negativo). El camino `NO_ENCONTRADO` devuelve campos en `null` y evidencia de búsqueda, sin inventar. La validación oficial queda en `validador_extraccion.py` (`nullable`-aware + determinística); `validador_json.py` queda obsoleto. Con ambos pilotos negativos conformes, el Paso 3.3 se da por cerrado y se habilita el Paso 3.4 (auditoría del JSON).
