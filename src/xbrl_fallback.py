import glob
import os

import pandas as pd

CONCEPTOS = {
    "Assets": "Total activos",
    "Liabilities": "Total pasivos",
    "Equity": "Total patrimonio",
    "CashAndCashEquivalents": "Efectivo y equivalentes",
    "Revenue": "Ingresos de actividades ordinarias",
    "ProfitLoss": "Resultado del periodo",
}

XBRL_CARPETAS = {
    2021: r"C:\Users\Usuario\Desktop\mi_proyecto_finanzas\AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2021",
    2022: r"C:\Users\Usuario\Desktop\mi_proyecto_finanzas\AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2022",
    2023: r"C:\Users\Usuario\Desktop\mi_proyecto_finanzas\AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2023",
    2024: r"C:\Users\Usuario\Desktop\mi_proyecto_finanzas\AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2024",
    2025: r"C:\Users\Usuario\Desktop\mi_proyecto_finanzas\AUTOMAT ANALISIS FIN\Estados Financieros\ESTADOS_FINANCIEROS_2025",
}


def find_xbrl(ano, base_dir=None):
    folder = base_dir or XBRL_CARPETAS[ano]
    cands = glob.glob(os.path.join(folder, "*.xbrl"))
    if not cands:
        raise FileNotFoundError("No hay archivo XBRL para %d en %s" % (ano, folder))
    return sorted(cands)[0]


def leer_xbrl(path):
    import lxml.etree as etree

    root = etree.parse(path).getroot()
    periods = {}
    for c in root.xpath("//*[local-name()='context']"):
        inst = c.xpath("./*[local-name()='period']/*[local-name()='instant']/text()")
        if inst:
            periods[c.get("id")] = ("instant", inst[0])
        else:
            sd = c.xpath("./*[local-name()='period']/*[local-name()='startDate']/text()")
            ed = c.xpath("./*[local-name()='period']/*[local-name()='endDate']/text()")
            periods[c.get("id")] = ("duration", sd[0] if sd else "", ed[0] if ed else "")
    entity = root.xpath("//*[local-name()='identifier']/text()")
    entidad = entity[0].strip() if entity else None
    values = {k: {} for k in CONCEPTOS}
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag not in CONCEPTOS:
            continue
        ctx = el.get("contextRef")
        if not ctx or ctx not in periods:
            continue
        kind, *period = periods[ctx]
        year = int((period[1] if kind == "duration" else period[0])[:4])
        try:
            value = int(el.text)
        except (TypeError, ValueError):
            continue
        cur = values[tag]
        if year not in cur or (year in cur and kind == "instant"):
            cur[year] = value
    return entidad, values


def L_default():
    import lectura_pdfs as L

    return L.DEFAULT_FINANCIEROS


MAPEO_CANONICO = {
    "Assets": "b_activo_total",
    "Liabilities": "b_pasivo_total",
    "Equity": "b_patrimonio_total",
    "CashAndCashEquivalents": "b_efectivo",
    "Revenue": "i_comisiones",
    "ProfitLoss": "i_resultado_del_ejercicio",
}


def fallback_comparativo(base_dir=None, pdf_base=None):
    import estados_normalizados as EN

    df_pdf, _ = EN.normalizar(base_dir=pdf_base or L_default())
    filas = []
    notas = []
    for ano in sorted(XBRL_CARPETAS):
        path = find_xbrl(ano, base_dir)
        entidad, values = leer_xbrl(path)
        notas.append(
            "%d: entidad %s (XBRL de otra sociedad, NO comparable con FIDUCIARIA LA PREVISORA)"
            % (ano, entidad)
        )
        row = {"anio": ano, "entidad": entidad, "archivo": os.path.basename(path)}
        for tag, _rotulo in CONCEPTOS.items():
            v = values.get(tag, {}).get(ano)
            row["%s_millones" % tag] = v / 1e6 if v is not None else None
        filas.append(row)
    df = pd.DataFrame.from_records(filas).set_index("anio")
    return df, "\n".join(notas)


def main():
    df, notas = fallback_comparativo()
    print("ALERTAS XBRL (fallback no aplicable por entidad distinta):")
    print(notas)
    print()
    print(df.to_string())


if __name__ == "__main__":
    main()