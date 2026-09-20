# DIAGNÓSTICO DE RED FLAGS / ALERTAS TEMPRANAS (Fase 5)

Fuente: `salidas/indicadores.csv` (65 indicadores, 2020-2025) + lotes de extracción revisados.
Metodología: screening determinístico con umbrales documentados por indicador. Resultados: SEÑAL_ALERTA / OBSERVACION / OK / NO_ENCONTRADO / NO_APLICA_TIPO_ENTIDAD. Este diagnóstico **no** emite juicios de fraude; solo selecciona señales de alerta para revisión.

> **Alerta clave:** opiniones con salvedad en 2023, 2024 y 2025. Las salvedades requieren análisis de impacto en los estados (registradas en el lote de trazabilidad).

## Resumen por año

| Año | Señal alerta | Observación | OK | No encontrado | No aplica | Total |
|---|--:|--:|--:|--:|--:|--:|
| 2020 | 0 | 0 | 34 | 25 | 8 | 67 |
| 2021 | 0 | 0 | 59 | 0 | 8 | 67 |
| 2022 | 0 | 0 | 60 | 0 | 8 | 68 |
| 2023 | 2 | 3 | 55 | 0 | 8 | 68 |
| 2024 | 6 | 0 | 54 | 0 | 8 | 68 |
| 2025 | 4 | 0 | 56 | 0 | 8 | 68 |

## Resumen por clasificación

| Clasificación | Señal alerta | Observación | OK | No encontrado | No aplica |
|---|--:|--:|--:|--:|--:|
| Actividad y eficiencia | 0 | 0 | 31 | 5 | 24 |
| Calidad de resultados | 2 | 1 | 14 | 1 | 0 |
| Capital de trabajo y ciclo | 0 | 0 | 12 | 0 | 12 |
| Cobertura y capacidad de pago | 1 | 0 | 86 | 9 | 6 |
| Creacion de valor y DuPont | 0 | 0 | 5 | 1 | 0 |
| Crecimiento | 3 | 2 | 20 | 5 | 0 |
| Cualitativo (auditoría) | 6 | 0 | 10 | 0 | 0 |
| Endeudamiento y solvencia | 0 | 0 | 54 | 0 | 0 |
| Liquidez | 0 | 0 | 24 | 0 | 6 |
| Rentabilidad | 0 | 0 | 62 | 4 | 0 |

## Señales de alerta encontradas (SEÑAL_ALERTA)

| Año | # | Indicador | Clasificación | Motivo | Fuente de la regla |
|---|--:|---|--:|---|---|
| 2023 | 0 | tipo_opinion | Cualitativo (auditoría) | Opinión modificada: con_salvedad. Informe de auditoría 2023, pág 15, 'Fundamento de la conclusión con salvedad' (validado). | Lotes de extracción revisados y validados por año. |
| 2023 | 0 | salvedades | Cualitativo (auditoría) | Sí: salvedad en informe auditoría 2023 (pág 15). Requiere análisis de impacto.. Conclusión con salvedad 2023; impacto en estados a auditar. | Lotes de extracción revisados y validados por año. |
| 2024 | 0 | tipo_opinion | Cualitativo (auditoría) | Opinión modificada: con_salvedad. Informe de auditoría 2024, pág 13, 'Conclusión con salvedad' (validado). | Lotes de extracción revisados y validados por año. |
| 2024 | 0 | salvedades | Cualitativo (auditoría) | Sí: salvedad en informe auditoría 2024 (pág 13). Requiere análisis de impacto.. Conclusión con salvedad 2024. | Lotes de extracción revisados y validados por año. |
| 2024 | 58 | Crecimiento del EBITDA | Crecimiento | Crecimiento del EBITDA. Valor -0.311491 < umbral de alerta -0.3. | Caída del EBITDA > 20% vigila. |
| 2024 | 59 | Crecimiento del resultado operativo | Crecimiento | Crecimiento del resultado operativo. Valor -0.424256 < umbral de alerta -0.3. | Caída del RO > 20% vigila. |
| 2024 | 60 | Crecimiento de utilidad neta | Crecimiento | Crecimiento de la utilidad neta. Valor -0.700582 < umbral de alerta -0.5. | Caída de utilidad neta > 30% vigila; > 50% señal. |
| 2024 | 62 | Calidad de resultados | Calidad de resultados | Calidad de resultados (FCO utilidad neta). Valor -0.353336 < umbral de alerta 0. | FCO menor que utilidad: diferencia entre beneficio y caja generada. < 0,7 vigila; < 0 (FCO negativo con utilidad positiva) señal fuerte. |
| 2025 | 0 | tipo_opinion | Cualitativo (auditoría) | Opinión modificada: con_salvedad. Informe de auditoría 2025, pág 12, 'Conclusión con salvedad' (validado). | Lotes de extracción revisados y validados por año. |
| 2025 | 0 | salvedades | Cualitativo (auditoría) | Sí: salvedad en informe auditoría 2025 (pág 12). Requiere análisis de impacto.. Conclusión con salvedad 2025. | Lotes de extracción revisados y validados por año. |
| 2025 | 42 | Variacion de cuentas por cobrar | Cobertura y capacidad de pago | Variación de cuentas por cobrar. Valor 2.11093 > umbral de alerta 2. | CxC creciendo más que los ingresos (desfase recaudo vs ventas) es señal de calidad del recaudo. |
| 2025 | 62 | Calidad de resultados | Calidad de resultados | Calidad de resultados (FCO utilidad neta). Valor -0.481565 < umbral de alerta 0. | FCO menor que utilidad: diferencia entre beneficio y caja generada. < 0,7 vigila; < 0 (FCO negativo con utilidad positiva) señal fuerte. |

## Observaciones

| Año | # | Indicador | Motivo |
|---|--:|---|---|
| 2023 | 58 | Crecimiento del EBITDA | Crecimiento del EBITDA. Valor -0.274242 < umbral de observación -0.2. |
| 2023 | 59 | Crecimiento del resultado operativo | Crecimiento del resultado operativo. Valor -0.262952 < umbral de observación -0.2. |
| 2023 | 62 | Calidad de resultados | Calidad de resultados (FCO utilidad neta). Valor 0.662194 < umbral de observación 0.7. |

## Conclusiones del screening

- **12 señales de alerta** y **3 observaciones** en la ventana 2020-2025.
- La fortaleza estructural (bajo endeudamiento, alta autonomía, liquidez cómoda y cobertura de intereses amplia) persiste durante todo el período.
- Las señales de alerta se concentran en **calidad de resultados y opinión de auditoría** (2023-2025) y en **volatilidad de la utilidad neta** (2024).
