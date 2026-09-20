# AGENTS.md — Instrucciones persistentes para opencode (mi_proyecto_finanzas)

Fecha de vigencia: 2026-09-19 (actualización: directriz de agnosticismo y protocolo de validación universal).

## 1. Qué es el proyecto

Automatizar el análisis y la auditoría financiera de entidades a partir de información empresarial multifuente (estados financieros, notas, informe de gestión, informe de auditoría, actas, Excel, XBRL). Conservar trazabilidad total del dato, sin inventar ni interpolar valores.

Archivo fuente de verdad del estado: `ESTADO_PROYECTO_HANDOFF.md`. Prevalece sobre `DOCUMENTACION_PROYECTO\00_ESTADO_MAESTRO.md` (desactualizado).

## 2. Motor de IA (a partir de 2026-09-18)

- **opencode** es el motor generativo del proyecto: lee/resume/extrae de los archivos (herramienta Read), busca fuentes académicas y propone los valores/cálculos.
- **big pickle** es el agente de verificación, auditoría y decisión: revisa resultados, herramientas, código y datos (`DUDOSO`/`INCONSISTENTE`) antes de aceptar cualquier resultado.
- **Agnosticismo de Entidad Obligatorio:** Queda prohibido incluir nombres propios de entidades, NITs, filiales o casos particulares en instrucciones, scripts o prompts. Las reglas son universales (NIIF/IFRS, XBRL).
- **Protocolo de Validación Universal:** Ante anomalías (divergencia estructural, errores de metadatos XBRL, etc.):
  1. **Paso A (Detección):** Identificar la divergencia mediante cruce entre cabecera, notas y archivos fuente.
  2. **Paso B (Evaluación):** Analizar si compromete la trazabilidad contable o si es error de empaquetado del proveedor.
  3. **Paso C (Juicio Experto):** Si la ambigüedad impide una lectura financiera inequívoca, detener el proceso, emitir informe de auditoría lógica y solicitar intervención humana.
- No se usan claves API internas. Los runners históricos son respaldo y no se invocan.

## 3. Reglas permanentes (resumen)

1. **No inventar ni interpolar.** Sin evidencia → `NO_ENCONTRADO`; sin certeza → `DUDOSO`.
2. **Trazabilidad irrenunciable:** `documento → entidad → período → dato → variable_madre → fuente → evidencia → validación → indicador`.
3. **No mezclar fuentes** automáticamente; cada dato conserva su procedencia.
4. **Jerarquía de fuentes:** 1º Estados Financieros, 2º Informe de Gestión, 3º Auditoría, 4º otros oficiales, 5º XBRL (solo recuperación/verificación). No hay búsqueda automática en Internet para valores; si falta info → requerimiento al usuario.
5. **No iniciar fases sin OK explícito del usuario.**
6. Estados de validación: `ACEPTADO`, `DUDOSO`, `NO_ENCONTRADO`, `INCONSISTENTE`.
7. Consistencia contable obligatoria: `ACTIVO = PASIVO + PATRIMONIO`.

## 4. No tocar sin autorización explícita

- `src\taxonomia.py`, `src\xbrl_fallback.py`, `src\lectura_pdfs.py`.
- `taxonomia_variable_madre.csv` (no revertir).
- `esquema_extraccion_ia.json` y `esquema_calculo_ia.json`.
- Notebooks (solo lectura).
- Estructura de `DOCUMENTACION_PROYECTO\`.

## 5. Entorno y ejecución (actualizado 2026-09-19)

- Python solo con `venv\Scripts\python.exe` (3.12.10). No usar .venv\.
- No crear venv nuevo; no instalar en Python global.
- **Aclaración operativa 2026-09-19 (big pickle):** la prohibición de archivos `.py` obedece a la Regla 2 (uso estándar de notebooks `.ipynb` y `.md` para auditoría). Queda **autorizado** crear y ejecutar archivos `.py` estructurados **permanentes** dentro del proyecto, manteniendo siempre el registro documental de los cambios.
- **Pertenencia de los artefactos:** toda la información y resultados deben ser **persistentes y trazables en el entorno de trabajo oficial** del proyecto. No existe regla de `06_REGLAS_DEL_PROYECTO.md` que exija trabajar en archivos temporales por seguridad; no dejar resultados solo en `%TEMP%`.
- Comandos de referencia: ver `ESTADO_PROYECTO_HANDOFF.md` §10.

## 6. Protocolo de avance

1. Leer `ESTADO_PROYECTO_HANDOFF.md`, reportes de paso y documentación técnica relevante.
2. Registrar toda decisión y actualizar `ESTADO_PROYECTO_HANDOFF.md` al cierre de cada fase.
3. Cada sub-paso requiere aprobación explícita.