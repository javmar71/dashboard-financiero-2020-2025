# PASO_REVISION_FORMULAS.md — Revisión de fórmulas contra fuentes académicas

Fecha: 2026-09-18. Motor de la revisión: **opencode** (websearch/webfetch), auditoría: **big pickle**,
revisión humana: pendiente de decisión del usuario. Alcance acordado: **WACC primero, luego lote**
(EBITDA, flujo libre, coberturas, ROA/ROE, deuda/EBITDA). No se ha modificado la taxonomía ni
`03_INDICADORES.md`: primero se deciden los 2 puntos metodológicos abiertos (§4).

## 1. Método

- Se contrastó cada `formula_calculo` de `taxonomia_variable_madre.csv` y de `03_INDICADORES.md`
  contra fuentes académicas observables: Brealey & Myers (Principles of Corporate Finance, ch. 19),
  OpenStax (Principles of Finance 2e, §17.3), CFA Institute (Free Cash Flow Valuation, 2026),
  A. Damodaran (NYU Stern, "Discounted Cashflow Valuation"; Cost of Capital), Eugene Brigham
  (Intermediate Financial Management), Morgan Stanley (Cost of Capital, 2023), Velez-Pareja & Tham
  ("A Note on the Weighted Average Cost of Capital WACC", SSRN 254587).
- Veredicto por fórmula: `ACEPTADA` (estructura igual a la norma académica), `NOTA` (diferencia menor
  documentada) o `ABIERTA` (requiere decisión del usuario).

## 2. Resultados — WACC (caso señalado)

| Elemento documentado | Fórmula del proyecto | Norma académica | Fuente | Veredicto |
|---|---|---|---|---|
| wacc | `costo_deuda * (1 - tasa_efectiva_impuestos) * proporcion_deuda + costo_patrimonio * proporcion_patrimonio` | `(D/V)·Kd·(1−T) + (E/V)·Ke` | Brealey & Myers ch.19; OpenStax §17.3; Wikipedia; CFA; Velez-Pareja & Tham | **ACEPTADA** |
| proporcion_deuda | `deuda_financiera_total / (deuda_financiera_total + patrimonio)` | `D / (D + E)` | Brealey & Myers ch.19 (ej. 0,4 = 500/1.250) | **ACEPTADA** |
| proporcion_patrimonio | `patrimonio / (deuda_financiera_total + patrimonio)` | `E / (D + E)` | Brealey & Myers ch.19 | **ACEPTADA** |
| costo_deuda | `(c_intereses_pagados + c_intereses_arrendamiento) / deuda_financiera_total` | Costo antes de imp. mismo: con deuda negociada se prefiere YTM (yield to maturity); con deuda no transada, aproximación por intereses pagados / deuda es práctica aceptada | Morgan Stanley (Cost of Capital §Estimating Cost of Debt); Damodaran | **ACEPTADA con NOTA** (proxy implícito; la entidad no tiene deuda transada) |
| tasa_efectiva_impuestos | `(impuesto corriente + impuesto diferido) / resultado antes de impuestos` | Se recomienda la tasa **marginal/estatutaria**, no la efectiva histórica (distorsionable por partidas no recurrentes) | Brealey & Myers ch.19 ("Tc is the marginal corporate tax rate"); Morgan Stanley ("multiply … by one minus the marginal tax rate") | **ABIERTA** (ver §4.1) |
| costo_patrimonio | parámetro externo manual (CAPM) | `Re = rf + β·ERP` | Damodaran; CFA (Cost of Capital); Morgan Stanley | **ACEPTADA** (pendiente solo el valor, ya registrado como `PENDIENTE_PARAMETRO_EXTERNO` en Fase 4.7) |

Conclusión WACC: **la estructura coincide exactamente con la norma académica** (sin acciones preferentes,
la fórmula se reduce a `(D/V)·Kd·(1−T) + (E/V)·Ke`, que es lo documentado). No hay corrección de la
fórmula. Punto a decidir: tasa efectiva vs. marginal.

## 3. Resultados — lote de fórmulas

Abreviaturas: `i_op` = `i_resultado_operacional`; `D&A` = `i_depreciaciones` + `i_amortizaciones`.

| variable/indicador | Fórmula del proyecto | Norma académica | Fuente | Veredicto |
|---|---|---|---|---|
| EBITDA | `i_resultado_operacional + i_depreciaciones + i_amortizaciones` | `EBITDA = EBIT + Dep + Amort` | FE Training (EBITDA coverage); IJCAETR 2025 (Prediction of EBITDA); Brigham; Investopedia | **ACEPTADA** |
| ebitda_intereses | `EBITDA / Gastos_financieros` | EBITDA-to-interest coverage = EBITDA / intereses | FE Training | **ACEPTADA** |
| cobertura_intereses | `Utilidad_operacional / Gastos_financieros` | Times-Interest-Earned = EBIT / intereses | Brigham (Intermediate Financial Management) | **ACEPTADA** |
| deuda_ebitda | `Deuda_total / EBITDA` | Leverage estándar | Damodaran | **ACEPTADA** |
| flujo_operativo | `i_resultado_del_ejercicio + D&A + variacion_CapTrabajo` | Método indirecto, **signo**: ΔWC creciente es salida de caja (se resta) | CFA (FCFF = NI + NCC − FCInv − WCInv); Damodaran | **ABIERTA** (signo de `variacion_CapTrabajo`, ver §4.2) |
| flujo_libre | `flujo_operativo − capex` | FCF = CFO − CapEx | Damodaran; McKinsey (Koller) | **ACEPTADA** (como simplificación CFO-CapEx) |
| roe | `Utilidad_neta / Patrimonio_promedio` | ROE = NI / equity (promedio = buena práctica) | Brigham; Damodaran | **ACEPTADA** |
| roa | `Utilidad_neta / Activos_promedio` | ROA = NI / total assets (promedio = buena práctica) | Brigham | **ACEPTADA** |

## 4. Puntos metodológicos abiertos (decisiones del usuario — RESUELTOS 2026-09-18)

### 4.1 WACC — tasa de impuestos: efectiva vs. marginal (DECIDIDO: tasa estatutaria 35 %)
La norma académica usa **tasa marginal** (`rd(1−Tc)`). El proyecto usaba `tasa_efectiva_impuestos`
(impuesto corriente + diferido) / resultado antes de impuestos.

**Decisión del usuario (2026-09-18): Opción A — tasa estatutaria/marginal.** Aplicado:
- Nueva fila en la taxonomía: `tasa_estatutaria_impuestos` (`parametro_externo_manual`), tarifa general
  de personas jurídicas del Art. 240 E.T. vigente en el período. **Corrección de verificación
  (big pickle, 2026-09-18):** la tarifa de 2021 es **31 %** y la de 2020 es **32 %** (Ley 2010/2019);
  el **35 %** rige desde 2022 (Ley 2155/2021) y se mantiene 2023+ (Ley 2277/2022). El valor inicial
  documentado (35 % para 2021) era erróneo y fue corregido. La sobretasa para entidades financieras
  (Par. 7 Art. 240, declarado inexequible C-510/2019) no se aplica; para 2023+ verificar si la fiduciaria
  queda en la tarifa especial financieras (38 %) de la Ley 2277/2022.
- La fórmula `wacc` pasó de `tasa_efectiva_impuestos` a `tasa_estatutaria_impuestos`.
- `tasa_efectiva_impuestos` se mantiene para **NOPAT** (roic/rona), donde sí corresponde la tasa
  efectiva.
- Sin repercusión en los resultados de Fase 4.7 (`wacc` sigue NO_CALCULABLE por `costo_deuda`=0/0 y
  `costo_patrimonio` pendiente).

### 4.2 flujo_operativo — signo de `variacion_CapTrabajo` (DECIDIDO: restar)
`variacion_CapTrabajo = (AC[t]−PC[t]) − (AC[t−1]−PC[t−1])` es **positiva cuando el capital de trabajo
crece**. En el método indirecto un aumento del capital de trabajo es una **salida de caja**, por lo que
el término debe **restarse**.

**Decisión del usuario (2026-09-18): Opción A — corregir a restar.** Aplicado en la taxonomía:
`flujo_operativo = concepto:i_resultado_del_ejercicio + concepto:i_depreciaciones +
concepto:i_amortizaciones - variacion_CapTrabajo`.
**Recorrida Fase 4.7 hecha** (2026-09-18, opencode propone / Python verifica, `dif rel 0.0`):
- `flujo_operativo` 2021: 51.857 → **72.399** (ACEPTADO; ΔCapTrabajo = −10.271 = contracción de capital
  de trabajo → entrada de caja).
- `flujo_libre` 2021: 56.073 → **76.615** (ACEPTADO; capex = −4.216).
- 2020: sigue **NO_CALCULABLE** (faltan ACTIVO/PASIVO CORRIENTE 2019 para `variacion_CapTrabajo`).
- `wacc`: sin cambio de resultado (NO_CALCULABLE); fórmula actualizada a `tasa_estatutaria_impuestos`.

## 5. Cambios aplicados (2026-09-18)

| Archivo | Cambio |
|---|---|
| `taxonomia_variable_madre.csv` | `flujo_operativo` → signo `- variacion_CapTrabajo`; `wacc` → `tasa_estatutaria_impuestos`; nueva fila `tasa_estatutaria_impuestos` (params. externo). CSV íntegro: 151 filas. |
| `calculadas_2021_2020.json` (Fase 4.7) | Re-calculados: `flujo_operativo` 2021 = 72.399, `flujo_libre` 2021 = 76.615 (ACEPTADO); 2020 NO_CALCULABLE; `wacc` fórmula/insumo actualizados. Resumen intacto: 34/24/2. |
| `03_INDICADORES.md` | WACC (§1, §2.9, §3, §5, §6) y flujo_operativo (§2.8) actualizados a las decisiones. |

Sin cambios en `esquema_calculo_ia.json`. La re-corrida de `flujo_operativo`/`flujo_libre` quedó
ejecutada y verificada (dif rel 0.0).

## 6. Fuentes consultadas (trazabilidad)

- Brealey, R.; Myers, S.; Allen, F. — Principles of Corporate Finance, ch. 19 (Financing and Valuation):
  WACC after-tax = `r_D(1−Tc)(D/V) + r_E(E/V)`. (erenow.org/common/principles-of-corporate-finance/19.php)
- OpenStax — Principles of Finance 2e, §17.3 "Calculating the Weighted Average Cost of Capital":
  `WACC = D%·rd(1−T) + E%·re` (sin preferentes).
  (openstax.org/books/principles-finance-2e/pages/17-3-calculating-the-weighted-average-cost-of-capital)
- CFA Institute — Free Cash Flow Valuation (2026): `FCFF = NI + NCC − FCInv − WCInv`;
  `FCFF = EBIT(1−T)+Dep−FCInv−WCInv`; firm value descontado con WACC.
- Damodaran, A. — Discounted Cashflow Valuation (NYU Stern): FCFE = NI − (CapEx−Dep) − Δno-cash WC + (deuda nueva − repagos); FCFF/FCFE y costos con CAPM.
- Velez-Pareja, I.; Tham, J. — A Note on the Weighted Average Cost of Capital WACC (SSRN 254587).
- Morgan Stanley — Cost of Capital (2023): after-tax cost of debt = pre-tax × (1 − marginal tax rate);
  book value of debt como proxy razonable de market value.
- Brigham, E. — Intermediate Financial Management (debt management, profitability ratios, TIE/EBITDA coverage).
- FE Training — EBITDA Coverage Ratio / EBITDA-to-interest coverage.
- IJCAETR 2025 — Evaluating Company Performance: The Role of EBITDA (EBITDA = EBIT + Dep + Amort).