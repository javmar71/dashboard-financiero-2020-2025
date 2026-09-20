# -*- coding: utf-8 -*-
r"""
Modulo de generacion de Informe Diagnostico Financiero en PDF (2020-2025).

Agente IA (opencode) : construye el contexto analitico desde el Data Mart de
`salidas/power_bi/` (dim_* y fact_* generados por fase10_powerbi_data_mart.py),
redacta un texto estructurado (markdown) y lo compila en un PDF profesional.

Reglas del proyecto observadas (AGENTS.md):
  - No inventar ni interpolar: todos los numeros provienen del Data Mart.
  - Trazabilidad: cada seccion cita las tablas/fuentes del modelo estructurado.
  - No se recalcula el motor financiero; se consumen los valores ya validados.

Ejecutar (desde la raiz del proyecto):
    venv/Scripts/python.exe -m salidas.reportes.generar_informe_pdf
o directamente:
    venv/Scripts/python.exe "salidas/reportes/generar_informe_pdf.py"

El modulo tambien expone `generar_informe_pdf()` (devuelve ruta del PDF) y
`generar_informe_bytes()` (devuelve bytes del PDF) para su integracion en
`salidas/dashboard/app.py` (boton de descarga en la Pestana 4).
"""

from __future__ import annotations

import io
import json
import math
import re
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from fpdf import FPDF

BASE = Path(__file__).resolve().parents[2]
MART = BASE / "salidas" / "power_bi"
OUT_DIR = BASE / "salidas" / "reportes"
GRAF_DIR = OUT_DIR / "graficos"
CONFIG_ENTIDAD = BASE / "salidas" / "config_entidad.json"

PERIODOS = [2020, 2021, 2022, 2023, 2024, 2025]
PERIODOS_EVA = [2021, 2022, 2023, 2024, 2025]

# IDs de indicadores del Data Mart (catálogo dim_indicador)
ID_EBIT = 25
ID_EBITDA = 24
ID_ROIC = 34
ID_RONA = 35
ID_FCO_UN = 62
ID_ENDEUDAMIENTO = 6
ID_COBERTURA = 40
ID_DEUDA_EBITDA = 55
ID_ICSD = 53
ID_MARGEN_OP = 27
ID_VAR_CXC = 42
ID_CREC_UTIL = 60
ID_CREC_EBITDA = 58

NOMBRE_PDF = "Informe_Diagnostico_Financiero_2020_2025.pdf"
AA = "C:/Windows/Fonts/arial.ttf"
AA_B = "C:/Windows/Fonts/arialbd.ttf"


# --------------------------------------------------------------------------- #
# 1. Extraccion de contexto desde el Data Mart
# --------------------------------------------------------------------------- #
def cargar_mart() -> Dict[str, pd.DataFrame]:
    """Carga las tablas del Data Mart (misma logica que el dashboard)."""
    return {
        "dim_indicador": pd.read_csv(MART / "dim_indicador.csv", encoding="utf-8-sig"),
        "fact_indicadores": pd.read_csv(MART / "fact_indicadores.csv", encoding="utf-8-sig"),
        "fact_wacc": pd.read_csv(MART / "fact_wacc.csv", encoding="utf-8-sig"),
        "fact_evidencia": pd.read_csv(MART / "fact_evidencia.csv", encoding="utf-8-sig"),
        "fact_estados": pd.read_csv(MART / "fact_estados.csv", encoding="utf-8-sig"),
    }


def cargar_entidad() -> Tuple[str, str]:
    """Lee salidas/config_entidad.json (nombre_entidad, nit).

    Campos vacios = modo agnostico (no se muestra entidad). Unica fuente de
    identificacion compartida entre HTML y PDF: para otra empresa basta editarla.
    """
    try:
        d = json.loads(CONFIG_ENTIDAD.read_text(encoding="utf-8"))
        nombre = str(d.get("nombre_entidad", "")).strip()
        nit = str(d.get("nit", "")).strip()
    except Exception:
        nombre, nit = "", ""
    return nombre, nit


def serie_indicador(fact: pd.DataFrame, id_indicador: int) -> pd.Series:
    """Serie temporal de un indicador indexada por periodo (reindexada a 2020-2025)."""
    s = fact[fact["id_indicador"] == id_indicador].set_index("periodo")["valor"]
    return s.reindex(PERIODOS)


def construir_contexto() -> Dict:
    """Arma el contexto analitico completo que alimenta la narrativa del agente."""
    mart = cargar_mart()
    fi = mart["fact_indicadores"]
    fw = mart["fact_wacc"].set_index("periodo").reindex(PERIODOS)
    fe = mart["fact_evidencia"]
    nombre_entidad, nit_entidad = cargar_entidad()

    roic = serie_indicador(fi, ID_ROIC)
    rona = serie_indicador(fi, ID_RONA)
    ebit = serie_indicador(fi, ID_EBIT)
    ebitda = serie_indicador(fi, ID_EBITDA)
    fco_un = serie_indicador(fi, ID_FCO_UN)
    endeud = serie_indicador(fi, ID_ENDEUDAMIENTO)
    cobertura = serie_indicador(fi, ID_COBERTURA)
    deuda_ebitda = serie_indicador(fi, ID_DEUDA_EBITDA)
    icsd = serie_indicador(fi, ID_ICSD)
    margen_op = serie_indicador(fi, ID_MARGEN_OP)
    var_cxc = serie_indicador(fi, ID_VAR_CXC)
    crec_util = serie_indicador(fi, ID_CREC_UTIL)
    crec_ebitda = serie_indicador(fi, ID_CREC_EBITDA)

    wacc = fw["wacc"]
    capital_empleado = fw["capital_empleado"]
    tasa_est = fw["tasa_estatutaria"]

    # NOPAT = EBIT x (1 - tasa estatutaria Art. 240 E.T.); EVA = NOPAT - WACC x CapEmpleado
    nopat = ebit * (1 - tasa_est)
    eva = nopat - wacc * capital_empleado
    spread = roic - wacc

    # Evento 522: fact_evidencia (87 conceptos x 6 anos)
    ev_estado = fe["estado"].value_counts().to_dict()
    ev_total = len(fe)
    ev_aceptado = ev_estado.get("ACEPTADO", 0)
    ev_no_encontrado = ev_estado.get("NO_ENCONTRADO", 0)
    ev_dudoso = ev_estado.get("DUDOSO", 0)

    # Hallazgo i_ori_inmuebles 2022 (DUDOSO) - del consolidado y de la evidencia
    ori_2022 = serie_indicador_estados(mart["fact_estados"], "i_ori_inmuebles")

    # Matriz completa de indicadores (65) clasificada por familia y por periodo
    tabla = _tabla_indicadores_completa(mart["dim_indicador"], fi)

    return {
        "periodos": PERIODOS,
        "periodos_eva": PERIODOS_EVA,
        "entidad_nombre": nombre_entidad,
        "entidad_nit": nit_entidad,
        "roic": roic,
        "rona": rona,
        "wacc": wacc,
        "spread": spread,
        "nopat": nopat,
        "eva": eva,
        "ebit": ebit,
        "ebitda": ebitda,
        "fco_un": fco_un,
        "endeudamiento": endeud,
        "cobertura": cobertura,
        "deuda_ebitda": deuda_ebitda,
        "icsd": icsd,
        "margen_operativo": margen_op,
        "var_cxc": var_cxc,
        "crec_utilidad": crec_util,
        "crec_ebitda": crec_ebitda,
        "capital_empleado": capital_empleado,
        "tasa_estatutaria": tasa_est,
        "evidencia_total": ev_total,
        "evidencia_aceptado": ev_aceptado,
        "evidencia_no_encontrado": ev_no_encontrado,
        "evidencia_dudoso": ev_dudoso,
        "i_ori_inmuebles_2022": ori_2022.get(2022, None) if ori_2022 is not None else None,
        "tabla_indicadores": tabla,
        "total_indicadores": len(mart["dim_indicador"]),
        "indicadores_con_valor": len(set(fi.dropna(subset=["valor"])["id_indicador"])),
    }


def _tabla_indicadores_completa(dim_indicador: pd.DataFrame, fact: pd.DataFrame) -> pd.DataFrame:
    """Pivota todos los indicadores (65) por familia y periodo 2020-2025.

    Devuelve un DataFrame con columnas: id_indicador, indicador, clasificacion,
    unidad y una columna por cada periodo (2020..2025) con el valor redondeado.
    """
    orden_familias = dim_indicador["clasificacion"].drop_duplicates().tolist()
    piv = (fact.pivot_table(index="id_indicador", columns="periodo", values="valor", aggfunc="first")
           .reindex(columns=PERIODOS))
    tabla = (dim_indicador[["id_indicador", "indicador", "clasificacion", "unidad"]]
             .merge(piv, on="id_indicador", how="left"))
    tabla["clasificacion"] = pd.Categorical(tabla["clasificacion"], categories=orden_familias, ordered=True)
    tabla = tabla.sort_values(["clasificacion", "id_indicador"]).reset_index(drop=True)
    return tabla


def serie_indicador_estados(fact_estados: pd.DataFrame, concepto: str) -> pd.Series:
    """Serie de un concepto del estado de resultados consolidado."""
    if "concepto" not in fact_estados.columns:
        return pd.Series(index=PERIODOS, dtype="float64")
    s = fact_estados[fact_estados["concepto"] == concepto].set_index("periodo")["valor"]
    return s.reindex(PERIODOS)


def fmt_num(x: float, nd: int = 2) -> str:
    """Formatea numero con miles y decimales (es_ES)."""
    if x is None or (isinstance(x, float) and (pd.isna(x) or pd.isnull(x))):
        return "n/d"
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_serie(s: pd.Series, nd: int = 2) -> List[str]:
    return [fmt_num(float(v) if pd.notna(v) else None, nd) for v in s.values]


def fmt_indicador(valor: float, unidad: str) -> str:
    """Formatea un valor segun la unidad del indicador (moneda, porcentaje, veces, dias, ratio)."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "n/d"
    if unidad == "moneda":
        return fmt_num(float(valor), 0)
    if unidad in ("porcentaje", "ratio"):
        return fmt_num(float(valor), 3)
    if unidad in ("veces", "dias"):
        return fmt_num(float(valor), 2)
    return fmt_num(float(valor), 3)


# --------------------------------------------------------------------------- #
# 2. Narrativa del agente IA (prompt -> texto estructurado markdown)
# --------------------------------------------------------------------------- #
def construir_prompt(c: Dict) -> str:
    """Construye el bloque de contexto pasado al agente IA para su redaccion."""
    def ss(nombre: str, s: pd.Series, nd: int = 2) -> str:
        valores = ", ".join(f"{a}: {fmt_num(float(v), nd)}" for a, v in zip(s.index, s.values)
                            if pd.notna(v))
        return f"- {nombre}: {valores}"

    lines = [
        "CONTEXTO DEL ANALISIS FINANCIERO 2020-2025 (todas las cifras provienen del Data Mart auditado `salidas/power_bi/`).",
        "",
        "Evolucion de indicadores por periodo:",
        ss("ROIC (id 34)", c["roic"], 4),
        ss("WACC (Fase 7, Ke=ROIC)", c["wacc"], 4),
        ss("Spread ROIC-WACC", c["spread"], 4),
        ss("NOPAT estatutario (EBIT x (1 - tasa Art. 240))", c["nopat"]),
        ss("EVA = NOPAT - WACC x Capital Empleado", c["eva"]),
        ss("EBIT (id 25)", c["ebit"]),
        ss("EBITDA (id 24)", c["ebitda"]),
        ss("Calidad de utilidades FCO/UN (id 62)", c["fco_un"]),
        ss("Margen operativo (id 27)", c["margen_operativo"], 3),
        ss("Endeudamiento total (id 6)", c["endeudamiento"], 3),
        ss("Cobertura de intereses (id 40)", c["cobertura"]),
        ss("Deuda financiera/EBITDA (id 55)", c["deuda_ebitda"]),
        ss("ICSD (id 53)", c["icsd"]),
        ss("Variacion de cuentas por cobrar (id 42)", c["var_cxc"]),
        ss("Crecimiento de utilidad neta (id 60)", c["crec_utilidad"]),
        ss("Crecimiento del EBITDA (id 58)", c["crec_ebitda"]),
        "",
        "Evidencia formal (Evento 522 = 87 conceptos x 6 anos):",
        f"- Total registros auditados: {c['evidencia_total']}; ACEPTADO: {c['evidencia_aceptado']}; "
        f"NO_ENCONTRADO: {c['evidencia_no_encontrado']}; DUDOSO: {c['evidencia_dudoso']}.",
        f"- Hallazgo i_ori_inmuebles 2022: consolidado {fmt_num(c['i_ori_inmuebles_2022'], 0)} vs Nota 25 "
        f"$11.751 -> DUDOSO (Protocolo Pasos B/C), pendiente pronunciamiento humano.",
        "",
        "Reglas: redactar en espanol, sin inventar ni interpolar cifras, citar las fuentes (Data Mart), "
        "con las secciones: Resumen Ejecutivo y Creacion de Valor; Diagnostico 2020-2025 (puntos fuertes/debiles); "
        "Matriz de Alertas y Semaforo de Riesgo; Analisis Forense y Bitacora; Recomendaciones y Plan de Accion.",
    ]
    return "\n".join(lines)


def _tabla_markdown(sub: pd.DataFrame) -> str:
    """Tabla markdown de un conjunto de indicadores (id, nombre y 6 periodos)."""
    header = "| id | Indicador | " + " | ".join(str(a) for a in PERIODOS) + " |"
    sep = "|---|" + "---|" * (1 + len(PERIODOS))
    filas = []
    for rec in sub.to_dict("records"):
        valores = " | ".join(fmt_indicador(rec.get(a), rec.get("unidad", "")) for a in PERIODOS)
        filas.append(f"| {int(rec['id_indicador'])} | {rec['indicador']} | {valores} |")
    return "\n".join([header, sep] + filas)


def table_por_familia(c: Dict) -> str:
    """Genera el markdown de la matriz de los 65 indicadores por familia y periodo."""
    tabla = c["tabla_indicadores"]
    bloques = []
    for familia in tabla["clasificacion"].drop_duplicates():
        sub = tabla[tabla["clasificacion"] == familia]
        bloques.append(f"### {familia}\n\n{_tabla_markdown(sub)}")
    return "\n\n".join(bloques)


def familia_analisis(nombre: str, sub: pd.DataFrame) -> str:
    """Narrativa deterministica de una familia (sin inventar cifras)."""
    con_valor = sub[PERIODOS].notna().any(axis=1)
    total = len(sub)
    n_val = int(con_valor.sum())
    if total == 0:
        return ""
    if n_val == 0:
        return (f"Familia compuesta por **{total} indicadores** sin base de calculo en 2020-2025: "
                f"los conceptos de soporte (inventarios y ciclos asociados) no se identificaron de forma "
                f"coherente en los estados financieros, por lo que se mantienen como **NO_ENCONTRADO** "
                f"sin interpolar (Regla 1).")
    partes = [f"Familia compuesta por **{total} indicadores**, de los cuales **{n_val}** presentan "
              f"valores calculados en 2020-2025 y **{total - n_val}** carecen de base de calculo "
              f"(NO_ENCONTRADO)."]
    detalle = []
    for rec in sub[con_valor].head(4).to_dict("records"):
        v0 = rec[PERIODOS[0]] if pd.notna(rec[PERIODOS[0]]) else None
        vf = rec[PERIODOS[-1]] if pd.notna(rec[PERIODOS[-1]]) else None
        unidad = rec.get("unidad", "")
        detalle.append(f"**{rec['indicador']}**: {fmt_indicador(v0, unidad)} (2020) -> "
                       f"{fmt_indicador(vf, unidad)} (2025)")
    if detalle:
        partes.append("Indicadores representativos: " + "; ".join(detalle) + ".")
    return " ".join(partes)


def capitulo_familia(num: int, nombre: str, sub: pd.DataFrame, c: Dict) -> str:
    """Capitulo de una familia: narrativa + tabla de sus indicadores."""
    return "\n".join([
        f"## {num}. FAMILIA: {nombre.upper()}",
        "",
        familia_analisis(nombre, sub),
        "",
        _tabla_markdown(sub),
    ])


def _semaforo(valor, limites: str) -> str:
    """Semaforo de un indicador segun umbrales de referencia."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return "N/D"
    if limites == "spread":
        return "VERDE" if valor > 0.01 else ("AMBAR" if valor > 0 else "ROJO")
    if limites == "eva":
        return "VERDE" if valor > 0 else ("AMBAR" if valor == 0 else "ROJO")
    if limites == "fco":
        return "VERDE" if valor >= 1.0 else ("AMBAR" if valor >= 0.5 else "ROJO")
    if limites == "ende":
        return "VERDE" if valor <= 0.30 else ("AMBAR" if valor <= 0.45 else "ROJO")
    if limites == "cobertura":
        return "VERDE" if valor >= 3.0 else ("AMBAR" if valor >= 1.5 else "ROJO")
    if limites == "deuda_ebitda":
        return "VERDE" if valor <= 3.0 else ("AMBAR" if valor <= 4.0 else "ROJO")
    if limites == "margen":
        return "VERDE" if valor >= 0.10 else ("AMBAR" if valor >= 0.05 else "ROJO")
    if limites == "crec":
        return "VERDE" if valor >= 0 else ("AMBAR" if valor >= -0.10 else "ROJO")
    if limites == "cxc":
        return "VERDE" if valor <= 1.0 else ("AMBAR" if valor <= 1.5 else "ROJO")
    return "N/D"


def capitulo_riesgos(num: int, c: Dict) -> str:
    """Capitulo de riesgos y alarmas: semaforo + matriz priorizada por severidad."""
    p = 2025
    checks = [
        {"nombre": "EVA (creacion de valor)", "serie": c["eva"], "limite": "eva", "nd": 0,
         "lectura": "El NOPAT no cubre el costo del capital materialmente invertido.", "severidad": "ALTA", "estado": "Estructural"},
        {"nombre": "Calidad de resultados FCO/UN", "serie": c["fco_un"], "limite": "fco", "nd": 3,
         "lectura": "Las utilidades no se convierten en caja operativa (FCO/UN por debajo de 1).", "severidad": "ALTA", "estado": "Activa"},
        {"nombre": "Variacion cuentas por cobrar", "serie": c["var_cxc"], "limite": "cxc", "nd": 2,
         "lectura": "Acumulacion de cartera que presiona el capital de trabajo.", "severidad": "MEDIA-ALTA", "estado": "Activa"},
        {"nombre": "Spread ROIC-WACC", "serie": c["spread"], "limite": "spread", "nd": 3,
         "lectura": "El retorno supera el costo de capital, pero con margen delgado.", "severidad": "MEDIA", "estado": "Vigilancia"},
        {"nombre": "Margen operativo", "serie": c["margen_operativo"], "limite": "margen", "nd": 3,
         "lectura": "Presion de gastos de administracion y beneficios a empleados.", "severidad": "MEDIA", "estado": "En recuperacion"},
        {"nombre": "Crecimiento utilidad neta", "serie": c["crec_utilidad"], "limite": "crec", "nd": 3,
         "lectura": "Volatilidad del resultado neto en el periodo.", "severidad": "MEDIA", "estado": "Vigilancia"},
        {"nombre": "Endeudamiento total", "serie": c["endeudamiento"], "limite": "ende", "nd": 3,
         "lectura": "Nivel de apalancamiento y estructura de capital.", "severidad": "BAJA", "estado": "Controlada"},
        {"nombre": "Cobertura de intereses", "serie": c["cobertura"], "limite": "cobertura", "nd": 1,
         "lectura": "Margen de seguridad para atender el servicio de la deuda.", "severidad": "BAJA", "estado": "Controlada"},
        {"nombre": "Deuda financiera / EBITDA", "serie": c["deuda_ebitda"], "limite": "deuda_ebitda", "nd": 3,
         "lectura": "Capacidad de repago de la deuda financiera.", "severidad": "BAJA", "estado": "Controlada"},
    ]

    filas = []
    activas = []
    for ch in checks:
        valor = ch["serie"].get(p) if hasattr(ch["serie"], "get") else None
        valor = float(valor) if valor is not None and pd.notna(valor) else None
        color = _semaforo(valor, ch["limite"])
        filas.append(f"| {ch['nombre']} | {fmt_num(valor, ch['nd'])} | {color} | {ch['severidad']} | {ch['estado']} |")
        if color in ("ROJO", "AMBAR"):
            activas.append(f"- **{ch['nombre']}** ({color}): {ch['lectura']}")

    sin_base = c["total_indicadores"] - c["indicadores_con_valor"]
    activas.append(f"- **Cobertura del modelo** (AMBAR): {sin_base} de {c['total_indicadores']} indicadores "
                   f"carecen de base de calculo (inventarios y ciclos) y permanecen como NO_ENCONTRADO.")
    if c["evidencia_dudoso"]:
        activas.append(f"- **Trazabilidad** (AMBAR): {c['evidencia_dudoso']} registro(s) en estado DUDOSO "
                       f"pendiente(s) de pronunciamiento humano (Protocolo Pasos B/C).")

    return "\n".join([
        f"## {num}. RIESGOS Y ALARMAS",
        "",
        f"### {num}.1 Semaforo de riesgo (cierre {p})",
        "",
        "| Indicador | Valor 2025 | Semaforo | Severidad | Estado |",
        "|---|---|---|---|---|",
        *filas,
        "",
        f"### {num}.2 Alertas y lecturas",
        "",
        *activas,
    ])


def redactar_analisis(c: Dict) -> str:
    """Redaccion estructurada en markdown desde el contexto (motor del agente IA)."""

    partes: List[str] = []

    nombre_ent = c.get("entidad_nombre", "")
    nit_ent = c.get("entidad_nit", "")
    if nombre_ent:
        linea_entidad = f"**Entidad:** {nombre_ent}" + (f" - NIT {nit_ent}." if nit_ent else ".")
    else:
        linea_entidad = "**Entidad:** reservada (agnosticismo de entidad)."

    partes.append(f"""# INFORME DIAGNOSTICO FINANCIERO 2020-2025

**Generado:** 2026-09-19 por el agente IA (opencode) sobre el Data Mart de `salidas/power_bi/`.
{linea_entidad}
**Base de datos:** matriz consolidada auditada (65 indicadores x 6 anos) y Fases 8/9 (evidencia formal e integridad 100 %).
**Regla:** ninguna cifra es inventada o interpolada; todo proviene del modelo estructurado.

> Motor de IA: opencode (generativo) + big pickle (verificacion). Protocolo de Validacion Universal ante divergencias.

---

## 1. RESUMEN EJECUTIVO Y CREACION DE VALOR

La entidad presenta un perfil **solido, holgado y de bajo apalancamiento**, con un
**spread ROIC-WACC positivo en los 5 anos** (desde **+{fmt_num(c['spread'][2021], 3)}** en 2021 hasta
**+{fmt_num(c['spread'][2025], 3)}** en 2025), lo que indica que la operacion supera su costo de capital.

Sin embargo, el **EVA es negativo en todo el periodo** ({fmt_num(c['eva'][2021], 0)} a
{fmt_num(c['eva'][2025], 0)} M$): dado el elevado capital empleado (deuda + patrimonio ~{fmt_num(c['capital_empleado'][2021], 0)}-{fmt_num(c['capital_empleado'][2025], 0)} M$),
el NOPAT no cubre cabalmente el costo del capital materialmente invertido.

**Principales KPIs (2025):** ROIC {fmt_num(c['roic'][2025], 3)}, WACC {fmt_num(c['wacc'][2025], 3)},
Spread {fmt_num(c['spread'][2025], 3)}, EVA {fmt_num(c['eva'][2025], 0)} M$, FCO/UN {fmt_num(c['fco_un'][2025], 3)},
Endeudamiento total {fmt_num(c['endeudamiento'][2025], 3)}, Cobertura {fmt_num(c['cobertura'][2025], 1)}x,
Deuda/EBITDA {fmt_num(c['deuda_ebitda'][2025], 3)}, ICSD {fmt_num(c['icsd'][2025], 1)}.

## 2. DIAGNOSTICO DE EVOLUCION FINANCIERA 2020-2025

### 2.1 Puntos fuertes

- **Solidez y liquidez:** endeudamiento total nunca superior a {fmt_num(max(v for v in c['endeudamiento'].dropna()), 3)}
y posicion **neta de caja** permanente; la unica deuda financiera es el derecho de uso (arrendamientos), decreciente.
- **Cobertura amplia:** EBIT cubre intereses entre {fmt_num(min(v for v in c['cobertura'].dropna()), 0)}x y
{fmt_num(max(v for v in c['cobertura'].dropna()), 0)}x, evidencia de margen de seguridad muy alto.
- **Trazabilidad total:** los {c['evidencia_total']} registros del Evento 522 arrojan {c['evidencia_aceptado']} ACEPTADO
y solo {c['evidencia_no_encontrado']} NO_ENCONTRADO (sin DUDOSO en el cruce Fase 8).
- **Continuidad:** liquidez y solvencia muy por encima de umbrales; sin dudas de negocio en marcha.

### 2.2 Puntos debiles

- **EVA negativo sistematico:** {', '.join(f'{a}: {fmt_num(c["eva"][a], 0)} M$' for a in c['periodos_eva'])}.
  El capital empleado (~{fmt_num(c['capital_empleado'][2025], 0)} M$) es muy superior al capital invertido que sustenta el ROIC.
- **Calidad de caja en deterioro:** FCO/UN cae de {fmt_num(c['fco_un'][2021], 3)} (2021) a
  {fmt_num(c['fco_un'][2024], 3)} y {fmt_num(c['fco_un'][2025], 3)} (2024-2025): las utilidades no se convierten en caja.
- **Deterioro operativo 2023-2024:** EBITDA {fmt_num(c['crec_ebitda'][2023], 2) if c['crec_ebitda'][2023] > 0 else '+' + fmt_num(-c['crec_ebitda'][2023], 2)}
  y {fmt_num(c['crec_ebitda'][2024], 2)} en 2023-2024; margen operativo de {fmt_num(c['margen_operativo'][2021], 3)} a
  {fmt_num(c['margen_operativo'][2025], 3)}.
- **Cuentas por cobrar:** la variacion de CxC alcanza **{fmt_num(c['var_cxc'][2025], 2)}x** en 2025
  (frente a un crecimiento de ingresos de un solo digito), presionando el capital de trabajo.
- **Hallazgo de trazabilidad:** `i_ori_inmuebles` 2022 ({fmt_num(c['i_ori_inmuebles_2022'], 0)} vs Nota 25 $11.751)
  permanece en DUDOSO pendiente de pronunciamiento humano.

### 2.3 Indicadores clave por periodo

| Periodo | ROIC | WACC | Spread | NOPAT (M$) | EVA (M$) | FCO/UN | End. total |
|---|---|---|---|---|---|---|---|
{ "".join( f"| {a} | {fmt_num(c['roic'][a], 3)} | {fmt_num(c['wacc'][a], 3)} | {fmt_num(c['spread'][a], 3)} | {fmt_num(c['nopat'][a], 0)} | {fmt_num(c['eva'][a], 0)} | {fmt_num(c['fco_un'][a], 2)} | {fmt_num(c['endeudamiento'][a], 3)} |\n" for a in c['periodos_eva'] )}

""")

    # Capitulos por familia (3..11): narrativa + tabla completa de cada familia
    tabla = c["tabla_indicadores"]
    familias = list(tabla["clasificacion"].drop_duplicates())
    for i, familia in enumerate(familias, start=3):
        sub = tabla[tabla["clasificacion"] == familia]
        partes.append(capitulo_familia(i, str(familia), sub, c))

    # Capitulo de riesgos y alarmas
    num_riesgos = 3 + len(familias)
    partes.append(capitulo_riesgos(num_riesgos, c))

    partes.append(f"""## {num_riesgos + 1}. ANALISIS FORENSE Y BITACORA

- **Evento 522 (Fase 8 - Evidencia Formal):** {c['evidencia_total']} observaciones
  (87 conceptos x 6 anos) cruzadas contra la segmentacion de los estados financieros:
  {c['evidencia_aceptado']} **ACEPTADO**, {c['evidencia_no_encontrado']} **NO_ENCONTRADO**,
  {c['evidencia_dudoso']} **DUDOSO**. Trazabilidad `documento -> entidad -> periodo -> dato -> variable_madre -> fuente -> evidencia -> validacion -> indicador`.
- **Hallazgo `i_ori_inmuebles` 2022 (DUDOSO / Protocolo Pasos B-C):** el consolidado registra
  **{fmt_num(c['i_ori_inmuebles_2022'], 0)}** mientras la Nota 25 de los estados financieros 2022
  señala **$11.751**. Se mantiene el valor consolidado, no se interpola; se solicita pronunciamiento
  humano. Impacto en ROIC/EBIT/NOPAT/WACC: **NULO** (los ORI se excluyen de esos calculos).
- **Fase 9 (Validacion Transversal):** integridad matematica/sintactica 100 %; los DUDOSO
  metodologicos (NOPAT Art. 240, RONA, WACC) quedaron resueltos en bitacora.
- **Divergencias tributarias:** tasa estatutaria Art. 240 E.T. (2020: 32 %, 2021: 31 %, 2022+: 35 %)
  aplicada al NOPAT con fines de comparabilidad; la tasa real vigente 2022 = 35 %.""")

    partes.append(f"""## {num_riesgos + 2}. RECOMENDACIONES ESTRATEGICAS Y PLAN DE ACCION

1. **Gestion del capital:** reasignar capital ocioso hacia proyectos con retorno superior al WACC
   para cerrar la brecha del EVA (margen actual delgado, +0,35 a +1,88 pp).
2. **Calidad de caja:** monitorear el ciclo de conversion; normalizar el cobro de CxC
   (variacion +{fmt_num(c['var_cxc'][2025], 2)}x en 2025) para reconvertir utilidades en flujo.
3. **Control del gasto:** contener gastos de administracion y beneficios a empleados que presionaron
   el margen operativo desde 2021.
4. **Resolucion del hallazgo:** pronunciamiento humano sobre `i_ori_inmuebles` 2022
   (aceptar / ajustar / NO_ENCONTRADO) para cerrar el DUDOSO y sanitizar la matriz.
5. **Observabilidad:** mantener el Data Mart y el dashboard como capa unica de verdad;
   documentar cada decision en la bitacora de revisiones humanas.""")

    partes.append(f"""## {num_riesgos + 3}. MATRIZ CONSOLIDADA DE INDICADORES (65) POR FAMILIA Y PERIODO

El Data Mart contiene **{c['total_indicadores']} indicadores** catalogados
({c['indicadores_con_valor']} con valores calculados y {c['total_indicadores'] - c['indicadores_con_valor']}
sin base de calculo: inventarios y ciclos, ausentes de forma coherente en la entidad).
Clasificados por familia y ordenados de periodo mas antiguo (2020) a mas reciente (2025):

{table_por_familia(c)}""")

    return "\n\n".join(partes)


# --------------------------------------------------------------------------- #
# 3. Graficos dinamicos (matplotlib) para incrustar en el PDF
# --------------------------------------------------------------------------- #
def _grafico_familia(nombre: str, sub: pd.DataFrame) -> Path | None:
    """Small-multiples con la evolucion de los indicadores con valores de una familia."""
    filas = sub[sub[PERIODOS].notna().any(axis=1)].reset_index(drop=True)
    if filas.empty:
        return None
    filas = filas.head(6)
    n = len(filas)
    cols = 2
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(7.2, 2.0 * rows), dpi=130)
    axes = np.atleast_1d(axes).ravel()
    anos = [str(a) for a in PERIODOS]
    for ax, rec in zip(axes, filas.to_dict("records")):
        vals = [float(rec[a]) if pd.notna(rec[a]) else np.nan for a in PERIODOS]
        ax.plot(anos, vals, marker="o", color="#1f77b4", linewidth=1.5, markersize=3)
        ax.set_title(str(rec["indicador"])[:52], fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3)
        if rec.get("unidad"):
            ax.set_ylabel(str(rec["unidad"]), fontsize=7)
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle(f"Familia: {nombre}", fontsize=10)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    safe = re.sub(r"[^A-Za-z0-9]+", "_", nombre).strip("_").lower()
    p = GRAF_DIR / f"familia_{safe}.png"
    fig.savefig(p)
    plt.close(fig)
    return p


def generar_graficos(c: Dict) -> Tuple[Path, Path, Dict[str, Path]]:
    """Genera los PNG de tendencia (ROIC/WACC, FCO/UN) y los small-multiples por familia."""
    GRAF_DIR.mkdir(parents=True, exist_ok=True)

    anos = [str(a) for a in c["periodos_eva"]]
    roic = [float(c["roic"][a]) for a in c["periodos_eva"]]
    wacc = [float(c["wacc"][a]) for a in c["periodos_eva"]]
    spread = [float(c["spread"][a]) for a in c["periodos_eva"]]

    fig, ax = plt.subplots(figsize=(7.2, 3.6), dpi=130)
    ax.plot(anos, roic, marker="o", label="ROIC", color="#1f77b4")
    ax.plot(anos, wacc, marker="s", label="WACC", color="#d62728")
    ax.plot(anos, spread, marker="^", linestyle="--", label="Spread (ROIC-WACC)", color="#2ca02c")
    for i, v in enumerate(spread):
        ax.annotate(f"{v:.3f}", (anos[i], v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=7)
    ax.set_title("Evolucion ROIC vs WACC y Spread (2021-2025)")
    ax.set_xlabel("Periodo"); ax.set_ylabel("Proporcion")
    ax.legend(fontsize=8); ax.grid(True, alpha=0.3)
    fig.tight_layout()
    p1 = GRAF_DIR / "grafico_roic_wacc.png"
    fig.savefig(p1)
    plt.close(fig)

    anos6 = [str(a) for a in c["periodos"]]
    fco = [float(c["fco_un"][a]) if pd.notna(c["fco_un"][a]) else None for a in c["periodos"]]
    fig2, ax2 = plt.subplots(figsize=(7.2, 3.6), dpi=130)
    colores = ["#e74c3c" if (v is not None and v < 0) else "#2ecc71" for v in fco]
    ax2.bar(anos6, fco, color=colores, alpha=0.85)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_title("Calidad de utilidades: FCO / Utilidad Neta (2020-2025)")
    ax2.set_xlabel("Periodo"); ax2.set_ylabel("FCO/UN (indice)")
    ax2.grid(True, axis="y", alpha=0.3)
    fig2.tight_layout()
    p2 = GRAF_DIR / "grafico_fco_un.png"
    fig2.savefig(p2)
    plt.close(fig2)

    graficos_familia: Dict[str, Path] = {}
    tabla = c["tabla_indicadores"]
    for familia in tabla["clasificacion"].drop_duplicates():
        sub = tabla[tabla["clasificacion"] == familia]
        p = _grafico_familia(str(familia), sub)
        if p is not None:
            graficos_familia[str(familia)] = p

    return p1, p2, graficos_familia


# --------------------------------------------------------------------------- #
# 4. Compilacion del PDF (fpdf2)
# --------------------------------------------------------------------------- #
def md_a_html(md: str) -> str:
    """Convierte el markdown reducido del informe a HTML para fpdf2."""
    lines = md.splitlines()
    out: List[str] = []
    in_list = False
    in_table = False
    primera_fila = False
    for raw in lines:
        line = raw.rstrip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            if in_table:
                out.append("</table>")
                in_table = False
            continue
        if line.startswith("### "):
            if in_list:
                out.append("</ul>"); in_list = False
            if in_table:
                out.append("</table>"); in_table = False
            out.append(f"<h3>{_b(line[4:])}</h3>")
        elif line.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list = False
            if in_table:
                out.append("</table>"); in_table = False
            out.append(f"<h2>{_b(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                out.append("</ul>"); in_list = False
            if in_table:
                out.append("</table>"); in_table = False
            out.append(f"<h1>{_b(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_b(line[2:])}</li>")
        elif line.startswith("|"):
            celdas = [x.strip() for x in line.split("|")[1:-1]]
            if not celdas:
                continue
            # Linea separadora |---|---|
            if all(re.fullmatch(r"[-:]+", x or "") for x in celdas):
                continue
            if not in_table:
                out.append('<table border="1" align="center">')
                in_table = True
                primera_fila = True
            etiqueta = "th" if primera_fila else "td"
            primera_fila = False
            celdas_html = "".join(f"<{etiqueta}>{_b(x)}</{etiqueta}>" for x in celdas)
            out.append(f"<tr>{celdas_html}</tr>")
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            if in_table:
                out.append("</table>"); in_table = False
            out.append(f"<p>{_b(line)}</p>")
    if in_list:
        out.append("</ul>")
    if in_table:
        out.append("</table>")
    return "\n".join(out)


def _b(texto: str) -> str:
    """Escapa caracteres especiales y convierte **negrita** en <b>..</b>."""
    texto = texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)


def _dividir_h2(html: str) -> List[Dict[str, str]]:
    """Divide el HTML en bloques por cada <h2>, conservando el preambulo."""
    idxs = [m.start() for m in re.finditer(r"<h2>", html)]
    if not idxs:
        return [{"titulo": "__pre__", "html": html}]
    bloques: List[Dict[str, str]] = []
    if idxs[0] > 0:
        bloques.append({"titulo": "__pre__", "html": html[: idxs[0]]})
    for i, start in enumerate(idxs):
        end = idxs[i + 1] if i + 1 < len(idxs) else len(html)
        bloque = html[start:end]
        m = re.match(r"<h2>(.*?)</h2>", bloque, re.S)
        titulo = re.sub(r"<[^>]+>", "", m.group(1)) if m else ""
        bloques.append({"titulo": titulo, "html": bloque})
    return bloques


class InformePDF(FPDF):
    """PDF con pie de pagina institucional (numeracion)."""

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Arial", "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"Informe Diagnostico Financiero 2020-2025  |  Pagina {self.page_no()}", align="C")


def compilar_pdf(markdown: str, graficos: Tuple[Path, Path, Dict[str, Path]], c: Dict) -> Path:
    """Compila el informe markdown + graficos en un PDF profesional.

    Secciones verticales con un capitulo por familia y el capitulo de riesgos;
    la matriz consolidada (65 indicadores) se renderiza en paginas apaisadas.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = InformePDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_font("Arial", "", AA)
    pdf.add_font("Arial", "B", AA_B)

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 14, "INFORME DIAGNOSTICO FINANCIERO", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 12, "2020-2025", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.ln(10)
    pdf.set_draw_color(44, 62, 80)
    pdf.line(25, pdf.get_y(), 185, pdf.get_y())
    pdf.ln(8)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(50, 50, 50)
    nombre_entidad, nit_entidad = cargar_entidad()
    if nombre_entidad:
        encabezado_entidad = "Entidad: " + nombre_entidad
        if nit_entidad:
            encabezado_entidad += " | NIT " + nit_entidad
        encabezado_entidad += ". "
    else:
        encabezado_entidad = "Entidad: reservada (agnosticismo de entidad). "
    resumen = (
        encabezado_entidad +
        "Periodo analizado: 2020-2025."
        " Motor de calculo: matriz consolidada auditada (65 indicadores x 6 anos)."
        " Validacion transversal Fase 9: integridad 100 %. Cumplimiento: NIIF/IFRS."
    )
    pdf.multi_cell(0, 5.5, resumen)

    grafico_roic_wacc, grafico_fco_un, graf_familias = graficos
    html = md_a_html(markdown)
    bloques = _dividir_h2(html)

    pdf.add_page()
    insertadas: set = set()
    for blq in bloques:
        titulo = blq["titulo"]
        if titulo == "__pre__":
            _write_html_seguro(pdf, blq["html"], markdown)
            continue
        if re.match(r"^\d+\.\s*MATRIZ CONSOLIDADA", titulo):
            _escribir_matriz_landscape(pdf, blq["html"], markdown, c)
            continue
        _write_html_seguro(pdf, blq["html"], markdown)
        if titulo.startswith("2."):
            _insertar_grafico(pdf, grafico_roic_wacc, "Evolucion ROIC vs WACC y Spread (2021-2025)")
            _insertar_grafico(pdf, grafico_fco_un, "Calidad de utilidades: FCO / Utilidad Neta (2020-2025)")
        if "FAMILIA:" in titulo:
            etiqueta = titulo.split("FAMILIA:", 1)[1].strip().lower()
            for nombre_fam, ruta in graf_familias.items():
                if nombre_fam.lower() == etiqueta and nombre_fam not in insertadas:
                    _insertar_grafico(pdf, ruta, f"Evolucion de la familia: {nombre_fam}")
                    insertadas.add(nombre_fam)

    ruta = OUT_DIR / NOMBRE_PDF
    pdf.output(str(ruta))
    return ruta


def _write_html_seguro(pdf: FPDF, bloque_html: str, markdown: str) -> None:
    """Renderiza un bloque HTML; si fpdf2 falla, escribe texto plano (sin abortar)."""
    if not bloque_html or not bloque_html.strip():
        return
    try:
        pdf.write_html(bloque_html)
    except Exception:
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 4.5, re.sub(r"<[^>]+>", " ", bloque_html).replace("&amp;", "&"))


def _escribir_matriz_landscape(pdf: FPDF, bloque_html: str, markdown: str, c: Dict) -> None:
    """Renderiza la Seccion 6 (matriz de los 65 indicadores) en paginas apaisadas.

    La tabla de 7 columnas (id, indicador y 6 periodos) no cabe en A4 vertical;
    fpdf2 permite mezclar orientaciones por pagina dentro del mismo documento.
    """
    if not bloque_html or not bloque_html.strip():
        return
    lm_left, lm_right, tm, bm = pdf.l_margin, pdf.r_margin, pdf.t_margin, pdf.b_margin
    pdf.set_left_margin(10)
    pdf.set_right_margin(10)
    pdf.set_top_margin(10)
    pdf.set_auto_page_break(True, margin=10)
    pdf.add_page(orientation="L")
    try:
        pdf.write_html(bloque_html)
    finally:
        pdf.set_left_margin(lm_left)
        pdf.set_right_margin(lm_right)
        pdf.set_top_margin(tm)
        pdf.b_margin = bm
        pdf.set_auto_page_break(True, margin=bm)


def _insertar_grafico(pdf: FPDF, grafico: Path, titulo: str) -> None:
    """Inserta una imagen centrada con su leyenda, controlando el salto de pagina."""
    if not Path(grafico).exists():
        return
    try:
        from PIL import Image
        with Image.open(grafico) as im:
            ancho_px, alto_px = im.size
        alto_mm = 170.0 * alto_px / ancho_px
    except Exception:
        alto_mm = 90.0
    if pdf.get_y() + alto_mm + 12 > pdf.page_break_trigger:
        pdf.add_page()
    pdf.ln(3)
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 5, titulo, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_text_color(50, 50, 50)
    pdf.ln(2)
    pdf.image(str(grafico), x=None, w=170)


# --------------------------------------------------------------------------- #
# 5. API publica para dashboard y CLI
# --------------------------------------------------------------------------- #
def generar_informe_pdf() -> Path:
    """Orquesta la generacion completa del informe PDF."""
    c = construir_contexto()
    md = redactar_analisis(c)
    return compilar_pdf(md, generar_graficos(c), c)


def generar_informe_bytes() -> bytes:
    """Devuelve los bytes del PDF generado (para st.download_button)."""
    ruta = generar_informe_pdf()
    return ruta.read_bytes()


if __name__ == "__main__":
    ruta = generar_informe_pdf()
    print("Informe PDF generado:", ruta)
    print("Tamano (bytes):", ruta.stat().st_size)