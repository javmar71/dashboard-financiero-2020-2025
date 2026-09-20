# PASO_B0_2_REPORTE.md — RESOLUCIÓN `fuente_esperada=informe_gestion`

Fecha: 2026-09-18
Etapa: Bloque 0 (eje transversal) — Paso 2 de 5
Estado: COMPLETADO

## 1. Objetivo

Resolver las filas de taxonomía cuyo `fuente_esperada=informe_gestion` tenía
`concepto_src=pendiente`: extraer la variable de `Informe de Gestion_2021.pdf` si existe
evidencia, o re-clasificarla a NO_ENCONTRADO estructural.

## 2. Hallazgo estructural (documental)

**`Informe de Gestion_2021.pdf` NO es un informe de gestión narrativo.** Es el paquete
"Estados Financieros por los Años que Terminaron el 31 de diciembre de 2021 y 2020 e
Informe del Revisor Fiscal":

- Portada (p1) + Notas a los Estados Financieros **Consolidados** (notas 1–41, paginación
  interna -17- a -123-; 109 páginas).
- Los estados condensados de situación financiera, resultado, patrimonio y flujos están en
  `Estados Financieros_2021.pdf` (6 páginas, pag. interna -11- a -16-).
- El dictamen está en `Informe de Audtoria_2021.pdf`.

En consecuencia, el conjunto documental **2021 no contiene informe de gestión narrativo**
(no hay sección de empleados/gestión/perspectivas corporativas). El nombre del archivo es
engañoso. Este hallazgo es transversal y aplica a los años 2022–2025 (mismo esquema de
nombres) → se verificará en Fase 5 la identidad documental de cada PDF.

## 3. Análisis por variable (10 filas `informe_gestion`)

| variable_madre_id | Evidencia en Informe de Gestion_2021.pdf | Decisión |
|-------------------|------------------------------------------|----------|
| numero_empleados | **SÍ, cuantitativa.** Nota 1, pág. 2: 251 empleados (2020) y 236 (2021) directos; 463/481 temporales; 13/15 aprendices SENA; 5/5 practicantes | **ACEPTADO** (2 registros 2020/2021) |
| riesgos | SÍ. Nota 39 "Políticas de Riesgo", págs. 103–107: VaR regulatorio/gerencial, SARL, IRL, modelo CAMEL | ACEPTADO (ya en lote, sin cambios) |
| cumplimiento_covenants | SÍ. Nota 37 "Patrimonio Técnico y Relación de Solvencia", págs. 102–103: solvencia 27,76% (2021) y 32,25% (2020) vs mínimo legal 9% | ACEPTADO (ya en lote, sin cambios) |
| hechos_relevantes | SÍ (negación). Nota 40 "Eventos Subsecuentes", pág. 107 | ACEPTADO (ya en lote, sin cambios) |
| crecimiento_adquisiciones | NO. Las coincidencias son la nota NIIF 3 (combinación de negocios, pág. 17–18) y activos NIIF 9; no hay narrativa de crecimiento por adquisiciones | NO_ENCONTRADO estructural |
| participacion_mercado | NO. 0 coincidencias en el PDF | NO_ENCONTRADO estructural |
| ventas_por_segmento | NO. Las coincidencias (pág. 53–54) son "deterioro de cartera por segmento", no ventas por segmento de negocio | NO_ENCONTRADO estructural |
| desempeno_por_segmento | NO. 0 coincidencias | NO_ENCONTRADO estructural |
| eficiencia_operativa | NO. La coincidencia (pág. 101) es "Bonificación Productividad" del personal clave, falso positivo | NO_ENCONTRADO estructural |
| perspectivas | NO. Las coincidencias (pág. 14, 99–100) son expectativas de mercado/inflación,tasas; no perspectivas corporativas de la Fiduciaria | NO_ENCONTRADO estructural |

## 4. Cambios aplicados

### 4.1 Lote `Temp\opencode\paso35_lote.json` (29 → 30 registros)

- **numero_empleados**: se reemplazó el registro NO_ENCONTRADO original (evidencia
  "informe_gestion (no presente)") por **2 registros ACEPTADO** (2021=236 y 2020=251
  empleados), con evidencia textual de la nota 1, pág. 2, confianza ALTA.
- **6 variables estructurales** (crecimiento_adquisiciones, participacion_mercado,
  ventas_por_segmento, desempeno_por_segmento, eficiencia_operativa, perspectivas):
  se actualizó la evidencia explicando el hallazgo documental (paquete EE.FF. vs informe
  de gestión) y se mantiene `estado=NO_ENCONTRADO` estructural con `confianza=NO_DETERMINADA`.
- Respaldo previo: `Temp\opencode\paso35_lote.before_b02.json`.

### 4.2 Taxonomía

Sin cambios. La taxonomía documenta el **diseño** (de dónde debe venir la variable);
la **disponibilidad real** se refleja en el lote (NO_ENCONTRADO estructural). Se deja
constancia del hallazgo documental para que Fase 5 verifique la naturaleza de cada PDF
por año.

## 5. Verificación

| Comprobación | Resultado |
|--------------|-----------|
| `validador_extraccion.py paso35_lote.json` | `valido=true`, errores esquema=0, errores determinísticos=0, advertencias=2 (DUDOSO partes_relacionadas, preexistentes) |
| Auditoría lote | 30 registros, ACEPTADO 21 / DUDOSO 2 / NO_ENCONTRADO 7 / INCONSISTENTE 0; confirmados por diseño 1 (salvedades); revisión humana 8; duplicados 0 |
| Registros numero_empleados | 2 (2021=236, 2020=251), ACEPTADO, confianza ALTA |

## 6. Conclusión

Quedan resueltas las 10 filas con `fuente_esperada=informe_gestion`:

- **3 extraídas** con evidencia textual del paquete (numero_empleados nuevo; riesgos,
  cumplimiento_covenants, hechos_relevantes ya presentes) → ACEPTADO.
- **7 re-clasificadas a NO_ENCONTRADO estructural** (documentadas en el lote y en esta
  sección) por ausencia de informe de gestión narrativo y de evidencia alternativa.

Hallazgo relevante para fases posteriores: el archivo "Informe de Gestion_YYYY.pdf" es en
realidad el paquete EE.FF. + dictamen, no un informe de gestión. Se recomienda renombrar/
anotar el mapa de fuentes al modelar la Fase 5.

## 7. Próximo paso (Bloque 0.3)

Resolver los duplicados de deuda: `pasivo_financiero_*` vs `deuda_financiera_*` → mapa
canónico.