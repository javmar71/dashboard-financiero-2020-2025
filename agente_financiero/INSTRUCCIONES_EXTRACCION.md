# INSTRUCCIONES_EXTRACCION.md — Consigna de extracción para opencode

Fecha de vigencia: 2026-09-18. opencode (motor generativo del proyecto) DEBE leer este documento
antes de proponer cualquier extracción de los PDF/segmentos. Aplica el esquema
`esquema_extraccion_ia.json` (12 campos `required`) y el contrato `CONTRATO_DATOS.md`.

## 1. Entrada

- Segmentos determinísticos: `segmentacion_YYYY.json` producido por `segmentador_pdf.py`
  (solo `pymupdf` + stdlib, sin IA). Si no existe, opencode puede leer el PDF con la herramienta
  Read, sección por sección, indicando `documento_origen` + `pagina`.
- Mapeo de secciones del año: `mapeo_variables_secciones_YYYY.json` (variable → sección).
- Taxonomía de madres: `taxonomia_variable_madre.csv` (`variable_madre_id`, `concepto_src`,
  `fuente_esperada`, `tipo_variable`, `formula_calculo`, `requerimiento_id`).

## 2. Reglas de extracción (las 12 del esquema)

1. Cada entrada lleva los **12 campos `required`** (`variable_madre_id`, `documento_origen`,
   `pagina`, `seccion`, `cuenta_original`, `valor`, `periodo`, `unidad`, `evidencia`, `confianza`,
   `estado`, `codigo_puc`), aunque el valor sea `null` cuando aplique.
2. `documento_origen`: string no vacío, perteneciente al inventario documental del año.
3. `pagina`: entero ≥ 1, nunca valor por defecto.
4. `variable_madre_id`: debe existir en `taxonomia_variable_madre.csv`.
5. Trazabilidad: `indicador → requerimiento → variable_madre → fuente_esperada → documento/sección → dato`.
   La `fuente_esperada` debe coincidir con el tipo de documento de la sección; **no** se extrae por IA
   con fuente `estados` (eso lo hace `src/`).
6. `estado` ∈ {`ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`}.
7. `confianza` ∈ {`ALTA`, `MEDIA`, `BAJA`, `NO_DETERMINADA`}; sin score numérico combinado.
8. Si `estado = ACEPTADO`: `valor` numérico no nulo, `periodo` no nulo, `cuenta_original` no vacío,
   `evidencia` con documento + página.
9. Si `estado = NO_ENCONTRADO`: `valor`/`periodo`/`unidad`/`cuenta_original` pueden ser `null`;
   `evidencia` no vacía describiendo la búsqueda; prohibido rellenar con `0`/placeholders o inferir.
10. `unidad`: string libre tal como se declara o `null`; nunca inferida por magnitud (la normalización
    la hace Python).
11. `codigo_puc`: string libre o `null`; solo si aparece explícitamente y con evidencia; nunca inferido.
12. `evidencia` no vacía en toda entrada y coherente con `documento_origen` + `pagina`.

## 3. Reglas reforzadas (Fase 4, reglas 10–14 del system_instruction)

- **Valores de uso:** no usar `0` como placeholder; `ACEPTADO = 0` solo si el texto lo respalda
  (p. ej. negación explícita: "no cuenta con pasivos financieros provenientes de prestamistas").
- **Verificación de captura:** para valores contables, verificar que la cifra capturada corresponda
  a la fila correcta del estado/nota (total vs desglose).
- **Especificidad de evidencias:** citar la parte del segmento que respalda el valor (sección, pág.,
  fragmento), no una referencia genérica.
- **Desambiguación total/desglose:** si la variable corresponde a un desglose específico (p. ej.
  `proveedores` vs agregado de cuentas por pagar), extraer la línea del desglose, no el agregado.
- **`DUDOSO` ante ambigüedad genuina:** si hay varias candidatas para el mismo valor (p. ej.
  `tasas_interes`), no elegir arbitrariamente; marcar `DUDOSO` y describir las candidatas.

## 4. Metadatos del sistema (los agrega Python, NO opencode)

`metodo_extraccion`, `modelo`, `version_esquema`, `requerimiento_ref`. En el nuevo motor,
`metodo_extraccion = "opencode"` y `modelo` = paquete/modelo usado (p. ej. `big-pickle`).

## 5. Prohibiciones

- No inventar ni interpolar valores; no mezclar fuentes; no sustituir la validación contable.
- No tocar `src/` (extracción estructurada) ni los esquemas JSON (salvo instrucción).
- No escribir ni modificar scripts del proyecto; cualquier script temporal solo en
  `%TEMP%\opencode\`.

## 6. Cierre de cada sub-paso

Antes de dar por buena una entrada: opencode propone → big pickle audita (estado/confianza/evidencia/
no-invención) → validación determinística con `validador_extraccion.py` y `auditor_lote_extraccion.py`
→ el usuario aprueba el avance.