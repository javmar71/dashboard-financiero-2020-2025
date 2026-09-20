# -*- coding: utf-8 -*-
r"""
Dashboard de Inteligencia Financiera 2020-2025 (Streamlit + Plotly).

Reconfiguración técnica de la Fase 10 (2026-09-19): sustituye Power BI por una
aplicación local 100 % open source. Consume el Data Mart estructurado en
`salidas/power_bi/` (dim_* y fact_* generadas por fase10_powerbi_data_mart.py).
Regla del proyecto: consume el modelo estructurado; NO recalcula.

Estructura de navegación: una pestaña por familia de indicadores (9) + Resumen
ejecutivo + Evidencia y Bitácora. Cada familia muestra sus indicadores (tabla
2020-2025), gráficos de small-multiples y heatmap de intensidad, y una lectura
determinística derivada del Data Mart.

Ejecutar:
    venv/Scripts/python.exe -m streamlit run "salidas/dashboard/app.py"
"""

from pathlib import Path
import math

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "reportes"))
import generar_informe_pdf as informe

BASE = Path(__file__).resolve().parents[2]
MART = BASE / "salidas" / "power_bi"
RED_FLAGS_PATH = BASE / "salidas" / "diagnostico_red_flags.csv"
BITACORA_PATH = BASE / "salidas" / "bitacora_revisiones_humanas.md"
REPORTE_PATH = BASE / "salidas" / "REPORTE_INTELIGENCIA_FINANCIERA.md"

PERIODOS = [2020, 2021, 2022, 2023, 2024, 2025]

IND_ROIC = 34
IND_RONA = 35
IND_EBIT = 25

# Paleta profesional por familia (asignada por posición en el catálogo)
PALETA = [
    "#1F4E79", "#2E75B6", "#548235", "#BF8F00", "#C00000",
    "#7030A0", "#008080", "#ED7D31", "#7F6000",
]

ETIQUETA_FAMILIA = {
    "Liquidez": "Liquidez",
    "Endeudamiento y solvencia": "Endeudamiento",
    "Actividad y eficiencia": "Actividad",
    "Rentabilidad": "Rentabilidad",
    "Capital de trabajo y ciclo": "Capital de trabajo",
    "Cobertura y capacidad de pago": "Cobertura",
    "Crecimiento": "Crecimiento",
    "Calidad de resultados": "Calidad",
    "Creacion de valor y DuPont": "Valor / DuPont",
}


# --------------------------------------------------------------------------- #
# Carga y preparación de datos del Data Mart
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner="Cargando Data Mart...")
def cargar_mart():
    dim_indicador = pd.read_csv(MART / "dim_indicador.csv", encoding="utf-8-sig")
    fact_indicadores = pd.read_csv(MART / "fact_indicadores.csv", encoding="utf-8-sig")
    fact_wacc = pd.read_csv(MART / "fact_wacc.csv", encoding="utf-8-sig")
    fact_evidencia = pd.read_csv(MART / "fact_evidencia.csv", encoding="utf-8-sig")
    fact_estados = pd.read_csv(MART / "fact_estados.csv", encoding="utf-8-sig")
    return {
        "dim_indicador": dim_indicador,
        "fact_indicadores": fact_indicadores,
        "fact_wacc": fact_wacc,
        "fact_evidencia": fact_evidencia,
        "fact_estados": fact_estados,
    }


@st.cache_data(show_spinner=False)
def cargar_red_flags():
    return pd.read_csv(RED_FLAGS_PATH, encoding="utf-8-sig")


def serie_indicador(fact, id_indicador):
    """Serie {periodo: valor} de un indicador del catálogo (id 1-65)."""
    s = fact.loc[fact["id_indicador"] == id_indicador, ["periodo", "valor"]]
    return s.set_index("periodo")["valor"].reindex(PERIODOS)


def tabla_familia(dim_indicador, fact, familia):
    """DataFrame de una familia: id, indicador, unidad y valor por periodo."""
    dim = dim_indicador[dim_indicador["clasificacion"] == familia]
    piv = (fact.pivot_table(index="id_indicador", columns="periodo", values="valor", aggfunc="first")
           .reindex(columns=PERIODOS))
    sub = dim[["id_indicador", "indicador", "unidad"]].merge(piv, on="id_indicador", how="left")
    return sub.sort_values("id_indicador").reset_index(drop=True)


def construir_valor(dim_indicador, fact):
    """KPIs de creación de valor para el Resumen ejecutivo."""
    wacc = cargar_mart()["fact_wacc"].set_index("periodo").reindex(PERIODOS)
    datos = pd.DataFrame({"periodo": PERIODOS})
    datos["ROIC"] = serie_indicador(fact, IND_ROIC).values
    datos["RONA"] = serie_indicador(fact, IND_RONA).values
    datos["WACC"] = wacc["wacc"].values
    datos["Spread"] = datos["ROIC"] - datos["WACC"]
    ebit = serie_indicador(fact, IND_EBIT)
    tasa = wacc["tasa_estatutaria"]
    ce = wacc["capital_empleado"]
    nopat = ebit * (1.0 - tasa)
    datos["NOPAT"] = nopat.values
    datos["EVA"] = nopat.values - ce.values * datos["WACC"].values
    return datos


# --------------------------------------------------------------------------- #
# Formateo por unidad
# --------------------------------------------------------------------------- #
def fmt_indicador(valor, unidad):
    """Valor formateado según la unidad del indicador (sin sufijo)."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)) or pd.isna(valor):
        return "—"
    valor = float(valor)
    if unidad == "moneda":
        return f"{valor:,.0f}"
    if unidad in ("porcentaje", "ratio"):
        return f"{valor:,.3f}"
    if unidad in ("veces", "dias"):
        return f"{valor:,.2f}"
    return f"{valor:,.3f}"


def fmt_card(valor, unidad):
    """Valor formateado con sufijo para tarjetas st.metric."""
    if valor is None or pd.isna(valor):
        return "n/d"
    valor = float(valor)
    if unidad == "moneda":
        if abs(valor) >= 1000:
            return f"{valor:,.0f} M$"
        return f"{valor:,.1f} M$"
    if unidad == "porcentaje":
        return f"{valor:.1%}"
    if unidad == "ratio":
        return f"{valor:,.3f}"
    if unidad == "veces":
        return f"{valor:,.2f}x"
    if unidad == "dias":
        return f"{valor:,.1f} d"
    return f"{valor:,.3f}"


def kpi_actual(datos, anio, col):
    """Métrica del periodo seleccionado formateada como proporción (porcentaje)."""
    v = datos.loc[datos["periodo"] == anio, col].iloc[0]
    if pd.isna(v):
        return "n/d"
    return f"{float(v):.1%}"


def fmt_pesos(valor, decimales=1):
    """Formatea un valor monetario del Data Mart (unidad base M$) de forma abreviada."""
    if valor is None or pd.isna(valor):
        return "n/d"
    signo = "-" if valor < 0 else ""
    return f"{signo}${abs(float(valor)):,.{decimales}f} M"


# --------------------------------------------------------------------------- #
# Gráficos profesionales
# --------------------------------------------------------------------------- #
def _eje_y(fig, unidad):
    if unidad == "porcentaje":
        fig.update_yaxes(tickformat=".0%")


def grafico_small_multiples(sub, familia, color):
    """Rejilla de small-multiples: un panel por indicador (evolución 2020-2025)."""
    n = len(sub)
    cols = 3 if n >= 3 else max(n, 1)
    rows = math.ceil(n / cols)
    titulos = [f"{int(r['id_indicador'])}. {r['indicador']}" for _, r in sub.iterrows()]
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titulos,
                        horizontal_spacing=0.07, vertical_spacing=0.14)
    for i, (_, r) in enumerate(sub.iterrows()):
        fila, col = divmod(i, cols)
        y = [None if pd.isna(r[a]) else float(r[a]) for a in PERIODOS]
        fig.add_trace(
            go.Scatter(x=PERIODOS, y=y, mode="lines+markers", name=str(int(r["id_indicador"])),
                       line=dict(color=color, width=2.2), marker=dict(size=6),
                       hovertemplate=f"<b>{r['indicador']}</b><br>%{{x}}: %{{y:,.4~g}}<extra></extra>"),
            row=fila + 1, col=col + 1)
        validos = [v for v in y if v is not None]
        if validos:
            idx = max(idx for idx, v in enumerate(y) if v is not None)
            fig.add_annotation(x=PERIODOS[idx], y=y[idx], text=fmt_indicador(y[idx], r["unidad"]),
                               showarrow=False, yshift=12, font=dict(size=8, color="#333"),
                               row=fila + 1, col=col + 1)
    fig.update_layout(height=230 * rows, template="plotly_white", showlegend=False,
                      title_text=f"{familia} — evolución 2020-2025",
                      title_font=dict(size=15, color="#1F4E79"),
                      margin=dict(l=50, r=20, t=70, b=40),
                      font=dict(family="Segoe UI, Arial", size=10))
    for i, (_, r) in enumerate(sub.iterrows()):
        fila, col = divmod(i, cols)
        if r["unidad"] == "porcentaje":
            fig.update_yaxes(tickformat=".0%", row=fila + 1, col=col + 1)
    return fig


def grafico_heatmap(sub, familia):
    """Heatmap de intensidad relativa (normalizado por indicador) con valores reales."""
    nombres = [f"{int(r['id_indicador'])}. {r['indicador']}" for _, r in sub.iterrows()]
    z, texto = [], []
    for _, r in sub.iterrows():
        vals = np.array([np.nan if pd.isna(r[a]) else float(r[a]) for a in PERIODOS], dtype=float)
        validos = vals[~np.isnan(vals)]
        if validos.size == 0:
            norm = np.full(len(PERIODOS), np.nan)
        elif validos.max() == validos.min():
            norm = np.where(np.isnan(vals), np.nan, 0.5)
        else:
            norm = (vals - validos.min()) / (validos.max() - validos.min())
        z.append(norm)
        texto.append(["—" if pd.isna(r[a]) else fmt_indicador(r[a], r["unidad"]) for a in PERIODOS])
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(a) for a in PERIODOS], y=nombres, text=texto, texttemplate="%{text}",
        textfont=dict(size=9), colorscale="RdYlGn", zmin=0, zmax=1, showscale=False,
        hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>", hoverongaps=False))
    fig.update_layout(height=max(240, 26 * len(sub) + 110), template="plotly_white",
                      title_text=f"{familia} — intensidad relativa por año (verde = mejor del periodo)",
                      title_font=dict(size=14, color="#1F4E79"),
                      margin=dict(l=10, r=10, t=60, b=40), font=dict(family="Segoe UI, Arial", size=9),
                      yaxis=dict(autorange="reversed"))
    return fig


def lectura_familia(sub):
    """Lectura determinística: mayores subidas/bajadas del periodo por indicador."""
    movimientos = []
    for _, r in sub.iterrows():
        vals = [(a, float(r[a])) for a in PERIODOS if pd.notna(r[a])]
        if len(vals) < 2:
            continue
        (a0, v0), (a1, v1) = vals[0], vals[-1]
        delta = v1 - v0
        rel = abs(delta) / abs(v0) if v0 != 0 else abs(delta)
        movimientos.append((rel, r["indicador"], a0, v0, a1, v1, delta, r["unidad"]))
    if not movimientos:
        return "Sin datos suficientes para evaluar la evolución de esta familia."
    movimientos.sort(reverse=True)
    lineas = []
    for _, nombre, a0, v0, a1, v1, delta, unidad in movimientos[:5]:
        flecha = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
        lineas.append(f"- {flecha} **{nombre}**: {fmt_indicador(v0, unidad)} ({a0}) → "
                      f"{fmt_indicador(v1, unidad)} ({a1})")
    return "\n".join(lineas)


# --------------------------------------------------------------------------- #
# Páginas
# --------------------------------------------------------------------------- #
def grid_metricas(sub, anio):
    """Tarjetas st.metric (año seleccionado) para cada indicador de la familia."""
    cols = st.columns(4)
    for i, (_, r) in enumerate(sub.iterrows()):
        with cols[i % 4]:
            st.metric(label=f"{int(r['id_indicador'])}. {r['indicador']}",
                      value=fmt_card(r[anio], r["unidad"]), help=r.get("formula"))


def pagina_familia(dim_indicador, fact, familia, color, anio):
    sub = tabla_familia(dim_indicador, fact, familia)
    con_valor = sum(1 for _, r in sub.iterrows() if pd.notna(r[anio]))

    st.header(familia)
    st.caption(f"{len(sub)} indicadores en la familia · {con_valor} con valor en {anio}. "
               "Datos del Data Mart `salidas\\power_bi\\` (sin recalculación).")

    st.subheader(f"Valores del periodo {anio}")
    grid_metricas(sub, anio)

    st.subheader("Evolución 2020-2025 (small multiples)")
    st.plotly_chart(grafico_small_multiples(sub, familia, color), width="stretch")

    st.subheader("Mapa de intensidad relativa")
    st.plotly_chart(grafico_heatmap(sub, familia), width="stretch")

    with st.expander("Tabla de la familia 2020-2025 (formato por unidad)"):
        tabla = sub.copy()
        for a in PERIODOS:
            tabla[a] = [fmt_indicador(v, u) for v, u in zip(sub[a], sub["unidad"])]
        tabla = tabla.rename(columns={"id_indicador": "#", "indicador": "Indicador", "unidad": "Unidad"})
        st.dataframe(tabla, width="stretch", hide_index=True)

    st.info("**Lectura determinística (derivada del Data Mart):**\n\n" + lectura_familia(sub))


def pagina_resumen(datos, dim_indicador, fact, anio):
    st.header("Resumen ejecutivo — Creación de valor")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROIC", kpi_actual(datos, anio, "ROIC"), help="UODI / Capital invertido promedio (id 34).")
    c2.metric("WACC", kpi_actual(datos, anio, "WACC"), help="Ke=ROIC; Kd=|intereses|/deuda (Fase 7).")
    c3.metric("Spread", kpi_actual(datos, anio, "Spread"),
              help="ROIC - WACC. Positivo en todo el periodo pero delgado.")
    eva_v = datos.loc[datos["periodo"] == anio, "EVA"].iloc[0]
    c4.metric("EVA", fmt_pesos(eva_v),
              help="NOPAT - WACC x Capital Empleado. Negativo en todo el periodo.")

    col_a, col_b = st.columns(2)
    with col_a:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=datos["periodo"], y=datos["ROIC"], name="ROIC", mode="lines+markers",
                                 line=dict(color="#1F4E79", width=3)))
        fig.add_trace(go.Scatter(x=datos["periodo"], y=datos["WACC"], name="WACC", mode="lines+markers",
                                 line=dict(color="#BF8F00", width=3)))
        fig.add_trace(go.Scatter(x=datos["periodo"], y=datos["Spread"], name="Spread", mode="lines+markers",
                                 line=dict(color="#C00000", width=2, dash="dot")))
        fig.update_layout(title="ROIC vs WACC — Spread", template="plotly_white",
                          yaxis=dict(tickformat=".0%"), height=340,
                          font=dict(family="Segoe UI, Arial"))
        st.plotly_chart(fig, width="stretch")
    with col_b:
        df = datos.dropna(subset=["EVA"])
        fig = go.Figure(go.Bar(x=df["periodo"], y=df["EVA"],
                               marker_color=["#C00000" if v < 0 else "#548235" for v in df["EVA"]]))
        fig.update_layout(title="EVA = NOPAT - WACC x Capital Empleado (M$)", template="plotly_white",
                          height=340, font=dict(family="Segoe UI, Arial"))
        st.plotly_chart(fig, width="stretch")

    st.subheader("Índice de familias")
    resumen = []
    for familia in dim_indicador["clasificacion"].drop_duplicates():
        sub = tabla_familia(dim_indicador, fact, familia)
        resumen.append({"Familia": familia, "Indicadores": len(sub),
                        "Con valor 2025": int(sub[2025].notna().sum())})
    st.dataframe(pd.DataFrame(resumen), width="stretch", hide_index=True)

    st.subheader("Matriz consolidada de los 65 indicadores (2020-2025)")
    completa = dim_indicador[["id_indicador", "clasificacion", "indicador", "unidad"]].merge(
        fact.pivot_table(index="id_indicador", columns="periodo", values="valor", aggfunc="first")
        .reindex(columns=PERIODOS), on="id_indicador", how="left")
    completa = completa.sort_values("id_indicador")
    vista = completa[["id_indicador", "clasificacion", "indicador"]].rename(
        columns={"id_indicador": "#", "clasificacion": "Familia"})
    for a in PERIODOS:
        vista[a] = [fmt_indicador(v, u) for v, u in zip(completa[a], completa["unidad"])]
    st.dataframe(vista, width="stretch", hide_index=True, height=520)


def pagina_evidencia(mart):
    st.header("Evidencia y Bitácora")
    ev = mart["fact_evidencia"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Registros auditados", f"{len(ev):,}", help="87 conceptos x 6 años = 522 observaciones.")
    c2.metric("ACEPTADO", int((ev["estado"] == "ACEPTADO").sum()))
    c3.metric("NO_ENCONTRADO", int((ev["estado"] == "NO_ENCONTRADO").sum()))

    estado_sel = st.multiselect("Filtrar por estado de validación",
                                sorted(ev["estado"].unique()), default=sorted(ev["estado"].unique()))
    cols = ["periodo", "concepto", "rotulo", "documento_origen", "estado_financiero",
            "pagina", "nota", "valor_pdf", "valor_consolidado", "coincide", "estado", "confianza"]
    st.dataframe(ev[ev["estado"].isin(estado_sel)][cols], width="stretch")

    st.markdown("---")
    st.subheader("Hallazgo formal: `i_ori_inmuebles` 2022")
    st.error("**DUDOSO — requiere pronunciamiento humano (Protocolo Pasos B/C).**")
    st.markdown(
        "| Atributo | Valor |\n|---|---|\n"
        "| Valor consolidado | **$2.465** |\n"
        "| Valor Nota 25 (estados financieros 2022) | **$11.751** |\n"
        "| Estado de validación | DUDOSO |\n"
        "| Impacto | SIN efecto en ROIC/EBIT/NOPAT/WACC (los ORI se excluyen) |\n"
        "| Acción | Pronunciamiento humano pendiente (aceptar / ajustar / NO_ENCONTRADO) |"
    )
    with st.expander("Bitácora completa de revisiones humanas"):
        try:
            st.markdown(BITACORA_PATH.read_text(encoding="utf-8"))
        except Exception:
            st.write("Ver `salidas\\bitacora_revisiones_humanas.md`")
    with st.expander("Reporte de Inteligencia Financiera"):
        try:
            st.markdown(REPORTE_PATH.read_text(encoding="utf-8"))
        except Exception:
            st.write("Ver `salidas\\REPORTE_INTELIGENCIA_FINANCIERA.md`")

    st.markdown("---")
    st.subheader("Informe Diagnóstico en PDF (generado por el agente IA)")
    st.caption("Extrae KPIs y series 2020-2025 del Data Mart `salidas\\power_bi\\`, analiza las 9 "
               "familias de indicadores y elabora un capítulo de riesgos y alarmas en un PDF profesional.")
    if st.button("Generar Informe PDF con IA", width="stretch"):
        with st.spinner("Generando Informe Diagnóstico Financiero 2020-2025..."):
            try:
                pdf_bytes = informe.generar_informe_bytes()
                st.success("Informe PDF generado correctamente.")
                st.download_button(
                    label="Descargar Informe_Diagnostico_Financiero_2020_2025.pdf",
                    data=pdf_bytes,
                    file_name="Informe_Diagnostico_Financiero_2020_2025.pdf",
                    mime="application/pdf",
                    width="stretch",
                )
            except Exception as e:
                st.error(f"No se pudo generar el informe: {e}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="Dashboard de Inteligencia Financiera 2020-2025",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.35rem;
        line-height: 1.2;
        white-space: normal;
        overflow: visible;
        text-overflow: clip;
    }
    [data-testid="stMetricLabel"] { white-space: normal; }
    .block-container {padding-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Inteligencia Financiera 2020-2025")
_nombre_entidad, _nit = informe.cargar_entidad()
if _nombre_entidad:
    st.markdown(f"**Entidad:** {_nombre_entidad}" + (f" — NIT {_nit}" if _nit else ""))
else:
    st.caption("Entidad: reservada (configurar `AUTOMAT ANALISIS FIN\\salidas\\config_entidad.json`)")
st.caption("Modelo financiero consolidado (Sin recalculaci\u00f3n)")

mart = cargar_mart()
dim_indicador = mart["dim_indicador"]
fact = mart["fact_indicadores"]
familias = dim_indicador["clasificacion"].drop_duplicates().tolist()
datos = construir_valor(dim_indicador, fact)

with st.sidebar:
    st.header("Filtros")
    anio = st.selectbox("Periodo", PERIODOS, index=5)
    st.info(f"Periodo seleccionado: **{anio}**")
    st.caption("Una pestaña por familia de indicadores. Las series muestran siempre 2020-2025.")

etiquetas = ["Resumen"] + [ETIQUETA_FAMILIA.get(f, f) for f in familias] + ["Evidencia"]
tabs = st.tabs(etiquetas)

with tabs[0]:
    pagina_resumen(datos, dim_indicador, fact, anio)

for i, familia in enumerate(familias):
    with tabs[i + 1]:
        pagina_familia(dim_indicador, fact, familia, PALETA[i % len(PALETA)], anio)

with tabs[len(familias) + 1]:
    pagina_evidencia(mart)

st.divider()
st.caption("Datos auditados 2020-2025 | Trazabilidad: `salidas\\` (Fases 8/9 integridad 100 %). No inventar ni interpolar (Regla 1).")
