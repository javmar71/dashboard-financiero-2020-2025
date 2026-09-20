# 04_FUENTES_DOCUMENTALES.md — ARQUITECTURA DOCUMENTAL

## OBJETIVO

Documentar la arquitectura documental del proyecto. Queda claro que el agente no debe asumir `1 empresa = 1 PDF`. Debe asumir `1 empresa = conjunto documental`.

---

## 1. PRINCIPIO FUNDAMENTAL

**EL AGENTE NO DEBE ASUMIR: `1 empresa = 1 PDF`.**

**EL AGENTE DEBE ASUMIR: `1 empresa = conjunto documental`.**

Una empresa puede proporcionar una carpeta que contenga múltiples documentos correspondientes a varios períodos. El agente debe analizar el conjunto documental, no depender de un único PDF.

---

## 2. EJEMPLO DE ESTRUCTURA DE CARPETA

```text
EMPRESA
│
├── 2022
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
├── 2023
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
├── 2024
│   ├── Estados financieros
│   ├── Notas
│   ├── Informe gestión
│   └── Auditoría
│
└── Excel / información regulatoria
```

**El agente debe identificar en cada documento:**

- año
- tipo documental
- empresa
- período
- formato
- contenido
- relevancia

---

## 3. TIPOS DE DOCUMENTOS QUE EL AGENTE DEBE RECONOCER

Como mínimo:

1. INFORME_GESTION
2. ESTADO_SITUACION_FINANCIERA
3. ESTADO_RESULTADOS
4. ESTADO_CAMBIOS_PATRIMONIO
5. ESTADO_FLUJOS_EFECTIVO
6. NOTAS_ESTADOS_FINANCIEROS
7. INFORME_AUDITORIA
8. INFORME_ANUAL
9. ACTAS_ASAMBLEA
10. INFORMACION_FINANCIERA_EXCEL
11. OTRO_DOCUMENTO_FINANCIERO

**No asumir que todos los documentos estarán presentes.** El agente identifica los que encuentra.

---

## 4. FORMATOS DE ARCHIVO

El agente debe contemplar como fuentes:

- PDF
- XLSX
- XLS
- CSV
- DOCX
- TXT

**La arquitectura debe permitir incorporar posteriormente otros formatos.**

**NO convertir automáticamente todo a PDF.** Cada formato se procesa utilizando su naturaleza original.

## 4B. PROCESO DE EXTRACCIÓN HÍBRIDA

El agente debe seguir esta secuencia para cada fuente documental:

1. **EXTRACTIÓN PYTHON/DOCLING:** Intento inicial de extracción de texto y tablas.
   - Si Docling recupera correctamente el contenido → proceder a normalización.
   - Si Docling no recupera correctamente una estructura → pasar al paso 2.

2. **EXTRACTIÓN IA MULTIMODAL (fallback):** Cuando la extracción convencional no sea suficiente.
   - Interpretación visual del documento para recuperar estructuras no detectadas.
   - La IA multimodal NO debe inventar valores, completar cifras faltantes ni interpolar.
   - La salida de la IA debe marcarse con baja confianza y someterse avalidación Python.

3. **NORMALIZACIÓN Y VALIDACIÓN PYTHON:** Recibo del resultado de la IA (si fue necesario) o del resultado de Docling.
   - Normalización de unidades, períodos y valores.
   - Validación de consistencia contable.
   - Control de duplicados.
   - Conservación de trazabilidad completa.

**En todo caso, el dato extraído deberá conservar como mínimo:**
- empresa, documento, tipo_documento, período, página, tabla, fila/concepto, columna/período, valor, unidad, variable_madre, método_extracción, confianza, estado_validación, evidencia/origen.

---

## 5. PRIORIDAD DEL EXCEL

Cuando exista información financiera estructurada en Excel y corresponda al mismo período, empresa y alcance que una información presentada en PDF:

**PREFERENTE:** Excel estructurado ↓ Estado financiero estructurado en PDF ↓ Notas ↓ Informe de gestión ↓ Otros documentos

**Estas demás fuentes se utilizan para:**
- Corroboración
- Contexto
- Desagregación
- Evidencia
- Explicación de variaciones
- Detección de inconsistencias

---

## 6. NO ASUMIR QUE UN DOCUMENTO = UN AÑO

Un documento puede contener:

- Un año
- Dos años comparativos
- Varios años
- Información histórica
- Información prospectiva

**El agente debe detectar el período real contenido en cada documento, no asumirlo por el nombre del archivo.**

*Ejemplo:* `Estados_Financieros_2025.pdf` puede contener `2025` y `2024`.

---

## 7. NO ASUMIR QUE EL NOMBRE DEL ARCHIVO ES SUFICIENTE

La clasificación documental debe utilizar:

- nombre del archivo
- extensión
- contenido
- encabezados
- títulos
- fechas
- períodos
- nombre de empresa
- estructura de tablas
- contexto

**Si existe contradicción: NO resolver silenciosamente.**

**Registrar: INCONSISTENCIA_DOCUMENTAL**

---

## 8. ACTAS DE ASAMBLEA

Las actas de asamblea deben considerarse **FUENTES DE CONTEXTO CORPORATIVO**. No deben tratarse como estados financieros.

**Pueden aportar información sobre:**

- aprobación de estados financieros
- distribución de utilidades
- dividendos
- capitalizaciones
- cambios patrimoniales
- decisiones societarias
- hechos relevantes
- decisiones estratégicas
- operaciones extraordinarias

**Esta información debe alimentar el CONTEXTO DEL AGENTE y no mezclarse con variables contables puras.**

---

## 9. INFORME DE AUDITORÍA

El informe de auditoría debe procesarse como una **fuente independiente**.

**Debe permitir identificar:**

- opinión del auditor
- opinión limpia
- salvedades
- opinión adversa
- abstención
- énfasis
- cuestiones clave de auditoría
- incertidumbres relevantes
- referencias a continuidad
- inconsistencias o riesgos señalados

**La información del auditor debe formar parte del DIAGNÓSTICO y de la EVIDENCIA.**

**NO modificar cifras contables basándose en la opinión del auditor.**

---

## 10. NOTAS CONTABLES

Las notas deben ser consideradas una fuente fundamental para ampliar variables madre.

**Especialmente:**

- composición de deuda
- vencimientos
- tasas
- obligaciones financieras
- arrendamientos
- depreciaciones
- amortizaciones
- deterioros
- provisiones
- contingencias
- inversiones
- inventarios
- cuentas por cobrar
- partes relacionadas
- compromisos
- hechos posteriores

---

## 11. INFORME DE GESTIÓN

Debe utilizarse para información que no necesariamente aparece como cuenta contable.

**Ejemplos:**

- evolución del negocio
- crecimiento
- estrategia
- mercado
- participación
- eficiencia
- riesgos
- perspectivas
- hechos relevantes
- segmentos
- calidad de resultados
- explicación de variaciones

**El agente debe distinguir:**

- DATO_CONTABLE vs. CONTEXTO_GERENCIAL

---

## 12. EXCEL FINANCIERO

Cuando existan archivos Excel provenientes de la empresa o de información financiera reportada:

**El agente debe:**

- identificar hojas
- identificar tablas
- identificar períodos
- identificar unidades
- identificar encabezados
- detectar fórmulas
- detectar valores
- detectar celdas vacías
- detectar duplicados
- identificar estados financieros
- identificar variables contables

**No limitarse a leer únicamente la primera hoja.** Construir un inventario de hojas y estructuras.

---

## 13. CONVERGENCIA DE FUENTES

Todas las fuentes deben alimentar una estructura común:

```
DOCUMENTO
↓
TIPO_DOCUMENTO
↓
PERÍODO
↓
INFORMACIÓN EXTRAÍDA
↓
VARIABLE MADRE / CONTEXTO
↓
EVIDENCIA
↓
VALIDACIÓN
↓
INDICADOR
↓
DIAGNÓSTICO
```

**Cada dato conserva:**

fuente, tipo_documento, archivo, período, página/hoja, sección/celda cuando corresponda, valor, unidad, confianza, estado

---

## 14. REGLA FUNDAMENTAL

**NO mezclar automáticamente información proveniente de:**

- estados financieros
- notas
- gestión
- auditoría
- actas
- Excel

**Cada dato debe conservar:**

fuente, tipo_documento, archivo, período, página/hoja, sección/celda cuando corresponda, valor, unidad, confianza, estado

---

## 15. VENTANA HISTÓRICA EN EXTRACCIÓN

La ventana estándar de análisis continuará siendo:

- **MÍNIMO:** 2 años
- **MÁXIMO:** 5 años

**Pero la carpeta puede contener información histórica superior a 5 años.**

**El agente:**

- identifica todo lo disponible
- conserva el inventario
- selecciona hasta 5 años para el análisis estándar
- utiliza información anterior como contexto cuando sea relevante

---

## 16. ARCHIVOS DE SOPORTE EN PROYECTO

Esta arquitectura se complementa con la especificación en `DOCUMENTACION_PROYECTO/`:

- `01_ARQUITECTURA.md` — Arquitectura general del sistema
- `02_VARIABLES_MADRE.md` — Catálogo de 112 variables madre
- `03_INDICADORES.md` — Fórmulas e requerimientos de cada indicador
- `05_SALIDAS_Y_POWER_BI.md` — Capas de presentación
- `06_REGLAS_DEL_PROYECTO.md` — Reglas permanentes
- `07_HISTORIAL_DE_CAMBIOS.md` — Registro de eventos del proyecto

---

## 17. POLÍTICA DE UTILIZACIÓN DE FUENTES EXTERNAS

### 17.1. Objetivo

Establecer las reglas operativas y documentales sobre el uso de fuentes externas en el análisis financiero del agente. El principio rector es:

**LA VERSION ACTUAL DEL AGENTE NO REALIZA BÚSQUEDA AUTOMÁTICA DE FUENTES EXTERNAS POR INTERNET.**

La documentación proporcionada por el usuario constituye la fuente primaria del análisis financiero. Las fuentes externas son complementarias, de corroboración, contextualización o recuperación de información faltante **solo cuando el usuario las aporte**. Nunca deben sustituir silenciosamente un dato de la fuente primaria.

> **Versión actual:** Sin automatización de consultas a Superintendencias, DANE, RUES, Banco de la República u otras fuentes Internet. La búsqueda automática queda fuera del alcance de esta versión.

### 17.2. Cuándo puede el agente salir de los documentos del usuario

#### NIVEL 1 — FUENTE PRIMARIA

Primero debe trabajar con:

- Estados financieros oficiales de la empresa.
- Notas a los estados financieros.
- Información financiera oficial entregada por el usuario.
- Otros documentos corporativos proporcionados por el usuario cuando sean pertinentes.

Los estados financieros y sus notas tienen prioridad para los datos financieros.

#### NIVEL 2 — REQUERIMIENTO AL USUARIO (MECANISMO OFICIAL)

Si un dato necesario no está disponible en los documentos proporcionados:

1. El agente debe determinar si realmente necesita ese dato.
2. Si es necesario, **el agente debe generar un requerimiento formal al usuario** especificando:
   - el dato que falta
   - el tipo de documento o información requerida
   - la razón por la que se necesita
3. El agente debe esperar la respuesta del usuario.

> **El agente NO debe salir automáticamente a Internet ni consultar fuentes externas** por cuenta propia ante cualquier ausencia de información.

> **El agente NO debe intentar recuperar información automáticamente** de Superintendencias, DANE, RUES, Banco de la República u otras fuentes Internet en la versión actual.

#### NIVEL 3 — FUENTES EXTERNAS CUANDO EL USUARIO las aporte

Fuentes externas podrán considerarse solo cuando el usuario:

1. Aporte espontánea o explícitamente el documento o información solicitada, o
2. Autorice al agente para consultar una fuente específica y resulte del flujo definido.

Cuando el usuario aporte la información externa, el agente la clasificará según la Sección 18 ( Clasificación Definitiva de Fuentes Externas) y la integrará al análisis siguiendo las reglas de fuente primaria/secundaria.

La consulta externa registrada nunca debe convertirse automáticamente en sustitución de la fuente primaria. En la versión actual, esta vía está fuera del flujo operativo automático.

> **Regla transversal definitiva:** Si el agente no puede completar una tarea por falta de información, debe generar un requerimiento para el usuario. Una vez que el usuario aporte la información, el agente reanuda el procesamiento desde el punto pendiente.

### 17.3. Jerarquía de fuentes

La jerarquía conceptual mantiene su sentido para la definición del proyecto a futuro, pero **en la versión actual el agente no consulta automáticamente ninguna fuente externa**:

#### Prioridad A — Fuente primaria empresarial (SOLO EN VERSION ACTUAL)

Máxima prioridad y **única vía automática** de la versión actual:

- Estados financieros oficiales de la empresa.
- Notas.
- Informes financieros oficiales de la empresa.
- Información auditada cuando corresponda.

> **Todas las demás prioridades (B-E) requieren aporte del usuario y NO son búsquedas automáticas.**

#### Prioridad B — Fuentes regulatorias/oficiales (con aportación de usuario)

Como fuentes secundarias de alta confiabilidad **cuando el usuario las aporte**:

- Superintendencia Financiera de Colombia — cuando el usuario aporte el documento.
- SIMEV y sistemas regulatorios relacionados — cuando el usuario aporte la información.
- Información XBRL/regulatoria — cuando el usuario la proporcione.
- Superintendencia de Sociedades — cuando el usuario aporte el documento.
- Banco de la República para información macroeconómica oficial — cuando el usuario la aporte.
- DANE para estadísticas oficiales — cuando el usuario la aporte.
- Otras entidades públicas oficiales pertinentes según el tipo de dato — cuando el usuario la aporte.

> **Restricción versión actual:** El agente no consulta estas fuentes automáticamente. Solo se consideran cuando el usuario las proporciona.

#### Prioridad C — Fuentes corporativas públicas (con aportación de usuario)

Cuando corresponda y el usuario las aporte:

- Sitio web oficial de la empresa.
- Informes corporativos públicos.
- Informes de sostenibilidad.
- Informes de gestión.
- Comunicados oficiales.
- Presentaciones corporativas.

#### Prioridad D — Fuentes de mercado y terceros especializados (con aportación de usuario)

Solo cuando sean pertinentes y el usuario las aporte:

- Bolsas de valores.
- Proveedores de información financiera.
- Agencias calificadoras.
- Fuentes sectoriales reconocidas.
- Bases de datos financieras.

#### Prioridad E — Fuentes abiertas no oficiales (con aportación de usuario)

Blogs, prensa, páginas informativas, etc. Solo cuando el usuario las aporte y justifique su uso.

> **Nota:** El agente no realizará búsquedas automáticas en ninguna de estas categorías en la versión actual. Todas las fuentes externas requieren aporte explícito del usuario.

### 17.4. Qué información puede obtener el agente de fuentes externas

#### A. Corroboración

Ejemplo:

El estado financiero reporta:

Activo total = X

Una fuente regulatoria reporta el mismo valor.

Resultado:

`CORROBORADO`

No se reemplaza el dato original.

#### B. Complementación

Ejemplo:

Los documentos del usuario no contienen determinada información sectorial o macroeconómica necesaria para contextualizar el desempeño.

El agente puede obtenerla externamente.

Resultado:

`COMPLEMENTARIA`

#### C. Contextualización

Puede obtener:

- Información macroeconómica.
- Variables sectoriales.
- Condiciones regulatorias.
- Información de mercado.
- Eventos corporativos relevantes.
- Información pública que permita interpretar cambios financieros.

#### D. Recuperación de información faltante

Cuando el dato sea necesario y:

- No esté disponible en los documentos del usuario.
- El usuario no pueda aportarlo.
- Exista una fuente externa confiable.

Podrá utilizarse como información secundaria. Debe quedar marcada:

`FUENTE_SECUNDARIA`

y, cuando corresponda:

`PENDIENTE_VALIDACION`

#### E. Detección de discrepancias

Las fuentes externas pueden utilizarse para detectar diferencias entre registros.

Esto es una función importante del agente.

### 17.5. Regla crítica: primaria vs secundaria

Implementar formalmente estas cuatro situaciones.

#### CASO 1 — Solo existe fuente primaria

Usar el dato primario.

Estado:

`FUENTE_PRIMARIA`

#### CASO 2 — Existe primaria y secundaria y coinciden

Conservar el dato primario.

Registrar la secundaria como corroboración.

Estado:

`CORROBORADO`

#### CASO 3 — No existe primaria pero existe secundaria

No presentar el dato como si fuera primario.

Conservarlo como:

`FUENTE_SECUNDARIA`

y marcar:

`PENDIENTE_VALIDACION`

si el dato tiene relevancia material.

#### CASO 4 — Primaria y secundaria presentan valores diferentes

**NO sobrescribir ninguno.**

Conservar ambos registros y generar:

`ALERTA_DISCREPANCIA_FUENTES`

Registrar:

- valor primario;
- valor secundario;
- unidad;
- período;
- fecha de corte;
- fecha de reporte;
- fecha de publicación;
- documento;
- fuente;
- contexto;
- explicación disponible;
- estado de validación.

El agente debe intentar determinar si la diferencia proviene de:

- período diferente.
- fecha de corte diferente.
- información intermedia vs anual.
- metodología diferente.
- reexpresión.
- consolidación vs información individual.
- actualización posterior.
- criterio regulatorio.
- error documental.

Si no puede determinarlo, debe conservar la discrepancia y solicitar validación.

### 17.6. Regla temporal obligatoria

No mezclar automáticamente información de diferentes períodos.

Cada dato debe conservar como mínimo:

- `fecha_corte`
- `periodo`
- `periodicidad`
- `fecha_reporte`
- `fecha_publicacion`
- `tipo_documento`
- `fuente`
- `nivel_fuente`
- `estado_validacion`

Ejemplo:

Un estado financiero anual a 31/12/2024 y un reporte regulatorio correspondiente a otra fecha NO deben combinarse automáticamente.

La equivalencia temporal debe verificarse antes de utilizar los datos conjuntamente.

### 17.7. La fuente externa no puede cambiar silenciosamente el histórico

Si posteriormente aparece una fuente externa que contradice un dato previamente registrado:

NO modificar silenciosamente el valor histórico.

Debe generarse una nueva evidencia/registro de la discrepancia.

El sistema debe conservar trazabilidad de:

`dato original → fuente → dato externo → discrepancia → resolución`

### 17.8. Regla especial para empresas supervisadas y no supervisadas

No aplicar el mismo flujo indiscriminadamente.

#### Empresa supervisada/regulada

El agente puede aprovechar fuentes regulatorias oficiales para:

- corroborar.
- complementar.
- identificar períodos.
- contextualizar.
- localizar información pública.
- detectar discrepancias.

Pero los estados financieros oficiales y sus notas siguen siendo la referencia primaria del análisis financiero.

#### Empresa no supervisada

La información suministrada por el usuario mantiene prioridad.

El agente puede consultar fuentes públicas cuando:

- El usuario las autorice.
- Exista una dirección web proporcionada por el usuario.
- Exista una fuente pública pertinente.
- Se requiera información contextual o complementaria.

Si una página bloquea bots, requiere autenticación o no puede ser consultada, **no interpretar automáticamente esa imposibilidad como ausencia de información de la empresa**.

### 17.9. Trazabilidad obligatoria

Todo dato obtenido externamente debe poder responder:

> ¿De dónde salió?

Por tanto, definir una estructura de evidencia que conserve como mínimo:

- empresa.
- variable/dato.
- valor.
- unidad.
- período.
- fecha de corte.
- fuente.
- URL o identificador de origen cuando exista.
- tipo de fuente.
- documento.
- página/sección cuando sea posible.
- fecha de consulta.
- nivel de fuente.
- estado de validación.
- observaciones.

### 17.10. No confundir fuentes externas con las 112 variables

Esta fase NO debe:

- modificar las 112 variables.
- agregar nuevas variables.
- eliminar variables.
- redefinir variables.
- calcular indicadores.
- mapear variables.
- ejecutar Fase 1.
- ejecutar Fase 5.

El objetivo es exclusivamente definir **de dónde puede obtener información el agente y cómo debe tratarla**.

### 17.11. Resultado esperado

La documentación debe incluir:

1. Objetivo.
2. **Principio de fuente primaria (confirmado: versión actual sin automatización externa).**
3. **Cuándo puede consultarse información externa: solo cuando el usuario la aporte.** (No hay búsqueda automática en esta versión).
4. Jerarquía de fuentes (conceptual, para futura evolución).
5. Tipos de información externa permitida (cuando el usuario la aporte).
6. Reglas primaria/secundaria.
7. Reglas para discrepancias.
8. Reglas temporales.
9. Reglas para empresas supervisadas y no supervisadas.
10. Trazabilidad.
11. Estados de validación.
12. **Casos en los que NO debe utilizarse información externa: en búsqueda automática (versión actual).**
13. Flujo operativo del agente (con requerimiento al usuario).

### 17.12. Flujo operativo que debe quedar documentado

Utiliza conceptualmente:

DOCUMENTOS DEL USUARIO
↓
¿Existe el dato necesario?
│
┌───┴───┐
SÍ       NO
│         │
↓         ↓
FUENTE     ¿Es necesario?
PRIMARIA       │
├── NO → continuar
│
└── SÍ
↓
¿Usuario puede aportarlo?
│
┌─────┴─────┐
SÍ           NO
│             │
↓             ↓
SOLICITAR AL USUARIO   FUENTE EXTERNA (FUERA DEL ALCANCE AUTOMÁTICO)
↓
VALIDAR Y ETIQUETAR
│
↓
COMPLEMENTAR / CORROBORAR
│
↓
TRAZABILIDAD

> **En ningún punto una fuente secundaria debe reemplazar silenciosamente una fuente primaria.**
>
> **Versión actual:** Si el agente no puede completar una tarea por falta de información,
> debe generar un requerimiento para el usuario. Una vez que el usuario aporte la información
> (documento, dato, aclaración), el agente reanuda el procesamiento desde el punto en que
> quedó pendiente. La búsqueda automática de fuentes externas (Superintendencias, DANE, RUES,
> Banco de la República, u otras Internet) queda FUERA DEL ALCANCE de la versión actual.
>
> **Flujo de decisión cuando falta información:**
> 1. Agente detecta información faltante en documentos del usuario
> 2. Agente genera requerimiento al usuario (solicita documento/dato)
> 3. Usuario aporta la información (puede ser documento externo, dato, aclaración)
> 4. Agente valida y etiqueta la información recibida (según Sección 18)
> 5. Agente reanuda procesamiento desde punto pendiente
> 6. Si el usuario no aporta, el proceso continúa con los datos disponibles
> 7. Nunca se realiza consulta automática a fuentes Internet en esta versión

### 17.12. Restricciones técnicas

Mantener las reglas permanentes del proyecto:

- Windows / PowerShell.
- Utilizar exclusivamente:

`C:\Users\Usuario\Desktop\mi_proyecto_finanzas\venv\Scripts\python.exe`

- Las librerías deben instalarse exclusivamente en:

`C:\Users\Usuario\Desktop\mi_proyecto_finanzas\venv\Lib\site-packages`

- NO crear otro entorno virtual.
- NO instalar dependencias en Python global.
- NO crear archivos `.py` dentro del proyecto.
- El proyecto debe continuar desarrollándose mediante notebooks y documentación.
- No modificar `02_VARIABLES_MADRE.md`.
- No modificar la definición de las 112 variables.
- No avanzar a Fase 1.
- No realizar extracción exhaustiva de documentos.
- No calcular indicadores.

### 17.13. Entrega final

Al finalizar:

1. **Documento actualizado:** `04_FUENTES_DOCUMENTALES.md` — Arquitectura Documental, sección 17 incorporada.
2. **Reglas formalizadas:** 13 políticas principales (secciones 17.1 a 17.13) sobre utilización de fuentes externas.
3. **Fuentes externas contempladas:** Niveles A-E (empresarial, regulatoria, corporativa, mercado, abiertas).
4. **Prioridad de fuente primaria:** Confirmada y establecida como regla irrenunciable.
5. **Discrepancias:** Conservadas y no sobrescritas; generan `ALERTA_DISCREPANCIA_FUENTES`.
6. **Fechas/períodos:** Mantener separados; verificar equivalencia temporal antes de combinar datos.
7. **112 variables:** NO fueron modificadas durante este proceso.
8. **Nuevos `.py` dentro del proyecto:** NO creados (documentación solo en `DOCUMENTACION_PROYECTO/`).
9. **Fase 0B CERRADA:** El archivo de raíz `Estados-Financieros.pdf` puede permanecer con período `NO_DETERMINADO` sin bloquear el procesamiento de los períodos 2021–2025. Los documentos financieros identificados para 2021–2025 son suficientes para continuar a la siguiente etapa. No solicitar al usuario información solo por la ausencia del período del documento de raíz.

---

### Nota de cierre de Fase 0B

**Estado actual de la Fase 0B: CERRADA.**

Las reglas definitivas establecen:

1. El archivo `Estados-Financieros.pdf` ubicado en la raíz de `Estados Financieros` puede permanecer con período `NO_DETERMINADO`. Su período desconocido NO bloquea el procesamiento de los períodos 2021–2025.

2. Los documentos financieros identificados para 2021–2025 son suficientes para continuar a la siguiente etapa. No solicitar al usuario completar información solo por la ausencia de ese período.

3. Fase 0B debe quedar registrada como CERRADA, dejando el archivo de raíz como pendiente de identificación no bloqueante.

4. NO modificar las 112 variables, NO realizar auditoría de variables y NO avanzar a extracción exhaustiva.

5. NO crear archivos `.py` dentro de `C:\Users\Usuario\Desktop\mi_proyecto_finanzas\`.

**Consecuencia:** La documentación 2021-2025 está cubierta y el proceso puede continuar sin necesidad de solicitar al usuario que determine el período del documento de raíz. El documento de raíz permanece como identificador pendiente pero no obstructivo.

### 18. CLASIFICACIÓN DE FUENTES EXTERNAS Y DE CONTEXTO

#### 18.1. Fuente contable empresarial primaria
**Estados Financieros oficiales de la empresa y sus Notas son la fuente primaria de información financiera.**

*Esta es la fuente principal para obtener información financiera de la empresa. Toda variable, indicador o análisis financiero debe fundamentarse primero en la información contenida en estos documentos.*

**Clasificación definitiva:**
- **ESTADOS FINANCIEROS + NOTAS** → Fuente contable primaria.
#### 18.2. Fuentes contables empresariales secundarias / de referencia (cuando el usuario las aporte)

**SFC/SIMEV, Superintendencia de Sociedades/SIIS y las demás Superintendencias cuando corresponda al tipo de entidad son fuentes contables empresariales secundarias o de referencia.**

> **Versión actual:** Estas fuentes NO son consultadas automáticamente por el agente. Solo se consideran como secundarias/de referencia **mientras el usuario las aporte dokumentalmente**. Cuando el usuario aporte un documento de Superintendencia, el agente la clasificará según esta sección.

*Estas fuentes pueden utilizarse para:*
- Corroborar información financiera de los Estados Financieros oficiales.
- Complementar datos no visibles en los estados financieros.
- Identificar períodos contables.
- Detectar discrepancias entre registros.
- Recuperar información financiera cuando corresponda y el usuario la haya aportado.

> **Regla fundamental (versión actual):** Nunca deben reemplazar silencientemente un dato proveniente de los Estados Financieros oficiales de la empresa. El agente no las consultará automáticamente.

**Si existe diferencia entre la fuente primaria y la Superintendencia, conservar ambos valores y generar ALERTA_DISCREPANCIA_FUENTES.**

> **Clasificación definitiva (cuando el usuario las aporte):**
> - **SUPERINTENDENCIAS** (SFC/SIMEV, Superintendencia de Sociedades, Supersalud, Superservicios/SUI, Supersolidaria y demás) → Fuente contable empresarial secundaria/de referencia (solo cuando el usuario las aporte).
#### 18.3. Fuentes externas de contexto (agente no consulta automáticamente)

**Estas fuentes NO son fuentes contables empresariales y NO deben clasificarse como tales.**

> **Versión actual:** El agente no consulta automáticamente estas fuentes por Internet. 
> Las clasificaciones que se presentan a continuación son definitivas para el tipo de fuente, 
> pero la consulta real dependerá aporte del usuario.

Incluyen:

**DANE:**
- Fuente oficial macroeconómica/contextual.
- Puede aportar IPC, inflación y otras variables económicas para interpretar el desempeño financiero.
- **Ejemplo:** Crecimiento real = (1 + crecimiento nominal) / (1 + inflación) - 1.
- **DANE no proporciona ni sustituye los Estados Financieros de la empresa.**

**RUES:**
- Fuente de contexto empresarial/registral.
- Puede aportar información sobre actividad económica, existencia y características registrales de la empresa y otros elementos de contexto.
- **RUES no es fuente contable y no debe utilizarse como sustituto de información financiera.**

**Banco de la República:**
- Fuente de contexto macroeconómico y monetario.
- Puede aportar tasas, inflación, condiciones monetarias y otras variables relevantes para interpretar el entorno económico.
- **No es fuente contable empresarial.**

**Otras fuentes oficiales o especializadas:**
- Se utilizarán exclusivamente como contexto económico, sectorial, empresarial, de mercado o institucional, según corresponda.
- Nunca como fuente contable empresarial primaria o secundaria.

> **Restricción versión actual:** El agente no realizará búsquedas automáticas a DANE, RUES, Banco de la República u otras fuentes Internet. Estas fuentes solo serán consideradas cuando el usuario las aporte dokumentalmente.

**Clasificación definitiva:**
- **DANE** → Contexto macroeconómico.
- **RUES** → Contexto empresarial/registral.
- **BANCO DE LA REPÚBLICA** → Contexto macroeconómico/monetario.
- **Otras fuentes oficiales o especializadas** → Contexto según corresponda.

#### 18.4. Fuentes no oficiales
**Se consideran únicamente fuentes de contexto o apoyo.**

*No deben utilizarse como fuente contable empresarial primaria ni secundaria.*

*Su utilización debe quedar identificada y trazable.*

*Incluye blogs, prensa, páginas informativas, redes sociales, opiniones de expertos no oficiales, etc.*

**Clasificación definitiva:**
- **FUENTES NO OFICIALES** → Contexto/apoyo.

---

#### 18.5. Regla fundamental de clasificación

**No clasificar una fuente como "contable" simplemente porque contenga información relacionada con una empresa.**

La pregunta que debe hacerse el agente es:

> **"¿Esta fuente proporciona información financiera/contable empresarial formal de la entidad?"**

Si la respuesta es **sí**:
→ Puede clasificarse como fuente contable, siempre que corresponda a Estados Financieros/Notas oficiales o a información financiera empresarial publicada por la Superintendencia competente.

Si la respuesta es **no**:
→ Debe clasificarse como **FUENTE DE CONTEXTO**.

**Por tanto:**

| Fuente | Clasificación |
|--------|--------------|
| ESTADOS FINANCIEROS + NOTAS | Fuente contable primaria |
| SUPERINTENDENCIAS (SFC/SIMEV, Superintendencia de Sociedades, etc.) | Fuente contable empresarial secundaria/de referencia |
| DANE | Contexto macroeconómico |
| RUES | Contexto empresarial/registral |
| BANCO DE LA REPÚBLICA | Contexto macroeconómico/monetario |
| OTRAS FUENTES NO OFICIALES | Contexto/apoyo |

---

**IMPORTANTE**

- No modificar las 112 variables.
- No avanzar a Fase 1 ni Fase 5.
- No realizar extracción exhaustiva.
- No crear archivos `.py` dentro de:
  `C:\Users\Usuario\Desktop\mi_proyecto_finanzas\`
- **Fuentes externas: la versión actual no realiza búsqueda automática. La incorporación de información externa requiere aporte explícito del usuario.** (Ver Sección 17.2 Nivel 2 y 17.12 Flujo operativo).

---
### 18.11. Entrega de la actualización

Al finalizar esta actualización:

1. **Archivo `.md` modificado:** `DOCUMENTACION_PROYECTO\04_FUENTES_DOCUMENTALES.md`.
2. **Sección modificada/creada:** Sección 18 "Clasificación Definitiva de Fuentes Externas" (4 categorías definitivas + regla fundamental + clasificación práctica).
3. **Clasificación final de cada tipo de fuente:** Establecida según la tabla de la regla 18.5.
4. **Sin contradicciones** con la documentación anterior; la Sección 18 reemplaza y actualiza los conceptos anteriores de la Sección 17 para especificar la clasificación definitiva.

**Fin de la sección de clasificación definitiva de fuentes externas.**