import argparse
import os
import json

import pandas as pd

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SALIDAS = os.path.join(BASE, "salidas")
OUT_DIR = os.path.join(SALIDAS, "power_bi")

PERIODOS = [2020, 2021, 2022, 2023, 2024, 2025]

MAP_CARPETA_PBI = {
    "Liquidez": "Efectivo & Liquidez",
    "Capital de trabajo y ciclo": "Efectivo & Liquidez",
    "Rentabilidad": "Rentabilidad & EVA",
    "Crecimiento": "Rentabilidad & EVA",
    "Creacion de valor y DuPont": "Rentabilidad & EVA",
    "Actividad y eficiencia": "Estructura & Riesgo",
    "Endeudamiento y solvencia": "Estructura & Riesgo",
    "Cobertura y capacidad de pago": "Estructura & Riesgo",
    "Calidad de resultados": "Estructura & Riesgo",
}

TIPO_UNIDAD = {
    4: "moneda", 5: "ratio", 24: "moneda", 25: "moneda", 26: "porcentaje",
    27: "porcentaje", 28: "porcentaje", 29: "porcentaje", 30: "porcentaje",
    33: "moneda", 36: "dias", 37: "dias", 38: "moneda", 39: "ratio",
    40: "veces", 41: "veces", 50: "moneda", 51: "moneda", 52: "moneda",
    53: "veces", 54: "moneda", 55: "veces", 56: "veces",
}


def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)


def _melt_indicadores():
    path = os.path.join(SALIDAS, "indicadores.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.rename(columns={"#": "id_indicador", "clasificacion": "clasificacion", "indicador": "indicador", "formula": "formula"})
    id_cols = ["id_indicador", "clasificacion", "indicador", "formula"]
    value_cols = [str(p) for p in PERIODOS]
    melted = df.melt(id_vars=id_cols, value_vars=value_cols, var_name="periodo", value_name="valor")
    melted["periodo"] = melted["periodo"].astype(int)
    return df, melted


def build_dim_fecha():
    return pd.DataFrame({
        "id_fecha": range(1, len(PERIODOS) + 1),
        "periodo": PERIODOS,
        "etiqueta": [str(p) for p in PERIODOS],
    })


def build_dim_indicador(wide):
    dim = wide[["id_indicador", "clasificacion", "indicador", "formula"]].copy()
    dim["carpeta_powerbi"] = dim["clasificacion"].map(MAP_CARPETA_PBI).fillna("Estructura & Riesgo")
    dim["unidad"] = dim["id_indicador"].map(TIPO_UNIDAD).fillna("ratio")
    dim = dim.rename(columns={"id_indicador": "id_indicador"})
    return dim


def build_fact_indicadores(melted):
    fact = melted[["periodo", "id_indicador", "valor"]].copy()
    fact = fact.sort_values(["id_indicador", "periodo"]).reset_index(drop=True)
    return fact


def build_dim_concepto():
    path = os.path.join(SALIDAS, "datos_estados_financieros.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    dim = df[["concepto", "rotulo", "estado", "clasificacion"]].copy()
    return dim


def build_fact_estados():
    path = os.path.join(SALIDAS, "datos_estados_financieros.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    id_cols = ["concepto", "rotulo", "estado", "clasificacion"]
    value_cols = [str(p) for p in PERIODOS]
    melted = df.melt(id_vars=id_cols, value_vars=value_cols, var_name="periodo", value_name="valor")
    melted["periodo"] = melted["periodo"].astype(int)
    fact = melted[["periodo", "concepto", "valor"]].sort_values(["concepto", "periodo"]).reset_index(drop=True)
    return fact


def build_fact_wacc():
    path = os.path.join(SALIDAS, "fase7_wacc_roi", "wacc_roi_2020_2025.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.rename(columns={"roi_ke_roic": "roic"})
    df["capital_empleado"] = df["deuda_financiera_total"] + df["patrimonio_total"]
    df["periodo"] = df["periodo"].astype(int)
    cols = ["periodo", "deuda_financiera_total", "patrimonio_total", "capital_empleado",
            "intereses_pagados_abs", "costo_deuda_bruto", "tasa_estatutaria", "costo_deuda_neto",
            "proporcion_deuda", "proporcion_patrimonio", "roic", "wacc", "estado"]
    return df[cols]


def build_fact_evidencia():
    path = os.path.join(SALIDAS, "fase8_evidencia_formal", "evidencia_formal_conceptos.csv")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df = df.rename(columns={"anio": "periodo"})
    df["periodo"] = df["periodo"].astype(int)
    df["coincide"] = df["coincide"].astype(bool)
    return df


def resolve_workspace(empresa):
    """Resuelve raiz de insumos/salidas del Data Mart.

    Sin --empresa usa la entidad ancla (raiz del repo). Con --empresa usa
    `almacen_empresas/<empresa>/salidas` completamente aislada.
    """
    global SALIDAS, OUT_DIR
    if empresa:
        base_empresa = os.path.join(BASE, "almacen_empresas", empresa, "salidas")
        SALIDAS = base_empresa
        OUT_DIR = os.path.join(base_empresa, "power_bi")
    else:
        SALIDAS = os.path.join(BASE, "salidas")
        OUT_DIR = os.path.join(SALIDAS, "power_bi")


def main():
    ap = argparse.ArgumentParser(
        description="Genera el Data Mart Power BI (7 tablas) para una entidad.")
    ap.add_argument("--empresa", default=None,
                    help="Identificador de empresa en almacen_empresas/<empresa>. "
                         "Si se omite, genera el Data Mart de la entidad ancla (raiz).")
    args = ap.parse_args()
    resolve_workspace(args.empresa)
    ensure_dirs()

    wide_inds, melt_inds = _melt_indicadores()

    dim_fecha = build_dim_fecha()
    dim_indicador = build_dim_indicador(wide_inds)
    fact_indicadores = build_fact_indicadores(melt_inds)
    dim_concepto = build_dim_concepto()
    fact_estados = build_fact_estados()
    fact_wacc = build_fact_wacc()
    fact_evidencia = build_fact_evidencia()

    tables = {
        "dim_fecha.csv": dim_fecha,
        "dim_indicador.csv": dim_indicador,
        "fact_indicadores.csv": fact_indicadores,
        "dim_concepto.csv": dim_concepto,
        "fact_estados.csv": fact_estados,
        "fact_wacc.csv": fact_wacc,
        "fact_evidencia.csv": fact_evidencia,
    }

    for fname, df in tables.items():
        df.to_csv(os.path.join(OUT_DIR, fname), index=False, encoding="utf-8-sig")

    resumen = {
        "carpetas_powerbi": sorted(dim_indicador["carpeta_powerbi"].unique().tolist()),
        "conteo_tablas": {fname: int(len(df)) for fname, df in tables.items()},
        "indicadores": int(dim_indicador.shape[0]),
        "periodos": PERIODOS,
        "fact_indicadores_no_nulo": int(fact_indicadores["valor"].notna().sum()),
        "fact_evidencia_total": int(fact_evidencia.shape[0]),
        "fact_evidencia_por_estado": fact_evidencia["estado"].value_counts().to_dict(),
    }

    with open(os.path.join(OUT_DIR, "data_mart_resumen.json"), "w", encoding="utf-8") as fh:
        json.dump(resumen, fh, ensure_ascii=False, indent=2)

    print("== DATA MART POWER BI GENERADO ==")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()