# REPORTE DE INTELIGENCIA FINANCIERA 2020–2025

**Entidad:** Reservado (agnosticismo de entidad) · **Período analizado:** 2020–2025
**Motor de cálculo:** `src\indicadores.py` (65 indicadores) · **Validación transversal:** Fase 9 (100 % integridad)
**Cumplimiento normativo:** NIIF/IFRS · **Fecha del reporte:** 2026-09-19

> **Garantía de trazabilidad:** todas las cifras de este documento provienen de las matrices auditadas y persistentes:
> `salidas\indicadores.csv`, `salidas\datos_estados_financieros.csv`, `salidas\fase7_wacc_roi\wacc_roi_2020_2025.csv`,
> `salidas\fase8_evidencia_formal\evidencia_formal_conceptos.csv` y `salidas\fase9_validacion_transversal\matriz_consistencia_transversal.csv`.
> No se inventa ni interpola ningún valor (Regla 1 del proyecto). Sección 7 detalla la consistencia.

---

## 1. RESUMEN EJECUTIVO (TL;DR para Dirección)

La entidad muestra un perfil financiero **sólido, holgado y de bajo apalancamiento**, con dos ciclos claramente diferenciados:

| Dimensión | Lectura 2020–2025 |
|---|---|
| **Creación de valor** | ROIC > WACC en los 5 años con spread (ROIC−WACC) positivo de **+0,35 pp a +1,88 pp**; sin embargo, el EVA en base Capital Empleado (definición DAX aprobada) es **negativo** en todo el período → la rentabilidad sobre el capital materialmente invertido es apenas marginal. |
| **Rentabilidad** | Pico 2021, **deterioro severo 2023–2024** (EBITDA −27,4 % y −31,1 %; margen EBITDA de 53,6 % a 23,9 %), recuperación parcial 2025 (EBITDA +32,4 %). |
| **Liquidez** | Holgura alta y constante: razón corriente **6,5× a 9,3×**; efectivo neto entre **20,6 y 47,1 M$**; sin inventarios (prueba ácida = razón corriente). |
| **Solvencia** | Endeudamiento total **17,3 % a 21,9 %**; deuda financiera únicamente **derechos de uso (5,3–9,7 M$)**; solvencia total 4,6–5,8×; posición **neta de caja** durante todo el período. |
| **Riesgos / alertas** | Calidad de resultados en negativo (FCO/UN **−0,35 y −0,48** en 2024–2025); cuentas por cobrar **+2,11× en 2025** frente a ingresos +15 %; utilidad neta **−70 % en 2024**; opinión de auditoría **con salvedad desde 2023**; hallazgo **i_ori_inmuebles 2022 (2.465 vs 11.751)** pendiente de pronunciamiento. |
| **Continuidad** | Sin indicios de duda material sobre negocio en marcha: solvencia y liquidez muy superiores a umbrales; riesgo principal es **eficiencia del capital** y **conversión de utilidades en caja**. |

**Conclusión de una frase:** entidad financieramente estable y solvente que **depende de inversiones valoradas a valor razonable**, cuya eficiencia de capital es **marginal** (spread ROIC−WACC delgado y EVA negativo) y que muestra **deterioro reciente de la calidad de caja** que exige seguimiento.

---

## 2. ANÁLISIS DE CREACIÓN DE VALOR (ROIC vs WACC y EVA)

### 2.1 Spread de rentabilidad (ROIC − WACC)

| Período | ROIC (id 34) | WACC (Fase 7) | **Spread (ROIC−WACC)** |
|---|---|---|---|
| 2021 | 0,7691 | 0,7503 | **+0,0188** |
| 2022 | 0,6970 | 0,6826 | **+0,0144** |
| 2023 | 0,3368 | 0,3312 | **+0,0057** |
| 2024 | 0,2236 | 0,2201 | **+0,0035** |
| 2025 | 0,3656 | 0,3603 | **+0,0053** |

- El spread es **positivo en todos los años**, pero **se estrecha** de +1,88 pp (2021) a solo +0,35–0,57 pp (2023–2025): la rentabilidad sobre capital generada por la operación apenas supera el costo de capital.
- El spread positivo está íntimamente ligado a la definición metodológica Ke = ROIC (Fases 7 y 9 aprobadas): el costo patrimonial se iguala internamente al rendimiento operativo, lo que **comprime estructuralmente** el spread. Lectura: **la operación no crea margen de valor sustancial sobre su costo de oportunidad.**

### 2.2 Dinámica del NOPAT

NOPAT estatutario = EBIT × (1 − tasa Art. 240) (2021: 31 %; 2022–2025: 35 % — ver bitácora §3):

| Período | EBIT (id 25) | NOPAT estatutario | Variación NOPAT |
|---|---|---|---|
| 2021 | 94.982 | **65.537,6** | — |
| 2022 | 92.975 | **60.433,8** | −7,8 % |
| 2023 | 68.527 | **44.542,6** | −26,3 % |
| 2024 | 39.454 | **25.645,1** | −42,4 % |
| 2025 | 55.943 | **36.363,0** | +41,8 % |

- El **EBIT cae 58,5 %** entre 2021 (94.982) y 2024 (39.454), arrastrando al NOPAT antes de la recuperación de 2025 (+41,8 %).
- Causas de la caída: incremento de **gastos de administración** (67.724 → 129.257 entre 2021 y 2024) y **beneficios a empleados** (29.709 → 47.165), que presionaron el resultado operativo pese al crecimiento de ingresos.
- El margen operativo (id 27) pasó de **0,465 (2021)** a **0,215 (2025)**, con mínimo de **0,174 en 2024**.

### 2.3 Evolución del EVA

EVA (definición DAX aprobada) = NOPAT − (WACC × Capital Empleado), con **Capital Empleado = deuda financiera + patrimonio**:

| Período | NOPAT | WACC × Capital Empleado | **EVA** |
|---|---|---|---|
| 2021 | 65.537,6 | 0,750317 × 290.655 = 218.083,4 | **−152.545,8** |
| 2022 | 60.433,8 | 0,682552 × 269.532 = 183.969,6 | **−123.535,9** |
| 2023 | 44.542,6 | 0,331181 × 299.980 = 99.347,7 | **−54.805,1** |
| 2024 | 25.645,1 | 0,220066 × 260.974 = 57.431,5 | **−31.786,4** |
| 2025 | 36.363,0 | 0,360281 × 293.140 = 105.612,8 | **−69.249,8** |

**Lectura crítica (debe leerse con la nota metodológica):**
- El EVA es **negativo en los cinco años**: el NOPAT generado no alcanza a cubrir el costo total del capital empleado (deuda + patrimonio ≈ 260–300 M$).
- Esto es coherente con un spread ROIC−WACC **positivo pero delgado**: la base de capital empleado (que incluye todo el patrimonio, ≈ 260–295 M$) es **mucho mayor** que la base de capital invertido (capital suscrito + obligaciones, ≈ 78 M$) sobre la que se calcula el ROIC.
- **Señal de alerta de eficiencia:** la entidad sostiene un gran monto de patrimonio con rentabilidad operativa baja por unidad de capital, lo que **destruye valor en términos absolutos** (EVA < 0) aunque el ROIC supere marginalmente al WACC.
- RONA (id 35, base capital empleado): **0,209 → 0,196 → 0,093 → 0,062 → 0,103** (2021→2025): confirma que la rentabilidad sobre el capital amplio es baja (6–21 %).

---

## 3. ANÁLISIS DE LIQUIDEZ, EFECTIVO Y CAPITAL DE TRABAJO

### 3.1 Ratios de liquidez

| Período | Razón corriente (id 1) | Prueba ácida (id 2) | Razón de efectivo (id 3) | Capital de trabajo neto (id 4) |
|---|---|---|---|---|
| 2020 | 8,69 | 8,69 | 1,20 | 281.459 |
| 2021 | 7,58 | 7,58 | 0,51 | 271.188 |
| 2022 | 6,86 | 6,86 | 0,48 | 252.853 |
| 2023 | 6,51 | 6,51 | 0,52 | 288.395 |
| 2024 | 8,92 | 8,92 | 1,53 | 243.243 |
| 2025 | 9,26 | 9,26 | 1,41 | 268.659 |

- **Nota (no es anomalía):** la entidad no maneja inventarios (activity ids 19–22 sin dato; margen bruto id 26 = 1,0 porque la "utilidad bruta" es el total de ingresos). Por ello **prueba ácida ≡ razón corriente**.
- Nivel de liquidez **sobradamente cubierto**: incluso la razón de efectivo mínima (0,48 en 2022) cubre la mitad del pasivo corriente.
- El **efectivo** (b_efectivo) evoluciona 43.925 → 20.991 → 20.559 → 27.333 → 47.069 → 46.020 M$; mínimos transitorios de ~21–27 M$ en 2021–2023 por pago de dividendos y mantenimiento de inversiones.

### 3.2 Ciclo operativo y capital de trabajo

- Días de inventario / ciclo operativo: **NO_CALCULABLE** (sin inventarios — id 19–22, 36–37 vacíos). Ausencia coherente.
- **Período medio de cobro (id 18):** 77,0 → 84,9 → 82,7 → 55,5 → 55,4 días (2021→2025); **mejoría ~29 días** desde 2022 gracias a mayor rotación de cartera (id 17: 4,30 → 6,59 veces).
  - ⚠️ **Excepción:** la rotación de CxC **empeora en 2025 con variación de +2,11×** (id 42) — ver alerta 5.3.
- Necesidad de capital de trabajo (id 38): 54.602 → 33.754 → 49.391 → 35.341 → 51.666 → 80.770 M$.
- Capital de trabajo / Ingresos (id 39): 1,43 → 1,03 (drenaje de 0,4 p.p. a favor de eficiencia), rotación del capital de trabajo (id 23) sube de 0,74 a 1,02.

### 3.3 Calidad de utilidades (FCO vs utilidad neta)

| Período | FCO estado de flujos (c_flujo_operacion) | Utilidad neta | **FCO / UN (id 62)** |
|---|---|---|---|
| 2020 | 64.532 | 58.220 | **1,108** |
| 2021 | 63.425 | 47.632 | **1,332** |
| 2022 | 46.077 | 36.237 | **1,272** |
| 2023 | 46.437 | 70.126 | **0,662** |
| 2024 | −7.419 | 20.997 | **−0,353** |
| 2025 | −14.903 | 30.947 | **−0,482** |

- **Deterioro crítico 2024–2025:** el flujo de caja operativo del estado de flujos se torna **negativo** (−7.419 y −14.903 M$) mientras la utilidad neta sigue positiva → las utilidades de esos dos años **no se están convirtiendo en caja**.
- El motor (id 50, "Flujo de caja operativo" = EBITDA − impuesto + variación CT) sigue siendo positivo (48.620 y 73.394), pero el **flujo del estado de flujos** —más fiel a la realidad de caja— se deteriora, señal de **crecimiento del capital de trabajo mediante cartera y otros activos corrientes** (ver alza de NCT a 80.770 en 2025 y variación CxC +2,11×).
- **Interpretación:** la calidad de las utilidades de 2024–2025 es la **principal bandera roja** del período.

---

## 4. ANÁLISIS DE ESTRUCTURA DE DEUDA Y SOLVENCIA

### 4.1 Nivel de endeudamiento

| Período | Endeudamiento total (id 6) | Endeudamiento patrimonial (id 7) | Autonomía (id 10) | Solvencia total (id 13) |
|---|---|---|---|---|
| 2020 | 0,184 | 0,225 | 0,816 | 5,44 |
| 2021 | 0,188 | 0,231 | 0,812 | 5,33 |
| 2022 | 0,214 | 0,272 | 0,786 | 4,68 |
| 2023 | 0,219 | 0,280 | 0,781 | 4,57 |
| 2024 | 0,191 | 0,236 | 0,809 | 5,24 |
| 2025 | 0,173 | 0,209 | 0,827 | 5,77 |

- **Perfil conservador:** los pasivos nunca superan el **22 %** de los activos; el patrimonio (293,0 → 287,8 M$) financia ~78–83 % del activo.
- La calidad de la deuda (id 12) oscila entre 0,51 y 0,64 (mitad corriente), con pasivos mayormente operativos: cuentas por pagar (18–35 M$), provisiones (13–24 M$), beneficios a empleados y pasivos fiscales.

### 4.2 Cobertura de intereses y perfil de vencimientos

| Período | Deuda financiera efectiva (id 54) | Cobertura intereses (id 40) | Cobertura EBITDA (id 41) | Deuda fin/EBITDA (id 55) | Deuda neta/EBITDA (id 56) | ICSD (id 53) |
|---|---|---|---|---|---|---|
| 2020 | 9.689 | 92,9 | 107,9 | 0,097 | −0,342 | — |
| 2021 | 7.767 | 127,3 | 146,8 | 0,071 | −0,121 | 34,3 |
| 2022 | 6.207 | 138,8 | 162,1 | 0,057 | −0,132 | 43,6 |
| 2023 | 6.331 | 102,7 | 118,2 | 0,080 | −0,266 | 8,2 |
| 2024 | 6.117 | 56,8 | 78,1 | 0,113 | −0,755 | 19,8 |
| 2025 | 5.306 | 96,8 | 124,3 | 0,074 | −0,567 | 25,7 |

- **La única deuda financiera es el derecho de uso (arrendamientos):** 9.689 → 5.306 M$, decreciente; no hay pasivos bancarios ni emisiones.
- **Coberturas muy altas:** el EBIT cubre los intereses entre **57 y 139 veces**; incluso en el peor año (2024, 56,8×) el margen de seguridad es amplísimo.
- **Deuda neta negativa** en todo el período (el efectivo supera la deuda): posición **neta de caja** permanente.
- Servicio de la deuda (id 52): 2.151 → 2.724 M$; ICSD mínimo de **8,2× en 2023** (mayor necesidad de caja previa a la recuperación) y 25,7× en 2025.
- **Riesgo crediticio: BAJO.** Perfil de vencimientos sin concentración de deuda financiera; el riesgo principal es **operativo/cualitativo**, no estructural.

---

## 5. MATRIZ DE ALERTAS TEMPRANAS (RED FLAGS) Y SALVEDADES

### 5.1 Matriz consolidada de alertas

| # | Alerta | Período | Evidencia (matriz) | Severidad | Estado |
|---|---|---|---|---|---|
| 1 | **i_ori_inmuebles: consolidado 2.465 vs Nota 25 11.751** | 2022 | `bitacora §1`, Fase 8 | **ALTA (trazabilidad)** | **DUDOSO — requiere pronunciamiento humano** |
| 2 | **Calidad de resultados FCO/UN < 0** | 2024–2025 | id 62: −0,353 / −0,482 | ALTA | Activa |
| 3 | **Variación CxC +2,11× frente a ingresos +15 %** | 2025 | id 42: 2,1109; id 57: 0,1502 | MEDIA-ALTA | Activa |
| 4 | **Caída de utilidad neta −70 %** | 2024 | id 60: −0,7006 | MEDIA | Punto 2024; rebote 2025 (+47,4 %) |
| 5 | **Opinión de auditoría con salvedad desde 2023** | 2023–2025 | `bitacora §5.1` | MEDIA (lectura de estados) | Pendiente análisis |
| 6 | **Deterioro de margen operativo** (0,465 → 0,174 → 0,215) | 2021→2024→2025 | id 27 | MEDIA | En recuperación |
| 7 | **EVA negativo sistemático** | 2021–2025 | Sección 2.3 | MEDIA-ALTA (eficiencia) | Estructural |
| 8 | **EBITDA negativo en crecimiento** (−27,4 % y −31,1 %) | 2023–2024 | id 58 | MEDIA | Rebote 2025 (+32,4 %) |

### 5.2 Hallazgo formal de auditoría lógica — i_ori_inmuebles 2022 (Protocolo Pasos B/C)

- **Dato:** valor consolidado **$2.465** vs Nota 25 del estado financiero **$11.751** (revalorización de bienes inmuebles).
- **Origen:** Fase 8 lo clasificó `NO_ENCONTRADO con valor` (sin match textual en el segmento RESULTADO), elevado a `DUDOSO` en la bitácora por posible compromiso de trazabilidad del ORI.
- **Decisión aplicada (no se interpola ni corrige):** se mantiene el valor consolidado **2.465**; **se solicita pronunciamiento humano** para determinar si procede ajuste, reclasificación o marcación NO_ENCONTRADO. **Impacto moderado:** este concepto no participa en ROIC/EBIT/NOPAT/WACC (se excluyen ORI), por lo que **los indicadores de valor quedan inalterados**; el ORI total (i_ori_total = 1.072 en 2022) sí alimenta el resultado integral total.

### 5.3 Divergencias tributarias (bitácora §2 §3)

- Se combinan **tasa efectiva** (impuesto corriente / EBIT) para el desempeño operativo real (UODI) y **tasa estatutaria Art. 240 E.T.** (2020: 32 %, 2021: 31 %, 2022+: 35 %) como parámetro de comparación y escudo fiscal del WACC.
- **Tasa 2022 = 35 % CONFIRMADA** como correcta (Ley 2155 de 2021) por la revisión humana; la Fase 9 registró el DUDOSO metodológico `T_ART240(2022)=0,30 vs 0,35` únicamente con carácter documental.
- Las diferencias ROIC_estatutario vs ROIC_efectivo (Fase 9, grupo J, DUDOSO 2021–2025) son **de naturaleza metodológica, no de error de datos**.

### 5.4 Integridad del pipeline (respaldos)

- **Fase 8 Evidencia Formal:** 486 ACEPTADO / 36 NO_ENCONTRADO / 0 DUDOSO (522 registros, 87 conceptos × 6 años).
- **Fase 9 Validación Transversal:** 74 ACEPTADO / 0 DESCUDRE / 11 DUDOSO (todos metodológicos: J_NOPAT_Art240, J_RONA, K_WACC) / 4 NO_ENCONTRADO (2020 sin t−1). **Integridad 100 %.**

---

## 6. DICTAMEN DE SOSTENIBILIDAD Y CONTINUIDAD DEL NEGOCIO (HIPÓTESIS DE NEGOCIO EN MARCHA)

**Veredicto: hipótesis de negocio en marcha VÁLIDA sin indicios de duda material.**

Fundamentos positivos:
1. **Solvencia estructural sólida:** solvencia 4,6–5,8×, endeudamiento ≤22 %, autonomía ≥78 %, posición neta de caja permanente.
2. **Coberturas de interés excepcionales** (57–139×); sin deuda bancaria concentrada.
3. **Liquidez holgada y creciente:** capital de trabajo 243–288 M$, razón corriente 6,5–9,3×; caja acumulada 46 M$ en 2025.
4. **Recuperación 2025:** EBITDA +32,4 %, ingestos +15,0 %, margen operativo 0,174 → 0,215.

Riesgos que exigen seguimiento (sin comprometer la continuidad):
1. **Eficiencia del capital:** spread ROIC−WACC delgado y EVA<0: el patrimonio (≈ 288 M$) no genera rendimiento proporcional al capital comprometido; la sostenibilidad de largo plazo dependerá de **mejorar la rentabilidad operativa sobre el capital empleado** (RONA 0,062 → 0,103).
2. **Conversión de caja 2024–2025:** FCO negativo dos años consecutivos por crecimiento de cartera y otros activos corrientes; si persiste, limitará la capacidad de pago de dividendos y mantenimiento de inversiones.
3. **Concentración en inversiones a valor razonable** (b_inversiones ≈ 172–266 M$, ~52–78 % del activo): vulnerabilidad a la valoración de mercado.
4. **Salvedad de auditoría desde 2023** y hallazgo i_ori_inmuebles 2022 (pendientes de pronunciamiento).

**Lectura de futuro (proyección direccional, sin invención de valores):** la estabilidad patrimonial y la liquidez garantizan la continuidad operativa en el mediano plazo; el desafío estratégico es **cerrar la brecha de eficiencia** (spread y EVA) y **restaurar la conversión de utilidades en caja**, condiciones necesarias para sostener la creación de valor en el siguiente ciclo.

---

## 7. CONSISTENCIA DE CIFRAS

Todas las cifras del presente reporte provienen de fuentes auditadas, sin interpolación:

| Referencia del reporte | Fuente (matriz) |
|---|---|
| ROIC, RONA, ROE, margen neto/operativo/EBITDA | `salidas\indicadores.csv`, ids 27, 28, 30, 32, 34, 35 |
| WACC, capital empleado, tasas | `salidas\fase7_wacc_roi\wacc_roi_2020_2025.csv` (ke=ROIC, kd=|intereses|/deuda) |
| NOPAT (EBIT × (1−tasa)) | `indicadores.csv` id 25 × tasa Art. 240 (bitácora §3) |
| EVA = NOPAT − WACC×CE | Derivación definida en `GUIA_IMPLEMENTACION_POWER_BI.md` §2.4 |
| Liquidez, capital de trabajo, PDM, rotaciones | `indicadores.csv` ids 1–5, 17, 18, 23, 38, 39 |
| FCO, calidad de resultados | `indicadores.csv` id 50/62 y `datos_estados_financieros.csv` (c_flujo_operacion) |
| Endeudamiento, solvencia, coberturas, ICSD, deuda | `indicadores.csv` ids 6, 7, 10, 12, 13, 40, 41, 52–56 |
| Alertas y salvedades | `bitacora_revisiones_humanas.md` §§1–5 |
| Integridad/validación | `fase9_validacion_transversal\matriz_consistencia_transversal.csv` + `resumen_validacion_transversal.json` |
| Evidencia formal | `fase8_evidencia_formal\evidencia_formal_conceptos.csv` |

**Regla aplicada:** consistencia contable `ACTIVO = PASIVO + PATRIMONIO` verificada por la Fase 9 (ACEPTADO en los 6 años). El hallazgo i_ori_inmuebles 2022 (sección 5.2) se reporta con su estado **DUDOSO** sin que afecte indicadores centrales de valor.

---

## 8. MATRIZ COMPLETA DE LOS 65 INDICADORES POR FAMILIA Y PERÍODO (2020–2025)

Catálogo completo (65 indicadores) agrupado por familia y ordenado del período más antiguo (2020) al más reciente (2025). Los 7 indicadores sin base de cálculo (inventarios y ciclos operativos: ids 19–22, 36–37, 43) figuran como «—». Fuente: `salidas\indicadores.csv`.

### Liquidez

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 1 | Razon corriente | 8,685 | 7,579 | 6,858 | 6,509 | 8,923 | 9,260 |
| 2 | Prueba acida | 8,685 | 7,579 | 6,858 | 6,509 | 8,923 | 9,260 |
| 3 | Razon de efectivo | 1,199 | 0,509 | 0,476 | 0,522 | 1,533 | 1,415 |
| 4 | Capital de trabajo neto | 281.459 | 271.188 | 252.853 | 288.395 | 243.243 | 268.659 |
| 5 | Capital de trabajo / Activos | 0,784 | 0,779 | 0,755 | 0,767 | 0,772 | 0,772 |

### Endeudamiento y solvencia

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 6 | Endeudamiento total | 0,184 | 0,188 | 0,214 | 0,219 | 0,191 | 0,173 |
| 7 | Endeudamiento patrimonial | 0,225 | 0,231 | 0,272 | 0,280 | 0,236 | 0,209 |
| 8 | Deuda financiera / Activos | 0,027 | 0,022 | 0,019 | 0,017 | 0,019 | 0,015 |
| 9 | Deuda financiera / Patrimonio | 0,033 | 0,027 | 0,024 | 0,022 | 0,024 | 0,018 |
| 10 | Autonomia financiera | 0,816 | 0,812 | 0,786 | 0,781 | 0,809 | 0,827 |
| 11 | Apalancamiento financiero | 1,225 | 1,231 | 1,272 | 1,280 | 1,236 | 1,209 |
| 12 | Calidad de la deuda | 0,555 | 0,630 | 0,604 | 0,636 | 0,511 | 0,539 |
| 13 | Solvencia total | 5,439 | 5,326 | 4,683 | 4,567 | 5,240 | 5,774 |
| 14 | Pasivo / Capital | 0,184 | 0,188 | 0,214 | 0,219 | 0,191 | 0,173 |

### Actividad y eficiencia

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 15 | Rotacion de activos totales | — | 0,578 | 0,644 | 0,622 | 0,656 | 0,787 |
| 16 | Rotacion de activos fijos | — | 5,319 | 5,891 | 5,968 | 5,947 | 5,930 |
| 17 | Rotacion de cuentas por cobrar | — | 4,743 | 4,300 | 4,414 | 6,578 | 6,593 |
| 18 | Periodo medio de cobro | — | 76,959 | 84,883 | 82,696 | 55,484 | 55,361 |
| 19 | Rotacion de inventarios | — | — | — | — | — | — |
| 20 | Dias de inventario | — | — | — | — | — | — |
| 21 | Rotacion de cuentas por pagar | — | — | — | — | — | — |
| 22 | Periodo medio de pago | — | — | — | — | — | — |
| 23 | Rotacion del capital de trabajo | — | 0,739 | 0,840 | 0,816 | 0,853 | 1,019 |
| 24 | EBITDA | 100.136 | 109.478 | 108.605 | 78.821 | 54.269 | 71.835 |

### Rentabilidad

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 25 | Resultado operativo antes de intereses e impuestos (EBIT) | 86.251 | 94.982 | 92.975 | 68.527 | 39.454 | 55.943 |
| 26 | Margen bruto | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 | 1,000 |
| 27 | Margen operativo | 0,438 | 0,465 | 0,423 | 0,310 | 0,174 | 0,215 |
| 28 | Margen EBITDA | 0,509 | 0,536 | 0,494 | 0,357 | 0,239 | 0,275 |
| 29 | Margen antes de impuestos | 0,458 | 0,353 | 0,296 | 0,536 | 0,161 | 0,223 |
| 30 | Margen neto | 0,296 | 0,233 | 0,165 | 0,317 | 0,093 | 0,119 |
| 31 | ROA | — | 0,135 | 0,106 | 0,197 | 0,061 | 0,093 |
| 32 | ROE | — | 0,165 | 0,133 | 0,252 | 0,077 | 0,114 |
| 33 | Capital invertido | 81.649 | 79.727 | 78.167 | 78.291 | 78.077 | 77.266 |
| 34 | ROIC | — | 0,769 | 0,697 | 0,337 | 0,224 | 0,366 |
| 35 | Rendimiento sobre capital total | — | 0,209 | 0,196 | 0,093 | 0,062 | 0,102 |

### Capital de trabajo y ciclo

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 36 | Ciclo operativo | — | — | — | — | — | — |
| 37 | Ciclo de conversion de efectivo | — | — | — | — | — | — |
| 38 | Necesidad de capital de trabajo | 54.602 | 33.754 | 49.391 | 35.341 | 51.666 | 80.770 |
| 39 | Capital de trabajo / Ingresos Operacionales | 1,430 | 1,328 | 1,149 | 1,305 | 1,073 | 1,030 |

### Cobertura y capacidad de pago

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 40 | Cobertura de intereses | 92,94 | 127,32 | 138,77 | 102,74 | 56,77 | 96,79 |
| 41 | Cobertura de intereses EBITDA | 107,91 | 146,75 | 162,10 | 118,17 | 78,08 | 124,28 |
| 42 | Variacion de cuentas por cobrar | — | 1,130 | 1,239 | 0,768 | 0,585 | 2,111 |
| 43 | Variacion inventarios | — | — | — | — | — | — |
| 44 | Variacion de cuentas por pagar | — | 1,137 | 0,850 | 1,278 | 0,605 | 0,856 |
| 45 | Variacion de otros activos corrientes operativos | — | 1,591 | 1,180 | 1,247 | 1,154 | 1,075 |
| 46 | Variacion de otros pasivos corrientes operativos | — | 1,105 | 1,057 | 1,248 | 0,962 | 1,344 |
| 47 | Variacion Propiedades, planta y equipo | — | 0,923 | 1,115 | 1,000 | 0,974 | 1,234 |
| 48 | Variacion Activos intangibles | — | 0,803 | 0,563 | 1,396 | 1,012 | 0,999 |
| 49 | Variacion Otros activos no corrientes operativos | — | 0,784 | 0,640 | 1,225 | 0,997 | 0,948 |
| 50 | Flujo de caja operativo | 72.603 | 55.705 | 86.292 | 22.595 | 48.620 | 73.394 |
| 51 | Flujo de caja disponible para deuda | — | 64.941 | 96.049 | 17.387 | 49.036 | 70.010 |
| 52 | Servicio de la deuda | 2.151 | 1.892 | 2.205 | 2.130 | 2.478 | 2.724 |
| 53 | Indice de Cobertura del Servicio de la Deuda | — | 34,32 | 43,56 | 8,16 | 19,79 | 25,70 |
| 54 | Deuda financiera | 9.689 | 7.767 | 6.207 | 6.331 | 6.117 | 5.306 |
| 55 | Deuda financiera / EBITDA | 0,10 | 0,07 | 0,06 | 0,08 | 0,11 | 0,07 |
| 56 | Deuda financiera neta / EBITDA | -0,34 | -0,12 | -0,13 | -0,27 | -0,75 | -0,57 |

### Crecimiento

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 57 | Crecimiento de ingresos | — | 0,038 | 0,077 | 0,004 | 0,026 | 0,150 |
| 58 | Crecimiento del EBITDA | — | 0,093 | -0,008 | -0,274 | -0,311 | 0,324 |
| 59 | Crecimiento del resultado operativo | — | 0,101 | -0,021 | -0,263 | -0,424 | 0,418 |
| 60 | Crecimiento de utilidad neta | — | -0,182 | -0,239 | 0,935 | -0,701 | 0,474 |
| 61 | Crecimiento de activos | — | -0,030 | -0,039 | 0,123 | -0,162 | 0,105 |

### Calidad de resultados

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 62 | Calidad de resultados | 1,108 | 1,332 | 1,272 | 0,662 | -0,353 | -0,482 |
| 63 | Rotacion de activos | 0,548 | 0,586 | 0,657 | 0,588 | 0,720 | 0,749 |
| 64 | Multiplicador de capital | — | 1,228 | 1,251 | 1,276 | 1,260 | 1,222 |

### Creacion de valor y DuPont

| # | Indicador | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| 65 | ROE DuPont | — | 0,168 | 0,135 | 0,238 | 0,084 | 0,109 |

---

*Fin del reporte. Cifras en millones de pesos (M$); ratios en unidades adimensionales. Trazabilidad completa en `salidas\`.*