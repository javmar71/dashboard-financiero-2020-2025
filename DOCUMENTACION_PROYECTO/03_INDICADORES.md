# 03_INDICADORES.md — INDICADORES FINANCIEROS

Documentar los indicadores financieros del proyecto. Para cada indicador incluir:

* nombre;
* categoría;
* fórmula;
* variables madre requeridas;
* fuente primaria esperada;
* período requerido;
* si requiere promedio;
* si requiere variación;
* si requiere información externa;
* observaciones metodológicas.

No inventar fórmulas.

Si existe ambigüedad metodológica, registrarla como pendiente de definición.

> **Actualización 2026-09-19 (conciliación desfase):** la documentación prevista registraba 32 indicadores canónicos, pero el pipeline (`src/indicadores.py`) implementa y emite **65 indicadores** (`salidas\indicadores.csv`, `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv`, ids 1-65). El presente documento queda **conciliado a 65**: §1 contiene la lista completa de los 65; §7 contiene el catálogo máquina detallado (nombre técnico, categoría, fórmula estricta, variables madre, condicionales) para los 65; §8 documenta el mapeo 32 previstos ↔ 65 máquina y las divergencias metodológicas (Paso C).

> **Actualización 2026-09-19 (cierre Fases 5/6 — aprobado por el usuario):** sobre el consolidado de los 65 indicadores (2020-2025) se ejecutaron y cerraron:
> - **Fase 5 — Screening de Red Flags / Alertas Tempranas:** `agente_financiero\fase5_diagnostico.py` (determinístico, umbrales documentados por indicador; resultado `SEÑAL_ALERTA / OBSERVACION / OK / NO_ENCONTRADO / NO_APLICA_TIPO_ENTIDAD`; nunca emite juicios de fraude). Salidas: `salidas\diagnostico_red_flags.{json,csv}` y `salidas\diagnostico_red_flags.md`.
> - **Fase 6 — Salidas en Excel e informe interactivo HTML:** `agente_financiero\fase6_salidas.py`. Salidas: `salidas\REPORTE_FINAL_INDICADORES.xlsx` (5 hojas), `salidas\informe_financiero_interactivo.html` (gráficos plotly por clasificación) y regeneración de `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv` con nombres y valores reales (el stub previo con `1.0` quedó eliminado).
> - **Hallazgo central del screening:** opinión de auditoría **con salvedad desde 2023** (2021-2022 limpia); en 2024-2025 la **calidad de resultados (FCO/UN < 0)** y la **variación de CxC (+2,1× en 2025 vs +15 % de ingresos)** concentran las señales cuantitativas. Requieren revisión humana antes de una conclusión final.

---

## 1. LISTA DE INDICADORES (65 — catálogo máquina `src/indicadores.py`)

| ID máq. | indicador (técnico, máquina) | categoria | requiere_promedio | requiere_externo | condicion_tipo_entidad | observaciones |
|---|-----------|-----------|-------------------|------------------|--------------|--------------|
| 1 | razon_corriente | Liquidez | N | N | — | Activo_corriente / Pasivo_corriente |
| 2 | prueba_acida | Liquidez | N | N | **NO APLICA servicios_financieros** | (Activo_corriente - Inventarios) / Pasivo_corriente; requiere `inventarios`. **Divergencia código:** la máquina la calcula como AC/PC (no resta inventarios); alinear (Paso C). |
| 3 | razon_efectivo | Liquidez | N | N | — | Efectivo y equivalentes / Pasivo corriente |
| 4 | capital_trabajo_neto | Liquidez | N | N | — | Activo corriente - Pasivo corriente |
| 5 | capital_trabajo_activos | Liquidez | N | N | — | (CT neto) / Activo total |
| 6 | endeudamiento_total | Endeudamiento | N | N | — | Pasivo total / Activo total |
| 7 | endeudamiento_patrimonial | Endeudamiento | N | N | — | Pasivo total / Patrimonio |
| 8 | deuda_financiera_activos | Endeudamiento | N | N | **proxy arrendamiento** | Deuda financiera / Activo total; `deuda_financiera` = pasivo por derecho de uso (sin obligaciones financieras) |
| 9 | deuda_financiera_patrimonio | Endeudamiento | N | N | **proxy arrendamiento** | Deuda financiera / Patrimonio |
| 10 | autonomia_financiera | Endeudamiento | N | N | — | Patrimonio / Activo total |
| 11 | apalancamiento_financiero | Apalancamiento | N | N | — | Activo total / Patrimonio |
| 12 | calidad_de_la_deuda | Endeudamiento | N | N | — | Pasivo corriente / Pasivo total |
| 13 | solvencia_total | Endeudamiento | N | N | — | Activo total / Pasivo total |
| 14 | pasivo_capital | Estructura Capital | N | N | — | Pasivo total / (Pasivo total + Patrimonio) |
| 15 | rotacion_activos_totales | Actividad/Eficiencia | S | N | — | Ingresos / Activos promedio |
| 16 | rotacion_activos_fijos | Actividad/Eficiencia | S | N | — | Ingresos / Activos no corrientes promedio |
| 17 | rotacion_cartera | Actividad/Eficiencia | S | N | — | Ingresos / CxC promedio |
| 18 | dias_cartera | Actividad/Eficiencia | N | N | — | 365 / rotacion_cartera |
| 19 | rotacion_inventarios | Actividad/Eficiencia | S | N | **NO APLICA servicios_financieros** | Costo de ventas / Inventarios promedio; requiere `inventarios` + `costo_operacional` |
| 20 | dias_inventario | Actividad/Eficiencia | N | N | **NO APLICA servicios_financieros** | 365 / rotacion_inventarios |
| 21 | rotacion_cuentas_por_pagar | Actividad/Eficiencia | S | N | **NO APLICA servicios_financieros** | Compras a crédito / CxP promedio; requiere `compras` (**no está en el catálogo 112**: retirada dec. 2026-09-18) |
| 22 | periodo_medio_pago | Actividad/Eficiencia | N | N | **NO APLICA servicios_financieros** | 365 / rotacion_cuentas_por_pagar; requiere `compras` (no está en el catálogo) |
| 23 | rotacion_capital_trabajo | Actividad/Eficiencia | S | N | — | Ingresos / CT promedio |
| 24 | ebitda | Capacidad Operativa | N | N | — | EBIT + depreciación + amortización |
| 25 | ebit | Rentabilidad | N | N | — | EBIT (resultado operativo antes de intereses e impuestos) |
| 26 | margen_bruto | Márgenes | N | N | — | Utilidad bruta / Ingresos |
| 27 | margen_operativo | Márgenes | N | N | — | EBIT / Ingresos |
| 28 | margen_ebitda | Márgenes | N | N | — | EBITDA / Ingresos |
| 29 | margen_antes_impuestos | Márgenes | N | N | — | Utilidad antes de impuestos / Ingresos |
| 30 | margen_neto | Márgenes | N | N | — | Utilidad neta / Ingresos |
| 31 | roa | Rentabilidad | S | N | — | Utilidad neta / Activos promedio |
| 32 | roe | Rentabilidad | S | N | — | Utilidad neta / Patrimonio promedio |
| 33 | capital_invertido | Estructura Capital | N | N | **proxy arrendamiento** | Capital suscrito y pagado + Obligaciones financieras (`obligaciones_financieras` = pasivo derecho de uso) |
| 34 | roic | Rentabilidad | S | N | — | UODI / Capital invertido promedio; UODI = EBIT × (1 − tasa_efectiva). **Metadato (2026-09-19):** UODI usa tasa EFECTIVA (impuesto corriente/EBIT) para el desempeño operativo real; la tasa ESTATUTARIA Art. 240 E.T. queda registrada como parámetro de comparación (ver §2.4 y fase9). |
| 35 | rendimiento_capital_total (RONA) | Rentabilidad | S | N | **proxy arrendamiento** | UODI / Capital empleado promedio (deuda_financiera_total + patrimonio_total); **denominador ajustado 2026-09-19** conforme canon §2.4 (antes: capital invertido) |
| 36 | ciclo_operativo | Actividad/Eficiencia | N | N | **NO APLICA servicios_financieros** | Días de inventario + días de cartera |
| 37 | ciclo_conversion_efectivo | Actividad/Eficiencia | S | N | **NO APLICA servicios_financieros** | Días inventario + días cartera − días proveedores |
| 38 | necesidad_capital_trabajo | Liquidez | N | N | — | Activo corriente operativo − Pasivo corriente operativo |
| 39 | capital_trabajo_ingresos | Actividad/Eficiencia | N | N | — | Capital de trabajo / Ingresos |
| 40 | cobertura_intereses | Endeudamiento | N | N | — | EBIT / Gastos financieros |
| 41 | cobertura_intereses_ebitda | Capacidad Operativa | N | N | — | EBITDA / Gastos financieros |
| 42 | variacion_cuentas_por_cobrar | Actividad/Eficiencia | N | N | — | CxC[t] / CxC[t-1] |
| 43 | variacion_inventarios | Actividad/Eficiencia | N | N | **NO APLICA servicios_financieros** | Inventarios[t] / [t-1] |
| 44 | variacion_cuentas_por_pagar | Actividad/Eficiencia | N | N | — | CxP[t] / CxP[t-1] |
| 45 | variacion_otros_activos_corr_op | Actividad/Eficiencia | N | N | — | Otros AC operativos[t] / [t-1] |
| 46 | variacion_otros_pasivos_corr_op | Actividad/Eficiencia | N | N | — | Otros PC operativos[t] / [t-1] |
| 47 | variacion_ppye | Actividad/Eficiencia | N | N | — | PPyE[t] / PPyE[t-1] |
| 48 | variacion_activos_intangibles | Actividad/Eficiencia | N | N | — | Intangibles[t] / [t-1] |
| 49 | variacion_otros_anc_op | Actividad/Eficiencia | N | N | — | Otros ANC operativos[t] / [t-1] |
| 50 | flujo_caja_operativo | Flujo de Caja | N | N | — | EBITDA − impuesto de renta + variación capital de trabajo operativo |
| 51 | flujo_caja_disponible_deuda | Flujo de Caja | N | N | — | FCO − variaciones PPyE, intangibles y otros ANC operativos |
| 52 | servicio_de_la_deuda | Flujo de Caja | N | N | — | Gastos financieros + amortización de deuda |
| 53 | dscr | Flujo de Caja | N | N | — | Flujo disponible para deuda / Servicio total de la deuda |
| 54 | deuda_financiera | Estructura Capital | N | N | **proxy arrendamiento** | = pasivo por derecho de uso (`deuda_financiera`) |
| 55 | deuda_ebitda | Capacidad Operativa | N | N | **proxy arrendamiento** | Obligaciones financieras / EBITDA |
| 56 | deuda_neta_ebitda | Capacidad Operativa | N | N | **proxy arrendamiento** | (Deuda financiera − Efectivo) / EBITDA |
| 57 | crecimiento_ingresos | Actividad/Eficiencia | N | N | — | (Ingresos[t] / [t-1]) − 1 |
| 58 | crecimiento_ebitda | Actividad/Eficiencia | N | N | — | (EBITDA[t] / [t-1]) − 1 |
| 59 | crecimiento_resultado_operativo | Actividad/Eficiencia | N | N | — | (EBIT[t] / [t-1]) − 1 |
| 60 | crecimiento_utilidad_neta | Actividad/Eficiencia | N | N | — | (Utilidad neta[t] / [t-1]) − 1 |
| 61 | crecimiento_activos | Actividad/Eficiencia | N | N | — | (Activo total[t] / [t-1]) − 1 |
| 62 | calidad_resultados | Rentabilidad | N | N | — | Flujo de efectivo de actividades operativas / Utilidad neta |
| 63 | rotacion_activos | Actividad/Eficiencia | N | N | — | Ingresos operacionales / Activos totales |
| 64 | multiplicador_capital | Estructura Capital | S | N | — | Activo promedio / Patrimonio promedio |
| 65 | roe_dupont | Rentabilidad | N | N | — | Margen neto × Rotación de activos × Multiplicador de capital |

---

## 2. DETALLE POR INDICADOR (referencia histórica: 32 indicadores previstos)

### 2.1 Liquidez

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| razon_corriente | Activo_corriente / Pasivo_corriente | activo_corriente, pasivo_corriente | Estados financieros | N | N | Snapshot un período |
| prueba_acida | (Activo_corriente - Inventarios) / Pasivo_corriente | activo_corriente, inventarios, pasivo_corriente | Estados financieros | N | N | Snapshot un período |
| capital_trabajo | Activo_corriente - Pasivo_corriente | activo_corriente, pasivo_corriente | Estados financieros | N | N | Snapshot un período |

### 2.2 Actividad / Eficiencia

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| rotacion_activos | Ingresos / Activos_promedio | ingresos_operacionales, activo_total | Estado resultados, Estado situación | S | N | Promedio requiere 2 balances |
| rotacion_cartera | Ventas / Cxc_promedio | ventas, cuentas_por_cobrar | Estado resultados, Notas | S | N | Promedio requiere 2 balances |
| dias_cartera | 365 / rotacion_cartera | rotacion_cartera | Cálculo derivado | N | N | Cálculo simple, requiere rotacion |
| rotacion_inventarios | Costo_operacional / Inventarios_promedio | costo_operacional, inventarios | Estado resultados, Estado situación | S | N | **NO APLICA si tipo_entidad=servicios (condicional)**: requiere cuentas inventarios/costo_operacional. Promedio requiere 2 balances |
| dias_inventario | 365 / rotacion_inventario | rotacion_inventario | Cálculo derivado | N | N | **NO APLICA si tipo_entidad=servicios (condicional)**: depende de rotacion_inventarios. Cálculo simple, requiere rotacion |
| rotacion_proveedores | Compras / Proveedores_promedio | proveedores | Notas, Estado situación | S | N | **NO APLICA si tipo_entidad=servicios (condicional)**: requiere cuenta compras (solo-comercial). Promedio requiere 2 balances |
| dias_proveedores | 365 / rotacion_proveedores | rotacion_proveedores | Cálculo derivado | N | N | **NO APLICA si tipo_entidad=servicios (condicional)**: depende de rotacion_proveedores. Cálculo simple |
| ciclo_conversion_efectivo | dias_cartera + dias_inventario - dias_proveedores | rotacion_cartera, rotacion_inventario, rotacion_proveedores | Cálculo derivado | S | N | **NO APLICA si tipo_entidad=servicios (condicional)**: incluye dias_proveedores y dias_inventario. Requiere 3 ratios |

**Regla condicional por tipo de entidad (2026-09-18; ratificada 2026-09-19):** la entidad objeto es un **servicio financiero**: no maneja inventarios ni compras de mercancías y no revela línea de costo en el estado de resultados (sus costos van en gastos operacionales). Con `tipo_entidad=servicios_financieros`, los indicadores que requieren las cuentas `inventarios`, `costo_ventas` (→ **`costo_operacional`**) o `compras` se clasifican **NO APLICA (condicional)** — no se eliminan (ver §2.10). Las cuentas permanecen en la taxonomía para entidades comercial/industrial.

### 2.3 Márgenes

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| margen_bruto | Utilidad_bruta / Ingresos_operacionales | utilidad_bruta, ingresos_operacionales | Estado resultados | N | N | Snapshot un período |
| margen_operacional | Utilidad_operacional / Ingresos_operacionales | utilidad_operacional, ingresos_operacionales | Estado resultados | N | N | Snapshot un período |
| margen_neto | Utilidad_neta / Ingresos_operacionales | utilidad_neta, ingresos_operacionales | Estado resultados | N | N | Snapshot un período |

### 2.4 Rentabilidad

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| roe | Utilidad_neta / Patrimonio_promedio | utilidad_neta, patrimonio | Estado situación, Estado resultados | S | N | 2 balances mínimos |
| roa | Utilidad_neta / Activos_promedio | utilidad_neta, activo_total | Estado resultados, Estado situación | S | N | 2 balances mínimos |
| roic | NOPAT / Capital_empleado_promedio | NOPAT, capital_empleado | Cálculo derivado | S | N | Definición canónica Bloque 0.4: NOPAT = utilidad_operacional × (1 − tasa_efectiva_impuestos); tasa_efectiva_impuestos = (impuesto corriente + impuesto diferido) / resultado antes de impuestos; capital_empleado = deuda_financiera_total + patrimonio_total. La tasa efectiva se deriva de los estados (no externa). |
| rona | NOPAT / Activos_netos_promedio | NOPAT, activos_netos | Cálculo derivado | S | N | Definición canónica Bloque 0.4: NOPAT igual que roic; activos_netos = capital_empleado (deuda_financiera_total + patrimonio_total). **Implementado 2026-09-19 en motor id 35 (RONA)**: denominador = deuda_financiera_total + patrimonio_total; UODI con tasa efectiva; tasa estatutaria Art. 240 E.T. como parámetro de comparación. |

### 2.5 Endeudamiento

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| endeudamiento_total | Pasivo_total / Activo_total | pasivo_total, activo_total | Estado situación | N | N | Snapshot un período |
| autonomia_financiera | Patrimonio_total / Activo_total | patrimonio, activo_total | Estado situación | N | N | Snapshot un período |
| deuda_patrimonio | Pasivo_total / Patrimonio_total | pasivo_total, patrimonio | Estado situación | N | N | Snapshot un período |
| cobertura_intereses | Utilidad_operacional / Gastos_financieros | utilidad_operacional, gastos_financieros | Estado resultados | N | N | Snapshot un período |

### 2.6 Apalancamiento

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| grado_apalancamiento_operativo | %ΔUtilidad_operacional / %ΔIngresos | ingresos_operacionales, utilidad_operacional | Estado resultados (2 períodos) | S | N | Definición canónica Bloque 0.4: variaciones porcentuales = (valor[t] − valor[t−1]) / |valor[t−1]|; se aplican sobre serie 2020→2021. No calculable si |valor[t−1]|=0. |
| grado_apalancamiento_financiero | %ΔUtilidad_neta / %ΔUtilidad_operacional | utilidad_operacional, utilidad_neta | Estado resultados (2 períodos) | S | N | Mismo método de variaciones porcentuales. Requiere serie 2+ períodos. |
| grado_apalancamiento_total | grado_apalancamiento_operativo × grado_apalancamiento_financiero | ingresos_operacionales, utilidad_operacional, utilidad_neta | Estados completos | S | N | Definición canónica Bloque 0.4: producto de ambos grados (no fórmula combinada independiente). |

### 2.7 Capacidad Operativa (EBITDA)

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| ebitda | Utilidad_operacional + Depreciaciones + Amortizaciones | utilidad_operacional, depreciaciones, amortizaciones | Estado resultados, Estado situación | N | N | Snapshot un período (reconstrucción) |
| margen_ebitda | EBITDA / Ingresos_operacionales | ebitda, ingresos_operacionales | Cálculo derivado | N | N | Snapshot un período |
| ebitda_intereses | EBITDA / Gastos_financieros | ebitda, gastos_financieros | Cálculo derivado | N | N | Snapshot un período |
| deuda_ebitda | Deuda_total / EBITDA | deuda_total, ebitda | Estado situación, Cálculo | N | N | Snapshot un período |

### 2.8 Flujo de Caja

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| flujo_operativo | utilidad_neta + depreciaciones + amortizaciones − variacion_CapTrabajo | utilidad_neta, depreciaciones, amortizaciones, variacion_CapTrabajo | Estado resultados, Estado situación, Notas | S | N | Definición canónica Bloque 0.4 corregida (2026-09-18): método indirecto. variacion_CapTrabajo = (AC[t]−PC[t]) − (AC[t−1]−PC[t−1]); **signo restado** porque un aumento del capital de trabajo es una salida de caja. Las variaciones CXC/Inventarios/CxP NO se suman por separado (ya están dentro del delta de capital de trabajo). |
| flujo_libre | flujo_operativo − CAPEX | flujo_operativo, capex | Estado situación, Cálculo | S | N | Definición canónica Bloque 0.4: CAPEX = c_adquisicion_ppye + c_adquisicion_intangibles. |

### 2.9 Estructura de Capital

| indicador | formula | variables_madre | fuente_primaria | requiere_promedio | requiere_externo | observaciones |
|-----------|---------|----------------|-----------------|-------------------|------------------|--------------|
| wacc | (costo_deuda × (1 − tasa_estatutaria_impuestos) × proporcion_deuda) + (ROI × proporcion_patrimonio) | costo_deuda, ROI (ROIC id 34), tasa_estatutaria_impuestos, proporcion_deuda, proporcion_patrimonio | Estados financieros (catálogo interno) | S | **N** | Definición canónica **actualizada (2026-09-19)** por instrucción ejecutiva: **queda descartado CAPM** y todo insumo externo de mercado (beta, tasa libre de riesgo, prima de riesgo). **Ke = ROI = ROIC (id 34)** = rentabilidad operativa interna (utilidad operativa después de impuestos / capital invertido promedio). Escudo fiscal con **tasa estatutaria/marginal**; `tasa_estatutaria_impuestos` = tarifa general personas jurídicas Art. 240 E.T. vigente en el periodo (2020: 32 %; 2021: 31 %; 2022+: 35 %), único parámetro legal (regla universal, no insumo de mercado). proporcion_deuda = deuda_financiera_total / (deuda_financiera_total + patrimonio); proporcion_patrimonio = patrimonio / (deuda_financiera_total + patrimonio); costo_deuda = |c_intereses_pagados| / deuda_financiera_total (intereses pagados como gasto financiero, consistente con cobertura de intereses id 40). **Sin parámetros externos manuales.** |

### 2.10 Condicionales por tipo de entidad

Regla de aplicabilidad por tipo de entidad: las variables/cuentas **no se eliminan** por el tipo de la entidad; se **condiciona** su uso según el parámetro `tipo_entidad`.

- **Parámetro:** `tipo_entidad`. Valor del proyecto (2021): **`servicios_financieros`**.
- **Cuentas condicionadas:**

| cuenta | aplica_en | nota |
|--------|-----------|------|
| `inventarios` | comercial, industrial | La fiduciaria no maneja inventarios (sin línea en el balance). |
| `costo_ventas` → en la entidad se llama **`costo_operacional`** | comercial, industrial | El ERI fiduciario no revela línea de costo (ingresos → gastos); los costos ya están en `i_gastos_*`. |
| `compras` | comercial, industrial | Retirada de la taxonomía para la entidad actual (dec. 2026-09-18); definición conservada para otros tipos. **No está en el catálogo de variables madre.** |
| `proveedores` | todos | Cuenta de pasivo comercial que SÍ existe en la fiduciaria (nota 15). |

- **Regla general:** un indicador es **NO APLICA (condicional)** si requiere ≥ 1 cuenta cuyo `aplica_en` no incluye el `tipo_entidad` del análisis. No es `NO_ENCONTRADO` ni eliminación.
- **Indicadores NO APLICA para `tipo_entidad=servicios_financieros` (catálogo máquina 65):** `prueba_acida` (2), `rotacion_inventarios` (19), `dias_inventario` (20), `rotacion_cuentas_por_pagar` (21), `periodo_medio_pago` (22), `ciclo_operativo` (36), `ciclo_conversion_efectivo` (37), `variacion_inventarios` (43). Resultado máquina = `None` → **NO_ENCONTRADO / no calculable**, sin interpolación.
- **Implementación en pipeline:** `src/indicadores.py` (`NA_MOTIVOS`: inventarios / costo_ventas / compras_credito; ids 19/20/21/22/36/37/43), regla machine-readable en `agente_financiero\condicionales_tipo_entidad.json` y bitácora de fichas de razonamiento en `agente_financiero\RAZONAMIENTO_DECISIONES.md` (Fichas F-01 a F-03).

---

## 3. VACÍOS METODOLÓGICOS IDENTIFICADOS

| Indicador | Falta | Razón | Estado |
|-----------|-------|-------|--------|
| roic | NOPAT, capital_empleado | Requiere tasa impositiva efectiva y definición de capital empleado | RESUELTO B0.4: NOPAT = utilidad_operacional × (1 − tasa_efectiva_impuestos); capital_empleado = deuda_financiera_total + patrimonio_total (ver §2.4) |
| rona | NOPAT, activos_netos | Requiere definición de qué compone "activos netos" | RESUELTO B0.4: activos_netos = capital_empleado (deuda_financiera_total + patrimonio_total) (ver §2.4) |
| flujo_operativo | variacion_CapTrabajo, variaciones detalle | Requiere extracto de notas: variaciones CXC, Inventarios, CxP | RESUELTO B0.4: método indirecto; solo variacion_CapTrabajo (ver §2.8) |
| wacc | beta, prima riesgo, tasa libre, costo deuda/capital | Requieren datos de mercado externos (no en estados financieros) | **RESUELTO (2026-09-19)** — instrucción ejecutiva: **Ke = ROI = ROIC (id 34)** del catálogo interno; **CAPM y parámetros externos descartados**. Fórmula canónica en §2.9 (Fase 7 calculada 2020-2025; ver §8). `wacc` NO está en el catálogo máquina 65 (ver §8) |
| grados_apalancamiento | series históricas 2+ períodos | Requieren comparativas de ingresos/utilidades años anteriores | RESUELTO B0.4: variaciones porcentuales (ver §2.6); GAO/GAF/GAT NO están en el catálogo máquina 65 (ver §8) |
| prueba_acida (2) | Divergencia fórmula código vs regla | La máquina calcula AC/PC (idéntico a razon_corriente) aunque la regla es NO APLICA | **PENDIENTE de alineación (Paso C) 2026-09-19**: decidir si la máquina debe emitir None (NO_ENCONTRADO) para id 2 siendo servicios_financieros |
| deuda financiera (proxy) | Sin obligaciones financieras en la entidad | La máquina usa `pasivo por derecho de uso` como proxy de obligaciones financieras (ids 8/9/33/34/35/54/55/56) | DOCUMENTADO (NA_MOTIVOS `creditos_financieros`); la extracción 2022 verificó ausencia estructural de deuda (ver lote revisado) |

**Acciones:** Definir fórmulas definitivas, identificar fuentes de datos externos, establecer procedimiento de extracción de series históricas.

---

## 4. MATRIZ VARIABLE MADRE → INDICADORES

| variable_madre | indicadores_posibles | requiere_promedio | requiere_externo | requiere_2_periodos |
|---------------|---------------------|-------------------|------------------|--------------------|
| efectivo_y_equivalentes | razon_corriente, prueba_acida | N | N | N |
| activo_total | roa, rotacion_activos, endeudamiento_total | S | N | S (promedio) |
| cuentas_por_cobrar | rotacion_cartera, dias_cartera | S | N | S (promedio cxc) |
| inventarios | rotacion_inventarios, dias_inventario | S | N | S (promedio inventarios) |
| pasivo_total | endeudamiento_total, deuda_patrimonio | N | N | N |
| patrimonio | roe, autonomia_financiera | S | N | S (promedio patrimonio) |
| ingresos_operacionales | margen_bruto, margen_operacional, margen_neto | N | N | N |
| utilidad_operacional | ebitda, margen_ebitda | N | N | N |
| utilidad_neta | roe, roa, margen_neto | S | N | S (promedio utilidad) |
| depreciaciones | ebitda | N | N | N |
| amortizaciones | ebitda | N | N | N |
| deuda_financiera_total (canónica; pasivo_financiero_total es alias) | cobertura_intereses, deuda_ebitda, endeudamiento_total, roic, rona | N | S | N |
| deuda_financiera_corriente (canónica; pasivo_financiero_corriente es alias) | (desglose de deuda_financiera_total) | S | N | N |
| pasivo_corriente | razon_corriente | S | N | N |
| utilidad_operacional | ebitda, margen_ebitda | N | N | N |
| utilidad_neta | roe, roa, margen_neto | S | N | S |

---

## 5. MATRIZ INDICADOR → VARIABLES MADRE REQUERIDAS

| indicador | variables_madre | periodo | promedio | externo |
|-----------|----------------|---------|----------|---------|
| razon_corriente | activo_corriente, pasivo_corriente | snapshot | N | N |
| prueba_acida | activo_corriente, inventarios, pasivo_corriente | snapshot | N | N |
| capital_trabajo | activo_corriente, pasivo_corriente | snapshot | N | N |
| rotacion_activos | ingresos_operacionales, activos_promedio | 2_periodos | S | N |
| rotacion_cartera | ventas, cxc_promedio | 2_periodos | S | N |
| dias_cartera | rotacion_cartera | snapshot | N | N |
| rotacion_inventarios | costo_operacional, inventarios_promedio | 2_periodos | S | N |
| dias_inventario | rotacion_inventario | snapshot | N | N |
| margen_bruto | utilidad_bruta, ingresos_operacionales | snapshot | N | N |
| margen_operacional | utilidad_operacional, ingresos_operacionales | snapshot | N | N |
| margen_neto | utilidad_neta, ingresos_operacionales | snapshot | N | N |
| roe | utilidad_neta, patrimonio_promedio | 2_periodos | S | N |
| roa | utilidad_neta, activos_promedio | 2_periodos | S | N |
| roic | NOPAT, capital_empleado | 2+_periodos | S | N |
| rona | NOPAT, activos_netos | 2+_periodos | S | N |
| endeudamiento_total | pasivo_total, activo_total | snapshot | N | N |
| autonomia_financiera | patrimonio_total, activo_total | snapshot | N | N |
| cobertura_intereses | utilidad_operacional, gastos_financieros | snapshot | N | N |
| ebitda | utilidad_operacional, depreciaciones, amortizaciones | snapshot | N | N |
| flujo_operativo | utilidad_neta, depreciaciones, amortizaciones, variacion_CapTrabajo | 2_periodos | N | N |
| flujo_libre | flujo_operativo, capex | snapshot | N | N |
| wacc | costo_deuda, ROI (ROIC id 34), tasa_estatutaria_impuestos, proporciones | promedio | S | **N** |

---

## 6. PROXIMIDAD DE DEFINICIÓN

Los siguientes indicadores tenían ambigüedad metodológica pendiente de definición. Con la **definición canónica del Bloque 0.4** quedan resueltos (ver §2.4, §2.6, §2.8, §2.9 y §3):

1. ~~**roic / rona:**~~ RESUELTO — NOPAT sobre utilidad operacional ajustada por tasa impositiva efectiva; capital_empleado = deuda_financiera_total + patrimonio_total; activos_netos = capital_empleado.
2. ~~**flujo_operativo:**~~ RESUELTO — método indirecto; solo variacion_CapTrabajo.
3. ~~**wacc:**~~ RESUELTO (metodología) — **fórmula canónica actualizada (2026-09-19): Ke = ROI = ROIC (id 34)**; escudo fiscal con tasa **estatutaria/marginal** (Art. 240 E.T.: 2020: 32 %, 2021: 31 %, 2022+: 35 %); **eliminado CAPM y parámetros externos manuales**.
4. ~~**grados_apalancamiento:**~~ RESUELTO — variaciones porcentuales (valor[t]−valor[t−1])/|valor[t−1]|; GAO = %ΔUO/%ΔIngresos, GAF = %ΔUN/%ΔUO, GAT = GAO × GAF.

**Ningún insumo externo manual pendiente para wacc** (2026-09-19): Ke proviene del catálogo interno (ROIC id 34). Único valor legal (tasa estatutaria) es regla universal, no dato de mercado.

---

## 7. CATÁLOGO MÁQUINA COMPLETO — 65 INDICADORES (`src/indicadores.py`)

Reglas generales (inquebrantables):

1. **No calcular por interpolación ni suposición.** Si una variable madre no existe en el origen (cuenta ausente en el balance, ERI o notas), el indicador **DEBE** devolver `NO_ENCONTRADO`/`None`.
2. Denominador `None` o `0` → resultado `None` / `NO_ENCONTRADO` (nunca infinito ni signo inventado).
3. Promedios solo si existen los dos balances (`t` y `t−1`); variaciones solo si existe el comparativo.
4. En `tipo_entidad=servicios_financieros`, los indicadores que requieren `inventarios`, `costo_operacional` o `compras` → **NO APLICA** → `NO_ENCONTRADO`.
5. Los signos y definiciones provienen del código: **fuente de verdad** = `src/indicadores.py` (`INDICADORES`, ids 1-65). `REPORTE_FINAL_65_INDICADORES.csv` referencia los ids 1-65 (nombres resueltos por el catálogo).

Abreviaturas de agregados (iguales a `src/indicadores.py`):

- **AC** = efectivo_y_equivalentes + inversiones + cuentas_por_cobrar + impuestos(corriente activo) + otros_activos
- **ANC** = impuestos_diferidos + activos_fijos + arrendamientos(activo) + intangibles
- **PC** = cuentas_por_pagar + obligaciones_laborales + impuestos(corriente pasivo) + otros_pasivos
- **ACO** = efectivo_y_equivalentes + cuentas_por_cobrar + otros_activos
- **PCO** = cuentas_por_pagar + otros_pasivos
- **AOTNCO** = intangibles + arrendamientos(activo)
- **ingresos** = utilidad_bruta (i_utilidad_bruta) → `ingresos_operacionales`
- **EBIT** = ingresos − gastos_generales − deterioro_cxc + otros_ingresos_egresos  (gastos_generales = obligaciones_laborales + gastos_administracion + gastos op. conjuntas)
- **EBITDA** = EBIT + depreciaciones + amortizaciones
- **UODI** = EBIT × (1 − tasa_efectiva), tasa_efectiva = impuesto corriente / EBIT
- **deuda_financiera** = pasivo por derecho de uso (`arrendamientos`, b_derecho_uso_pasivo) — **proxy** documentado (sin obligaciones financieras en la entidad)
- **gastos_financieros** = |c_intereses_pagados|; **amortización_deuda** = |c_pagos_arrendamiento|

| ID | nombre técnico | categoría (§doc) | fórmula estricta (máquina) | variables_madre (catálogo) | prom. | 2 per. | condicional tipo_entidad / proxy | NO_ENCONTRADO |
|----|----------------|------------------|----------------------------|------------------------------|-------|--------|----------------------------------|---------------|
| 1 | Razon corriente | Liquidez | AC / PC | activo_corriente, pasivo_corriente | N | N | — | si falta AC o PC |
| 2 | Prueba acida | Liquidez | (AC − Inventarios) / PC *(código: AC/PC)* | activo_corriente, inventarios, pasivo_corriente | N | N | **NO APLICA servicios_financieros** (requiere inventarios); alinear máquina (Paso C) | siempre NO_ENCONTRADO si no hay inventarios |
| 3 | Razon de efectivo | Liquidez | Efectivo / PC | efectivo_y_equivalentes, pasivo_corriente | N | N | — | si falta efectivo o PC |
| 4 | Capital de trabajo neto | Liquidez | AC − PC | activo_corriente, pasivo_corriente | N | N | — | si falta algún componente |
| 5 | Capital de trabajo / Activos | Liquidez | (AC − PC) / Activo_total | activo_corriente, pasivo_corriente, activo_total | N | N | — | si falta componente |
| 6 | Endeudamiento total | Endeudamiento | Pasivo_total / Activo_total | pasivo_total, activo_total | N | N | — | si falta pasivo o activo |
| 7 | Endeudamiento patrimonial | Endeudamiento | Pasivo_total / Patrimonio | pasivo_total, patrimonio | N | N | — | si falta pasivo o patrimonio |
| 8 | Deuda financiera / Activos | Endeudamiento | deuda_financiera / Activo_total | arrendamientos, activo_total | N | N | **proxy derechouso** | si falta arrendamiento o activo |
| 9 | Deuda financiera / Patrimonio | Endeudamiento | deuda_financiera / Patrimonio | arrendamientos, patrimonio | N | N | **proxy derechouso** | idem |
| 10 | Autonomia financiera | Endeudamiento | Patrimonio / Activo_total | patrimonio, activo_total | N | N | — | idem |
| 11 | Apalancamiento financiero | Apalancamiento | Activo_total / Patrimonio | activo_total, patrimonio | N | N | — | idem |
| 12 | Calidad de la deuda | Endeudamiento | PC / Pasivo_total | pasivo_corriente, pasivo_total | N | N | — | idem |
| 13 | Solvencia total | Endeudamiento | Activo_total / Pasivo_total | activo_total, pasivo_total | N | N | — | idem |
| 14 | Pasivo / Capital | Estructura Capital | Pasivo_total / (Pasivo_total + Patrimonio) | pasivo_total, patrimonio | N | N | — | idem |
| 15 | Rotacion de activos totales | Actividad/Eficiencia | Ingresos / ((Activo t + Activo t-1)/2) | ingresos_operacionales, activo_total | S | S | — | falta activo en t-1 |
| 16 | Rotacion de activos fijos | Actividad/Eficiencia | Ingresos / ((ANC t + ANC t-1)/2) | ingresos_operacionales, impuestos_diferidos, activos_fijos, arrendamientos, intangibles | S | S | — | idem |
| 17 | Rotacion de cuentas por cobrar | Actividad/Eficiencia | Ingresos / ((CxC t + CxC t-1)/2) | ingresos_operacionales, cuentas_por_cobrar | S | S | — | idem |
| 18 | Periodo medio de cobro | Actividad/Eficiencia | 365 / rotacion CxC | derivado de 17 | N | S | — | NO_ENCONTRADO si 17=NO_ENCONTRADO |
| 19 | Rotacion de inventarios | Actividad/Eficiencia | Costo de ventas / ((Inventarios t + t-1)/2) | costo_operacional, inventarios | S | S | **NO APLICA servicios_financieros** | siempre NO_ENCONTRADO (sin inventarios/costo) |
| 20 | Dias de inventario | Actividad/Eficiencia | 365 / rotacion inventarios | derivado de 19 | N | S | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin inventarios) |
| 21 | Rotacion de cuentas por pagar | Actividad/Eficiencia | Compras a credito / ((CxP t + t-1)/2) | cuentas_por_pagar, **compras (ausente catálogo)** | S | S | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin compras) |
| 22 | Periodo medio de pago | Actividad/Eficiencia | 365 / rotacion CxP | derivado de 21 | N | S | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin compras) |
| 23 | Rotacion del capital de trabajo | Actividad/Eficiencia | Ingresos / ((CT t + CT t-1)/2) | ingresos_operacionales, activo_corriente, pasivo_corriente | S | S | — | falta CT t-1 |
| 24 | EBITDA | Capacidad Operativa | EBIT + depreciaciones + amortizaciones | ingresos_operacionales, obligaciones_laborales, gastos_administracion, deterioro_cuentas_por_cobrar, otros_ingresos_egresos, depreciaciones, amortizaciones | N | N | — | si falta algún componente |
| 25 | EBIT | Rentabilidad | Ingresos − gastos generales − deterioro_cxc + otros ingresos/egresos | ingresos_operacionales, obligaciones_laborales, gastos_administracion, deterioro_cuentas_por_cobrar, otros_ingresos_egresos | N | N | — | idem |
| 26 | Margen bruto | Márgenes | Utilidad bruta / Ingresos | utilidad_bruta, ingresos_operacionales | N | N | — | si falta alguno |
| 27 | Margen operativo | Márgenes | EBIT / Ingresos | componentes de 25, ingresos_operacionales | N | N | — | idem |
| 28 | Margen EBITDA | Márgenes | EBITDA / Ingresos | componentes de 24, ingresos_operacionales | N | N | — | idem |
| 29 | Margen antes de impuestos | Márgenes | Utilidad antes de impuestos / Ingresos | resultado_antes_impuestos (i_resultado_antes_impuestos), ingresos_operacionales | N | N | — | idem |
| 30 | Margen neto | Márgenes | Utilidad neta / Ingresos | utilidad_neta (i_resultado_del_ejercicio), ingresos_operacionales | N | N | — | idem |
| 31 | ROA | Rentabilidad | Utilidad neta / ((Activo t + t-1)/2) | utilidad_neta, activo_total | S | S | — | falta activo t-1 |
| 32 | ROE | Rentabilidad | Utilidad neta / ((Patrimonio t + t-1)/2) | utilidad_neta, patrimonio | S | S | — | falta patrimonio t-1 |
| 33 | Capital invertido | Estructura Capital | Capital suscrito y pagado + Obligaciones financieras | capital_social, arrendamientos (proxy obligaciones) | N | N | **proxy derechouso** | si falta alguno |
| 34 | ROIC | Rentabilidad | UODI / ((Capital invertido t + t-1)/2) | componentes de 25, impuestos (i_gasto_impuesto_corriente), capital_social, arrendamientos | S | S | **proxy derechouso** | idem |
| 35 | Rendimiento sobre capital total | Rentabilidad | UODI / ((Capital total t + t-1)/2) | componentes de 25, impuestos, capital_social, arrendamientos | S | S | **proxy derechouso** | idem |
| 36 | Ciclo operativo | Actividad/Eficiencia | Dias inventario + Dias cartera | inventarios, cuentas_por_cobrar | N | N | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin inventarios) |
| 37 | Ciclo de conversion de efectivo | Actividad/Eficiencia | Dias inventario + Dias cartera − Dias proveedores | inventarios, cuentas_por_cobrar, cuentas_por_pagar | N | N | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin inventarios/compras) |
| 38 | Necesidad de capital de trabajo | Liquidez | ACO − PCO | efectivo_y_equivalentes, cuentas_por_cobrar, otros_activos, cuentas_por_pagar, otros_pasivos | N | N | — | si falta componente |
| 39 | Capital de trabajo / Ingresos | Actividad/Eficiencia | (AC − PC) / Ingresos | activo_corriente, pasivo_corriente, ingresos_operacionales | N | N | — | idem |
| 40 | Cobertura de intereses | Endeudamiento | EBIT / Gastos financieros | componentes de 25, gastos_financieros (c_intereses_pagados) | N | N | — | si falta gastos_financieros |
| 41 | Cobertura de intereses EBITDA | Capacidad Operativa | EBITDA / Gastos financieros | componentes de 24, gastos_financieros | N | N | — | idem |
| 42 | Variacion de cuentas por cobrar | Actividad/Eficiencia | CxC[t] / CxC[t-1] | cuentas_por_cobrar | N | S | — | falta t-1 o t-1=0 |
| 43 | Variacion inventarios | Actividad/Eficiencia | Inventarios[t] / [t-1] | inventarios | N | S | **NO APLICA servicios_financieros** | NO_ENCONTRADO (sin inventarios) |
| 44 | Variacion de cuentas por pagar | Actividad/Eficiencia | CxP[t] / CxP[t-1] | cuentas_por_pagar | N | S | — | falta t-1 |
| 45 | Variacion de otros activos corrientes operativos | Actividad/Eficiencia | Otros AC op.[t] / [t-1] | otros_activos | N | S | — | idem |
| 46 | Variacion de otros pasivos corrientes operativos | Actividad/Eficiencia | Otros PC op.[t] / [t-1] | otros_pasivos | N | S | — | idem |
| 47 | Variacion PPyE | Actividad/Eficiencia | PPyE[t] / PPyE[t-1] | activos_fijos | N | S | — | idem |
| 48 | Variacion activos intangibles | Actividad/Eficiencia | Intangibles[t] / [t-1] | intangibles | N | S | — | idem |
| 49 | Variacion otros activos no corrientes operativos | Actividad/Eficiencia | Otros ANC op.[t] / [t-1] | intangibles, arrendamientos | N | S | — | idem |
| 50 | Flujo de caja operativo | Flujo de Caja | EBITDA − impuesto corriente + ΔCT operativo | componentes de 24, impuestos (i_gasto_impuesto_corriente), efectivo_y_equivalentes, cuentas_por_cobrar, otros_activos, cuentas_por_pagar, otros_pasivos | N | S | — | falta ΔCT op. |
| 51 | Flujo de caja disponible para deuda | Flujo de Caja | FCO − ΔPPyE − ΔIntangibles − ΔOtros ANC op. | componentes de 50, activos_fijos, intangibles, arrendamientos | N | S | — | cualquier Δ ausente |
| 52 | Servicio de la deuda | Flujo de Caja | Gastos financieros + Amortizacion de deuda | gastos_financieros, arrendamientos (c_pagos_arrendamiento) | N | N | **proxy derechouso** | si falta alguno |
| 53 | DSCR | Flujo de Caja | Flujo disponible para deuda / Servicio de la deuda | componentes de 51 y 52 | N | N | **proxy derechouso** | si falta 51 o 52 |
| 54 | Deuda financiera | Estructura Capital | Obligaciones financieras corrientes + no corrientes | arrendamientos (proxy b_derecho_uso_pasivo) | N | N | **proxy derechouso** | si falta arrendamiento |
| 55 | Deuda financiera / EBITDA | Capacidad Operativa | Obligaciones financieras / EBITDA | arrendamientos, componentes de 24 | N | N | **proxy derechouso** | si falta alguno |
| 56 | Deuda financiera neta / EBITDA | Capacidad Operativa | (Deuda financiera − Efectivo) / EBITDA | arrendamientos, efectivo_y_equivalentes, componentes de 24 | N | N | **proxy derechouso** | idem |
| 57 | Crecimiento de ingresos | Actividad/Eficiencia | (Ingresos[t] / [t-1]) − 1 | ingresos_operacionales | N | S | — | falta t-1 o t-1=0 |
| 58 | Crecimiento del EBITDA | Actividad/Eficiencia | (EBITDA[t] / [t-1]) − 1 | componentes de 24 | N | S | — | idem |
| 59 | Crecimiento del resultado operativo | Actividad/Eficiencia | (EBIT[t] / [t-1]) − 1 | componentes de 25 | N | S | — | idem |
| 60 | Crecimiento de utilidad neta | Actividad/Eficiencia | (Utilidad neta[t] / [t-1]) − 1 | utilidad_neta | N | S | — | idem |
| 61 | Crecimiento de activos | Actividad/Eficiencia | (Activo total[t] / [t-1]) − 1 | activo_total | N | S | — | idem |
| 62 | Calidad de resultados | Rentabilidad | Flujo de efectivo de actividades operativas / Utilidad neta | subtotal_calculado (c_flujo_operacion), utilidad_neta | N | N | — | si falta flujo operativo |
| 63 | Rotacion de activos | Actividad/Eficiencia | Ingresos operacionales / Activos totales | ingresos_operacionales, activo_total | N | N | — | idem |
| 64 | Multiplicador de capital | Estructura Capital | (Activo avg) / (Patrimonio avg) | activo_total, patrimonio | S | S | — | falta t-1 |
| 65 | ROE DuPont | Rentabilidad | Margen neto × Rotacion de activos × Multiplicador de capital | utilidad_neta, ingresos_operacionales, activo_total, patrimonio | N | S | — | si falta 30, 63 o 64 |

---

## 8. CONCILIACIÓN: 32 PREVISTOS ↔ 65 MÁQUINA (2026-09-19)

La documentación prevista (secciones 2.1-2.9) usaba una nomenclatura propia. El catálogo máquina (`src/indicadores.py`) es la fuente de verdad de ejecución. Mapeo y divergencias:

| ID máq. | nombre máquina | indicador previsto §2 |
|---------|----------------|------------------------|
| 1 | Razon corriente | razon_corriente |
| 2 | Prueba acida | prueba_acida (ver divergencia abajo) |
| 3 | Razon de efectivo | — (nuevo) |
| 4 | Capital de trabajo neto | capital_trabajo |
| 5 | Capital de trabajo / Activos | — (nuevo) |
| 6 | Endeudamiento total | endeudamiento_total |
| 7 | Endeudamiento patrimonial | deuda_patrimonio |
| 8 | Deuda financiera / Activos | — (nuevo) |
| 9 | Deuda financiera / Patrimonio | — (nuevo) |
| 10 | Autonomia financiera | autonomia_financiera |
| 11 | Apalancamiento financiero | — (nuevo; 1/Autonomía) |
| 12 | Calidad de la deuda | — (nuevo) |
| 13 | Solvencia total | — (nuevo) |
| 14 | Pasivo / Capital | — (nuevo) |
| 15 | Rotacion de activos totales | rotacion_activos |
| 16 | Rotacion de activos fijos | — (nuevo) |
| 17 | Rotacion de cuentas por cobrar | rotacion_cartera |
| 18 | Periodo medio de cobro | dias_cartera |
| 19 | Rotacion de inventarios | rotacion_inventarios |
| 20 | Dias de inventario | dias_inventario |
| 21 | Rotacion de cuentas por pagar | rotacion_proveedores (⚠️ la máquina usa CxP + compras, no `proveedores`) |
| 22 | Periodo medio de pago | dias_proveedores (⚠️ idem) |
| 23 | Rotacion del capital de trabajo | rotacion_del_capital_de_trabajo (matriz §4) |
| 24 | EBITDA | ebitda |
| 25 | EBIT | — (nuevo) |
| 26 | Margen bruto | margen_bruto |
| 27 | Margen operativo | margen_operacional |
| 28 | Margen EBITDA | margen_ebitda |
| 29 | Margen antes de impuestos | — (nuevo) |
| 30 | Margen neto | margen_neto |
| 31 | ROA | roa |
| 32 | ROE | roe |
| 33 | Capital invertido | — (nuevo; base de ROIC máquina) |
| 34 | ROIC | roic (⚠️ la máquina usa capital_invertido = capital suscrito + arrendamiento; el previsto usaba capital_empleado = deuda + patrimonio) |
| 35 | Rendimiento sobre capital total | rona (⚠️ el previsto definía activos_netos = capital_empleado; la máquina usa capital total) |
| 36 | Ciclo operativo | — (nuevo) |
| 37 | Ciclo de conversion de efectivo | ciclo_conversion_efectivo |
| 38 | Necesidad de capital de trabajo | — (nuevo) |
| 39 | Capital de trabajo / Ingresos | — (nuevo) |
| 40 | Cobertura de intereses | cobertura_intereses |
| 41 | Cobertura de intereses EBITDA | ebitda_intereses |
| 42-49 | Variaciones de partidas | — (nuevos) |
| 50 | Flujo de caja operativo | flujo_operativo (⚠️ la máquina usa EBITDA − impuesto + ΔCT op.; el previsto usaba UN + dep + amort − ΔCapTrabajo) |
| 51 | Flujo de caja disponible para deuda | flujo_libre (⚠️ la máquina no usa CAPEX; usa variaciones de ANC) |
| 52 | Servicio de la deuda | — (nuevo) |
| 53 | DSCR | — (nuevo) |
| 54 | Deuda financiera | — (nuevo) |
| 55 | Deuda financiera / EBITDA | deuda_ebitda |
| 56 | Deuda financiera neta / EBITDA | — (nuevo) |
| 57-61 | Crecimientos | — (nuevos) |
| 62 | Calidad de resultados | calidad_resultados (matriz taxonomía) |
| 63 | Rotacion de activos | rotacion_activos (⚠️ sin promedio; ratio DuPont) |
| 64 | Multiplicador de capital | — (nuevo) |
| 65 | ROE DuPont | — (nuevo) |

**Indicadores previstos SIN equivalente en el catálogo máquina 65** (documentar como pendientes o absorberse):

| previsto §2 | estado en máquina | acción |
|-------------|-------------------|--------|
| rona | solo parcial (id 35 usa otra base) | **Paso C**: unificar definición de capital / activos netos |
| grado_apalancamiento_operativo | ausente | documentar como analítico complementario (no en 65) |
| grado_apalancamiento_financiero | ausente | idem |
| grado_apalancamiento_total | ausente | idem |
| flujo_libre | solo parcial (id 51 sin CAPEX) | **Paso C**: decidir si incorporar CAPEX en máquina |
| wacc | ausente | **Paso C**: la máquina no calcula WACC; taxonomía lo define como `calculado` con `costo_patrimonio` externo |

**Divergencias estructurales (Paso C):**

1. `prueba_acida` (2): la máquina la calcula como AC/PC (idéntico a id 1). **Resuelta por decisión del usuario (2026-09-19):** la coincidencia es **correcta** y se conserva tal cual — es una empresa de servicios sin inventarios, por lo que AC/PC = (AC − Inventarios)/PC = AC/PC. No recalcular 2022. En el screening Fase 5 se clasifica `NO_APLICA_TIPO_ENTIDAD` (formaliza la regla §2.10 sin cambiar el valor emitido).
2. `rotacion_cuentas_por_pagar` / `periodo_medio_pago` (21/22): la máquina usa cuentas por pagar + `compras` (cuenta retirada del catálogo); los previstos 9/10 usaban `proveedores`. Correlación taxonómica directa inexistente; mantienen NO_ENCONTRADO por ausencia de `compras`.
3. Deuda: la máquina usa `pasivo por derecho de uso` como proxy de obligaciones financieras (ids 8/9/33/34/35/54/55/56); la extracción 2022 confirmó ausencia estructural de obligaciones financieras → los indicadores de deuda derivan del proxy de arrendamiento, documentado en evidencia.

---

*Fin del documento. Catálogo máquina = `src/indicadores.py`; salida = `salidas\indicadores.csv`, `agente_financiero\REPORTE_FINAL_65_INDICADORES.csv` (ids 1-65, valores reales), `salidas\REPORTE_FINAL_INDICADORES.xlsx` e `informe_financiero_interactivo.html`; diagnóstico Fase 5 = `salidas\diagnostico_red_flags.{json,csv,md}`; WACC con Ke=ROI (Fase 7, 2026-09-19) = `salidas\fase7_wacc_roi\wacc_roi_2020_2025.{json,csv}`.*