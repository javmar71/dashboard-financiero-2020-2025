# PASO_B0_3_REPORTE.md — MAPA CANÓNICO DE DEUDA (duplicados `pasivo_financiero_*` vs `deuda_financiera_*`)

Fecha: 2026-09-18
Etapa: Bloque 0 (eje transversal) — Paso 3 de 5
Estado: COMPLETADO

## 1. Problema

Existían dos familias de filas en la taxonomía que designaban la misma deuda financiera:

| `pasivo_financiero_*` (alias) | `deuda_financiera_*` (canónica) | Equivalencia |
|-------------------------------|--------------------------------|--------------|
| `pasivo_financiero_total` (calculada, sin fórmula) | `deuda_financiera_total` (calculada) | Misma deuda total |
| `pasivo_financiero_corriente` (primaria, PUC `Obligaciones_financieras_corrientes`) | `deuda_financiera_corriente` (primaria, mismo PUC) | Misma cuenta |

Además, la fórmula de `deuda_financiera_total` mezclaba ambas familias:
`pasivo_financiero_corriente + deuda_financiera_no_corriente`.

## 2. Decisión (mapa canónico)

- **Familia canónica:** `deuda_financiera_*` (ya usada en el lote, las notas y las demás fórmulas).
- **`pasivo_financiero_total`** → fila conservada como `calculada` con `formula_calculo=deuda_financiera_total`
  (redirección) y `fuente_esperada=calculado` (no se extrae por separado). Sus indicadores
  (deuda_ebitda, cobertura_intereses, endeudamiento_total, roic, rona) se consolidan en la canónica.
- **`pasivo_financiero_corriente`** → fila conservada como `calculada` con
  `formula_calculo=deuda_financiera_corriente` y `fuente_esperada=calculado`. Se corrige su uso
  anterior: `razon_corriente` la listaba como insumo, pero la razón corriente se calcula con
  `pasivo_corriente` (ya existente en la taxonomía); no con el desglose financiero.
- **`deuda_financiera_total`** → fórmula corregida a
  `deuda_financiera_corriente + deuda_financiera_no_corriente` (familia homogénea).

## 3. Cambios aplicados

### 3.1 `taxonomia_variable_madre.csv`

| variable_madre_id | tipo_variable | fuente_esperada | formula_calculo | regla_diseno |
|-------------------|---------------|-----------------|-----------------|--------------|
| deuda_financiera_total | calculada | calculado | `deuda_financiera_corriente + deuda_financiera_no_corriente` | CANÓNICA de deuda |
| pasivo_financiero_total | calculada | calculado (antes `calculado`) | `deuda_financiera_total` | ALIAS de deuda_financiera_total |
| pasivo_financiero_corriente | calculada (antes `primaria`) | calculado (antes `estados`) | `deuda_financiera_corriente` | ALIAS de deuda_financiera_corriente |

Respaldo previo: `Temp\opencode\taxonomia_variable_madre.before_b03.csv`.
Conteo de fuentes: estados 90 (antes 91), calculado 26 (antes 25), resto sin cambios.

### 3.2 Documentación

- `README_taxonomia.md`: nueva sección "Mapa canónico de deuda" + ejemplo corregido en la
  "Regla de tokens" (`pasivo_financiero_corriente` → `deuda_financiera_no_corriente`).
- `03_INDICADORES.md` (§4 Matriz variable → indicador): las filas `pasivo_financiero_total` y
  `pasivo_financiero_corriente` se reemplazan por las canónicas; se explicita que `razon_corriente`
  usa `pasivo_corriente`.

## 4. Verificación

| Comprobación | Resultado |
|--------------|-----------|
| Validador de fórmulas (regla de tokens, `fase25c_verificar.py`) | conformes 18 / violan 0 / total 18 |
| `validador_extraccion.py paso35_lote.json` | `valido=true`, 0 errores, 2 advertencias (DUDOSO preexistentes) |
| Lote | Sin cambios (30 registros); no referencia `pasivo_financiero_*` |
| Duplicados restantes en la pareja (variable_madre_id, periodo) | 0 |

## 5. Conclusión

Queda eliminada la ambigüedad sintáctica entre `pasivo_financiero_*` y `deuda_financiera_*`. La
taxonomía mantiene una única familia canónica de deuda, con las filas alias redirigiendo por
fórmula, sin romper la validación oficial ni los indicadores existentes.

## 6. Próximo paso (Bloque 0.4)

Cerrar los vacíos metodológicos de `03_INDICADORES.md`: roic/rona (NOPAT, capital_empleado,
activos_netos), flujo_operativo, wacc, grados_de_apalancamiento.