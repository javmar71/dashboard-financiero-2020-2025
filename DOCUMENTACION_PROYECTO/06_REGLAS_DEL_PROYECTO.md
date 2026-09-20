# 06_REGLAS_DEL_PROYECTO.md — REGLAS PERMANENTES

Crear una lista de reglas permanentes para el proyecto. Como mínimo:

## 1. Verificar antes de modificar.

Toda modificación a notebooks, código, datos o configuración debe iniciar con una verificación exhaustiva del estado actual. No asumir que las condiciones siguen siendo las mismas sin confirmar.

## 2. No crear código sin autorización.

Está absolutamente prohibido crear archivos `.py` salvo autorización explícita posterior. El proyecto trabaja con notebooks `.ipynb` y documentación Markdown. Cualquier necesidad de código nuevo debe ser autorizada y registrada.

> **Aclaración operativa (2026-09-19, big pickle):** la prohibición de `.py` es el **uso estándar** de notebooks `.ipynb` y Markdown para auditoría. Con el entorno estabilizado queda **autorizado** crear y ejecutar archivos `.py` estructurados **permanentes** dentro del proyecto (manteniendo siempre registro documental). Los artefactos deben ser **persistentes y trazables en el entorno oficial** del proyecto; no existe regla que exija archivos temporales por seguridad (no dejar resultados solo en `%TEMP%`).

## 3. No modificar notebooks existentes sin autorización.

No modificar estos notebooks sin autorización explícita:
- `agente_financiero/puc.ipynb`
- `agente_financiero/agente.ipynb`
- `agente_financiero/contexto_contable.ipynb`
- `agente_financiero/evidencia.ipynb`
- `agente_financiero/pruebas.ipynb`
- `Estados_Financieros/Analisis_Financiero.ipynb`

Cualquier modificación requiere decisión documentada y autorización.

## 4. No eliminar archivos sin autorización.

No eliminar archivos ni carpetas sin autorización explícita. Los archivos `.py` creados anteriormente deben solamente quedar REGISTRADOS en la documentación. No eliminarlos en esta fase.

## 5. No instalar paquetes sin autorización.

No instalar paquetes Python, extensiones, dependencias, herramientas o plugins sin autorización explícita. El entorno actual debe conocerse y usarse responsablemente.

## 6. No duplicar funciones existentes.

Antes de crear cualquier nueva función o variable, verificar que no existe ya en el proyecto (revisar notebooks, CONTRATO_DATOS.md, catálogos). La duplicación introduce mantenimiento y riesgo de inconsistencia.

## 7. No duplicar catálogos.

Antes de crear nuevos catálogos o listas de verificación, verificar que no existen ya (revisar `02_VARIABLES_MADRE.md`, fases anteriores). El catálogo maestro debe ser único y evolucionar por adición, no por replicación.

## 8. No hardcodear parámetros que deben ser configurables.

Parámetros como la ventana histórica (2-5 años), tolerancias de consistencia, rangos de confianza, deben definirse como configurables, no hardcodeados en el código o notebooks.

## 9. Mantener trazabilidad.

Cada dato relevante debe poder relacionarse con: empresa, período, documento, tipo de documento, página/hoja, concepto original, variable madre, valor, unidad, fuente, nivel de confianza, estado de validación. Esta regla es irrenunciable.

## 10. Mantener separación entre extracción, variables madre, indicadores, diagnóstico y presentación.

Las cinco capas del sistema deben mantenerse separadas y no mezclarse indistintamente:
- Extracción: lectura y extracción de datos brutos
- Variables madre: datos fuente primarios
- Indicadores: cálculos derivados de variables madre
- Diagnóstico: validación, consistencia, hallazgos
- Presentación: Excel, HTML, Power BI

## 11. No confundir cuenta madre con indicador derivado.

**Regla de oro:** Si requiere una fórmula matemática para obtenerse → **NO es variable madre**, es **indicador derivado**. Esta distinción debe quedar clara en toda la documentación y código.

## 12. Respetar ventana histórica 2–5 años.

La ventana de análisis histórico debe permitir mínimo 2 años y máximo 5 años para el análisis estándar. La carpeta puede contener información histórica superior a 5 años, la cual debe conservarse como contexto pero no usarse en cálculos estándar sin autorización.

## 13. Admitir múltiples documentos.

El agente debe poder procesar múltiples documentos por empresa, no asumir `1 empresa = 1 PDF`. La carpeta documental puede contener estados de diferentes años, formatos mixtos y tipos documentales variados.

## 14. Admitir múltiples formatos.

El agente debe poder procesar PDF, XLSX, XLS, CSV, DOCX, TXT y, en futuro, otros formatos. No convertir automáticamente todo a un solo formato.

## 15. No asumir que todos los documentos corresponden a un único período.

Un documento puede contener un año, dos años comparativos, varios años, información histórica o prospectiva. El agente debe detectar los períodos reales contenidos.

## 16. Registrar incertidumbre.

Si la extracción o validación encuentra ambigüedad, la respuesta más segura es devolver `DUDOSO` o `NO_ENCONTRADO` en lugar de inventar valores. La conservadurismo es preferible a la inventación.

## 17. No presentar como hecho aquello que no haya sido verificado.

Los resultados del agente deben reflejar siempre el estado de evidencia disponible. No afirmar conclusiones que no están respaldados por los datos extraídos y validados.

## 18. Si una instrucción del usuario contradice una arquitectura previa, detenerse y solicitar confirmación.

Cuando un usuario indique una dirección que choca con la arquitectura documentada (AGENTS.md, 00_ESTADO_MAESTRO.md, 01_ARQUITECTURA.md, etc.), detener el trabajo actual y solicitar confirmación explícita antes de proceder. No asumir que la arquitectura antigua estaba equivocada ni que la nueva instrucción sustituye el diseño sin discusión.

## 19. Si una variable requiere interpolar datos faltantes, devolver NO_ENCONTRADO.

Nunca interpolar datos faltantes. Si no hay evidencia para un período o variable específica, devolver `NO_ENCONTRADO`. La interpolación está prohibida por regla de integridad del dato.

## 20. Distinción entre variable madre, indicador derivado y prueba/auditoría/red flag.

**Regla de oro:** Si requiere una fórmula matemática para obtenerse → **NO es variable madre**, es **indicador derivado**. Si es un análisis de screening sobre variables madre → **es prueba/auditoría/red flag**.

**Clasificaciones definitivas:**

| Tipo | definición | Fórmula | Ejemplo |
|------|-----------|---------|---------|
| variable_madre | Dato fuente primario | Ninguna | efectivo_y_equivalentes, activo_total, utilidad_neta |
| indicador_derivado | Cálculo matemático combinando 1+ variables madre | Requiere fórmula | razon_corriente, ROE, EBITDA |
| prueba_auditoria_red_flag | Análisis de screening con criterios y umbrales | Umbrales y criterios, no fórmula única | Beneish M-Score > -1,78, Accruals Ratio > 0,10, Divergencia utilidad-CFO |

**Salida esperada en todos los casos:**

- `tipo_dato` en el diccionario de variables debe indicar: `variable_madre`, `indicador_derivado`, o `prueba_auditoria_red_flag`
- El resultado de una prueba/auditoría/red flag debe expresarse como: `RED_FLAG / SEÑAL DE ALERTA`, nunca como `FRAUDE CONFIRMADO`
- Una red flag debe generar investigación/documentation adicional, no conclusión definitiva.

**Distinción crítica:**

- **FALTA INFORMACIÓN NECESARIA PARA LA PRUEBA** → generar requerimiento al usuario (tipo: FUENTE_REQUERIDA o DOCUMENTO_REQUERIDO según qué falte)
- **FALTA INFORMACIÓN QUE NO ES NECESARIA PARA CONTINUAR LA PRUEBA** → NO generar requerimiento; el agente puede calcular qué pueda y marcar lo restante como NO_CALCULABLE

---

## 21. Respetar la separación entre cuenta madre e indicador derivado en toda salida.

Todo dato saliente del agente debe clasificarse explícitamente como:
- `variable_madre` — dato fuente primario, extraíble directamente
- `indicador_derivado` — cálculo que combina una o más variables madre

La clasificación debe aparecer en la estructura de salida (ej: campo `tipo_dato` o campo `clasificacion` en el diccionario de variables).

---

## 22. No crear atajos que eviten la detección de períodos reales.

El agente debe siempre detectar el período real contenido en cada documento, no asumirlo por el nombre del archivo, nombre de la carpeta o posición en el tiempo. Los atajos que eviten esta detección están prohibidos.

---

## 23. Registrar toda decisión de diseño como documentación.

Cualquier decisión de arquitectura, diseño de catálogo, regla metodológica o cambio de comportamiento debe registrarse inmediatamente en la documentación correspondiente (preferiblemente en `07_HISTORIAL_DE_CAMBIOS.md` o en los archivos de especificación pertinentes).

## 24. No modificar la estructura de carpetas de documentación.

La carpeta `DOCUMENTACION_PROYECTO/` y su contenido (archivos `00_ESTADO_MAESTRO.md` hasta `07_HISTORIAL_DE_CAMBIOS.md`) deben mantenerse intactos como estructura de referencia. No reorganizar, renombrar ni eliminar archivos de esta carpeta sin autorización explícita.

## 25. El agente debe funcionar aunque no existan todos los documentos.

El diseño del agente debe contemplar que no todos los documentos de tipos INFORME_GESTION, ESTADO_SITUACION_FINANCIERA, etc., estarán presentes en toda carpeta. El agente debe identificar los que encuentra y procesar solo los disponibles, registrando como `NO_ENCONTRADO` aquellos que esperaría pero no existen.

---

## 26. REGLA MAESTRA DE FUENTES Y JERARQUÍA OBLIGATORIA

### 26.1. OBJETIVO

Establecer formalmente la política obligatoria de fuentes documentales que deberá cumplir el agente durante todo el proceso de extracción, validación, cálculo de indicadores y análisis financiero. Esta regla es irrenunciable y forma parte integral de la arquitectura documental del proyecto.

### 26.2. CATEGORÍAS OFICIALES DE FUENTES DOCUMENTALES PRIMARIAS

La información financiera deberá buscarse prioritariamente en los DOCUMENTOS FUENTE PRIMARIOS OFICIALES disponibles para cada entidad. Estas cuatro categorías constituyen las fuentes documentales primarias del proyecto:

1. **ESTADOS FINANCIEROS** — Estados de situación financiera, resultados, cambios en el patrimonio y flujos de efectivo.
2. **INFORME DE GESTIÓN** — Informes que contienen información sobre el funcionamiento de la empresa, evolución del negocio, crecimiento, estrategia, mercado, riesgos, perspectivas, etc.
3. **INFORME DE AUDITORÍA** — Informes de auditoría que proporcionan opinión, salvedades, observaciones y hallazgos sobre la información financiera.
4. **OTROS DOCUMENTOS OFICIALES** — Cualquier otro documento oficial relevante para la entidad (actas de asamblea, certificados, comunicados, etc.). **La categoría "OTROS" NO significa XBRL exclusivamente**. Dependerá de la entidad y de la documentación oficial disponible.

### 26.3. JERARQUÍA OBLIGATORIA DE FUENTES

Cuando el agente necesite obtener una variable madre, deberá seguir este orden obligatorio:

**PRIMER NIVEL:** Estados Financieros.

**SEGUNDO NIVEL:** Informe de Gestión.

**TERCER NIVEL:** Informe de Auditoría.

**CUARTO NIVEL:** Otros documentos oficiales relevantes disponibles.

**QUINTO NIVEL:** XBRL oficial, únicamente cuando exista para la entidad y cuando el dato requerido no haya podido obtenerse de forma suficiente mediante los documentos fuente primarios anteriores.

### 26.4. REGLA DE PRIORIDAD

Si un dato está disponible de manera suficiente y verificable en un documento fuente primario, el agente **DEBE** utilizar ese dato y **NO** sustituirlo automáticamente por un dato obtenido de XBRL.

El XBRL funciona como **FUENTE SECUNDARIA DE RECUPERACIÓN**, no como sustituto automático de las fuentes documentales primarias.

### 26.5.1. EXCEPCIÓN AÑO 2025 (XBRL)
Para el ejercicio del año 2025, el archivo XBRL descargado de la Superintendencia Financiera será considerado **fuente primaria** independientemente de la coincidencia del NIT de la entidad, basándose en la validación directa de la fuente oficial (Superfinanciera).

El agente podrá acudir al XBRL solo cuando cumplan todas las siguientes condiciones:

* El dato no aparezca en los documentos primarios (ESTADOS FINANCIEROS, INFORME DE GESTIÓN, INFORME DE AUDITORÍA, OTROS DOCUMENTOS OFICIALES);
* El dato no pueda identificarse suficientemente en los documentos primarios;
* El documento primario tenga una limitación de extracción que lo haga insuficiente;
* El documento primario sea ilegible para el proceso automatizado;
* Exista una necesidad de complementar o recuperar información que no pudo obtenerse de los documentos primarios.

Cuando utilice XBRL, deberá conservar obligatoriamente:

* archivo XBRL utilizado;
* entidad;
* período;
* concepto;
* valor;
* unidad;
* contexto;
* variable madre relacionada;
* evidencia;
* motivo por el cual fue necesario acudir al XBRL.

**Prohibiciones:**

* NO utilizar XBRL simplemente porque sea más fácil de procesar.
* NO reemplazar un valor de Estados Financieros por un valor XBRL sin justificación.
* NO combinar valores de diferentes fuentes sin conservar su procedencia.
* NO inventar información cuando ninguna fuente permita obtenerla.

### 26.6. REGLA DE TRAZABILIDAD

Todo dato utilizado por el agente deberá poder rastrearse mediante:

`DOCUMENTO → ENTIDAD → PERÍODO → DATO → VARIABLE MADRE → FUENTE → EVIDENCIA → VALIDACIÓN → INDICADOR`.

La fuente utilizada deberá quedar registrada explícitamente.

Los estados de información deberán distinguir, como mínimo, entre:

* **FUENTE_PRIMARIA** — Dato obtenido de ESTADOS FINANCIEROS, INFORME DE GESTIÓN, INFORME DE AUDITORÍA u otros documentos oficiales oficiales.
* **FUENTE_SECUNDARIA_XBRL** — Dato obtenido de XBRL oficial cuando las condiciones de la Sección 26.5 se cumplen.
* **PENDIENTE_VALIDACION** — Dato cuya procedencia o validez requiere confirmación adicional.
* **NO_DISPONIBLE** — Dato que no ha sido posible obtener de ninguna fuente autorizada.

No se crearán otros estados sin necesidad.

### 26.7. REGLA PARA ENTIDADES SIN XBRL

Si una entidad no dispone de XBRL oficial aplicable, el agente **NO** deberá intentar buscar XBRL de otra entidad ni utilizar una fuente no autorizada para reemplazarlo.

Deberá continuar utilizando los documentos fuente primarios disponibles.

Si después de revisar las fuentes autorizadas el dato continúa sin estar disponible, deberá registrarlo como faltante y aplicar las reglas existentes de `REQUERIMIENTOS_USUARIO.xlsx` cuando corresponda.

### 26.8. REGLA DE NO INVENCIÓN

El agente NO podrá:

* inventar valores;
* interpolar valores faltantes;
* estimar valores financieros sin autorización metodológica;
* sustituir un dato por otro conceptualmente parecido;
* asumir equivalencias contables no demostradas;
* modificar las variables madre para acomodar una fuente;
* modificar indicadores para acomodar datos disponibles.

La ausencia de información debe permanecer explícitamente identificada como ausencia de información.

### 26.9. CONSECUENCIAS DE NO CUMPLIR

El incumplimiento de la REGLA MAESTRA DE FUENTES conllevará:

* Invalidación del resultado del proceso afectado.
* Generación de requerimiento al usuario para regularizar la situación.
* Posible reinicio del proceso desde el punto de incumplimiento una vez regularizada la fuente.
* Registro de la infracción en el historial de decisiones (`07_HISTORIAL_DE_CAMBIOS.md`).

---

## 27. Respetar la separación entre cuenta madre e indicador derivado en toda salida.

## 28. No crear atajos que eviten la detección de períodos reales.

## 29. Registrar toda decisión de diseño como documentación.

## 30. No modificar la estructura de carpetas de documentación.

## 31. El agente debe funcionar aunque no existan todos los documentos.

## 31. Extracción documental híbrida (copiar desde la línea 390 original)

---
EOF