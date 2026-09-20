# BITÁCORA DE REVISIONES HUMANAS

**Propósito:** consolidar los puntos atípicos detectados por el pipeline (consolidado, evidencia formal y validación transversal) que requieren revisión cualitativa humana antes de su incorporación definitiva en las capas finales (Tableros / Power BI / Reportes de Inteligencia Financiera).

**Regla:** todo hallazgo aquí NO se corrige en la taxonomía ni en el código sin decisión explícita de la revisión humana. Se registra con trazabilidad `documento → entidad → período → dato → variable_madre → fuente → evidencia → validación → indicador`.

Creada: 2026-09-19 (cierre Fases 8/9).

---

## 1. HALLAZGO: `i_ori_inmuebles` 2022 — desfase consolidado vs Nota 25

| Atributo | Detalle |
|---|---|
| Concepto | `i_ori_inmuebles` (ORI — bienes inmuebles, estado de resultados integral) |
| Período | 2022 |
| Valor consolidado | **$2.465** |
| Valor Nota 25 (estados financieros) | **$11.751** |
| Evidencia | `salidas\datos_estados_financieros.csv` (i_ori_inmuebles 2022 = 2465.0); Nota 25 del estado financiero 2022 (revalorización de bienes inmuebles) |
| Módulo de detección | Fase 8 Evidencia Formal — `NO_ENCONTRADO` con valor (nativo en consolidado, sin match textual en segmento RESULTADO) |
| Estado de validación | `DUDOSO` |
| Protocolo aplicado | Paso B (evaluación: podría comprometer trazabilidad de ORI) → Paso C (ambigüedad; requiere intervención humana) |

**Contexto:** el importe de la Nota 25 ($11.751) no coincide con el valor consolidado del concepto ORI inmuebles 2022 ($2.465). El dato no se interpola ni se corrige automáticamente: la revisión humana debe determinar la procedencia (¿reclasificación, entidad cabe, medición a valor razonable parcial?). Registrado 2026-09-19.

**Acción solicitada a revisión humana:** confirmar origen del desfase y emitir pronunciamiento (aceptar consolidado / ajustar con evidencia / marcar NO_ENCONTRADO).

---

## 2. DIVERGENCIA METODOLÓGICA: tasa efectiva vs tasa estatutaria (ROIC/NOPAT)

| Atributo | Detalle |
|---|---|
| Indicadores | id 34 ROIC; id 35 RONA (Rendimiento sobre capital total); UODI/NOPAT |
| Fuente | `src\indicadores.py` (`_ebit_op_total`) |
| Práctica implementada | **Tasa efectiva** = impuesto corriente / EBIT → UODI para el desempeño operativo real |
| Tasa estatutaria | Art. 240 E.T. (2020: 32 %, 2021: 31 %, 2022+: 35 %) — paramétrica, registrada como **parámetro de comparación** |
| Estado | Resuelto como **decisión documental 2026-09-19** (ver `03_INDICADORES.md` §2.4, Evento 15): NO se cambia la metodología efectiva; la estatutaria se registra como comparación |
| Repercute en | WACC (id Ke = ROIC; escudo fiscal con tasa estatutaria según `fase7_wacc_roi.py`) |

**Acción solicitada a revisión humana:** validar la coexistencia (tasa efectiva para desempeño, estatutaria para escudo fiscal) o instruir cambio de base. Sin acción pendiente de corrección inmediata.

---

## 3. TASA ESTATUTARIA 2022 = 35 % (confirmación)

| Atributo | Detalle |
|---|---|
| Período | 2022 |
| Base legal invocada | Ley 2155 de 2021 (Art. 240 E.T.), tarifa personas jurídicas 35 % |
| Uso | Escudo fiscal WACC (`fase7_wacc_roi.py`, `T_ESTATUTARIA`); metadato `03_INDICADORES.md` §2.9 |
| Estado | **CONFIRMADO por la revisión humana (2026-09-19)** — se mantiene en la taxonomía; no se modifica |

**Nota:** la validación transversal (Fase 9) reportó como DUDOSO la comparación T_ART240(2022)=0.30 vs T_FASE7=0.35; la revisión humana resolvió que **35 % es la tasa correcta vigente para el período 2022**. Registrado únicamente con carácter documental.

---

## 4. AUSENCIAS COHERENTES (NO_ENCONTRADO sin valor) — sin acción pendiente

Conceptos sin línea en el estado financiero y cuyo valor consolidado queda vacío (ausencia coherente, no datos perdidos):

- `b_impuesto_corriente_activo` 2022, 2023
- `b_impuesto_corriente_pasivo` 2025
- `b_impuesto_diferido_pasivo` 2023, 2024, 2025
- `i_ori_inmuebles` 2020, 2021, 2023, 2024
- `c_baja_amortizacion_intangibles` 2020–2024

**Estado de validación:** NO_ENCONTRADO (ausencia coherente). Se mantienen vacíos según regla de no interpolación.

---

## 5. OBSERVACIONES CUALITATIVAS PENDIENTES (heredadas de Fase 5/6)

Señales detectadas por el screening de red flags, pendientes de análisis humano:

1. Opiniones de auditoría **con salvedad desde 2023** (impacto en lectura de estados).
2. Calidad de resultados: FCO/UN **< 0 en 2024 y 2025** (−0,35 y −0,48).
3. Variación de CxC **+2,11× en 2025** frente a ingresos +15 %.
4. Utilidad neta 2024 **−70 %** vs 2023.

Detalle completo: `salidas\diagnostico_red_flags.{json,csv,md}` y `salidas\informe_financiero_interactivo.html`.

---

## 6. ESTADO GENERAL DE LA REVISIÓN Y PRÓXIMOS PASOS

| Ítem | Fecha | Estado |
|---|---|---|
| Fase 8 — Evidencia Formal (486 ACEPTADO / 36 NO_ENCONTRADO / 0 DUDOSO) | 2026-09-19 | **CERRADA y aprobada** |
| Fase 9 — Validación Transversal (100 % integridad; DUDOSO metodológicos) | 2026-09-19 | **CERRADA** (resoluciones en §2/§3) |
| Hallazgo i_ori_inmuebles 2022 (§1) | 2026-09-19 | **Pendiente de pronunciamiento humano** |
| Observaciones cualitativas (§5) | 2026-09-19 | Pendientes de análisis humano |

**Siguiente capítulo (con OK explícito de Big Pickle):** capas finales — Tableros / Power BI / Reportes de Inteligencia Financiera.