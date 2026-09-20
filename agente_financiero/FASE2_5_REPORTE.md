# Fase 2.5 — Auditoría de tipo de variable (reporte)

Fecha: 2026-09-17. Alcance: exclusivamente la auditoría de tipo de variable (primaria vs calculada) sobre `taxonomia_variable_madre.csv`. **No se inició el Paso 3.3.**

> **Estado final: las secciones 1–8 documentan la primera ronda (histórico). Las decisiones del usuario y el estado definitivo del CSV están en la sección 10.**

## 1. Cambios aplicados

| # | Cambio |
|---|---|
| 1 | Se agregó la columna `tipo_variable` (`primaria` / `calculada`) y la columna `formula_calculo`. |
| 2 | Se marcaron como `calculada` con fórmula: `NOPAT`, `tasa_efectiva_impuestos`, `deuda_neta`, `EBITDA`. |
| 3 | Se marcaron como `calculada`, con `formula_calculo` vacía y `fuente_esperada=pendiente_decision_usuario`: `capital_empleado`, `activos_netos`, `costo_deuda`, `costo_patrimonio`. |
| 4 | Toda fila `calculada` con fórmula pasó a `fuente_esperada=calculado` (nuevo valor de enum, no documental). |
| 5 | Se revisaron las 52 filas madre-solo; el resultado se reporta en la sección 4. **No se corrigió ninguna fila adicional.** |

**Filas:** 139 → **144**. Se agregaron 5 filas que **no existían** y que tus instrucciones citaban: `tasa_efectiva_impuestos`, `deuda_neta`, `EBITDA`, `costo_deuda`, `costo_patrimonio` (todas como madre-solo, `cuenta_puc=pendiente`, `concepto_src=pendiente`).
Respaldo del CSV original (139 filas): `C:\Users\Usuario\AppData\Local\Temp\opencode\taxonomia_variable_madre.csv.bak`.

**Columnas finales:** `variable_madre_id, cuenta_puc, concepto_src, indicador(es)_que_la_usan, fuente_esperada, tipo_variable, formula_calculo`.

## 2. Conteos resultantes

| `tipo_variable` | Filas |
|---|---|
| primaria | 136 |
| calculada | 8 |

| `fuente_esperada` | Filas |
|---|---|
| estados | 100 |
| notas | 12 |
| informe_gestion | 16 |
| informe_auditoria | 8 |
| calculado | 4 |
| pendiente_decision_usuario | 4 |

## 3. Las 8 calculadas

| variable_madre_id | tipo_variable | fuente_esperada | formula_calculo |
|---|---|---|---|
| NOPAT | calculada | calculado | `resultado_operacional * (1 - tasa_efectiva_impuestos)` |
| tasa_efectiva_impuestos | calculada | calculado | `(gasto_impuesto_corriente + gasto_impuesto_diferido) / resultado_antes_impuestos` |
| deuda_neta | calculada | calculado | `deuda_financiera_total - efectivo_y_equivalentes` |
| EBITDA | calculada | calculado | `resultado_operacional + depreciaciones + amortizaciones` |
| capital_empleado | calculada | pendiente_decision_usuario | *(vacía — espera decisión)* |
| activos_netos | calculada | pendiente_decision_usuario | *(vacía — espera decisión)* |
| costo_deuda | calculada | pendiente_decision_usuario | *(vacía — espera decisión)* |
| costo_patrimonio | calculada | pendiente_decision_usuario | *(vacía — espera decisión)* |

**Interpretación aplicada (confírmala):** en el punto 4 pediste que *toda* fila `calculada` pase a `fuente_esperada=calculado`, pero en el punto 3 pediste para estas 4 dejarla en `pendiente_decision_usuario`. Se aplicó el punto 3 como excepción sobre el punto 4.

## 4. Auditoría de las 52 filas madre-solo (punto 5)

De las 52, 3 ya fueron tratadas (NOPAT, capital_empleado, activos_netos). En las **49 restantes** encontré filas que, con el criterio "¿aparece literalmente en un documento o es un cálculo?", **también deberían ser `calculada`**. **No las corregí.**

### 4.1 Claras — no se imprimen literalmente; son cálculo (8)

| variable_madre_id | Motivo | Fórmula probable (a validar) |
|---|---|---|
| `deuda_financiera_total` | `README_taxonomia.md` nota 6 ya la declara derivada. Hoy está `primaria`/`estados`. | `pasivo_financiero_corriente + pasivo_financiero_no_corriente` |
| `variacion_CapTrabajo` | Variación entre dos períodos; no es un saldo impreso. | Δ(activo_corriente − pasivo_corriente) |
| `variacion_CXC` | Variación entre períodos. | Δ(cuentas_por_cobrar) |
| `variacion_Inventarios` | Variación entre períodos. | Δ(inventarios) |
| `variacion_CxP` | Variación entre períodos. | Δ(cuentas_por_pagar) |
| `opinion_limpia` | Booleano derivado de `tipo_opinion`. | clasificación de `tipo_opinion` |
| `opinion_adversa` | Booleano derivado de `tipo_opinion`. | clasificación de `tipo_opinion` |
| `abstencion` | Booleano derivado de `tipo_opinion`. | clasificación de `tipo_opinion` |

**Impacto si se aprueban:** `opinion_limpia`, `opinion_adversa` y `abstencion` son hoy `informe_auditoria`; al pasar a `calculado`, los objetivos de búsqueda de la IA bajan de **36 a 33** filas.

### 4.2 Probables — dependen de convención o de si el documento lo imprime literalmente (9)

| variable_madre_id | Motivo |
|---|---|
| `utilidad_bruta` | Normalmente `ingresos_operacionales − costo_ventas`; puede o no venir impresa. |
| `pasivo_financiero_total` | Usualmente suma de corriente + no corriente; además duplica `deuda_financiera_total` (ver hallazgo Fase 2). |
| `compras` | Suele derivarse (`costo_ventas + Δinventarios`) o venir declarada en nota. |
| `capex` | Puede ser suma de adquisiciones (`c_adquisicion_ppye` + intangibles) o dato de nota/gestión. |
| `evolucion_ingresos` | Puede ser variación % (cálculo) o narrativa textual (primaria). |
| `evolucion_utilidad` | Igual que la anterior. |
| `crecimiento_organico` | Puede ser variación % o narrativa. |
| `productividad` | Puede ser ratio/índice (cálculo) o afirmación textual. |
| `calidad_resultados` | Evaluación derivada de otros datos. |

### 4.3 Sin observaciones
Las demás 32 filas madre-solo (notas operativas, segmentos, riesgos, etc.) sí corresponden a datos que se leen literalmente en documento → `primaria`.

## 5. Objetivos de búsqueda de la IA (estado actual)

Con los cambios aplicados, las filas `primaria` con `fuente_esperada ∈ {notas, informe_gestion, informe_auditoria}` son **36**:

- **Notas (12):** compras, proveedores, composicion_deuda, deuda_financiera_corriente, deuda_financiera_no_corriente, tasas_interes, vencimientos, composicion_inventarios, inversiones_detalle, adquisiciones_activos, contingencias, partes_relacionadas.
- **Gestión (16):** evolucion_ingresos, evolucion_utilidad, crecimiento_organico, crecimiento_adquisiciones, participacion_mercado, ventas_por_segmento, desempeno_por_segmento, eficiencia_operativa, productividad, numero_empleados, capex, perspectivas, riesgos, hechos_relevantes, calidad_resultados, cumplimiento_covenants.
- **Auditoría (8):** tipo_opinion, opinion_limpia, salvedades, opinion_adversa, abstencion, enfasis, cuestiones_key, incertidumbre.

## 6. Problemas detectados en las fórmulas (requieren tu decisión)

Las fórmulas se guardaron **tal como las escribiste**, pero varios tokens **no son `variable_madre_id` existentes**. No los "arreglé" para no inventar el mapeo:

| Token en tu fórmula | ¿Existe como `variable_madre_id`? | Candidato real en el CSV |
|---|---|---|
| `resultado_operacional` | No | `utilidad_operacional` (concepto `i_resultado_operacional`) |
| `resultado_antes_impuestos` | No | concepto `i_resultado_antes_impuestos` (hoy fila `subtotal_calculado`) |
| `gasto_impuesto_corriente` | No | concepto `i_gasto_impuesto_corriente` / `c_gasto_impuesto_corriente` (madre `impuestos`) |
| `gasto_impuesto_diferido` | No | concepto `i_gasto_impuesto_diferido` / `c_gasto_impuesto_diferido` (madre `impuestos_diferidos`) |
| `tasa_efectiva_impuestos` | Sí, recién agregada | — |
| `deuda_financiera_total` | Sí | — |
| `efectivo_y_equivalentes` | Sí | — |
| `depreciaciones`, `amortizaciones` | Sí | — |

**Consecuencia:** la fórmula de `tasa_efectiva_impuestos` referencia conceptos, no madres; y las de `NOPAT`/`EBITDA` usan `resultado_operacional` en vez de `utilidad_operacional`.

## 7. Pendiente de tu decisión

1. **`capital_empleado`** — convención (capital empleado = activo − pasivo corriente no financiero, u otra).
2. **`activos_netos`** — definición de "activos netos".
3. **`costo_deuda`** — ¿pre o post impuesto?; además, ¿es `primaria` (tasa de mercado externa) o `calculada`?
4. **`costo_patrimonio`** — CAPM con datos externos no documentales.
5. **Fórmulas de la sección 6** — confirmar/normalizar tokens a `variable_madre_id`.
6. **Reclasificaciones de la sección 4** — 8 claras + 9 probables.

## 8. Archivos creados / modificados

| Acción | Archivo |
|---|---|
| Modificado | `AUTOMAT ANALISIS FIN\agente_financiero\taxonomia_variable_madre.csv` (139 → 144 filas; +2 columnas) |
| Creado | `AUTOMAT ANALISIS FIN\agente_financiero\FASE2_5_REPORTE.md` |
| Respaldo (fuera del proyecto) | `...\Temp\opencode\taxonomia_variable_madre.csv.bak` |
| Sin tocar | `src/taxonomia.py`, `xbrl_fallback.py`, `esquema_extraccion_ia.json`, notebooks, `README_taxonomia.md` (su actualización queda pendiente de tu decisión) |

## 9. Estado

Fase 2.5 ejecutada. **Detenido a la espera de tu decisión** sobre los puntos de la sección 7. No se inició el Paso 3.3.

---

## 10. Segunda ronda — decisiones aplicadas (estado definitivo)

Aplicadas el 2026-09-17 tras las decisiones del usuario. CSV: **144 → 145 filas**. Respaldo previo: `C:\Users\Usuario\AppData\Local\Temp\opencode\taxonomia_variable_madre_v2.csv.bak`.

### 10.1 Cambios aplicados

| # | Decisión | Aplicación |
|---|---|---|
| 1 | Normalización de fórmulas | Se sustituyó `resultado_operacional` → `utilidad_operacional`; `gasto_impuesto_corriente + gasto_impuesto_diferido` → `impuestos + impuestos_diferidos`; `resultado_antes_impuestos` → nueva madre (ver #5). Verificado: **ninguna fórmula contiene ya tokens que no sean `variable_madre_id`**. |
| 2 | 4 pendientes (sec. 7) | `capital_empleado`, `activos_netos` → `calculada` + `fuente_esperada=calculado` (fórmula aún pendiente). `costo_deuda`, `costo_patrimonio` → `calculada` + `fuente_esperada=parametro_externo_manual`. |
| 3 | 8 claras (sec. 4.1) | `deuda_financiera_total`, `variacion_CapTrabajo`, `variacion_CXC`, `variacion_Inventarios`, `variacion_CxP`, `opinion_limpia`, `opinion_adversa`, `abstencion` → `calculada` + `fuente_esperada=calculado`. |
| 4 | 9 probables (sec. 4.2) | `utilidad_bruta`, `pasivo_financiero_total`, `compras`, `capex`, `evolucion_ingresos`, `evolucion_utilidad`, `crecimiento_organico`, `productividad`, `calidad_resultados` → `calculada` + `fuente_esperada=calculado`. |
| 5 | Token `resultado_antes_impuestos` | Se agregó como fila madre-solo `primaria`, `fuente_esperada=estados`, `cuenta_puc=pendiente`, `concepto_src=pendiente`. |
| 6 | `inventarios` | `tipo_variable=no_aplica_tipo_entidad`, `fuente_esperada=no_aplica_tipo_entidad` (única fila). |
| 7 | Nuevos valores de enum | `no_aplica_tipo_entidad` y `parametro_externo_manual` documentados en `README_taxonomia.md` (nota de columna `fuente_esperada`). |

### 10.2 Fórmulas normalizadas (las 4 con expresión)

| variable_madre_id | formula_calculo |
|---|---|
| `NOPAT` | `utilidad_operacional * (1 - tasa_efectiva_impuestos)` |
| `tasa_efectiva_impuestos` | `(impuestos + impuestos_diferidos) / resultado_antes_impuestos` |
| `deuda_neta` | `deuda_financiera_total - efectivo_y_equivalentes` |
| `EBITDA` | `utilidad_operacional + depreciaciones + amortizaciones` |

Las restantes 23 filas `calculada` tienen `formula_calculo` **vacía** (convención pendiente): `capital_empleado`, `activos_netos`, las 8 claras, las 9 probables y `costo_deuda`/`costo_patrimonio`. No se inventó ninguna.

### 10.3 Conteos finales

| `tipo_variable` | Filas |
|---|---|
| primaria | 117 |
| calculada | 27 |
| no_aplica_tipo_entidad | 1 |
| **Total** | **145** |

| `fuente_esperada` | Filas |
|---|---|
| estados | 91 |
| calculado | 25 |
| notas | 11 |
| informe_gestion | 10 |
| informe_auditoria | 5 |
| parametro_externo_manual | 2 |
| no_aplica_tipo_entidad | 1 |

**Objetivos de búsqueda de la IA (primaria + notas/gestion/auditoria): 36 → 26.** La reducción es consecuencia directa de reclasificar a `calculada` `compras`, `capex` (×3), `evolucion_ingresos`, `evolucion_utilidad`, `crecimiento_organico`, `productividad`, `calidad_resultados`, `opinion_limpia`, `opinion_adversa` y `abstencion`.
- Notas (11): proveedores, composicion_deuda, deuda_financiera_corriente, deuda_financiera_no_corriente, tasas_interes, vencimientos, composicion_inventarios, inversiones_detalle, adquisiciones_activos, contingencias, partes_relacionadas.
- Gestión (10): crecimiento_adquisiciones, participacion_mercado, ventas_por_segmento, desempeno_por_segmento, eficiencia_operativa, numero_empleados, perspectivas, riesgos, hechos_relevantes, cumplimiento_covenants.
- Auditoría (5): tipo_opinion, salvedades, enfasis, cuestiones_key, incertidumbre.

### 10.4 Duplicados de `variable_madre_id` — discrepancia a confirmar

El usuario pidió confirmar que no quedan duplicados sin resolver "salvo 4 por diseño". Tras recalcular, hay **24 ids con más de una fila** (no 4):

`subtotal_calculado` (9), `impuestos` (6), `efectivo_y_equivalentes` (5), `impuestos_diferidos` (5), `arrendamientos` (4), `provisiones` (4), `ori_acumulado` (4), `ingresos_operacionales` (4), `inversiones` (3), `obligaciones_laborales` (3), `utilidad_neta` (3), `amortizaciones` (3), `capex` (3), `cuentas_por_cobrar` (2), `otros_activos` (2), `activos_fijos` (2), `intangibles` (2), `cuentas_por_pagar` (2), `capital_social` (2), `gastos_administracion` (2), `deterioro_cuentas_por_cobrar` (2), `depreciaciones` (2), `gastos_financieros` (2), `bajas_activos` (2).

**No son conflictos sin resolver:** cada fila extra es un `concepto_src` distinto de la misma madre (p. ej. `i_*` y `c_*`, o variantes corriente/no corriente). La unicidad real es `(variable_madre_id, concepto_src)`, que sí es única en las 145 filas. Los 4 ids que citaste son un subconjunto; faltan ~20 más por el mismo motivo. **Se requiere tu confirmación** de que este diseño es correcto (o indícame cuáles deben fusionarse).

### 10.5 Pendiente de decisión (no se inventó)

- `formula_calculo` vacía en `capital_empleado`, `activos_netos`, `productividad`, las 8 claras y las 9 probables (convención).
- Definir si `costo_deuda` es pre/post impuesto y su origen (hoy `parametro_externo_manual`).
- Actualización de `README_taxonomia.md`: **hecha** (columnas y enums).

---

## 11. Tercera ronda — regla de tokens y fórmulas de cálculo (estado definitivo)

Aplicada el 2026-09-17. Respaldo previo: `C:\Users\Usuario\AppData\Local\Temp\opencode\taxonomia_variable_madre_v3.csv.bak`. CSV: **145 filas** (sin cambio de número).

### 11.1 Regla de tokens aplicada

- `concepto:<clave>` → concepto de `src/taxonomia.py` (87).
- `<variable_madre_id>` a secas → solo si la fila es `calculada` y tiene `concepto_src=pendiente` (sin concepto propio).

### 11.2 Fórmulas aplicadas (14 ids)

| variable_madre_id | formula_calculo |
|---|---|
| `NOPAT` | `concepto:i_resultado_operacional * (1 - tasa_efectiva_impuestos)` |
| `tasa_efectiva_impuestos` | `(concepto:i_gasto_impuesto_corriente + concepto:i_gasto_impuesto_diferido) / concepto:i_resultado_antes_impuestos` |
| `deuda_neta` | `deuda_financiera_total - concepto:b_efectivo` |
| `EBITDA` | `concepto:i_resultado_operacional + concepto:i_depreciaciones + concepto:i_amortizaciones` |
| `deuda_financiera_total` | `pasivo_financiero_corriente + deuda_financiera_no_corriente` |
| `capital_empleado` | `deuda_financiera_total + concepto:b_patrimonio_total` |
| `activos_netos` | `capital_empleado` |
| `costo_deuda` | `(concepto:c_intereses_pagados + concepto:c_intereses_arrendamiento) / deuda_financiera_total` |
| `variacion_CapTrabajo` | `(agregado:ACTIVO_CORRIENTE[t] - agregado:PASIVO_CORRIENTE[t]) - (agregado:ACTIVO_CORRIENTE[t-1] - agregado:PASIVO_CORRIENTE[t-1])` |
| `variacion_CXC` | `concepto:b_cuentas_por_cobrar[t] - concepto:b_cuentas_por_cobrar[t-1]` |
| `variacion_CxP` | `concepto:b_cuentas_por_pagar[t] - concepto:b_cuentas_por_pagar[t-1]` |
| `capex` | `concepto:c_adquisicion_ppye + concepto:c_adquisicion_intangibles` |
| `evolucion_ingresos` | `(concepto:i_comisiones[t] + concepto:i_ingresos_operaciones_conjuntas[t]) / (concepto:i_comisiones[t-1] + concepto:i_ingresos_operaciones_conjuntas[t-1]) - 1` |
| `evolucion_utilidad` | `concepto:i_resultado_del_ejercicio[t] / concepto:i_resultado_del_ejercicio[t-1] - 1` |

Otros cambios de esta ronda: `costo_deuda` → `fuente_esperada=calculado` (ya no `parametro_externo_manual`); `variacion_Inventarios` → `tipo_variable=no_aplica_tipo_entidad` + `fuente_esperada=no_aplica_tipo_entidad`; `productividad` sin cambios (`formula_calculo` vacía). `costo_patrimonio` permanece `parametro_externo_manual`.

### 11.3 Conteos finales

| `tipo_variable` | Filas |
|---|---|
| primaria | 117 |
| calculada | 26 |
| no_aplica_tipo_entidad | 2 |
| **Total** | **145** |

| `fuente_esperada` | Filas |
|---|---|
| estados | 91 |
| calculado | 25 |
| notas | 11 |
| informe_gestion | 10 |
| informe_auditoria | 5 |
| no_aplica_tipo_entidad | 2 |
| parametro_externo_manual | 1 |

### 11.4 Verificación de tokens — **16/16 conformes**

**Regla de tokens definitiva** (documentada en `README_taxonomia.md`):

- `concepto:<clave>` → uno de los 87 conceptos de `src/taxonomia.py`.
- `agregado:<NOMBRE>` → agrupación ya definida en `src/indicadores.py` (`ACTIVO_CORRIENTE`, `PASIVO_CORRIENTE`, etc.); se reutilizan, no se redefinen.
- `<variable_madre_id>` a secas → referencia a otra fila **sin `concepto_src` propio** (`concepto_src=pendiente`), sea `primaria` madre-solo o `calculada`.
- Notación temporal: `[t]` = período en análisis, `[t-1]` = período anterior; sin sufijo se asume `[t]`.

Resultado del validador (16 filas con fórmula, 14 ids; `capex` ×3): **conformes 16 / violan 0**. Los 87 `concepto:`, los `agregado:ACTIVO_CORRIENTE`/`agregado:PASIVO_CORRIENTE` (existen en `src/indicadores.py`) y todos los ids desnudos (`tasa_efectiva_impuestos`, `deuda_financiera_total`, `pasivo_financiero_corriente`, `deuda_financiera_no_corriente`, `capital_empleado`) pasan la regla.

### 11.5 Estado

**Fase 2.5 cerrada.** Todas las fórmulas conformes con la regla definitiva. Se autorizó el Paso 3.3 (piloto sobre una sección).
