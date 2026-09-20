# PASO 3.6 — Verificación XBRL Superfinanciera y cierre definitivo (2021)

**Fecha:** 2026-09-18 · **Periodo:** 2021 (con 2020 comparativo) · **Entidad:** Fiduciaria La Previsora S.A. (FIDUPREVISORA)

## 1. Verificación de entidad del XBRL

Archivo: `Otros (Superfinanciera) 2021.xbrl` — **entidad CONFIRMADA: coincide con Fiduciaria La Previsora S.A.**

- Identificador de entidad único en todos los contextos del archivo: **NIT `830053105-3`** (scheme `rut`), presente en los 253 contextos con corte `2021-12-31` y 240 con corte `2020-12-31`.
- El NIT `830.053.105-3` corresponde a FIDUPREVISORA (Fiduciaria La Previsora S.A.), validado contra fuentes oficiales: Rama Judicial, UNGRD y Gobernación de Arauca (documentos que identifican a la fiduciaria con ese NIT).
- La razón social declarada en el propio XBRL (`DisclosureOfGeneralInformationAboutFinancialStatements`) confirma: *"Fiduciaria La Previsora S.A. ... autorizada por la Superintendencia Financiera de Colombia, mediante Resolución 2521 de mayo 27 de 1985"*.
- **Conclusión:** el diagnóstico inicial del proyecto que señalaba que el XBRL no correspondía a la entidad era **incorrecto**. El XBRL sí pertenece a la entidad y se usa como fuente estructurada de verificación/negación explícita en el cierre de la Fase 3.

## 2. Resultado de la verificación XBRL por variable

### `incertidumbre` → RECLASIFICADA a ACEPTADO (fuente XBRL)

- Estado previo: `NO_ENCONTRADO` (ausencia pasiva: el dictamen solo describía responsabilidad metodológica del auditor, sin negación explícita).
- Estado final: **ACEPTADO** · confianza **ALTA** · valor `"sin incertidumbre material sobre negocio en marcha"`.
- **Evidencia (tags XBRL 2021, contexto TrimestreAcumuladoActual 2021-01-01/2021-12-31):**
  - `<ifrs:DisclosureOfGoingConcernExplanatory>` = **"No aplica"**
  - `<ifrs:DescriptionOfUncertaintiesOfEntitysAbilityToContinueAsGoingConcern>` = **"No aplica"**
- El XBRL no incluye un tag equivalente para 2020; la ausencia de partida y la opinión limpia del dictamen (2021/2020) sostienen la misma conclusión para ambos periodos.
- Resultado: sale de la revisión humana.

### `partes_relacionadas` → DUDOSO DEFINITIVO (el XBRL no lo resuelve)

- El XBRL solo trae dos tags de balance: `CuentasCobrarPartesRelacionadasAsociadasCorrientes` y `CuentasPagarEntidadesRelacionadas`, ambos en **0** para 2021 y 2020.
- No existe tag de **total consolidado de transacciones** con partes relacionadas; los 0 del XBRL **contradicen** el detalle de la nota 36 del EF (p. 100-102: Casa Matriz, Personal Clave, Junta Directiva, Operaciones Conjuntas con saldos e ingresos/gastos distintos de cero).
- Por tanto, el XBRL **no aporta una fuente adicional** para reconciliar: **DUDOSO queda definitivo** (2 registros, 2021 y 2020), sin estado pendiente.

### 7 variables narrativas de informe de gestión → NO_ENCONTRADO ESTRUCTURAL

`crecimiento_adquisiciones`, `participacion_mercado`, `ventas_por_segmento`, `desempeno_por_segmento`, `eficiencia_operativa`, `numero_empleados`, `perspectivas`:
- El XBRL es un estándar de datos financieros estructurados (IFRS/SFC); **no aplica** para contenido estratégico/cualitativo del informe de gestión.
- **No se buscaron**: quedan `NO_ENCONTRADO` con carácter estructural (limitación del año), ya documentado previamente.

## 3. Cierre de Fase 3 (2021) — estado final consolidado

| Métrica | Valor |
|---|---|
| Lote total | 29 registros (22 IA + 7 estructurales por diseño) |
| Validación | **valido=true** · 0 errores de esquema · 0 determinísticos · 2 advertencias (DUDOSO de partes_relacionadas) |
| Cobertura variables | **20/23** |
| Cobertura objetivos (variable × periodo) | 19/46 (2021: 10, 2020: 9) |
| ACEPTADO | **19** |
| DUDOSO | **2** (partes_relacionadas 2021/2020 — definitivo) |
| NO_ENCONTRADO | **8** (7 estructurales + 1 `costo_ventas_gastos` sin partida) |
| INCONSISTENTE | 0 |
| Confirmados por diseño | **1** (`salvedades` NO_ENCONTRADO con `tipo_opinion=sin_salvedad`) |
| Revisión humana final | **9** (2 DUDOSO + 7 estructurales) |
| Duplicados | 0 |

### Lista de revisión humana final (9)

| # | variable | periodo | estado | motivo |
|---|---|---|---|---|
| 1-2 | partes_relacionadas | 2021/2020 | DUDOSO | desglose por categorías sin total; XBRL no resuelve (solo tags de balance en 0, sin total consolidado) |
| 3-9 | 7 estructurales de informe de gestión | — | NO_ENCONTRADO | limitación estructural del año (no hay informe narrativo; XBRL no aplica) |

### Resumen de reclasificaciones en Fase 3 (2021)

| variable | antes | después | fuente |
|---|---|---|---|
| deuda_financiera_corriente / no_corriente | NO_ENCONTRADO | ACEPTADO = 0 (2021/2020) | nota 34 y §2.2.6 (p17-18) "no cuenta con pasivos financieros provenientes de prestamistas" |
| hechos_relevantes | NO_ENCONTRADO | ACEPTADO "sin hechos posteriores relevantes reportados" | §40 (p107) negación explícita |
| incertidumbre | NO_ENCONTRADO | ACEPTADO "sin incertidumbre material sobre negocio en marcha" | XBRL 2021 `DisclosureOfGoingConcernExplanatory` y `DescriptionOfUncertaintiesOfEntitysAbilityToContinueAsGoingConcern` = "No aplica" |
| tipo_opinion / salvedades | — | ACEPTADO `sin_salvedad` / NO_ENCONTRADO por diseño | dictamen limpio (p1) + regla de diseño en taxonomía |

## 4. FASE 3 (2021) — CERRADA

La extracción para el ejercicio 2021 queda **cerrada**: validación oficial sin errores, cobertura documentada, fuentes corroboradas (EF, dictamen, XBRL Superfinanciera) y lista de revisión humana reducida a 9 registros con estados definitivos.