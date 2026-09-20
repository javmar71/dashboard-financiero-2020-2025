# PASO_F4_CALC_REPORTE.md — CÁLCULO DE VARIABLES DERIVADAS 2021/2020 (FASE 4.7)

Fecha: 2026-09-18
Etapa: Fase 4.7 — Capa de variables calculadas (`tipo_variable = calculada`)
Estado: CERRADO (con pendientes externos: `costo_patrimonio`)

> **Nota de vigencia (2026-09-18, tarde):** reporte HISTÓRICO ejecutado con Gemini (retirado).
> Motor vigente: **opencode** propone / **big pickle** audita / `f4calc_verificar.py` recalcula.
> El flujo "IA propone / Python verifica" y el esquema `esquema_calculo_ia.json` (v1) siguen igual.

## 1. Objetivo y decisiones

Calcular las **30 variables calculadas** de la taxonomía para los periodos **2021 y 2020**
(60 entradas `(variable_madre_id, periodo)`), con el esquema **"IA propone / Python verifica"**,
usando como insumos:

- `salidas/datos_estados_financieros.csv` (conceptos `b_/i_/c_`) — fuente `estados`;
- `src/indicadores.py` (agregados `ACTIVO_CORRIENTE` / `PASIVO_CORRIENTE`) — fuente `calculado`;
- `paso35_lote.json` (lote Fase 4) — fuente `notas`.

Decisiones del usuario que acotan el resultado:

1. **Método:** la IA propone; Python recalcula de forma independiente y decide el estado final.
2. **Convención canónica B0.3:** `deuda = 0`, por lo que `deuda_financiera_total = 0` y, en
   consecuencia, `costo_deuda` es **NO_CALCULABLE** (0/0).
3. **`costo_patrimonio` diferido:** parámetro externo manual (CAPM) → `PENDIENTE_PARAMETRO_EXTERNO`;
   `wacc` queda **NO_CALCULABLE** al depender de `costo_deuda` y `costo_patrimonio`.
4. **Alcance: las 30** (9 sin fórmula documentada se marcan según disponibilidad de insumos).
5. **Períodos: 2021 y 2020**; las variaciones t/t-1 solo son calculables para 2021 porque
   requieren `t-1 = 2019`, fuera del alcance de la Fase 4.

## 2. Método

- **Insumos (Python):** `f4calc_insumos.py` resuelve los tokens de cada `formula_calculo`
  (`concepto:`, `agregado:`, variable desnuda del lote u otra calculada), con orden topológico y
  memoización, y emite `calculadas_insumos.json` (60 entradas; 21 con fórmula, 9 sin fórmula).
- **IA propone:** `f4calc_ia.py` (modelo `gemini-3.5-flash`, temperature 0, `response_schema`
  `esquema_calculo_ia.json`) resuelve las 60 entradas en **1 llamada** (ambos períodos), con el
  contexto de notas del lote. Respaldo: `calculadas_ia_raw.json` / `calculadas_ia_meta.json`
  (35.958 chars de contexto; 8.047 tokens de salida). `gemini-3.6-flash` estaba agotado (HTTP 429),
  por lo que se usó el modelo de respaldo.
- **Python verifica:** `f4calc_verificar.py` recalcula con la fórmula y los insumos, compara contra
  la propuesta IA (tolerancia relativa 0,5 % o absoluta ≤ 0,01) y aplica controles cruzados.
  - `opinion_{limpia,adversa,abstencion}` se derivan **determinísticamente** de
    `tipo_opinion` (lote): `sin_salvedad` ⇒ limpia=1, adversa=0, abstención=0.
- **Corrección relevante:** el primer run marcaba todo `NO_CALCULABLE` por un desajuste de tipo
  `str`/`int` en las claves de `STATES`/`LOTE` (claves de período string, búsquedas con entero).
  Se normalizó el período en `V()`/`detalle()`; tras el arreglo los valores son coherentes.

## 3. Resultado final

Estados finales (60 entradas): **34 ACEPTADO · 24 NO_CALCULABLE · 2 PENDIENTE_PARAMETRO_EXTERNO**
(0 INCONSISTENTE). Los 7 controles cruzados por período pasan sin observaciones
(`deuda=0`, `pasivo_financiero_total = deuda`, `capital_empleado = activos_netos`,
`proporcion_deuda + proporcion_patrimonio = 1`, `flujo_libre = flujo_operativo − capex`,
`deuda_neta = 0 − b_efectivo`).

### 3.1 ACEPTADAS (34)

| Variable | Período | Valor verificado |
|----------|---------|------------------|
| `capex` | 2021 / 2020 | −4.216 / −6.743 |
| `deuda_financiera_total` | 2021 / 2020 | 0 / 0 |
| `pasivo_financiero_total` | 2021 / 2020 | 0 / 0 |
| `pasivo_financiero_corriente` | 2021 / 2020 | 0 / 0 |
| `NOPAT` | 2021 / 2020 | 46.853,18 / 53.950,22 |
| `capital_empleado` | 2021 / 2020 | 282.888 / 293.000 |
| `activos_netos` | 2021 / 2020 | 282.888 / 293.000 |
| `variacion_CapTrabajo` | 2021 | −10.271 |
| `variacion_CXC` | 2021 | 5.272 |
| `variacion_CxP` | 2021 | 3.900 |
| `evolucion_ingresos` | 2021 | 0,037922 (3,79 %) |
| `evolucion_utilidad` | 2021 | −0,181862 (−18,19 %) |
| `opinion_limpia` / `opinion_adversa` / `abstencion` | 2021 | 1 / 0 / 0 |
| `tasa_efectiva_impuestos` | 2021 / 2020 | 0,339984 / 0,354238 |
| `deuda_neta` | 2021 / 2020 | −20.991 / −43.925 |
| `EBITDA` | 2021 / 2020 | 85.484 / 97.430 |
| `flujo_operativo` | 2021 | 51.857 |
| `flujo_libre` | 2021 | 56.073 |
| `proporcion_deuda` | 2021 / 2020 | 0 / 0 |
| `proporcion_patrimonio` | 2021 / 2020 | 1 / 1 |

### 3.2 NO_CALCULABLE (24)

| Variable | Períodos | Motivo |
|----------|----------|--------|
| `costo_deuda` | 2021 / 2020 | División por cero (`deuda_financiera_total = 0`, convención B0.3) |
| `wacc` | 2021 / 2020 | Depende de `costo_deuda` (no calculable) y `costo_patrimonio` (pendiente) |
| `variacion_CapTrabajo` / `variacion_CXC` / `variacion_CxP` | 2020 | Requiere `t-1 = 2019` |
| `evolucion_ingresos` / `evolucion_utilidad` | 2020 | Requiere `t-1 = 2019` |
| `flujo_operativo` / `flujo_libre` | 2020 | Dependen de la variación de capital de trabajo 2020 |
| `opinion_limpia` / `opinion_adversa` / `abstencion` | 2020 | `tipo_opinion` no extraído en Fase 4 (solo 2021) |
| `utilidad_bruta` / `compras` / `crecimiento_organico` / `productividad` / `calidad_resultados` | 2021 / 2020 | Sin fórmula documentada ni insumos trazables en el lote |

### 3.3 PENDIENTE_PARAMETRO_EXTERNO (2)

- `costo_patrimonio` (2021 / 2020): parámetro externo manual (CAPM). Al incorporarlo se podrá
  recalcular `wacc` (aunque seguirá sin término de deuda por la convención B0.3).

## 4. Lote resultante y trazabilidad

- Lote final: `calculadas_2021_2020.json` (60 registros; campos `valor_propuesto_ia`,
  `valor_verificado_python`, `estado_final`, `metodo_verificacion`, `diferencia_relativa`, `notas`).
- Intermedios: `calculadas_insumos.json`, `calculadas_ia_raw.json`, `calculadas_ia_meta.json`.
- Esquema IA: `esquema_calculo_ia.json` (v1). Scripts en `%TEMP%\opencode`.

## 5. Limitaciones y pendientes

1. **`costo_patrimonio`**: requiere el parámetro externo (CAPM) para cerrar `wacc`.
2. **Variaciones 2020**: requieren el estado financiero 2019 (escalado Fase 5).
3. **5 variables sin fórmula** (`utilidad_bruta`, `compras`, `crecimiento_organico`,
   `productividad`, `calidad_resultados`): no tienen `formula_calculo` en la taxonomía ni insumos
   asociados en el lote; se marcan NO_CALCULABLE. Su cálculo exige definir la convención/formula y
   la fuente (notas) en Bloque 0.
4. **`tipo_opinion` 2020**: no se extrajo en Fase 4 (el Informe de Auditoría disponible es 2021);
   las tres banderas de opinión 2020 quedan NO_CALCULABLE.

## 6. Conclusión

Fase 4.7 **cerrada**: 34 variables derivadas verificadas y aceptadas, con los controles cruzados
sin observaciones; quedan 24 NO_CALCULABLE por causas documentadas (convención deuda=0, períodos
t-1 fuera de alcance, fórmulas sin insumos) y 2 `costo_patrimonio` a la espera de parámetro externo.
