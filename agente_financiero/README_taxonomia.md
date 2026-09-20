# Tabla única de taxonomía variable madre (Fase 2)

Archivo: `taxonomia_variable_madre.csv` (UTF-8 BOM).

Columnas:

- `variable_madre_id`: variable madre por nombre documentado (NO existen IDs formalizados de las 112 variables madre en el repositorio; hallazgo confirmado, no une pendiente del proyecto).
- `cuenta_puc`: cuenta PUC según `PU_CATALOGO` (21 cuentas) solo cuando el nombre coincide; `(200)`, `(1000)`, `(2000)` traen código, el resto sin código.
- `concepto_src`: concepto de `src/taxonomia.py` (87 en total: `b_*` balance, `i_*` resultados, `c_*` flujos) o `pendiente` si la fila corresponde a una variable madre sin concepto.
- `indicador(es)_que_la_usan`: IDs de `salidas/indicadores.csv` (trazabilidad calculada) o nombres documentados en `03_INDICADORES.md`.
- `fuente_esperada`: una de `estados`, `notas`, `informe_gestion`, `informe_auditoria`, `calculado`, `parametro_externo_manual`, `no_aplica_tipo_entidad` (no se usó `xbrl`). Valores añadidos en Fase 2.5:
  - `calculado`: la fila no se lee en un documento; se deriva internamente (ver `tipo_variable=calculada` y `formula_calculo`).
  - `parametro_externo_manual`: dato externo al proyecto que se suministra a mano (p. ej. costo de deuda/patrimonio); no proviene de los PDF.
  - `no_aplica_tipo_entidad`: la entidad no aplica para esa variable (p. ej. `inventarios`, por tratarse de una entidad sin inventarios operativos).
- `tipo_variable`: una de `primaria` (dato que se lee literalmente en un documento o estado) o `calculada` (se deriva de otras variables). Valor adicional `no_aplica_tipo_entidad` cuando la variable no aplica a la entidad.
- `formula_calculo`: expresión que define la variable cuando `tipo_variable=calculada`; vacía si es primaria, no aplica, o si la convención de cálculo aún está pendiente de decisión.
- `requerimiento_id`: clave canónica del amarre `indicador -> requerimiento -> variable_madre` (formalizada en Bloque 0.1, 2026-09-18). Formato `REQ-<VARIABLE_MADRE_ID>` en mayúsculas; identifica la necesidad de información de la **variable madre**, por lo que una madre desagregada en varias filas comparte el mismo id (no es duplicado). Las filas etiqueta `subtotal_calculado` usan `REQ-SUBTOTAL-<CONCEPTO_SRC>`. Columna añadida al final (11.ª) preservando el orden previo. El modelo de IA (motor generativo: **opencode**; ver `GUIA_MOTOR_IA.md`) no emite este campo: es un campo de sistema que Python agrega al persistir (ver `esquema_extraccion_ia.json` v4).

**Regla de tokens definitiva (Fase 2.5c):**

- `concepto:<clave>` → el valor viene de uno de los 87 conceptos de `src/taxonomia.py` (prefijos `b_`/`i_`/`c_`), p. ej. `concepto:i_resultado_operacional`.
- `agregado:<NOMBRE>` → el valor viene de una agrupación ya definida en `src/indicadores.py` (`ACTIVO_CORRIENTE`, `PASIVO_CORRIENTE`, etc.). No redefinir esas listas: se reutilizan.
- `<variable_madre_id>` a secas (sin prefijo) → referencia a otra fila de esta tabla que **NO tiene `concepto_src` propio** (`concepto_src=pendiente`), sea `primaria` madre-solo (`deuda_financiera_no_corriente`, `numero_empleados`) o `calculada` (`deuda_financiera_total`, `capital_empleado`, `tasa_efectiva_impuestos`, ...).
- Notación temporal: `[t]` = período en análisis, `[t-1]` = período inmediatamente anterior. Un token sin sufijo se asume `[t]`.

### Mapa canónico de deuda (Bloque 0.3, 2026-09-18)

La familia canónica es `deuda_financiera_*`. Las filas `pasivo_financiero_total` y `pasivo_financiero_corriente` son **alias** (duplicados sintácticos resueltos): la primera equivale a `deuda_financiera_total`, la segunda a `deuda_financiera_corriente` (mismo PUC `Obligaciones_financieras_corrientes`). Se conservan como filas `calculada` con `formula_calculo` de redirección y `fuente_esperada=calculado` (no se extraen por separado). La `razon_corriente` usa `pasivo_corriente`, no el desglose financiero.

## Notas

1. `i_utilidad_bruta` en `src/taxonomia.py` corresponde en realidad a `ingresos_operacionales`, no a utilidad bruta — nombre heredado del código original, no corregido en esta fase para no alterar el pipeline funcional.
2. Por la nota anterior, `utilidad_bruta` se mantiene como fila madre-solo separada de `i_utilidad_bruta`.
3. `variable_madre_id` admite dos estados sin asignación real:
   - `pendiente`: la madre aún no está definida (falta decidirla). Hoy no quedan conceptos en este estado (0/87).
   - `subtotal_calculado`: la fila es resultado de una suma/subtotal y NO requiere madre como cuenta contable independiente (9/87: totales de balance parcial, totales del ORI, resultados intermedios y totales de flujo). Desde Fase 2.5, las variables derivadas de indicadores que se decidió modelar (`deuda_neta`, `EBITDA`, etc.) sí se registran como madre con `tipo_variable=calculada`.
4. Madres unificadas (Fase 2, aprobado): `efectivo` y `efectivo_y_equivalentes` → `efectivo_y_equivalentes` (c_efectivo_restriccion, c_efectivo_sin_restriccion, c_efectivo_inicio, c_efectivo_cierre). No queda ninguna fila con `efectivo` a secas.
5. `ventas` e `ingresos_operacionales` se unifican en `ingresos_operacionales`: la fila madre-solo usada por rotación de cartera en `03_INDICADORES.md` ahora apunta a `ingresos_operacionales` (ya no existe `ventas` como madre).
6. `deuda_total` y `deuda_financiera` se unifican en `deuda_financiera_total` con `fuente_esperada=estados`, derivada de `pasivo_financiero_corriente + pasivo_financiero_no_corriente`. El detalle de tasas y composición que el cálculo de WACC (02) necesita y que solo vive en notas se cubre con las madres de `fuente_esperada=notas` ya existentes (`tasas_interes`, `composicion_deuda`); NO es una fuente distinta para el total. (`vencimientos` fue retirada de la taxonomía por decisión del usuario 2026-09-18: no es una variable; con deuda financiera = 0 no aplica perfil de vencimiento de deuda.)
7. `proveedores` es un subconjunto de `cuentas_por_pagar`: se mantienen como madres separadas a propósito (no son duplicados). `capital_social` agrupa `capital_suscrito` + `prima_colocacion` (decisión aprobada, sin cambios).
8. Total de madres distintas: 85 (139 filas = 87 conceptos + 52 madre-solo) antes de Fase 2.5. Tras Fase 2.5 el CSV tiene **145 filas** (se agregaron 6 filas madre-solo que no existían: `tasa_efectiva_impuestos`, `deuda_neta`, `EBITDA`, `costo_deuda`, `costo_patrimonio`, `resultado_antes_impuestos`).
9. Los `.xlsx` originales de matrices (MATRIZ_INDICADORES_VARIABLES.xlsx, CATALOGO_INDICADORES.xlsx) ya no existen en el repositorio; la trazabilidad a indicadores se reconstruyó desde `03_INDICADORES.md` y el código del pipeline.
10. Fase 2.5 (auditoría de tipo de variable): ver `FASE2_5_REPORTE.md` para el detalle y los conteos finales. `variable_madre_id` **no es único** por diseño: una misma madre puede aparecer en varias filas (un `concepto_src` distinto por fila). La unicidad real es la pareja `(variable_madre_id, concepto_src)`.
11. `resultado_antes_impuestos` se agregó como madre `primaria` (`fuente_esperada=estados`) para que la fórmula de `tasa_efectiva_impuestos` referencie solo `variable_madre_id` existentes, sin tokens de concepto.
12. `inventarios` y `variacion_Inventarios` son las filas con `tipo_variable=no_aplica_tipo_entidad` y `fuente_esperada=no_aplica_tipo_entidad` (2 filas).
13. Fase 2.5c: se aplicaron las fórmulas de cálculo con la convención de tokens anterior. `costo_deuda` pasó de `parametro_externo_manual` a `calculado` (ahora tiene fórmula); `costo_patrimonio` sigue siendo `parametro_externo_manual` (sin fórmula).