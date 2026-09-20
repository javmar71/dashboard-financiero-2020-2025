import os

import pandas as pd

import lectura_pdfs as L
import taxonomia as T
from lectura_pdfs import EstadoIDs

YEARS_SOURCE = (2021, 2022, 2023, 2024, 2025)
YEARS_OUT = (2020, 2021, 2022, 2023, 2024, 2025)

ROTULOS = {
    "b_efectivo": "Efectivo y equivalentes",
    "b_inversiones": "Inversiones",
    "b_cuentas_por_cobrar": "Cuentas por cobrar",
    "b_impuesto_corriente_activo": "Impuesto corriente (activo)",
    "b_impuesto_diferido_activo": "Impuesto diferido (activo)",
    "b_otros_activos_no_financieros": "Otros activos no financieros",
    "b_propiedades_planta_equipo": "Propiedades y equipo",
    "b_derecho_uso_activo": "Derecho de uso (activo)",
    "b_activos_intangibles": "Activos intangibles",
    "b_activo_total": "Total activos",
    "b_cuentas_por_pagar": "Cuentas por pagar",
    "b_derecho_uso_pasivo": "Derecho de uso (pasivo)",
    "b_beneficios_empleados": "Beneficios a empleados",
    "b_provisiones": "Provisiones",
    "b_impuesto_corriente_pasivo": "Impuesto corriente (pasivo)",
    "b_impuesto_diferido_pasivo": "Impuesto diferido (pasivo)",
    "b_otros_pasivos_no_financieros": "Otros pasivos no financieros",
    "b_pasivo_total": "Total pasivos",
    "b_capital_suscrito": "Capital suscrito y pagado",
    "b_prima_colocacion": "Prima en colocacion de acciones",
    "b_reservas": "Reservas",
    "b_utilidad_periodo": "Utilidad del periodo",
    "b_utilidad_ejercicios_anteriores": "Utilidad de ejercicios anteriores",
    "b_efecto_ncif": "Efecto NCIF",
    "b_ori_valorizacion": "Ganancias no realizadas (ORI)",
    "b_patrimonio_total": "Total patrimonio",
    "b_total_pasivo_patrimonio": "Total pasivo y patrimonio",
    "i_comisiones": "Comisiones y honorarios",
    "i_ingresos_operaciones_conjuntas": "Ingresos operaciones conjuntas",
    "i_utilidad_bruta": "Resultado antes de gastos de operacion",
    "i_gasto_beneficios": "Gasto beneficios a empleados",
    "i_gastos_administracion": "Gastos de administracion",
    "i_gastos_operaciones_conjuntas": "Gastos operaciones conjuntas",
    "i_deterioro_cxc": "Deterioro cuentas por cobrar",
    "i_depreciaciones": "Depreciacion",
    "i_amortizaciones": "Amortizacion",
    "i_resultado_despues_gastos": "Resultado despues de gastos",
    "i_resultado_financiero_neto": "Resultado financiero neto",
    "i_resultado_operacional": "Resultado operacional",
    "i_otros_ingresos_egresos": "Otros ingresos/(egresos)",
    "i_resultado_antes_impuestos": "Resultado antes de impuestos",
    "i_gasto_impuesto_corriente": "Gasto impuesto corriente",
    "i_gasto_impuesto_diferido": "Gasto/(ingreso) impuesto diferido",
    "i_resultado_del_ejercicio": "Resultado del ejercicio",
    "i_ori_titulos": "ORI - titulares participativos",
    "i_ori_actuarial": "ORI - actuarial pensionados",
    "i_ori_inmuebles": "ORI - bienes inmuebles",
    "i_impuesto_diferido_ori": "ORI - impuesto diferido",
    "i_ori_total": "Total otro resultado integral",
    "i_comprehensivo_total": "Resultado integral total",
    "c_utilidad_del_ejercicio": "CF - Utilidad del ejercicio",
    "c_depreciacion": "CF - Depreciacion",
    "c_depreciacion_derecho_uso": "CF - Depreciacion derecho de uso",
    "c_provisiones": "CF - Provisiones",
    "c_deterioro_cxc": "CF - Deterioro cuentas por cobrar",
    "c_reintegro_provisiones": "CF - Reintegro provisiones",
    "c_valoracion_inversiones": "CF - Valoracion inversiones",
    "c_amortizacion_intangibles": "CF - Amortizacion intangibles",
    "c_amortizacion_otros": "CF - Amortizacion otros activos",
    "c_intereses_arrendamiento": "CF - Intereses arrendamiento",
    "c_gasto_impuesto_corriente": "CF - Gasto impuesto corriente",
    "c_gasto_impuesto_diferido": "CF - Gasto impuesto diferido",
    "c_baja_ppye": "CF - Baja propiedades y equipo",
    "c_baja_depreciacion_ppye": "CF - Baja por depreciacion PyE",
    "c_baja_intangibles": "CF - Baja activos intangibles",
    "c_baja_amortizacion_intangibles": "CF - Baja por amortizacion intangibles",
    "c_cuentas_por_cobrar": "CF - Cambio cuentas por cobrar",
    "c_otros_activos": "CF - Cambio otros activos",
    "c_cuentas_por_pagar": "CF - Cambio cuentas por pagar",
    "c_impuestos_neto": "CF - Impuestos netos",
    "c_beneficios_empleados": "CF - Beneficios a empleados",
    "c_pasivos_provisiones": "CF - Pasivos por provisiones",
    "c_intereses_pagados": "CF - Intereses pagados",
    "c_impuestos_pagados": "CF - Impuestos pagados",
    "c_flujo_operacion": "Flujo neto actividades de operacion",
    "c_inversiones": "CF - Inversiones",
    "c_adquisicion_ppye": "CF - Adquisicion propiedades y equipo",
    "c_adquisicion_intangibles": "CF - Adquisicion intangibles",
    "c_flujo_inversion": "Flujo neto actividades de inversion",
    "c_pagos_arrendamiento": "CF - Pagos parte principal arrendamientos",
    "c_dividendos": "CF - Dividendos decretados",
    "c_flujo_financiacion": "Flujo neto actividades de financiacion",
    "c_aumento_neto": "Aumento neto de efectivo",
    "c_efectivo_restriccion": "Efectivo restringido (al inicio)",
    "c_efectivo_sin_restriccion": "Efectivo sin restriccion (al inicio)",
    "c_efectivo_inicio": "Efectivo al inicio del periodo",
    "c_efectivo_cierre": "Efectivo al cierre del periodo",
}

ESTADO_DE = {}
for k, _ in T.BALANCE_ORDER:
    ESTADO_DE[k] = "balance"
for k, _ in T.INCOME_ORDER:
    ESTADO_DE[k] = "ingresos"
for k, _ in T.CFLOW_ORDER:
    ESTADO_DE[k] = "flujos"

ALL_KEYS = list(ROTULOS.keys())


def clasificacion(k):
    for grp in ("activo_corriente", "activo_no_corriente", "pasivo_corriente", "pasivo_no_corriente"):
        if k in T.CORRIENTE_RULES[grp]:
            return grp
    return ""


def cargar_classified(anos=None, base_dir=L.DEFAULT_FINANCIEROS):
    anos = anos if anos is not None else YEARS_SOURCE
    return {a: T.classify_all(L.statement_pages(L.find_pdf(a, base_dir))) for a in anos}


def build_series(classified):
    series = {k: {} for k in ALL_KEYS}
    conflicts = []
    for yr in sorted(classified):
        m = classified[yr]
        for st in (EstadoIDs.BALANCE, EstadoIDs.INCOME, EstadoIDs.CASHFLOW):
            for k, r in m.get(st, {}).items():
                _set_value(series[k], yr, r["cur"], yr, "cur", conflicts)
                if yr - 1 >= min(YEARS_OUT):
                    _set_value(series[k], yr - 1, r["prev"], yr, "prev", conflicts)
    return series, conflicts


def _set_value(cell, year, value, src_year, column, conflicts):
    if value is None:
        return
    cur = cell.get(year)
    if cur is None:
        cell[year] = value
        return
    if cur != value:
        conflicts.append((year, value, src_year, column, cur))


def normalizar(anos=None, base_dir=L.DEFAULT_FINANCIEROS):
    classified = cargar_classified(anos, base_dir)
    series, conflicts = build_series(classified)
    rows = []
    for k in ALL_KEYS:
        row = {"concepto": k, "rotulo": ROTULOS[k], "estado": ESTADO_DE.get(k, "")}
        if ESTADO_DE.get(k) == "balance":
            row["clasificacion"] = clasificacion(k)
        for y in YEARS_OUT:
            row[str(y)] = series[k].get(y)
        rows.append(row)
    df = pd.DataFrame.from_records(rows).set_index("concepto")
    reporte = _reporte(classified, series, conflicts)
    return df, reporte


def _reporte(classified, series, conflicts):
    lines = []
    for yr in sorted(classified):
        m = classified[yr]
        parts = []
        for st in (EstadoIDs.BALANCE, EstadoIDs.INCOME, EstadoIDs.CASHFLOW):
            n = len(m.get(st, {}))
            total = len(T.ORDER[st])
            parts.append("%s %d/%d" % (st, n, total))
        lines.append("%d: %s" % (yr, "; ".join(parts)))
    lines.append("")
    for year in YEARS_OUT:
        n = sum(1 for k in ALL_KEYS if series[k].get(year) is not None)
        lines.append("Anio %d: %d/%d cuentas con valor" % (year, n, len(ALL_KEYS)))
    lines.append("")
    if conflicts:
        lines.append("CONFLICTOS cur/prev (%d):" % len(conflicts))
        for c in conflicts[:50]:
            lines.append("  anio=%d prev=%s (fuente pdf %d col %s) vs cur=%s" % c)
    else:
        lines.append("Sin conflictos cur/prev: todos los anios coinciden entre PDFs.")
    return "\n".join(lines)


def main():
    import sys

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "salidas")
    os.makedirs(out_dir, exist_ok=True)
    df, reporte = normalizar()
    csv_path = os.path.join(out_dir, "datos_estados_financieros.csv")
    df.to_csv(csv_path, index_label="concepto")
    report_path = os.path.join(out_dir, "reporte_cobertura.txt")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write(reporte + "\n")
    print(reporte)
    print("\nCSV guardado en %s (%d filas x %d columnas)" % (csv_path, df.shape[0], df.shape[1]))


if __name__ == "__main__":
    main()