# PASO_B0_4_REPORTE.md — CIERRE DE VACÍOS METODOLÓGICOS DE 03_INDICADORES.md

Fecha: 2026-09-18
Etapa: Bloque 0 (eje transversal) — Paso 4 de 5
Estado: COMPLETADO

## 1. Vacíos cerrados y decisiones definitivas

| Indicador | Decisión (definición canónica Bloque 0.4) | Ref. § 03_INDICADORES |
|-----------|---------------------------------------------|------------------------|
| **roic** | NOPAT = utilidad_operacional × (1 − tasa_efectiva_impuestos); tasa_efectiva_impuestos = (impuesto corriente + impuesto diferido) / resultado antes de impuestos; capital_empleado = deuda_financiera_total + patrimonio_total; roic = NOPAT / capital_empleado_promedio (2 períodos). | §2.4, §1/17 |
| **rona** | NOPAT igual que roic; activos_netos = capital_empleado (deuda_financiera_total + patrimonio_total); rona = NOPAT / activos_netos_promedio (2 períodos). | §2.4, §1/18 |
| **flujo_operativo** | Método indirecto: utilidad_neta + depreciaciones + amortizaciones + variacion_CapTrabajo; variacion_CapTrabajo = (AC[t]−PC[t]) − (AC[t−1]−PC[t−1]). Las variaciones de CXC/Inventarios/CxP **NO se suman por separado** (ya incluidas en el delta del CT corriente). | §2.8, §1/30 |
| **flujo_libre** | flujo_operativo − CAPEX (CAPEX = c_adquisicion_ppye + c_adquisicion_intangibles). | §2.8, §1/31 |
| **wacc** | wacc = costo_deuda × (1 − tasa_efectiva_impuestos) × proporcion_deuda + costo_patrimonio × proporcion_patrimonio. proporcion_deuda = deuda_financiera_total / (deuda_financiera_total + patrimonio); proporcion_patrimonio = patrimonio / (deuda_financiera_total + patrimonio). costo_patrimonio = parámetro externo manual (único dato externo). | §2.9, §1/32 |
| **grados_apalancamiento** | Variaciones porcentuales simples: (valor[t] − valor[t−1]) / |valor[t−1]|; no calculable si denominador 0. GAO = %ΔUtilidad_operacional / %ΔIngresos (sensibilidad del RO); GAF = %ΔUtilidad_neta / %ΔUtilidad_operacional (sensibilidad UN/RO); GAT = GAO × GAF. (Corrección: fórmulas del documento original estaban invertidas.) | §2.6, §1/23–25 |

## 2. Cambios en `03_INDICADORES.md`

- §1 (Lista): filas 17, 18, 30, 31, 32 actualizadas (requiere_externo corregido, fórmula definida).
- §2.4 (Rentabilidad): roic y rona reescritos con definición definitiva; `requiere_externo` corregido de S a N (tasa efectiva es derivada, no externa).
- §2.6 (Apalancamiento): GAO/GAF/GAT redefinidos (fórmulas invertidas corregidas) con método de variaciones porcentuales explícito.
- §2.8 (Flujo de Caja): flujo_operativo y flujo_libre redefinidos; eliminado el doble conteo de CXC/Inv/CxP.
- §2.9 (Estructura de Capital): WACC redefinido con `tasa_efectiva_impuestos` (antes `tasa_impuestos`) y proporciones explícitas.
- §3 (Vacíos): 5 vacíos marcados como RESUELTO (roic, rona, flujo_operativo, wacc, grados); columnas añadidas.
- §5 (Matriz indicador→variables): roic/rona/flujo_* y wacc actualizados.
- §6 (Proximidad): 4 puntos marcados como RESUELTO; únicos insumos externos = `costo_patrimonio` (manual) + PRM (externo, si disponible).

## 3. Cambios en `taxonomia_variable_madre.csv`

| nueva variable_madre_id | tipo | fórmula | insumos |
|--------------------------|------|---------|---------|
| flujo_operativo | calculada | `concepto:i_resultado_del_ejercicio + concepto:i_depreciaciones + concepto:i_amortizaciones + variacion_CapTrabajo` | utilidad_neta, dep, amort, variacion_CapTrabajo |
| flujo_libre | calculada | `flujo_operativo − capex` | flujo_operativo, capex |
| proporcion_deuda | calculada | `deuda_financiera_total / (deuda_financiera_total + concepto:b_patrimonio_total)` | deuda_financiera_total, patrimonio |
| proporcion_patrimonio | calculada | `concepto:b_patrimonio_total / (deuda_financiera_total + concepto:b_patrimonio_total)` | deuda_financiera_total, patrimonio |
| wacc | calculada | `costo_deuda * (1 - tasa_efectiva_impuestos) * proporcion_deuda + costo_patrimonio * proporcion_patrimonio` | costo_deuda, tasa_efectiva, proporcion_deuda, costo_patrimonio, proporcion_patrimonio |

Totales tras B0.4: 150 filas, 96 variable_madre_id únicos.
Conteo por fuente: estados 90 / calculado 31 / notas 11 / informe_gestion 10 / informe_auditoria 5 / parametro_externo_manual 1 / no_aplica_tipo_entidad 2.

Respaldo previo: `Temp\opencode\taxonomia_variable_madre.before_b04.csv`

## 4. Verificación

| Comprobación | Resultado |
|--------------|-----------|
| Validador de tokens (`fase25c_verificar.py`) | **23 conformes / 0 violaciones** |
| Nuevos bare ids referenciados | variacion_CapTrabajo, capex, deuda_financiera_total, costo_patrimonio, costo_deuda, proporcion_deuda, proporcion_patrimonio, tasa_efectiva_impuestos (todas existían) |
| Duplicados (variable_madre_id, periodo) en taxonomía | 0 |
| `validador_extraccion.py` lote 2021 | `valido=true`, 0 errores, 2 advertencias preexistentes |

## 5. Conclusión

Los 5 vacíos metodológicos están cerrados con definiciones canónicas y alineados con la taxonomía. Las fórmulas son computables; el único dato externo requerido para implementar los 32 indicadores es `costo_patrimonio` (parametro_externo_manual). La taxonomía pasó de 145 a 150 filas y mantiene 100% de conformidad de tokens.

## 6. Próximo paso (Bloque 0.5)

Verificar identidad XBRL por año (2020–2025): comprobar que los archivos `.xbrl` de cada año son consistentes con sus correspondientes estados financieros en PDF (claves de cuentas, rangos de valores), para confirmar que el bloque XBRL es válido antes de la Fase 9.
