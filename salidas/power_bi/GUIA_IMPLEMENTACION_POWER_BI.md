# GUIA_IMPLEMENTACION_POWER_BI — Modelo + DAX + Layout (Paso 1, Capas Finales)

> Fecha: 2026-09-19 · Paso 1 autorizado por Big Pickle.
> Consumo estricto del Data Mart en `salidas\power_bi\`. Power BI **no** recalcula el motor financiero (Regla 05_SALIDAS_Y_POWER_BI.md §5.1): consume el modelo estructurado generado por el sistema.

---

## 1. MODELO TABULAR (STAR SCHEMA)

### 1.1 Componentes

| Tabla | Archivo | Rol | Tipo |
|-------|---------|-----|------|
| `dim_fecha` | `power_bi\dim_fecha.csv` | Dimensión de tiempo (año) | Dimensión |
| `dim_indicador` | `power_bi\dim_indicador.csv` | Catálogo de 65 indicadores + carpeta Power BI | Dimensión |
| `dim_concepto` | `power_bi\dim_concepto.csv` | Catálogo de 87 conceptos del estado financiero consolidado | Dimensión |
| `fact_indicadores` | `power_bi\fact_indicadores.csv` | Hechos: indicador × año (largo, 390 filas) | Hechos |
| `fact_estados` | `power_bi\fact_estados.csv` | Hechos: concepto × año (522 filas) | Hechos |
| `fact_wacc` | `power_bi\fact_wacc.csv` | Hechos: estructura de capital + ROIC/WACC por año (6 filas) | Hechos |
| `fact_evidencia` | `power_bi\fact_evidencia.csv` | Hechos: evidencia formal concepto × año (522 filas) | Hechos |

### 1.2 Columnas clave

**`dim_fecha`**
- `id_fecha` (int), `periodo` (int, 2020–2025), `etiqueta` (str, "2020"…"2025").

**`dim_indicador`**
- `id_indicador` (int, 1–65), `clasificacion`, `indicador`, `formula`, `carpeta_powerbi`, `unidad` (`ratio`, `dominio_otro`…).
- `carpeta_powerbi` agrupa en las 3 carpetas de medidas: **Efectivo & Liquidez**, **Rentabilidad & EVA**, **Estructura & Riesgo**.

**`dim_concepto`**
- `concepto`, `rotulo`, `estado` (balance / flujos / resultado), `clasificacion` (activo corriente, pasivo, patrimonio…).

**`fact_indicadores`**
- `periodo` (int), `id_indicador` (int), `valor` (float o null). Formato tabular largo (MOLAP order: cargar con Power Query desde CSV; usar rapporto `dim_indicador.id_indicador ⇢ fact_indicadores.id_indicador` y `dim_fecha.periodo ⇢ fact_indicadores.periodo`).

**`fact_estados`**
- `periodo`, `concepto`, `valor`.

**`fact_wacc`**
- `periodo`, `deuda_financiera_total`, `patrimonio_total`, `capital_empleado` (calculado: deuda + patrimonio), `intereses_pagados_abs`, `costo_deuda_bruto`, `tasa_estatutaria`, `costo_deuda_neto`, `proporcion_deuda`, `proporcion_patrimonio`, `roic` (= Ke de Fase 7, id 34), `wacc`, `estado`.

**`fact_evidencia`**
- `periodo`, `concepto`, `rotulo`, `documento_origen`, `estado_financiero`, `pagina`, `nota`, `evidencia_linea`, `valor_pdf`, `valor_consolidado`, `coincide` (bool), `estado` (ACEPTADO/NO_ENCONTRADO/DUDOSO), `confianza`.

### 1.3 Relaciones (Star Schema)

```
dim_fecha (1) ──► fact_indicadores (N)   [periodo]
dim_fecha (1) ──► fact_estados    (N)   [periodo]
dim_fecha (1) ──► fact_wacc      (1)   [periodo]
dim_fecha (1) ──► fact_evidencia (N)   [periodo]
dim_indicador (1) ──► fact_indicadores (N)   [id_indicador]
dim_concepto (1) ──► fact_estados   (N)   [concepto]
dim_concepto (1) ──► fact_evidencia (N)   [concepto]
```

Filtración unidireccional de dimensiones hacia hechos, forme en cascada por `periodo`; así un solo slicer de año controla todos los objetos visuales.

### 1.4 Carga en Power BI Desktop

1. **Obtener datos** → *Carpeta* → `salidas\power_bi\` (combinar archivos CSV).
2. Cada archivo es una tabla del modelo con nombre homónimo (sin transcripciones).
3. Tipos: `periodo`/`id_fecha` como *Entero*; `valor`/montos como *Decimal*; `etiqueta` como texto.
4. **Verificar catalogo:** `carpeta_powerbi` debe contener exactamente 3 valores (las 3 carpetas de medidas).
5. Crear las relaciones de la §1.3 en *Administrar relaciones*.
6. **Desactivar fecha/hora automática** (Modelado → Fecha y hora automática → Apagado) y marcar `dim_fecha.periodo` como columna de ordenación de `etiqueta`.

---

## 2. LIBRERIA DE MEDIDAS DAX

Convenciones:
- Los indicadores se consumen desde `fact_indicadores` → medidas de "pivot" que extraen el `id_indicador` deseado.
- El período se controla con el slicer (relación `dim_fecha`); las medidas son sensibles al contexto de período salvo indicación contraria.
- Convención de nombres: `M_<Carpeta>_<Medida>`.

### 2.1 Carpetas de medidas (cerradas)

| Carpeta | Contenido |
|---------|-----------|
| `[Efectivo & Liquidez]` | Ratios de liquidez, prueba ácida, días de trabajo neto (capital de trabajo). |
| `[Rentabilidad & EVA]` | ROIC, RONA, WACC, Spread (ROIC−WACC), EVA. |
| `[Estructura & Riesgo]` | Cobertura de intereses, Nivel de endeudamiento, Z-Score (si aplica). |

### 2.2 Medidas base de apoyo

```dax
// Valor de un indicador en el contexto de período actual
Valor_Indicador =
VAR vId = SELECTEDVALUE ( dim_indicador[id_indicador] )
RETURN
    CALCULATE ( SUM ( fact_indicadores[valor] ), fact_indicadores[id_indicador] = vId )
```

```dax
// EBIT (id 25) — palanca central de rentabilidad
M_Base_EBIT =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 25 )
```

```dax
// Capital Empleado del período (Fase 7)
M_Base_Capital_Empleado =
SUM ( fact_wacc[capital_empleado] )
```

```dax
// Impuesto a la renta = tasa estatutaria del período × EBIT (decisión metodológica Fase 7/9)
M_Base_Impuesto =
[M_Base_EBIT] * SUM ( fact_wacc[tasa_estatutaria] )
```

---

### 2.3 CARPETA [Efectivo & Liquidez]

```dax
// Razón corriente (id 1)
M_Liq_RazonCorriente =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 1 )
```

```dax
// Prueba ácida (id 2)
M_Liq_PruebaAcida =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 2 )
```

```dax
// Razón de efectivo (id 3)
M_Liq_RazonEfectivo =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 3 )
```

```dax
// Capital de trabajo neto (id 4) — millones
M_Liq_CapitalTrabajoNeto =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 4 )
```

```dax
// Días de trabajo neto (NWC days) = Capital de trabajo / Ingresos × 365
M_Liq_DiasTrabajoNeto =
DIVIDE ( [M_Liq_CapitalTrabajoNeto] * 365, [M_Base_Ingresos] )
```

```dax
// Ingresos (palanca auxiliar, desde estados consolidados: concepto b_utilidad_bruta / resultado)
// En el consolidado se usa como proxy de ingresos operacionales el concepto de margen:
M_Base_Ingresos =
CALCULATE (
    SUM ( fact_estados[valor] ),
    dim_concepto[concepto] = "i_utilidad_bruta"
)
```

> Nota metodológica: la entidad no maneja inventarios (calidad de ingresos por prestación de servicios); prueba ácida y razón corriente son idénticas por diseño (id 1 = id 2). Se conservan ambas para trazabilidad.

### 2.4 CARPETA [Rentabilidad & EVA]

```dax
// ROIC (id 34) — UODI / Capital invertido promedio
M_Rent_ROIC =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 34 )
```

```dax
// RONA (id 35) — UODI / Capital empleado promedio (deuda financiera + patrimonio)
M_Rent_RONA =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 35 )
```

```dax
// WACC (Fase 7, mesa fact_wacc) — Ke=ROIC(id34), Kd=|intereses|/deuda
M_Rent_WACC =
SUM ( fact_wacc[wacc] )
```

```dax
// Spread de rentabilidad = ROIC − WACC
M_Rent_Spread =
[M_Rent_ROIC] - [M_Rent_WACC]
```

```dax
// EVA = NOPAT − (WACC × Capital Empleado)
// NOPAT = EBIT − Impuesto a la renta (tasa estatutaria)
M_Rent_EVA =
VAR NOPAT = [M_Base_EBIT] - [M_Base_Impuesto]
VAR CAP_EMPLEADO = [M_Base_Capital_Empleado]
VAR WACC = [M_Rent_WACC]
RETURN
    NOPAT - WACC * CAP_EMPLEADO
```

```dax
// Margen neto (id 30) — rentabilidad descubierta
M_Rent_MargenNeto =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 30 )
```

```dax
// ROE (id 32)
M_Rent_ROE =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 32 )
```

### 2.5 CARPETA [Estructura & Riesgo]

```dax
// Cobertura de intereses (id 40) = EBIT / Gastos financieros
M_Ries_CoberturaIntereses =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 40 )
```

```dax
// Cobertura de intereses EBITDA (id 41)
M_Ries_CoberturaInteresesEBITDA =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 41 )
```

```dax
// Nivel de endeudamiento (id 6) = Pasivo total / Activo total
M_Ries_EndeudamientoTotal =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 6 )
```

```dax
// Deuda financiera / EBITDA (id 55)
M_Ries_DeudaFinancieraEBITDA =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 55 )
```

```dax
// Deuda financiera neta / EBITDA (id 56)
M_Ries_DeudaNetaEBITDA =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 56 )
```

```dax
// Índice de Cobertura del Servicio de la Deuda (id 53)
M_Ries_ICSD =
CALCULATE ( SUM ( fact_indicadores[valor] ), dim_indicador[id_indicador] = 53 )
```

#### Z-Score (Altman)

**NO aplica a la entidad auditada.** Fundamentación:
- El Z-Score de Altman fue calibrado para empresas manufactureras que cotizan (Z / Z′ ) o emergentes (Z″).
- La entidad es un vehículo de inversión/tenencia patrimonial (banca/tenencia de acciones), sin capitalización bursátil observable; el modelo requiere `Valor de mercado de capital / Pasivos` (X4) y activos productivos manufactureros.
- Emitir Z-Score sin mercado ni manufactura implicaría **inventar un parámetro** (Regla 1: sin evidencia → NO_ENCONTRADO). Se documenta como **NO_APLICA** en la librería y en la guía, quedando excluido del tablero.

---

## 3. ESPECIFICACIÓN DE PANTALLAS Y VISUALES (4 PÁGINAS)

Tema: limpieza corporativa; tipografía sans; paleta: azul #2C3E50, acento dorado #C9A227, alertas rojo #C0392B / naranja FA. Datos: 2020–2025 (6 períodos).

### PÁGINA 1 — RESULTADOS: ROIC VS WACC Y EVA

**Filtro de tarjeta (slice):**
- Slicer deslizador de **año** (dim_fecha.etiqueta), modo "entre".

**KPIs superiores (tarjetas):**
1. `M_Rent_ROIC` (%). Mucho: "ROIC — Rentabilidad operativa".
2. `M_Rent_WACC` (%). Mucho: "WACC — Costo de capital".
3. `M_Rent_Spread` con etiqueta inteligente de color (verde if ≥0, rojo if <0).
4. `M_Rent_EVA` (millones), con variación vs año anterior (DAX `VAR ant = CALCULATE(...)` filtro `dim_fecha[periodo] = SELECTEDVALUE(dim_fecha[periodo]) - 1`).

**Gráficos:**
5. **Gráfico de líneas,** serie temporal 2020–2025: ROIC, WACC y Spread; eje doble (%). Puntos claves señalados en tooltip: ¿cuándo Spread<0?
6. **Gráfico de barras agrupadas** por año: EVA (millones), con colores condicionales (positivo/negativo).

**Detalle (abajo):**
7. **Matriz:** filas `dim_fecha.etiqueta`; columnas: `M_Rent_ROIC`, `M_Rent_WACC`, `M_Rent_Spread`, `M_Rent_EVA`, `M_Rent_MargenNeto`, `M_Rent_RONA`.

### PÁGINA 2 — EFECTIVO Y LIQUIDEZ

**Filtro de tarjeta:** slicer año (deslizador entre).

**KPIs superiores:**
1. `M_Liq_RazonCorriente` (veces).
2. `M_Liq_PruebaAcida` (veces).
3. `M_Liq_CapitalTrabajoNeto` (millones).
4. `M_Liq_DiasTrabajoNeto` (días).

**Gráficos:**
5. **Gráfico de líneas** 2020–2025: `M_Liq_RazonCorriente` y `M_Liq_RazonEfectivo` (%). Tooltip: evolución de holgura.
6. **Gráfico de barras** por año: `M_Liq_CapitalTrabajoNeto` (millones) y referencia `M_Liq_DiasTrabajoNeto` en eje secundario.

**Detalle:**
7. **Matriz:** filas año; columnas: RazónCorriente, PruebaAcida, RazónEfectivo, CapitalTrabajoNeto (millones), Días de Trabajo Neto.

> La entidad no posee inventarios: prueba ácida ≡ razón corriente (documentado, no es anomalía).

### PÁGINA 3 — ESTRUCTURA, COBERTURA Y ENDEUDAMIENTO

**Filtro de tarjeta:** slicer año.

**KPIs superiores:**
1. `M_Ries_EndeudamientoTotal` (%).
2. `M_Ries_CoberturaIntereses` (veces).
3. `M_Ries_DeudaFinancieraEBITDA` (veces).
4. `M_Ries_ICSD` (veces).

**Gráficos:**
5. **Gráfico de líneas** 2020–2025: `M_Ries_EndeudamientoTotal` (%) y `M_Ries_DeudaNetaEBITDA` (eje secundario).
6. **Gráfico de barras** 2020–2025: `M_Ries_CoberturaIntereses` vs `M_Ries_CoberturaInteresesEBITDA` (veces).

**Detalle:**
7. **Matriz:** filas año; columnas: EndeudamientoTotal, EndeudamientoPatrimonial (id 7), Calidad deuda (id 12), CoberturaIntereses, DeudaFinancieraEBITDA, ICSD.

### PÁGINA 4 — EVIDENCIA FORMAL Y TRAZABILIDAD

**Filtro de tarjeta:** slicer año.

**KPIs superiores (resumen de auditoría):**
1. Total conceptos auditados (`COUNTROWS(fact_evidencia)`).
2. Conceptos ACEPTADO (`CALCULATE(COUNTROWS(fact_evidencia), fact_evidencia[estado]="ACEPTADO")`).
3. Conceptos NO_ENCONTRADO / DUDOSO (`CALCULATE(COUNTROWS(...),[estado] IN {"NO_ENCONTRADO","DUDOSO"})`).
4. % coincidencia consolidado vs PDF (`DIVIDE(ACEPTADO, total)`).

**Detalle:**
5. **Matriz/Lista:** documento_origen, estado_financiero, concepto, rotulo, pagina, nota, valor_pdf, valor_consolidado, coincide (bool), confianza, estado.
   - Filtros visual: `estado` para aislar NO_ENCONTRADO/DUDOSO.
6. **Gráfico de barras** por `estado` (auditoría visual del volumen de evidencia formal).

---

## 4. REGLAS DE VALIDACIÓN AL CARGAR

1. `carpeta_powerbi` debe tener **3 valores** (carpetas de medidas); si apareciera 4º, revisar catálogo id 1–65.
2. `fact_indicadores`: 390 filas (65×6), 323 con valor (67 no calculables: 2020 sin t-1 en id 15–23, 31–35, 57, 60–61, 64–65, e id 19–22 sin inventarios en la entidad).
3. `fact_evidencia`: 522 filas = 486 ACEPTADO + 36 NO_ENCONTRADO; NO inventar complementos.
4. Todo visual temporal usa `dim_fecha` (nunca columna de hechos) para garantizar la secuencia 2020→2025.

---

## 5. ESTADO DE ENTREGA (PASO 1 CERRADO)

- Data Mart generado: `salidas\power_bi\*.csv` + `data_mart_resumen.json` ✔
- Script de preparación/modelado: `fase10_powerbi_data_mart.py` ✔
- Librería de medidas DAX (carpetas Efectivo & Liquidez / Rentabilidad & EVA / Estructura & Riesgo) ✔
- Layout 4 páginas (Resultados, Liquidez, Estructura y Riesgo, Evidencia) ✔
- Z-Score: documentado **NO_APLICA** por ausencia de mercado/manufactura (Regla 1).