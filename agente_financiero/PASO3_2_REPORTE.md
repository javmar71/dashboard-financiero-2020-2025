# Paso 3.2 — Segmentador determinístico de PDF (reporte)

Fecha: 2026-09-17. Alcance: exclusivamente el Paso 3.2. **No se avanzó al Paso 3.3.**

## 1. Cumplimiento de condiciones

| Condición | Estado |
|---|---|
| No llama a Gemini ni a ningún proveedor IA | Cumple (`usa_ia: false` en el JSON; sin imports de red). |
| Segmentador exclusivamente determinístico | Cumple: solo reglas fijas (regex + geometría), sin umbrales aleatorios ni modelos. |
| No interpreta cuentas | Cumple. No lee semántica contable. |
| No asigna `variable_madre_id` | Cumple: el término no existe en el módulo. |
| No asigna indicadores | Cumple. |
| No asigna PUC | Cumple. |
| No infiere valores | Cumple: solo transcribe texto; no crea ni completa cifras. |
| No decide qué fuente semántica es correcta | Cumple: no emite `fuente_esperada`. |
| No genera JSON de extracción IA | Cumple: el JSON es de segmentos, no de extracción. |
| No modifica `src/taxonomia.py`, `xbrl_fallback.py`, Fase 2, `taxonomia_variable_madre.csv`, `esquema_extraccion_ia.json` | Cumple: ningún archivo de esos fue tocado. |
| Nombre de archivo y contenido como hechos independientes | Cumple: `documento_origen = "Informe de Gestion_2021.pdf"` y `titulo_seccion = "NOTAS A LOS ESTADOS FINANCIEROS CONSOLIDADOS"`; no se transformó en `fuente_esperada="informe_gestion"`. |

## 2. Entrada / salida

`PDF → páginas → filas → segmentos` con metadatos de origen. Por cada segmento:

| Campo | Descripción |
|---|---|
| `orden_documento` | Orden dentro del documento (1-based). |
| `documento_origen` | Nombre exacto del archivo. |
| `tipo_segmento` | `titulo_patron`, `seccion_numerada`, `subseccion_numerada`, `titulo_mayusculas`, `titulo_heuristica`, `preambulo`. |
| `nivel` | 1–3 según regla (jerarquía detectada). |
| `titulo_seccion` | Texto literal del encabezado detectado (o `null`). |
| `titulo_resumen` | Recorte determinístico del título hasta el primer delimitador. |
| `pagina_inicio` / `pagina_fin` | Rango de páginas del segmento (puede iniciar/terminar a mitad de página). |
| `texto` | Texto completo del segmento (continuidad entre páginas, sin cortar tablas). |
| `bloques_por_pagina` | Lista `{pagina, texto}` para trazabilidad fina. |
| `num_filas` | Filas de texto incluidas. |
| `encabezado_origen` | `{pagina, y, tamano, fuentes}` del encabezado. |

Extra a nivel de documento: `num_paginas`, `num_segmentos`, `ruido_repetitivo_detectado`, `num_filas_ruido_excluidas`, `segmentos`.

## 3. Reglas deterministas

**Reconstrucción de filas.** Se fusionan líneas cuyo centro vertical difiere ≤ 2.5 px (así `"2."` + `"BASES DE PRESENTACIÓN"` quedan en una fila). Dentro de cada fila el texto se ordena por x.

**Ruido repetitivo (marca de agua / pies).** Un texto corto (≤ 90 caracteres, dígitos normalizados a `#`) que aparece en ≥ 50 % de las páginas (PDF con ≥ 4 páginas) y en la banda de borde (arriba < 13 % o abajo > 85 % de la altura) se excluye del texto y se reporta. Se documenta que **solo** se excluye así: no se borra contenido contable.

| Documento | Ruido detectado |
|---|---|
| Estados Financieros_2021.pdf | `- # -`, `FIDUCIARIA LA PREVISORA S.A.`, `VERIFIED` |
| Informe de Gestion_2021.pdf | `- # -`, `VERIFIED` |
| Informe de Audtoria_2021.pdf | `- # -`, `VERIFIED` |

**Encabezados (en orden de prioridad).**
1. `titulo_patron`: títulos estructurales de estados financieros (NOTAS A LOS ESTADOS FINANCIEROS, INFORME DEL REVISOR FISCAL, INFORME SOBRE LA AUDITORÍA…, CERTIFICACIÓN…, ESTADO DE SITUACIÓN FINANCIERA, RESULTADO INTEGRAL, CAMBIOS EN EL PATRIMONIO, FLUJOS DE EFECTIVO), con ≥ 80 % de mayúsculas.
2. `subseccion_numerada`: `x.y...` con componentes de 1–2 dígitos (evita confundir miles tipo `81.254`) y siguiente palabra iniciando en letra.
3. `seccion_numerada`: `N. TÍTULO` con ≥ 40 % de mayúsculas.
4. `titulo_mayusculas`: ≥ 85 % mayúsculas, fuente ≥ 10.5 pt, sin punto final.
5. `titulo_heuristica` (opcional, `--sin-heuristica` la desactiva): línea de ≤ 85 caracteres y ≤ 8 palabras, **sin cifras**, que empieza en mayúscula, no termina en puntuación, está aislada por huecos ≥ 1.5× la mediana de la página y va seguida de prosa (≥ 55 caracteres).

**Continuidad.** Un encabezado se absorbe (no abre segmento) si su título normalizado coincide con el del segmento actual (encabezado repetido de página) o si es un subtítulo `MAYUS`/`PATRON` inmediatamente posterior a otro `MAYUS`/`PATRON` sin contenido entre ambos. Así las tablas y bloques **no se cortan por cambio de página**.

## 4. Prueba ejecutada

```
venv\Scripts\python.exe "AUTOMAT ANALISIS FIN\agente_financiero\segmentador_pdf.py" ^
  --out "AUTOMAT ANALISIS FIN\agente_financiero\segmentacion_2021.json"
```

| Documento | Páginas | Segmentos | Filas ruido | Texto retenido* |
|---|---|---|---|---|
| Estados Financieros_2021.pdf | 6 | 6 | 18 | 76.6 % |
| Informe de Gestion_2021.pdf | 109 | 76 | 217 | 93.1 % |
| Informe de Audtoria_2021.pdf | 9 | 7 | 17 | 96.2 % |

\* Caracteres del segmentado sobre caracteres de `get_text()`. La diferencia se explica por normalización de espacios/saltos y por el ruido excluido (no por pérdida de contenido contable: se verificó presencia de cifras y textos clave).

**Segmentos por tipo**

| Documento | preambulo | titulo_patron | seccion_numerada | subseccion_numerada | titulo_mayusculas | titulo_heuristica |
|---|---|---|---|---|---|---|
| Estados Financieros | 0 | 4 | 0 | 0 | 2 | 0 |
| Informe de Gestion | 1 | 2 | 41 | 18 | 0 | 14 |
| Informe de Audtoria | 1 | 3 | 0 | 0 | 0 | 3 |

En el Informe de Gestión se detectaron las 41 secciones numeradas (1–41) y en la Audtoria las secciones Opinión, Fundamento de la Opinión y Otros Asuntos.

## 5. Ejemplos de segmentos (con página inicial/final)

| # | Documento | pág. inicio–fin | Tipo | Filas | Título detectado |
|---|---|---|---|---|---|
| 1 | Estados Financieros_2021.pdf | 1–1 | titulo_patron | 44 | ESTADO DE SITUACIÓN FINANCIERA |
| 2 | Informe de Gestion_2021.pdf | 2–15 | seccion_numerada | 616 | 1. INFORMACIÓN GENERAL |
| 3 | Informe de Gestion_2021.pdf | 96–97 | seccion_numerada | 33 | 29. GASTOS DE ADMINISTRACIÓN |
| 4 | Informe de Gestion_2021.pdf | 109–109 | titulo_patron | 20 | CERTIFICACIÓN DE LOS ESTADOS FINANCIEROS |
| 5 | Informe de Audtoria_2021.pdf | 1–1 | titulo_heuristica | 9 | Opinión |
| 6 | Informe de Audtoria_2021.pdf | 3–9 | titulo_patron | 303 | INFORME SOBRE OTROS REQUERIMIENTOS LEGALES Y REGLAMENTARIOS |
| 7 | Informe de Gestion_2021.pdf | 57–61 | titulo_heuristica | 186 | Nombre Consorcio Objeto *(falso positivo de tabla en modo heurístico)* |

El ejemplo 2 confirma continuidad de 14 páginas (`bloques_por_pagina` = páginas 2–15, sin cortar). El ejemplo 3 confirma una tabla que cruza de la página 96 a la 97 dentro de un mismo segmento.

## 6. Problemas y ambigüedades detectadas

1. **Nombre ≠ contenido.** `Informe de Gestion_2021.pdf` contiene las NOTAS (`NOTAS A LOS ESTADOS FINANCIEROS CONSOLIDADOS`, p. 2), sin un encabezado literal "INFORME DE GESTIÓN". El segmentador conserva ambos hechos y **no** clasifica la fuente.
2. **Falsos positivos de la heurística.** Encabezados de tabla sin cifras se detectan como `titulo_heuristica` (p. ej. `Nombre Consorcio Objeto` p. 57–61 y `Tipo Técnica de valuación` p. 40–41). Se mitiga con `--sin-heuristica`, pero entonces se pierden títulos Title Case reales (Opinión, Fundamento de la Opinión, Otros Asuntos).
3. **Erratas del PDF.** `ESTADODE CAMBIOS EN EL PATRIMONIO` (p. 3), `PATRIMONO` (p. 4), `POR LOS AÑOS TERMINARON` (p. 4): la continuidad por título normalizado no une esas variantes (se transcribieron literalmente).
4. **Encabezado de página eliminado.** `FIDUCIARIA LA PREVISORA S.A.` se repite en el borde superior de los Estados Financieros y se excluye como ruido; por eso el nombre de la entidad no queda dentro de un segmento de ese PDF.
5. **Subtítulo en la misma línea que el párrafo.** Varias subsecciones (p. ej. `2.1 Normas Contables Aplicables - La Fiduciaria…`) comparten línea con el primer párrafo; `titulo_seccion` conserva el texto completo y se añadió `titulo_resumen` como recorte.
6. **Fuentes casi uniformes.** El cuerpo y los títulos Title Case comparten `Calibri-Light` 10 pt en la auditoría; no son distinguibles por fuente, solo por la heurística de aislamiento.
7. **Sin tabla de contenido con páginas**, por lo que la segmentación depende de la estructura física del documento.
8. **Riesgo de sobre-exclusión de ruido** si un texto corto se repite en bordes en ≥ 50 % de páginas; documentado como regla (actualmente solo afecta pies y marca de agua).

## 7. Archivos creados / modificados

| Acción | Archivo |
|---|---|
| Creado | `AUTOMAT ANALISIS FIN\agente_financiero\segmentador_pdf.py` |
| Creado | `AUTOMAT ANALISIS FIN\agente_financiero\segmentacion_2021.json` |
| Creado | `AUTOMAT ANALISIS FIN\agente_financiero\PASO3_2_REPORTE.md` |
| Modificado | Ninguno de Fase 2, `src/taxonomia.py`, `xbrl_fallback.py`, `taxonomia_variable_madre.csv` ni `esquema_extraccion_ia.json` |

## 8. Estado

Paso 3.2 terminado. **Detenido a la espera de aprobación explícita.** No se inició el Paso 3.3.
