# PASO_B0_5_REPORTE.md — VERIFICACIÓN DE IDENTIDAD XBRL POR AÑO (2020–2025)

Fecha: 2026-09-18
Etapa: Bloque 0 (eje transversal) — Paso 5 de 5 (CIERRE DEL BLOQUE 0)
Estado: COMPLETADO

## 1. Método

Archivo XBRL por año (`Otros (Superfinanciera) {ano}.xbrl`) evaluado en tres ejes:
1. Identificador `<xbrli:identifier>` en todos los `<xbrli:context>` del archivo.
2. Razón social declarada en `<ifrs:DisclosureOfGeneralInformationAboutFinancialStatements>` u otros tags de identidad.
3. Concordancia con la razón social y NIT del conjunto documental PDF del mismo año.

## 2. Resultado por año

| Año | NIT en XBRL | Razón social XBRL (tag) | Entidad confirmada | DDPDF coincide | Estado |
|-----|------------|--------------------------|--------------------|----------------|--------|
| 2021 | `830053105-3` | Fiduciaria La Previsora S.A. | FIDUPREVISORA ✓ | SÍ (mismo nombre) | **OK** |
| 2022 | `830053105-3` | (no extraído, mesmo contexto que 2021) | FIDUPREVISORA ✓ | SÍ | **OK** |
| 2023 | `830053105-3` | Fiduciaria La Previsora S.A. | FIDUPREVISORA ✓ | SÍ | **OK** |
| 2024 | **`900251864-8`** | — (tag sin razón social explícita) | **DIFERENTE ENTIDAD** ✗ | PDF dice "Fiduciaria La Previsora S.A." ≠ NIT XBRL | **⚠ BLOQUEO** |
| 2025 | **`901870663-3`** | — | **DIFERENTE ENTIDAD** ✗ | PDF dice "FIDUCIARIA LA PREVISORA S.A." ≠ NIT XBRL | **⚠ BLOQUEO** |

### 2.1 Hallazgo 2024 y 2025

Los archivos XBRL de 2024 y 2025 corresponden a entidades con NIT distintos al de Fiduciaria La Previsora S.A. (NIT 830053105-3). Los NIT detectados:

- **2024: `900251864-8`** → entidad diferente (falta confirmar nombre).
- **2025: `901870663-3`** → entidad diferente (falta confirmar nombre).

Los PDFs correspondientes (`Estados Financieros_{2024,2025}.pdf`) sí dicen "Fiduciaria La Previsora S.A." en la portada, pero **no incluyen NIT** en el texto extraíble.

Conclusión: los XBRL de 2024 y 2025 **no son de la misma entidad** que 2021–2023. El contenido de cuentas, comparativos y anexos XBRL de esos años no es válido para reconciliar contra los estados PDF de FIDUPREVISORA.

### 2.2 Periodos cubiertos por cada XBRL

Todos los XBRL incluyen contextos con 3 fechas de corte:
- `{ano-2}`, `{ano-1}`, `{ano}` (solo en 2021 se validó: 2019, 2020, 2021).

## 3. Impacto en el proyecto

| Área | Impacto |
|------|---------|
| Fase 5 (reusar pipeline 2022–2025) | **BLOQUEA** el uso del XBRL como fuente complementaria para 2024 y 2025 |
| Fase 9 (estudio XBRL 2021–2025) | Solo incluirá 2021, 2022 y 2023 (3 de 5 años); los otros dos requieren XBRL correctos o eliminación del paso XBRL para ellos |
| Fase 10 (conciliación XBRL vs estados) | No aplica para 2024 y 2025 |
| Pipeline base (PDF-only) | **No afectado**: los estados 2024 y 2025 se pueden extraer desde PDF y notas por IA |

## 4. Acciones recomendadas (pendientes de decisión del usuario)

1. **Verificar origen de los XBRL 2024 y 2025**: confirmar si fueron descargados de la Superfinanciera para la entidad correcta o son de otra sociedad (consolidados, otra fiduciaria, etc.).
2. **Si no existen XBRL correctos de FIDUPREVISORA para 2024 y 2025**: excluirlos del flujo XBRL (usar solo PDF/Notas para esos años).
3. **Si se obtienen XBRL correctos**: volver a ejecutar este bloque de verificación.

## 5. Conclusión del Bloque 0

El eje transversal está cerrado con las siguientes resoluciones:

| Paso | Estado | Resolución clave |
|------|--------|------------------|
| 0.1 requerimiento_id | OK | REQ-* formalizados; esquema v4; 145 filas (antes); auditoría 100% |
| 0.2 fuente_esperada=informe_gestion | OK | numero_empleados=ACEPTADO (2021: 236, 2020: 251); 6 restantes=NO_ENCONTRADO estructural |
| 0.3 duplicados deuda | OK | Familia canónica `deuda_financiera_*`; alias `pasivo_financiero_*` |
| 0.4 vacíos metodológicos | OK | 5 fórmulas definidas definitivamente (roic/rona, flujo_operativo, wacc, grados) |
| 0.5 identidad XBRL | OK (parcial) | 2021–2023 OK; **2024–2025 BLOQUEADO** (NIT ≠ FIDUPREVISORA) |

**Estado del eje transversal: CERRADO con salvedad XBRL 2024–2025.**

La Fase 4 (extracción IA 2021) puede proceder. La decisión XBRL para 2024–2025 queda pendiente del usuario.