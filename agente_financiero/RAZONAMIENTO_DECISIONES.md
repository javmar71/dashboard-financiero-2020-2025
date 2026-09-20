# RAZONAMIENTO_DECISIONES.md — Bitácora de Fichas de Razonamiento IA (Capa 4)

Fecha de vigencia: 2026-09-18. Registra las decisiones de aplicabilidad y profundización contextual del motor de IA (`opencode` propone → `big pickle` audita → Python verifica → usuario aprueba) bajo el esquema `esquema_razonamiento_ia.json`.

## 1. Resumen de Fichas Emitidas

| Ficha ID | Fecha | Tema / Variable | Decisión | Estado |
|---|---|---|---|---|
| **F-01** | 2026-09-18 | `vencimientos` | Retirada de la taxonomía (no es variable financiera estándar) | `ACEPTADO_INFERENCIA` |
| **F-02** | 2026-09-18 | `compras` | Retirada de la taxonomía (palabra ausente en EEFF fiduciarios) | `ACEPTADO_INFERENCIA` |
| **F-03** | 2026-09-18 | Regla condicional por `tipo_entidad` | Servicios financieros: inventarios, costo operacional, compras y sus indicadores derivados = **NO APLICA (condicional)**. `costo_ventas` renombrada a `costo_operacional` (NA). Cuentas no se borran. | `ACEPTADO_INFERENCIA` |
| **F-04** | 2026-09-18 | `utilidad_bruta` | ERI sin línea de costo; `i_utilidad_bruta` = resultado antes de gastos de operación (ingresos). Definida como ingreso operativo; margen bruto no aplica. | `ACEPTADO_INFERENCIA` |
| **F-05** | 2026-09-18 | `crecimiento_organico` | Fórmula: ingresos_operacionales[t] / ingresos_operacionales[t-1] - 1. 2021 calculable; 2020 NO_CALCULABLE. | `ACEPTADO_INFERENCIA` |
| **F-06** | 2026-09-18 | `productividad` | Fórmula: ingresos_operacionales / numero_empleados. 2021 y 2020 NO_CALCULABLE (sin planta de personal reportada). | `ACEPTADO_INFERENCIA` |
| **F-07** | 2026-09-18 | `calidad_resultados` | Fórmula: flujo_operativo / resultado_del_ejercicio. 2021 calculable (≈ 1.52); 2020 NO_CALCULABLE. | `ACEPTADO_INFERENCIA` |
| **F-08** | 2026-09-18 | Verificación XBRL 2022–2025 | 2022 y 2023 corresponden a Fuprevisora (NIT 830053105-3); 2024 (NIT 900251864-8) y 2025 (NIT 901870663-3) pertenecen a otras entidades/fondos y se descartan (`no_corresponde_a_entidad`). | `ACEPTADO_INFERENCIA` |

---

## 2. Detalle de Fichas (F-01 a F-03)

### Ficha F-01: Retirada de `vencimientos`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`taxonomia_variable_madre.csv`, `paso35_lote.json`].
- **Pregunta:** ¿Debe mantenerse la variable madre `vencimientos` en la taxonomía financiera?
- **Marco general:** Estándar de maduración de cartera o vencimientos comerciales.
- **Propuesta IA (`opencode`):** Retirar la variable. No corresponde a una variable madre de estados financieros (balance/ERI).
- **Verificación `big pickle`:** ACEPTADA. No existe cuenta contable en PUC ni nota asociada a "vencimientos" como partida financiera balanceada.
- **Validación Python:** Fila eliminada del CSV (151 → 150), 2 registros removidos del lote (39 → 37), mapeos y reportes actualizados.
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-02: Retirada de `compras`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`taxonomia_variable_madre.csv`, `calculadas_2021_2020.json`].
- **Pregunta:** ¿Debe mantenerse la variable madre `compras` en la taxonomía de la fiduciaria?
- **Marco general:** Insumo universal para costo de ventas y rotación de proveedores en comercio/industria.
- **Propuesta IA (`opencode`):** Retirar `compras`. La palabra no se usa en los estados financieros de una fiduciaria ni forma parte de la utilidad bruta.
- **Verificación `big pickle`:** ACEPTADA con instrucción explícita del usuario. Cero menciones en notas o balance de La Previsora.
- **Validación Python:** Fila eliminada del CSV (150 → 149), 2 registros NO_CALCULABLE removidos del lote (58 total, resumen 34/22/2).
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-03: Regla condicional por `tipo_entidad` (`servicios_financieros`)
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`03_INDICADORES.md`, `src/indicadores.py`].
- **Pregunta:** ¿Cómo tratar indicadores que requieren cuentas ausentes en empresas de servicios (inventarios, costos, proveedores)?
- **Marco general:** Fórmulas universales de rotación y prueba ácida.
- **Propuesta IA (`opencode`):** No eliminar cuentas (excepto compras). Establecer regla condicional por `tipo_entidad`: si `servicios_financieros`, los indicadores de inventarios, costo operacional, proveedores y prueba ácida pasan a **NO APLICA (condicional)**. Renombrar `costo_ventas` a `costo_operacional` (`no_aplica_tipo_entidad`).
- **Verificación `big pickle`:** ACEPTADA. Respeta la contabilidad de servicios sin corromper el modelo para empresas industriales/comerciales.
- **Validación Python:** CSV actualizado (`costo_operacional` con tag NA), `condicionales_tipo_entidad.json` creado, `NA_MOTIVOS` en `src/indicadores.py` verificado.
- **Estado final:** `ACEPTADO_INFERENCIA`.

---

## 3. Detalle de Fichas (F-04 a F-07: Bloque B2)

### Ficha F-04: Definición contextual de `utilidad_bruta`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`salidas\\datos_estados_financieros.csv`, `03_INDICADORES.md`].
- **Pregunta:** ¿Cómo calcular `utilidad_bruta` en una entidad que no revela costo de ventas?
- **Marco general:** $\text{Utilidad Bruta} = \text{Ingresos Operacionales} - \text{Costo de Ventas}$.
- **Propuesta IA (`opencode`):** El ERI fiduciario presenta directamente `i_utilidad_bruta` (204.261 en 2021) catalogada como "Resultado antes de gastos de operación", equivalente a la suma de comisiones y operaciones conjuntas (sin línea de costo). Por tanto, `utilidad_bruta` toma el valor de los ingresos operacionales (`i_utilidad_bruta`). El indicador `margen_bruto` se marca **NO APLICA (condicional)** al no haber divisor de costo diferenciado.
- **Verificación `big pickle`:** ACEPTADA. Consistente con la estructura ERI fiduciario.
- **Validación Python:** Fórmula actualizada en taxonomía; registro recalculado en lote de derivadas.
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-05: `crecimiento_organico`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`salidas\\datos_estados_financieros.csv`].
- **Pregunta:** ¿Cómo calcular el crecimiento orgánico interanual?
- **Marco general:** $\text{Crecimiento Orgánico} = \frac{\text{Ingresos}[t]}{\text{Ingresos}[t-1]} - 1$.
- **Propuesta IA (`opencode`):** Fórmula basada en la evolución de ingresos operacionales totales. Para 2021 es calculable usando 2020; para 2020 es `NO_CALCULABLE` por falta de 2019.
- **Verificación `big pickle`:** ACEPTADA.
- **Validación Python:** Fórmula aplicada en taxonomía y calculada para 2021.
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-06: `productividad`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`salidas\\datos_estados_financieros.csv`].
- **Pregunta:** ¿Es calculable la productividad (ingresos / empleado)?
- **Marco general:** $\text{Productividad} = \frac{\text{Ingresos Operacionales}}{\text{Número de Empleados}}$.
- **Propuesta IA (`opencode`):** `NO_CALCULABLE` estructural para ambos años; el número de empleados no es una variable cuantitativa reportada en el balance/ERI ni en notas auditadas del piloto.
- **Verificación `big pickle`:** ACEPTADA.
- **Validación Python:** Estado `NO_CALCULABLE` con nota de vacío estructural.
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-07: `calidad_resultados`
- **Contexto:** tipo_entidad=`servicios_financieros`, anio=`2021`, fuentes=[`salidas\\datos_estados_financieros.csv`, `f4calc_verificar.py`].
- **Pregunta:** ¿Cómo calcular la calidad de los resultados?
- **Marco general:** $\text{Calidad Resultados} = \frac{\text{Flujo de Caja Operativo}}{\text{Resultado del Ejercicio}}$.
- **Propuesta IA (`opencode`):** Para 2021: $\frac{72.399}{47.632} \approx 1,52$ (F/C operativo > utilidad neta, alta calidad). Para 2020: `NO_CALCULABLE` por ausencia de flujo operativo 2020 en el piloto.
- **Verificación `big pickle`:** ACEPTADA.
- **Validación Python:** Fórmula aplicada y calculada para 2021.
- **Estado final:** `ACEPTADO_INFERENCIA`.

### Ficha F-08: Verificación de Identidad XBRL (2022–2025)
- **Contexto:** tipo_entidad=`servicios_financieros`, anios=`2022-2025`, fuentes=[`ESTADOS_FINANCIEROS_YYYY/*.xbrl`].
- **Pregunta:** ¿Los archivos XBRL de la Superfinanciera para 2022, 2023, 2024 y 2025 corresponden a Fiduciaria La Previsora S.A. (NIT 830053105-3)?
- **Marco general:** Identificador de entidad en esquema XBRL (`identifier`).
- **Propuesta IA (`opencode`):** 
  - 2022: NIT `830053105-3` (Fuprevisora) — **Válido / Corresponde**.
  - 2023: NIT `830053105-3` (Fuprevisora) — **Válido / Corresponde**.
  - 2024: NIT `900251864-8` — **No corresponde** (XBRL de otra sociedad/fondo).
  - 2025: NIT `901870663-3` — **No corresponde** (XBRL de otra sociedad/fondo).
- **Verificación `big pickle`:** ACEPTADA. Se descartan los XBRL de 2024 y 2025 como fuente primaria de la entidad, siguiendo el precedente del diagnóstico XBRL de 2021.
- **Validación Python:** Script de inspección XML ejecutado.
- **Estado final:** `ACEPTADO_INFERENCIA`.
