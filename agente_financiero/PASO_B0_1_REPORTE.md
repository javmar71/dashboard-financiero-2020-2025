# PASO_B0_1_REPORTE.md — REQUERIMIENTO_ID (CLAVE CANÓNICA)

Fecha: 2026-09-18
Etapa: Bloque 0 (eje transversal) — Paso 1 de 5
Estado: COMPLETADO

## 1. Objetivo

Formalizar el `requerimiento_id` que el contrato dejaba como "amarre de requerimiento"
que Python agrega al persistir (cadena `indicador -> requerimiento -> variable_madre ->
fuente_esperada -> documento/seccion -> dato`). Antes de este paso NO existía un id de
requerimiento/fila ni en taxonomía ni en el lote de extracción (verificado por búsqueda
en el repositorio: cero coincidencias de `requerimiento_id`).

## 2. Definición de la clave canónica

### Formato

| Tipo de fila | `requerimiento_id` |
|--------------|---------------------|
| Variable madre real | `REQ-<VARIABLE_MADRE_ID>` (mayúsculas) |
| Fila etiqueta `subtotal_calculado` | `REQ-SUBTOTAL-<CONCEPTO_SRC>` (mayúsculas) |

### Semántica

- Un `requerimiento_id` identifica **la necesidad de información de una variable madre**,
  no a cada fila de la taxonomía. Por eso una misma madre desagregada en varias filas
  (distintos `concepto_src`) **comparte el mismo `requerimiento_id`** (p. ej.
  `impuestos` → `REQ-IMPUESTOS` en sus 6 filas). Esto es correcto y esperado, no un duplicado.
- Las filas `subtotal_calculado` (9) no son variables madre reales: son etiquetas de
  totales intermedios de balance/resultados/flujos. Se las distingue con el prefijo
  `REQ-SUBTOTAL-` para garantizar unicidad. No aparecen en el lote de extracción
  (verificado: 0 registros del lote con `subtotal_calculado`).
- La columna `indicador(es)_que_la_usan` (ya existente) resuelve el salto
  `indicador -> requerimiento`; `requerimiento_id` + `fuente_esperada` resuelven
  `requerimiento -> variable_madre -> fuente`.

## 3. Cambios aplicados

### 3.1 `taxonomia_variable_madre.csv` (agente_financiero/)

- Nueva columna `requerimiento_id` al final (11.ª columna; se conserva el orden de las
  otras 10).
- 145 filas procesadas, 0 sin `requerimiento_id`.
- 99 `requerimiento_id` únicos = 90 variables madre reales + 9 subtotales.
- Se conserva codificación `utf-8-sig` (BOM).
- Respaldo previo: `Temp\opencode\taxonomia_variable_madre.before_reqid.csv`.

### 3.2 `esquema_extraccion_ia.json` (agente_financiero/)

- Versión de título: **v3 → v4** (2026-09-18).
- Se agrega `requerimiento_id` en `properties` de cada ítem como **campo de sistema
  opcional**:
  - `required` NO se modifica: el modelo no debe generarlo (solo los 12 campos IA).
  - Si el registro persistido lo trae, es aceptado por `additionalProperties: false`.
- Se actualiza la `description` con la nueva semántica.

### 3.3 Lote `Temp\opencode\paso35_lote.json`

- 29 registros enriquecidos con `requerimiento_id` (0 sin resolver), derivado de la
  columna de taxonomía por `variable_madre_id`.

## 4. Verificación

| Comprobación | Resultado |
|--------------|-----------|
| `validador_extraccion.py paso35_lote.json` | `valido=true`, errores esquema=0, errores determinísticos=0, advertencias=2 (mismas de DUDOSO partes_relacionadas, preexistentes) |
| Auditoría lote | Sin cambios: 29 registros, ACEPTADO 19 / DUDOSO 2 / NO_ENCONTRADO 8 / INCONSISTENTE 0; confirmados por diseño 1; revisión humana 9; duplicados 0 |
| Registros lote con `requerimiento_id` | 29/29 |
| Filas taxonomía con `requerimiento_id` | 145/145 |

## 5. Conclusión

El amarre de trazabilidad `indicador -> requerimiento -> variable_madre` queda formalizado
en los tres artefactos (taxonomía, esquema, lote) sin alterar la validación oficial ni el
resultado de la auditoría. La FA principal (`requerimiento_id` en taxonomía y lote) se
considera cerrada.

## 6. Próximo paso (Bloque 0.2)

Resolver `fuente_esperada=informe_gestion` para las 58 filas con `concepto_src=pendiente`
o re-clasificarlas a NO_ENCONTRADO estructural.