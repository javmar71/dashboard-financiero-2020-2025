# PASO_F4_REPORTE.md — EXTRACCIÓN IA 2021 (FASE 4)

Fecha: 2026-09-18
Etapa: Fase 4 — Extracción/verificación IA de variables madre 2021
Estado: CERRADO (con 1 variable diferida: `vencimientos`)

> **Nota de vigencia (2026-09-18, tarde):** reporte HISTÓRICO ejecutado con Gemini (retirado).
> Motor vigente: **opencode** propone / **big pickle** audita / Python verifica. El esquema
> `requerimiento_id` como campo de sistema Agregado por Python sigue igual.

## 1. Objetivo y decisiones

Completar las variables madre pendientes de 2021 con el esquema `esquema_extraccion_ia.json` v4
(`requerimiento_id` como campo de sistema agregado por Python desde la taxonomía).

Decisiones del usuario que acotan el alcance:

1. **Las 38 variables de estados quedan FUERA del lote IA.** Se sirven por su pipeline propio
   (`salidas/datos_estados_financieros.csv`, indexado por concepto) y no por el lote de extracción.
   Fundamento: `src/indicadores.py` las consume desde dicho CSV; y el auditor solo exige
   `fuente_esperada ∈ {notas, informe_gestion, informe_auditoria}` para las variables IA-searchable.
2. **Fase 4 se ejecuta con 3 llamadas IA** (`composicion_deuda`, `tasas_interes`, `vencimientos`) más
   **3 registros estructurales** `no_aplica_tipo_entidad` (`composicion_inventarios`, `cuestiones_key`, `enfasis`).
3. **Cierre sin `vencimientos`**: su extracción quedó bloqueada por agotamiento de la cuota free-tier
   diaria de los modelos Gemini; se difiere a Fase 5 (escalado 2022–2025).

## 2. Método

- Modelo: `gemini-3.6-flash` (temperature 0, `response_schema` v4). Respaldos crudos por llamada en
  `f4_call_{orden}_raw.json` / `f4_call_{orden}_meta.json`.
- Una sección documental por llamada; una entrada atómica por `(variable_madre_id, periodo)`.
- `composicion_deuda` y `vencimientos` incluyeron contexto de corroboración de la sección 2.2.6
  ("no cuenta con pasivos financieros provenientes de prestamistas").
- Los 3 registros estructurales no usan IA: se generan con página obligatoria y
  `valor/periodo/unidad/cuenta_original = null`.

## 3. Resultado por variable

| Variable | Fuente | Pág. | Resultado | Confianza | Sustento |
|----------|--------|------|-----------|-----------|----------|
| `composicion_deuda` | Informe de Gestion_2021.pdf | 72 | ACEPTADO = 0 (2021 y 2020) | ALTA | Sección 18 (Derecho de uso pasivo: solo arrendamientos $7.767/$9.689) + corroboración 2.2.6 (sin pasivos con prestamistas) |
| `tasas_interes` | Informe de Gestion_2021.pdf | 99–100 | DUDOSO (sin valor único) | MEDIA | Múltiples candidatas: tasa de referencia Banco República 1.75%→3%, TES TF del 27 (4.77%→7.81%), Tesoros EEUU 1.51% |
| `vencimientos` | — | — | **PENDIENTE (Fase 5)** | — | Bloqueada por cuota free-tier diaria de Gemini |
| `composicion_inventarios` | Informe de Gestion_2021.pdf | 2 | NO_ENCONTRADO | ALTA | `no_aplica_tipo_entidad`: fiduciaria sin giro comercial ni partida de inventarios |
| `cuestiones_key` | Informe de Audtoria_2021.pdf | 1 | NO_ENCONTRADO | ALTA | `no_aplica_tipo_entidad`: dictamen sin sección KAM; entidad no listada |
| `enfasis` | Informe de Audtoria_2021.pdf | 2 | NO_ENCONTRADO | ALTA | `no_aplica_tipo_entidad`: sin párrafo de énfasis ("Otros Asuntos" se refiere al comparativo 2020) |

## 4. Registros estructurales (`no_aplica_tipo_entidad`)

- `composicion_inventarios`: la única mención de "inventario" en el documento corresponde a los
  estatutos sociales (arts. 51 y 59) y a la referencia normativa a la NIC 2 en las enmiendas a la NIC 16.
- `cuestiones_key`: el dictamen contiene Opinión, Fundamento de la Opinión y Otros Asuntos; no hay
  sección de asuntos clave de auditoría (NIA 701).
- `enfasis`: no existe párrafo de énfasis; el texto de "Otros Asuntos" describe la auditoría del
  comparativo 2020 por otro revisor fiscal.

## 5. Validación y auditoría

- **Validador oficial** (`validador_extraccion.py`): `valido = true`; 0 errores de esquema; 0 errores
  determinísticos; 4 advertencias (todas DUDOSO sin valor único, válidas por candidatos en evidencia).
- **Auditor de lote** (`auditor_lote_extraccion.py`): 37 registros totales (25 con periodo, 12 sin periodo);
  0 duplicados `(variable_madre_id, periodo)`; estado: 23 ACEPTADO / 4 DUDOSO / 10 NO_ENCONTRADO /
  0 INCONSISTENTE; 13 registros requieren revisión humana (los DUDOSO y los NO_ENCONTRADO estructurales).

## 6. Lote resultante

- Lote final: `paso35_lote.json` — **37 registros** (30 previos + 7 nuevos de esta fase).
- Respaldo del lote previo: `paso35_lote_pre_f4.json`.
- Candidato intermedio: `f4_lote_candidato.json`.
- Cobertura frente a las 23 variables IA-searchable: quedan pendientes las asociadas a estados
  (fuera de alcance por decisión) y `vencimientos` (diferida).

## 7. Pendientes

1. `vencimientos` (sección ord 34, "8. INVERSIONES", págs. 45–47, + corroboración 2.2.6): reintentar su
   extracción IA al restablecerse la cuota, e incorporarla al lote (Fase 5).
2. Revisión humana de los 4 registros DUDOSO (`partes_relacionadas` 2020/2021, `tasas_interes` 2020/2021).

## 8. Conclusión

Fase 4 **cerrada** con 5 de 6 variables resueltas (2 ACEPTADO, 1 DUDOSO, 3 NO_ENCONTRADO estructural),
lote de 37 registros validado y auditado sin errores ni duplicados. `vencimientos` queda diferida a Fase 5.
