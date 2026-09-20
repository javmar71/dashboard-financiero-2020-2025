# Paso 3.5 — Extracción IA por secciones (reporte final)

Fecha: 2026-09-18. Alcance: mapeo determinístico aprobado con ajustes + **13 llamadas** de extracción real (10 originales + 2 de corroboración de deuda + 1 re-ejecución de [73] riesgos-cualitativo) + validación y auditoría del lote. **`valido=true`**. Fase 3 de 2021 (pasos 3.1–3.5) cerrada; pendiente autorización del Paso 3.6.

> **Nota de vigencia (2026-09-18, tarde):** reporte HISTÓRICO ejecutado con Gemini (retirado).
> Motor vigente: **opencode** (extracción) + **big pickle** (auditoría/decisión) + validación
> determinística Python. Resultados y lote no cambian; el runner equivalente para nuevos años corre
> según `INSTRUCCIONES_EXTRACCION.md`.

## 1. Mapeo determinístico (reglas, sin IA) y ajustes aplicados

- 26 variables IA-searchable originales. Tras ajustes: **23** en alcance, **3** pasan a `no_aplica_tipo_entidad` en `taxonomia_variable_madre.csv` (misma condición que `inventarios`):
  - `composicion_inventarios` (ajuste 1): no existe nota de inventarios (menciones genéricas, NIC 2).
  - `enfasis`, `cuestiones_key` (ajuste 4): párrafos NIA 701/KAM obligatorios solo para entidades de interés público/listadas.
- **7 variables de informe_gestion** → `NO_ENCONTRADO` estructural, **sin llamada a IA**, evidencia: *"No existe informe de gestión narrativo en el conjunto documental de 2021; Informe de Gestion_2021.pdf contiene las notas a los estados financieros, no un informe de gestión separado."* Esto es una **limitación estructural del año**, no una búsqueda pendiente.
- **5 variables de la cadena deuda** (`composicion_deuda`, `deuda_financiera_corriente`, `deuda_financiera_no_corriente`, `tasas_interes`, `vencimientos`): resueltas en §2 con corroboración 2.2.6 + llamadas a [46]/[68] (`deuda_financiera_*` con ACEPTADO=0; las demás derivan de la misma ausencia).

**Llamadas agrupadas por sección:**

| Call | Sección (orden) | Variables | Doc |
|---|---|---|---|
| 1 | [4] Opinión (p1) | tipo_opinion, salvedades | Audtoria |
| 2 | [5] Fundamento de la Opinión (p1-2) | incertidumbre | Audtoria |
| 3 | [34] 8. Inversiones, neto (p45-47) | inversiones_detalle | Gestion/notas |
| 4 | [42] 14. Propiedades y equipo (p65-67) | adquisiciones_activos | Gestion/notas |
| 5 | [44] 16. Cuentas por pagar (p68-70) | proveedores | Gestion/notas |
| 6 | [50] 22. Provisiones (p75-77) | contingencias | Gestion/notas |
| 7 | [70] 36. Partes relacionadas (p100-102) | partes_relacionadas | Gestion/notas |
| 8 | [71] 37. Patrimonio técnico y solvencia (p102-103) | cumplimiento_covenants | Gestion/notas |
| 9 | [73] 39. Políticas de riesgo (p103-107) | riesgos | Gestion/notas |
| 10 | [74] 40. Eventos subsecuentes (p107) | hechos_relevantes | Gestion/notas |
| 11 | [46] 18. Derecho de uso pasivo (p72) | deuda_financiera_no_corriente | Gestion/notas |
| 12 | [68] 34. Resultado financiero neto (p99-100) | deuda_financiera_corriente | Gestion/notas |

Artefactos: `mapeo_variables_secciones.py` + `mapeo_variables_secciones_2021.json`.

## 2. Cadena deuda — corroboración con 2.2.6 + llamadas [46]/[68]

**Decisivo**, seg [15] (2.2.6 Mejoras anuales, p17-18): *"…no genera(n) impactos cuantificables, dado que **no cuenta con pasivos financieros provenientes de prestamistas**."* → la entidad **no tiene pasivos financieros con prestamistas**.

| variable_madre_id | 2021 | 2020 | estado | confianza |
|---|---|---|---|---|
| deuda_financiera_no_corriente | 0 | 0 | ACEPTADO | ALTA |
| deuda_financiera_corriente | 0 | 0 | ACEPTADO | ALTA |

Hallazgo en estados financieros: `datos_estados_financieros.csv` **no tiene** fila "Obligaciones financieras". Único pasivo tipo financiero: `b_derecho_uso_pasivo` (Derecho de uso pasivo) = 2020: 9.689, 2021: 7.767, clasificado `pasivo_no_corriente`. **`pasivo_financiero_corriente` no tiene partida → 0/sin saldo**, consistente con el ACEPTADO=0 de la IA.

## 3. Esquema de datos — tipo_dato 3 valores

`taxonomia_variable_madre.csv` con `tipo_dato` ∈ {`cuantitativo`, `cualitativo_enum`, `cualitativo_texto_libre`}:

- `tipo_opinion` → `cualitativo_enum` con enum `{sin_salvedad, con_salvedad, adversa, abstencion}`. Valor extraído: **`sin_salvedad`**.
- `riesgos`, `hechos_relevantes`, `incertidumbre`, `salvedades` → `cualitativo_texto_libre` (valor string no vacío).
- **Regla documentada en taxonomía para `salvedades`**: solo debe tener contenido si `tipo_opinion=con_salvedad`; si `sin_salvedad` (o global), `NO_ENCONTRADO` es el resultado esperado por diseño. → en el lote: `salvedades` NO_ENCONTRADO ✓ (consistente con `tipo_opinion=sin_salvedad`).
- `partes_relacionadas` → `cuantitativo` sin cambios, con estado DUDOSO actual (desglose por categorías sin total consolidado).
- `cumplimiento_covenants` → `cuantitativo` (ratio numérico 27.76%/32.25%).

`esquema_extraccion_ia.json` v3: `valor` acepta number o string (nullable); `esquema_utils.sanear_schema_para_sdk` omite constraints de tipo compuesto para el SDK. `validador_extraccion.py`: carga tipos de dato, exige string no vacío para texto_libre y miembro del enum para enum (columnas `valores_posibles` en taxonomía).

## 4. Resultado final del lote (29 registros: 22 IA + 7 estructurales)

| variable_madre_id | 2021 | 2020 | estado | confianza |
|---|---|---|---|---|
| proveedores | 4.742 | 2.272 | ACEPTADO | ALTA |
| inversiones_detalle | 242.899 | 225.836 | ACEPTADO | ALTA |
| adquisiciones_activos | 16 | 283 | ACEPTADO | ALTA |
| contingencias | 16.413 | 13.111 | ACEPTADO | ALTA |
| cumplimiento_covenants | 27,76% | 32,25% | ACEPTADO | ALTA |
| deuda_financiera_no_corriente | 0 | 0 | ACEPTADO | ALTA |
| deuda_financiera_corriente | 0 | 0 | ACEPTADO | ALTA |
| tipo_opinion | sin_salvedad | — | ACEPTADO (enum) | ALTA |
| riesgos | texto VaR/políticas | texto VaR/políticas | ACEPTADO (texto_libre) | ALTA |
| salvedades | — | — | NO_ENCONTRADO (esperado por diseño) | ALTA |
| incertidumbre | — | — | NO_ENCONTRADO (sin incertidumbre material) | NO_DETERMINADA |
| partes_relacionadas | desglose c/ categorías | ídem | DUDOSO (sin total consolidado) | MEDIA |
| hechos_relevantes | — | — | NO_ENCONTRADO ("no hubo eventos significativos") | ALTA |
| 7 gestión estructurales | — | — | NO_ENCONTRADO | NO_DETERMINADA |

## 5. Validación oficial — validador_extraccion.py

**`valido=true` · errores de esquema 0 · errores determinísticos 0 · advertencias 2 · n=29.**
Advertencias (no bloquean): `partes_relacionadas` DUDOSO en 2021/2020 sin valor único, con candidatos por categoría en evidencia.

Resueltos vs iteración anterior: `tipo_opinion` ACEPTADO sin valor (ahora enum `sin_salvedad`) y duplicado de `riesgos` (ahora ACEPTADO texto_libre 2021/2020, única entrada por periodo).

## 6. Auditoría de lote — auditor_lote_extraccion.py

- Registros: 29 (con periodo 19, sin periodo 10). Objetivos esperados: **46** = 23 × 2.
- **Cobertura: 19/46 objetivos cubiertos**; variables con resultado: **20/23**; sin resultado: 3 (`participacion_mercado`, `eficiencia_operativa`, `perspectivas` — todas estructurales de informe de gestión).
- Distribución estado: ACEPTADO 18, DUDOSO 2, NO_ENCONTRADO 9, INCONSISTENTE 0.
- Distribución confianza: ALTA 19, MEDIA 2, BAJA 0, NO_DETERMINADA 8.
- **Confirmados por diseño: 1** (`salvedades` NO_ENCONTRADO, condicion `tipo_opinion=sin_salvedad` según taxonomía → fuera de revisión humana; solo alerta si la condición se viola).
- **Revisión humana: 10** (ver §7). Duplicados: **0**.

### 6bis. Evidencia textual de ausencias — reclasificación (ajuste post-cierre)

- **`hechos_relevantes` → ACEPTADO** (negación explícita): sección [74] (p107) declara textualmente *"Entre el 1 de enero de 2022 y la fecha de aprobación de estos Estados Financieros no se presentaron eventos significativos que requieran ser revelados"* → valor `"sin hechos posteriores relevantes reportados"` (mismo criterio que deuda_financiera=0). Se salió de revisión humana.
- **`incertidumbre` → queda NO_ENCONTRADO** (ausencia pasiva): sección [5] (p1-2) solo describe la responsabilidad metodológica del auditor sobre negocio en marcha; **no hay negación activa** ("no se identificó incertidumbre material"), así que no se reclasifica.
- **`salvedades` → NO_ENCONTRADO confirmado por diseño** (taxonomía: esperado por diseño cuando `tipo_opinion=sin_salvedad`; el dictamen es opinión limpia).

## 7. Lista de revisión humana consolidada (10)

| # | variable | periodo | estado | motivo |
|---|---|---|---|---|
| 1 | incertidumbre | — | NO_ENCONTRADO | ausencia pasiva: el dictamen no niega incertidumbre material (solo describe responsabilidad metodológica) |
| 2-3 | partes_relacionadas | 2021/2020 | DUDOSO | desglose por categorías sin total; candidatos en evidencia |
| 4-10 | 7 estructurales de informe de gestión | — | NO_ENCONTRADO | limitación estructural del año (no hay informe narrativo) |

Excluidos por criterio aplicado: `salvedades` (confirmado por diseño, taxonomía), `hechos_relevantes` (ACEPTADO por negación explícita), `incertidumbre` (se quedó en revisión, ver arriba).

## 8. Tokens y costo

| Conjunto | Llamadas | prompt | completion | thoughts | total |
|---|---|---|---|---|---|
| Lote 3.5 final (13 llamadas) | 13 | 25.833 | 4.919 | 20.314 | **51.066** |
| Pilotos 3.3 (4 llamadas) | 4 | — | — | — | 14.838 |
| **Acumulado** | 17 | — | — | — | **65.904** |

Modelos: **8× `gemini-3.6-flash`** (órdenes 4…71) y **5+× `gemini-3.5-flash`** (46, 68, 70, 73, 74; re-ejecuciones de 4/73 también por cuota free-tier del 3.6-flash). El SDK no expone costo monetario.

## 9. Cierre

Fase 3 de 2021 (pasos 3.1–3.5) **cerrada con `valido=true`**. Pendiente: decisión/revisión humana de los 12 ítems y autorización del Paso 3.6 (fallback XBRL + consolidación).