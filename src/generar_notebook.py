# -*- coding: utf-8 -*-
"""Genera analisis_fiduciaria.ipynb (analisis financiero 2020-2025).

Usa nbformat; el notebook se puede abrir/editar en jupyter.
"""
import os
from pathlib import Path

import nbformat as nbf

BASE_DIR = Path(__file__).resolve().parent.parent
OUT = BASE_DIR / "analisis_fiduciaria.ipynb"

MD = "markdown"
CODE = "code"

MD_BLOCK = """# Análisis Financiero — FIDUCIARIA LA PREVISORA S.A. 2020–2025

Serie normalizada de los estados financieros (cifras en **millones de pesos colombianos**),
construida automáticamente a partir de los PDFs oficiales (2021–2025) con retro-proyección de 2020
desde la columna _Anterior_ del estado 2021.

- **87 conceptos canónicos** (balance, resultados, flujos e estado de resultados integral).
- Conciliaciones verificadas: `Activo = Pasivo + Patrimonio`, flujos → variación de efectivo,
  utilidad = resultado = CF para todos los años (**65/65 comprobaciones OK**).
- 65 indicadores calculados según la lógica del Excel `INDICADORES .xlsx`.
- Marcos N/A justificados: sin inventarios ni giro comercial (fiduciaria) y sin dato 2019
  para 2020 en razones que requieren promedio.
"""

MD_BLOCK_2 = """## 1. Carga de datos

Se leen los CSV generados por `estados_normalizados.py` e `indicadores.py`.
"""

CODE_CARGA = """import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

BASE = os.getcwd()
df = pd.read_csv(os.path.join(BASE, "salidas", "datos_estados_financieros.csv"))
IND = pd.read_csv(os.path.join(BASE, "salidas", "indicadores.csv"))
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

def serie(concepto):
    return df.set_index("concepto").loc[concepto, [str(a) for a in YEARS]].astype(float).values

def ind(n):  # indicador por numero
    return IND[IND["#"].isin([n])].iloc[0]

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
print("CSV estados:", df.shape, "| indicadores:", IND.shape)"""

MD_BLOCK_3 = """## 2. Balance: evolución y estructura

Los activos están concentrados en inversiones y cuentas por cobrar (activo corriente).
La entidad es altamente apalancada patrimonialmente (pasivo \u2248 17–22% del activo).
"""

CODE_BALANCE2 = """# -- Estructura del activo ------------------------------------------------
import numpy as np
efectivo = serie("b_efectivo")
inversiones = serie("b_inversiones")
ctas = serie("b_cuentas_por_cobrar")
corriente = efectivo + inversiones + ctas + serie("b_impuesto_corriente_activo") + serie("b_otros_activos_no_financieros")
no_corr = serie("b_propiedades_planta_equipo") + serie("b_derecho_uso_activo") + serie("b_activos_intangibles") + serie("b_impuesto_diferido_activo")

fig, ax = plt.subplots(figsize=(9, 4.2))
x = np.arange(len(YEARS))
ax.bar(x, no_corr, label="Activo no corriente", color="#e76f51")
ax.bar(x, corriente, bottom=no_corr, label="Activo corriente", color="#2a9d8f")
ax.set_xticks(x)
ax.set_xticklabels([str(a) for a in YEARS])
ax.set_ylabel("Millones COP")
ax.legend()
for i, (c, nc) in enumerate(zip(corriente, no_corr)):
    ax.text(i, c + nc + 4000, f"{c + nc:,.0f}", ha="center", fontsize=8)
plt.tight_layout()"""

CODE_BALANCE3 = """# -- Apalancamiento -------------------------------------------------------
pasivo = serie("b_pasivo_total")
patrimonio = serie("b_patrimonio_total")

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot([str(a) for a in YEARS], activo := serie("b_activo_total"), "-o", label="Activo total", color="#264653")
ax.plot([str(a) for a in YEARS], pasivo, "-o", label="Pasivo total", color="#e76f51")
ax.plot([str(a) for a in YEARS], patrimonio, "-o", label="Patrimonio", color="#2a9d8f")
ax.set_ylabel("Millones COP")
ax.legend()
for arr, col in [(activo, "#264653"), (pasivo, "#e76f51"), (patrimonio, "#2a9d8f")]:
    for i, v in enumerate(arr):
        ax.annotate(f"{v:,.0f}", (i, v), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=7, color=col)
plt.tight_layout()"""

MD_BLOCK_4 = """## 3. Resultados

Fiduciaria sin costo de ventas (giro por comisiones/honorarios), por lo que el margen bruto es 100%.
El resultado operacional muestra sensibilidad en 2024 (por deterioros y valoración de inversiones),
con fuerte recuperación de ingresos en 2025 (+15% en comisiones).
"""

CODE_RES = """# -- Ingresos y resultado neto --------------------------------------------
comisiones = serie("i_comisiones")
opc = serie("i_ingresos_operaciones_conjuntas")
neto = serie("i_resultado_del_ejercicio")

fig, ax = plt.subplots(figsize=(9, 4.2))
ax.bar([str(a) for a in YEARS], comisiones, label="Comisiones y honorarios", color="#457b9d")
ax.bar([str(a) for a in YEARS], opc, bottom=comisiones, label="Operaciones conjuntas", color="#a8dadc")
ax.plot([str(a) for a in YEARS], neto, "-o", color="#e76f51", label="Resultado neto")
ax.set_ylabel("Millones COP")
ax.legend()
plt.tight_layout()"""

CODE_MARG = """# -- Márgenes (según INDICADORES .xlsx) ------------------------------------
mm = lambda k: [ (lambda v: np.nan if pd.isna(v) else v)(IND[IND["#"].isin([k])][str(a)].iloc[0]) for a in YEARS ]
fig, ax = plt.subplots(figsize=(9, 4))
for k, lbl, col in [(30, "Margen neto", "#2a9d8f"),
                    (27, "Margen operativo (EBIT)", "#e76f51"),
                    (28, "Margen EBITDA", "#264653")]:
    ax.plot([str(a) for a in YEARS], mm(k), "-o", label=lbl, color=col)
ax.set_ylabel("Ratio")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
plt.tight_layout()"""

MD_BLOCK_5 = """## 4. Liquidez y solvencia

La razón corriente (sin inventarios) se mantiene holgada entre 6,5 y 9,3 x.
Endeudamiento total estable \u2248 17–22%; deuda financiera (derechos de uso) baja.
"""

CODE_LIQ = """fig, ax = plt.subplots(figsize=(9, 4))
r = mm(1); e = mm(6)
ax.plot([str(a) for a in YEARS], r, "-o", label="Razón corriente", color="#2a9d8f")
ax.plot([str(a) for a in YEARS], e, "-o", label="Endeudamiento total", color="#e76f51")
ax.set_ylabel("Ratio")
ax.legend()
plt.tight_layout()"""

MD_BLOCK_6 = """## 5. Flujo de efectivo

El flujo operacional es positivo 2020–2023 y negativo 2024–2025, compensado por inversiones
(recuperación de portafolios) para mantener el efectivo estable.
"""

CODE_FLUJO = """op = serie("c_flujo_operacion"); inv = serie("c_flujo_inversion"); fin = serie("c_flujo_financiacion")
fig, ax = plt.subplots(figsize=(9, 4.2))
x = np.arange(len(YEARS))
w = 0.27
ax.bar(x - w, op, w, label="Operación", color="#2a9d8f")
ax.bar(x, inv, w, label="Inversión", color="#e9c46a")
ax.bar(x + w, fin, w, label="Financiación", color="#e76f51")
ax.axhline(0, color="k", lw=0.6)
ax.set_xticks(x); ax.set_xticklabels([str(a) for a in YEARS])
ax.legend()
plt.tight_layout()"""

MD_BLOCK_7 = """## 6. Rentabilidad (ROE / ROA / DuPont)

ROE por DuPont 2025 ≈ 10,9%; la caída de 2024 refleja el menor resultado neto del período.
Como el patrimonio está muy concentrado en reservas (sin distribución), el ROE depende casi
exclusivamente del resultado del año.
"""

CODE_DUPONT = """fig, ax = plt.subplots(figsize=(9, 4))
ax.plot([str(a) for a in YEARS], mm(65), "-o", label="ROE DuPont", color="#2a9d8f")
ax.plot([str(a) for a in YEARS], mm(31), "-o", label="ROA", color="#e76f51")
ax.set_ylabel("Ratio")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
plt.tight_layout()"""

MD_BLOCK_8 = """## 7. Crecimiento (YoY)

Crecimiento de ingresos +15,0% en 2025; utilidad neta +47,4%. El año 2024 fue el más débil
(-31,2% EBITDA, utilidad -70,1%), por deterioro/valoración de inversiones.
"""

CODE_GRW = """fig, ax = plt.subplots(figsize=(9, 4))
ax.plot([str(a) for a in YEARS[1:]], mm(57)[1:], "-o", label="Ingresos", color="#2a9d8f")
ax.plot([str(a) for a in YEARS[1:]], mm(58)[1:], "-o", label="EBITDA", color="#e76f51")
ax.plot([str(a) for a in YEARS[1:]], mm(60)[1:], "-o", label="Utilidad neta", color="#264653")
ax.axhline(0, color="k", lw=0.6)
ax.set_xticks(range(len(YEARS[1:]))); ax.set_xticklabels([str(a) for a in YEARS[1:]])
ax.set_ylabel("Crecimiento YoY")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
plt.tight_layout()"""

MD_BLOCK_9 = """## 8. Tabla resumen de indicadores clave

Selección de indicadores para respaldar el análisis (cifras en millones al cierre del año).
"""

CODE_TABLA = """tabla = IND[["#", "clasificacion", "indicador"]].copy()
for a in YEARS:
    tabla[str(a)] = [IND[str(a)].iloc[i] for i in range(len(IND))]
seleccion = [1, 6, 10, 12, 26, 27, 29, 30, 31, 32, 33, 34, 38, 40, 52, 56, 62, 63, 65]
tabla = tabla[tabla["#"].isin(seleccion)].sort_values("#")
tabla.round(3)"""

MD_BLOCK_10 = """## 9. Conclusiones

1. **Solidez patrimonial**: patrimonio/activo 78–83%; pasivo \u2248 17–22% del activo, sin deuda
   bancaria relevante (solo derechos de uso).
2. **Liquidez holgada**: razón corriente 6,5–9,3 x, con portafolio de inversiones como principal
   activo (≈ 49–70% del total).
3. **Rentabilidad**: margen neto 9,3–31,7% con alta variabilidad; 2024 fue el peor año
   (deterioros y valoración de inversiones) y 2025 muestra recuperación (ingresos +15,0%,
   utilidad +47,4%).
4. **Flujo de caja**: operación negativa en 2024–2025; sostenida por la recuperación de
   inversiones y sin recurso a financiación externa.
5. **Limitaciones**: conceptos ausentes en los PDFs (N/A) y proxies acordados para gastos
   financieros/amortización y deuda; serie en millones sin NCIF detallado del período.
"""

MD_FIN = """---
*Generado por el pipeline automatizado (`src/lectura_pdfs.py` → `taxonomia.py` →
`estados_normalizados.py` → `indicadores.py` → `validaciones.py`). Validaciones: 65/65 OK.*"""


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell(MD_BLOCK),
        nbf.v4.new_markdown_cell(MD_BLOCK_2),
        nbf.v4.new_code_cell(CODE_CARGA),
        nbf.v4.new_markdown_cell(MD_BLOCK_3),
        nbf.v4.new_code_cell(CODE_BALANCE2),
        nbf.v4.new_code_cell(CODE_BALANCE3),
        nbf.v4.new_markdown_cell(MD_BLOCK_4),
        nbf.v4.new_code_cell(CODE_RES),
        nbf.v4.new_code_cell(CODE_MARG),
        nbf.v4.new_markdown_cell(MD_BLOCK_5),
        nbf.v4.new_code_cell(CODE_LIQ),
        nbf.v4.new_markdown_cell(MD_BLOCK_6),
        nbf.v4.new_code_cell(CODE_FLUJO),
        nbf.v4.new_markdown_cell(MD_BLOCK_7),
        nbf.v4.new_code_cell(CODE_DUPONT),
        nbf.v4.new_markdown_cell(MD_BLOCK_8),
        nbf.v4.new_code_cell(CODE_GRW),
        nbf.v4.new_markdown_cell(MD_BLOCK_9),
        nbf.v4.new_code_cell(CODE_TABLA),
        nbf.v4.new_markdown_cell(MD_BLOCK_10),
        nbf.v4.new_markdown_cell(MD_FIN),
    ]
    nb.metadata["kernelspec"] = {"display_name": "Python (fiduciaria)", "language": "python", "name": "fiduciaria"}
    OUT.write_text(nbf.writes(nb), encoding="utf-8")
    print(f"notebook guardado en {OUT}")


if __name__ == "__main__":
    main()