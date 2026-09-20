# 02_VARIABLES_MADRE.md — CATÁLOGO MAESTRO DE VARIABLES MADRE

## OBJETIVO

Diseñar un catálogo maestro de variables fuente que permita posteriormente calcular TODOS los indicadores financieros definidos para el proyecto.

El catálogo cubre como mínimo: liquidez, actividad/eficiencia, márgenes, rentabilidad, endeudamiento, apalancamiento, solidez, EBITDA, flujo de caja, capital de trabajo, WACC, estructura de capital, variables de notas, variables de informe de gestión, variables de auditoría, variables de gobierno corporativo/actas, variables externas requeridas.

---

## REGLA FUNDAMENTAL

**NO incorporar como variable madre ningún resultado que requiera una fórmula matemática.**

Ejemplos que **NO** son variables madre (son indicadores derivados):
- EBITDA, ROA, ROE, ROIC, WACC
- Margen EBITDA, Razón corriente, Prueba ácida
- Endeudamiento, Deuda/EBITDA, Flujo libre
- Cualquier ratio o cálculo que combine múltiples fuentes

Una variable madre debe representar un dato fuente que pueda ser:
- extraído;
- identificado;
- reportado;
- confirmado;
- localizado documentalmente.

---

## 1. ESTRUCTURA DEL CATÁLOGO

Para cada variable madre definir:

| Campo | Descripción |
|-------|-------------|
| variable_canonica | Nombre canonical estandarizado |
| nombre_descriptivo | Nombre humano legible |
| categoria | Liquidez, Actividad, Márgenes, Rentabilidad, etc. |
| subcategoria | Subclasificación dentro de la categoría |
| naturaleza | DEBITO, CREDITO, TEXT, PORCENTAJE, FECHA, NUMERICO |
| unidad | Moneda, Millones, Miles, %, etc. |
| periodicidad | Anual, Semestral, Quincenal, Mensual |
| tipo_dato | float, int, str, bool, DATE |
| fuente_preferente | Estado situación financiera, Notas, Gestión, Auditoría, Excel, Externa |
| fuentes_secundarias | Lista de fuentes alternativas posibles |
| documento_origen | Nombre del archivo o sección donde fue encontrado |
| requiere_nota | S/N — ¿necesita notas complementarias? |
| puede_provenir_excel | S/N |
| puede_provenir_pdf | S/N |
| puede_provenir_gestion | S/N |
| puede_provenir_auditoria | S/N |
| puede_provenir_acta | S/N |
| requiere_periodo | S/N — ¿necesita período actual? |
| requiere_periodo_anterior | S/N — ¿necesita período comparativo? |
| es_saldo | S/N — ¿es un saldo de cuenta? |
| es_flujo | S/N — ¿es un flujo (cash flow)? |
| es_porcentaje | S/N — ¿es un porcentaje? |
| es_monetaria | S/N — ¿es una cantidad monetaria? |
| es_cantidad | S/N — ¿es una cantidad (unidades)? |
| nivel_confianza_requerido | 0.0 a 1.0 |

---

## 2. FUENTES

Clasificar cada variable según su fuente primaria:

| Código | Fuente |
|--------|--------|
| A. | Estados financieros |
| B. | Notas contables |
| C. | Informe de gestión |
| D. | Informe de auditoría |
| E. | Actas de asamblea |
| F. | Excel financiero |
| G. | Fuente externa |

**Una variable puede tener más de una fuente posible, pero debe existir una FUENTE PREFERENTE.**

---

## 3. ESTADOS FINANCIEROS

Determinar todas las variables fuente necesarias provenientes de:

- **ESTADO DE SITUACIÓN FINANCIERA**
- **ESTADO DE RESULTADOS**
- **ESTADO DE CAMBIOS EN EL PATRIMONIO**
- **ESTADO DE FLUJOS DE EFECTIVO**

**No limitarse a las 21 cuentas actuales del PUC.** Determinar cuáles son REALMENTE necesarias para cubrir el universo de indicadores.

---

## 4. NOTAS CONTABLES

Identificar las variables fuente necesarias para obtener información que normalmente no aparece suficientemente desagregada en los estados principales.

**Como mínimo evaluar:**

| Variable | Descripción |
|----------|-------------|
| composicion_deuda | Desglose por tipo, moneda, garantía |
| deuda_financiera_corriente | Débitos a corto plazo |
| deuda_financiera_no_corriente | Débitos a largo plazo |
| tasas_interes | Tasa efectiva, diferida, mercado |
| vencimientos | Cronograma de amortizaciones |
| arrendamientos | Derecho de uso + obligación pago (IFRS 16/NIC 17) |
| deterioro_cuentas_por_cobrar | Provisiones por incobrabilidad |
| provisiones | Responsabilidades probables |
| composicion_inventarios | Mercancía, en Producción, Terminados |
| inversiones_detalle | Por tipo, valoración, plazos |
| activos_fijos | Neto depreciaciones acumuladas |
| adquisiciones_activos | CAPEX período |
| bajas_activos | Ventas/descarte activos |
| contingencias | Obligaciones inciertas |
| obligaciones_laborales | Pensiones, dotación, sueldos |
| impuestos | Impuesto corriente + diferido |
| impuestos_diferidos | Timing diferencia tributaria |
| partes_relacionadas | Transacciones accionistas |
| dividendos | Distribución utilidades |

**NO asumir que esta lista es exhaustiva.** Identificar qué variables adicionales son necesarias.

---

## 5. INFORME DE GESTIÓN

Identificar variables de contexto que permitan interpretar los indicadores.

**Como mínimo evaluar:**

| Variable | Categoría | Alimenta |
|----------|-----------|----------|
| evolucion_ingresos | Contexto gerencial | ROE, ROA, márgenes |
| evolucion_utilidad | Contexto gerencial | ROA, ROE, márgenes |
| crecimiento_organico | Contexto gerencial | Análisis negocio |
| crecimiento_adquisiciones | Contexto gerencial | Análisis estructural |
| participacion_mercado | Contexto gerencial | Análisis competitivo |
| ventas_por_segmento | Contexto gerencial | ROE segmento |
| desempeño_por_segmento | Contexto gerencial | Margen segmento |
| eficiencia_operativa | Contexto gerencial | Márgenes, rotaciones |
| productividad | Contexto gerencial | Costos, márgenes |
| numero_empleados | Contexto gerencial | ROE activos/persona |
| capex | Contexto financiero | Flujo libre |
| perspectivas | Contexto gerencial | Diagnóstico estratégico |
| riesgos | Contexto gerencial | Análisis riesgo |
| hechos_relevantes | Contexto gerencial | Eventos posteriores |
| calidad_resultados | Contexto gerencial | ROE/ROA calidad |
| cumplimiento_covenants | Contexto financiero | WEND, endeudamiento |

**Estas variables NO deben mezclarse con las cuentas contables.** Deben clasificarse como `CONTEXTO_GERENCIAL`.

---

## 6. AUDITORÍA

Definir variables documento para:

| Variable | Tipo | Uso en diagnóstico |
|----------|------|-------------------|
| tipo_opinion | Texto | Diagnóstico general |
| opinion_limpia | Booleano | Suficiencia contable |
| salvedades | Texto | Riesgos identificados |
| opinion_adversa | Booleano | Contraste cifras |
| abstencion | Booleano | Independencia |
| enfasis | Texto | Aspectos resaltados |
| cuestiones_key | Texto | Riesgos principales |
| incertidumbre | Texto | Continuidad empresa |

**Estas variables serán utilizadas por el motor de diagnóstico.**

---

## 7. ACTAS DE ASAMBLEA

Definir variables de contexto relacionadas con:

| Variable | Contexto que alimenta |
|----------|----------------------|
| dividendos | Política distribución |
| distribucion_utilidades | Decisión accionistas |
| capitalizaciones | Aumento capital |
| cambios_patrimoniales | Movimientos patrimonio |
| decisiones_sociedades | Acuerdos sociedad |
| operaciones_extraordinarias | Operaciones fuera ordinario |
| aprobacion_estados | Validación formal |
| hechos_relevantes | Impacto financiero |

**No convertir estas variables en cuentas contables.** Son de contexto corporativo.

---

## 8. EXCEL

El catálogo debe ser independiente del formato.

**Una variable madre puede ser extraída desde:**
- PDF
- Excel
- DOCX
- TXT
- etc.

**El formato NO define la variable.** La estructura financiera define la variable.

**El agente debe:**
- Identificar hojas
- Identificar tablas
- Identificar períodos
- Identificar unidades
- Identificar encabezados
- Detectar fórmulas
- Detectar valores
- Detectar celdas vacías
- Detectar duplicados
- Identificar estados financieros
- Identificar variables contables

**No limitarse a leer únicamente la primera hoja.** Construir inventario de hojas y estructuras.

---

## 9. WACC

**Separar explícitamente:**

### A. Variables contables (fuente interna)

| Variable | Descripción |
|----------|-------------|
| deuda_financiera | Total deuda del balance |
| efectivo | Efectivo y equivalentes |
| patrimonio | Patrimonio neto |
| deuda_neta | Deuda menos efectivo |
| impuestos | Impuestos por pagar/diferidos |
| gastos_financieros | Costo financiero del período |

### B. Variables externas (fuente externa, NO aparecen en estados)

| Variable | Fuente esperada |
|----------|----------------|
| tasa_libre_riesgo | Tesoro/Banco Central |
| prima_riesgo | Bloomberg/B.Central |
| prima_riesgo_pais | BAFER/B.Central |
| beta | Bloomberg/Compustat |
| costo_deuda | Mercado/Bancos |
| costo_patrimonio | CAPM o modelo de descuento |

**NO asumir que beta o prima de riesgo aparecen en los estados financieros.** Deben identificarse como `VARIABLES EXTERNAS`.

---

## 10. FLUJO DE CAJA

Determinar las variables fuente necesarias para construir:

| Flujo | Variables madre requeridas |
|-------|---------------------------|
| flujo_operativo | utilidad_neta + depreciaciones + amortizaciones + variacion_CapTrabajo + variacion_CXC + variacion_Inventarios + variacion_CxP |
| flujo_inversion | CAPEX, inversiones, adquisiciones |
| flujo_financiacion | Dividendos, emisión/amortización deuda |
| flujo_neto | Suma de los tres anteriores |
| flujo_libre | flujo_operativo - CAPEX |

**No asumir que "flujo operativo" es una variable madre.** Debe determinarse qué valores fuente permiten reconstruirlo.

**Evaluar específicamente:**

- utilidad_neta
- depreciaciones
- amortizaciones
- deterioros
- provisiones
- variaciones_de_capital_trabajo
- cxc (cuentas por cobrar)
- inventarios
- cxp (cuentas por pagar)
- inversiones
- CAPEX
- deuda
- dividendos
- otros_movimientos_relevantes

---

## 11. EBITDA

**Determinar las variables fuente necesarias para reconstruir EBITDA.**

**Como mínimo evaluar:**

| Variable | Origen |
|----------|--------|
| utilidad_operacional | Estado de resultados |
| depreciaciones | Estado situación/resultados |
| amortizaciones | Estado situación/resultados |

**NO crear "EBITDA" como cuenta madre.** Es un indicador derivado que se reconstruye a partir de variables madre.

---

## 12. APALANCAMIENTO

Determinar las variables históricas necesarias para calcular:

| Grado | Fórmula (conceptual) | Variables madre y requerimientos |
|-------|---------------------|--------------------------------|
| operativo | %ΔIngresos / %ΔUtilidad_operacional | Requiere serie histórica 2+ períodos |
| financiero | %ΔUtilidad_operacional / %ΔUtilidad_neta | Requiere serie histórica 2+ períodos |
| total | Combinado de los dos anteriores | Requiere serie histórica 2+ períodos |

**El diseño debe permitir disponer de una SERIE HISTÓRICA, no únicamente de un valor actual.** Ventana 2-5 años es mínima.

---

## 13. DIMENSIÓN TEMPORAL

**Todas las variables deberán diseñarse para trabajar con:**

- **MÍNIMO:** 2 años
- **MÁXIMO:** 5 años

**Registrar para cada variable:**

| Campo | Descripción |
|-------|-------------|
| período | Año ej: 2025 |
| valor | Valor numérico o texto |
| unidad | Moneda, %, etc. |
| fuente | Estado, Nota, Gestión, etc. |
| evidencia | Página, hoja, sección, celda |

**No interpolar datos faltantes.** Si no hay evidencia para un período dentro de la ventana, devolver `NO_ENCONTRADO`.

---

## 14. PUC ACTUAL

**NO eliminar el PUC actual.** Utilizarlo como REFERENCIA EXISTENTE.

### Comparación: PUC ACTUAL vs. CATÁLOGO MAESTRO PROPUESTO

Clasificar cada variable PUC como:

| Clasificacion | Descripción |
|--------------|-------------|
| REUTILIZABLE | Cuenta PUC = variable madre canónica directa (18 de 21) |
| REQUIERE_AMPLIACIÓN | Cuenta PUC existe pero requiere desagregación (ej: "Inversiones" → "corto/lon_plazo") |
| REQUIERE_NUEVA | No existe en PUC, debe añadirse |
| DEBE_EXCLUIRSE_POR_SER_DERIVADA | Es cálculo (ej: EBITDA, ROE) |
| DEBE_CLASIFICARSE_COMO_CONTEXTO | Información de gestión, actas, auditoría |
| DEBE_CLASIFICARSE_COMO_VARIABLE_EXTERNA | Datos de mercado, tasas externas |

### Resultado de la comparación:

| Total PUC | 21 variables |
|-----------|--------------|
| Reutilizables (85.7%) | 18 variables |
| Requieren ampliación (14.3%) | 3 variables |
| Descartadas por derivadas | 0 directamente, 30 en catálogo son derivadas (referencia) |

**Variables PUC definitivamente reutilizables:** efectivo_y_equivalentes, activo_total, pasivo_total, patrimonio, ingresos_operacionales, costo_ventas, utilidad_operacional (EBIT), utilidad_neta, y 13 más.

**Variables PUC que requieren ampliación:** inversiones (desagregación plazo), gastos operacionales (desagregación en costos/vendas/Administración).

---

## 15. RESULTADO ESPERADO

Entregar una MATRIZ MAESTRA con todas las variables fuente identificadas.

### Columnas mínimas:

| Columna | Descripción |
|---------|-------------|
| ID | Identificador único |
| variable_canonica | Nombre canonical |
| nombre | Nombre descriptivo |
| categoria | Liquidez, Actividad, Márgenes, etc. |
| subcategoria | Subclasificación |
| unidad | Moneda, %, etc. |
| tipo_dato | float, int, str, bool |
| naturaleza | DEBITO, CREDITO, TEXT, PORCENTAJE |
| fuente_preferente | A, B, C, D, E, F, G |
| fuentes_alternativas | Lista |
| documento_origen | Nombre archivo |
| es_contable | S/N |
| es_nota | S/N |
| es_gestion | S/N |
| es_auditoria | S/N |
| es_acta | S/N |
| es_externa | S/N |
| es_saldo | S/N |
| es_flujo | S/N |
| requiere_periodo_anterior | S/N |
| observaciones | Comentarios adicionales |

### Después construir:

| Matriz | Descripción |
|--------|-------------|
| MATRIZ_VARIABLE_MADRE → INDICADORES | Para cada variable madre, qué indicadores puede sostener |
| MATRIZ_INDICADOR → VARIABLES_MADRE | Para cada indicador, qué variables madre requiere |

---

## 16. CONTROL DE CALIDAD

**Antes de considerar terminada la Fase 3:**

Verificar que TODOS los indicadores previstos tengan variables madre suficientes.

**Si algún indicador no puede calcularse:**

| Acción | Descripción |
|--------|-------------|
| NO forzar una solución | Mantener integridad del diseño |
| Identificar variable faltante | Qué variable específica falta |
| Identificar fuente requerida | De qué fuente proviene la variable |
| Razón | Por qué no está disponible |
| Período requerido | Cuántos períodos se necesitan |

---

## 17. RESUMEN EJECUTIVO DEL CATÁLOGO

| Categoría | Total variables | Origen principal |
|-----------|----------------|------------------|
| Catálogo 1 — Variables madre contables | 21 | Estados financieros |
| Catálogo 2 — Variables madre de notas | 21 | Notas contables |
| Catálogo 3 — Variables de gestión | 17 | Informe gestión |
| Catálogo 4 — Variables de auditoría | 7 | Informe auditoría |
| Catálogo 5 — Variables de actas | 7 | Actas Asamblea |
| Catálogo 6 — Variables externas | 9 | Fuentes externas |
| Catálogo 7 — Variables derivadas (referencia) | 30 | Fórmulas de cálculo |
| **TOTAL GENERAL** | **112** | — |

### Desglose por clasificación:

- Variables madre contables puros: 21
- Variables madre de notas: 21
- Variables madre de gestión: 17
- Variables de diagnóstico/auditoría: 7
- Variables de contexto actas: 7
- Variables externas: 9
- Indicadores derivados (solo referencia, NO mother): 30

### Por estado de clasificación al PUC actual:

- Reutilizables del PUC: 18 (85.7%)
- Requieren ampliación: 3 (14.3%)
- Descartadas por derivadas: 0 (son referencia, no mother)

---

## 18. FALSOS POSITIVOS COMUNES (Variables que NO son madre)

| Variable | Por qué NO es madre | Clasificación correcta |
|----------|---------------------|-----------------------|
| razon_corriente | Cálculo: activo_corriente / pasivo_corriente | Indicador derivado |
| prueba_acida | Cálculo: (activo_corriente - inventarios) / pasivo_corriente | Indicador derivado |
| capital_trabajo | Cálculo: activo_corriente - pasivo_corriente | Indicador derivado |
| rotacion_activos | Cálculo: ingresos / activos_promedio | Indicador derivado |
| ROE | Cálculo: utilidad_neta / patrimonio_promedio | Indicador derivado |
| ROA | Cálculo: utilidad_neta / activos_promedio | Indicador derivado |
| EBITDA | Cálculo: utilidad_operacional + depreciaciones + amortizaciones | Indicador derivado |
| margen_ebitda | Cálculo: ebitda / ingresos_operacionales | Indicador derivado |
| deuda_ebitda | Cálculo: deuda_total / ebitda | Indicador derivado |
| flujo_operativo | Cálculo multifactorial | Indicador derivado |
| flujo_libre | Cálculo: flujo_operativo - inversiones_capital | Indicador derivado |
| grado_apalancamiento_operativo | Cálculo: %ΔIngresos / %ΔUtilidad_operacional | Indicador derivado |
| endeudamiento_total | Cálculo: pasivo_total / activo_total | Indicador derivado |

**Nota:** Estas variables aparecen en el catálogo como `DERIVADAS — REQUIERE FÓRMULA` y NO se incorporan como cuentas madre. Solo están para referencia en la matriz indicador → variable madre.

---

## 19. VERIFICACIÓN DE CONSISTENCIA

Antes de considerar el catálogo completo:

- [ ] Todas las variables tienen variable_canonical único
- [ ] Ninguna variable requiere fórmula matemática como fuente principal
- [ ] Cada variable tiene fuente_preferente definida
- [ ] Todas las variables con require_periodo_anterior están diseñadas para ventana 2-5 años
- [ ] Distinción clara variable madre vs indicador derivado en todos los casos
- [ ] Clasificación PUC vs catálogo maestro actualizada (18 reutilizables, 3 requieren ampliación)
- [ ] No hay variables madre que sean en realidad cálculos combinados

**Si alguna verificación falla:** Corregir en el diseño antes de considerar terminado.