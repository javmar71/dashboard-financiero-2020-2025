import os

import pandas as pd

from estados_normalizados import YEARS_OUT

YEARS = list(YEARS_OUT)


class _Serie(dict):
    def __getitem__(self, key):
        return super().get(key)

ACTIVO_CORRIENTE = [
    "b_efectivo",
    "b_inversiones",
    "b_cuentas_por_cobrar",
    "b_impuesto_corriente_activo",
    "b_otros_activos_no_financieros",
]
ACTIVO_NO_CORRIENTE = [
    "b_impuesto_diferido_activo",
    "b_propiedades_planta_equipo",
    "b_derecho_uso_activo",
    "b_activos_intangibles",
]
PASIVO_CORRIENTE = [
    "b_cuentas_por_pagar",
    "b_beneficios_empleados",
    "b_impuesto_corriente_pasivo",
    "b_otros_pasivos_no_financieros",
]
PASIVO_NO_CORRIENTE = ["b_provisiones", "b_impuesto_diferido_pasivo", "b_derecho_uso_pasivo"]
ACTIVO_CORRIENTE_OPERATIVO = ["b_efectivo", "b_cuentas_por_cobrar", "b_otros_activos_no_financieros"]
PASIVO_CORRIENTE_OPERATIVO = ["b_cuentas_por_pagar", "b_otros_pasivos_no_financieros"]
OTROS_ACTIVOS_NO_CORR_OPERATIVOS = ["b_activos_intangibles", "b_derecho_uso_activo"]

# N/A sin dato disponible en los estados (actividad fiduciaria, sin giro comercial)
NA_MOTIVOS = {
    "inventarios": "No aplica: la sociedad fiduciaria no maneja inventarios.",
    "costo_ventas": "No aplica: sin costo de ventas (actividad de servicios fiduciarios).",
    "compras_credito": "No aplica: sin compras a credito (sector servicios).",
    "creditos_financieros": "No aplica: sin desglose corriente/no corriente de obligaciones; se usa el pasivo por arrendamiento (derecho de uso) como proxy.",
    "sin_anterior": "Sin dato del periodo anterior para calcular el promedio/variacion.",
}


def cargar_base(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "salidas", "datos_estados_financieros.csv"
        )
    df = pd.read_csv(csv_path, index_col="concepto")
    base = {}
    for name, keys in {
        "activo_corriente": ACTIVO_CORRIENTE,
        "activo_no_corriente": ACTIVO_NO_CORRIENTE,
        "pasivo_corriente": PASIVO_CORRIENTE,
        "pasivo_no_corriente": PASIVO_NO_CORRIENTE,
        "activ_corr_operativo": ACTIVO_CORRIENTE_OPERATIVO,
        "pasiv_corr_operativo": PASIVO_CORRIENTE_OPERATIVO,
        "otros_anc_operativos": OTROS_ACTIVOS_NO_CORR_OPERATIVOS,
    }.items():
        base[name] = {
            y: _suma(df, keys, y) for y in YEARS
        }
    for k in [
        "b_efectivo",
        "b_inversiones",
        "b_cuentas_por_cobrar",
        "b_otros_activos_no_financieros",
        "b_propiedades_planta_equipo",
        "b_activos_intangibles",
        "b_activo_total",
        "b_cuentas_por_pagar",
        "b_derecho_uso_pasivo",
        "b_pasivo_total",
        "b_capital_suscrito",
        "b_impuesto_corriente_activo",
        "b_impuesto_diferido_activo",
        "b_otros_pasivos_no_financieros",
        "b_beneficios_empleados",
        "b_impuesto_corriente_pasivo",
        "b_patrimonio_total",
        "i_utilidad_bruta",
        "i_gasto_beneficios",
        "i_gastos_administracion",
        "i_gastos_operaciones_conjuntas",
        "i_deterioro_cxc",
        "i_otros_ingresos_egresos",
        "i_depreciaciones",
        "i_amortizaciones",
        "i_resultado_antes_impuestos",
        "i_gasto_impuesto_corriente",
        "i_resultado_del_ejercicio",
        "c_flujo_operacion",
        "c_intereses_pagados",
        "c_pagos_arrendamiento",
        "c_flujo_inversion",
    ]:
        base[k] = {y: _v(df, k, y) for y in YEARS}
    base["ingresos"] = base["i_utilidad_bruta"]
    base["utilidad_bruta"] = base["i_utilidad_bruta"]
    base["gastos_generales"] = {
        y: _sum(
            base["i_gasto_beneficios"][y],
            base["i_gastos_administracion"][y],
            base["i_gastos_operaciones_conjuntas"][y],
        )
        for y in YEARS
    }
    base["gastos_financieros"] = {y: _abs(base["c_intereses_pagados"][y]) for y in YEARS}
    base["amortizacion_deuda"] = {y: _abs(base["c_pagos_arrendamiento"][y]) for y in YEARS}
    base["obligaciones_financieras"] = base["b_derecho_uso_pasivo"]
    base["deuda_financiera"] = base["b_derecho_uso_pasivo"]
    base["efectivo"] = base["b_efectivo"]
    return {k: (_Serie(v) if isinstance(v, dict) else v) for k, v in base.items()}


def _suma(df, keys, year):
    total = None
    for k in keys:
        v = _v(df, k, year)
        total = v if total is None else _sum(total, v)
    return total


def _v(df, key, year):
    val = df.loc[key, str(year)]
    return None if pd.isna(val) else float(val)


def _sum(*args):
    vals = [a for a in args if a is not None]
    if not vals:
        return None
    return sum(vals)


def _abs(v):
    return None if v is None else abs(v)


def _neg(v):
    return None if v is None else -v


def _avg(v_cur, v_prev):
    if v_cur is None or v_prev is None:
        return None
    return (v_cur + v_prev) / 2


def _ratio(num, den):
    if num is None or den in (None, 0):
        return None
    return num / den


def _ebit(base, y):
    return _sum(
        base["ingresos"][y],
        _neg(base["gastos_generales"][y]),
        _neg(base["i_deterioro_cxc"][y]),
        base["i_otros_ingresos_egresos"][y],
    )


def _ebitda(base, y):
    v = _sum(_ebit(base, y), base["i_depreciaciones"][y], base["i_amortizaciones"][y])
    return v


def _ct(base, y):
    return _sum(base["activo_corriente"][y], _neg(base["pasivo_corriente"][y]))


def _ct_operativo(base, y):
    return _sum(base["activ_corr_operativo"][y], _neg(base["pasiv_corr_operativo"][y]))


def _var_abs(serie, y):
    if y - 1 not in YEARS or serie[y] is None or serie[y - 1] is None:
        return None
    return serie[y] - serie[y - 1]


def _var_ratio(serie, y):
    if y - 1 not in YEARS or serie[y - 1] in (None, 0):
        return None
    return _ratio(serie[y], serie[y - 1])


# id -> (clasificacion, nombre, formula, funcion(base, y))
INDICADORES = [
    (1, "Liquidez", "Razon corriente", "Activo corriente / Pasivo corriente",
     lambda b, y: _ratio(b["activo_corriente"][y], b["pasivo_corriente"][y])),
    (2, "Liquidez", "Prueba acida", "(Activo corriente - Inventarios) / Pasivo corriente",
     lambda b, y: _ratio(b["activo_corriente"][y], b["pasivo_corriente"][y])),
    (3, "Liquidez", "Razon de efectivo", "Efectivo y equivalentes de efectivo / Pasivo corriente",
     lambda b, y: _ratio(b["efectivo"][y], b["pasivo_corriente"][y])),
    (4, "Liquidez", "Capital de trabajo neto", "Activo corriente - Pasivo corriente",
     lambda b, y: _ct(b, y)),
    (5, "Liquidez", "Capital de trabajo / Activos", "Capital de trabajo neto / Activo total",
     lambda b, y: _ratio(_ct(b, y), b["b_activo_total"][y])),
    (6, "Endeudamiento y solvencia", "Endeudamiento total", "Pasivo total / Activo total",
     lambda b, y: _ratio(b["b_pasivo_total"][y], b["b_activo_total"][y])),
    (7, "Endeudamiento y solvencia", "Endeudamiento patrimonial", "Pasivo total / Patrimonio",
     lambda b, y: _ratio(b["b_pasivo_total"][y], b["b_patrimonio_total"][y])),
    (8, "Endeudamiento y solvencia", "Deuda financiera / Activos", "Deuda financiera / Activo total",
     lambda b, y: _ratio(b["deuda_financiera"][y], b["b_activo_total"][y])),
    (9, "Endeudamiento y solvencia", "Deuda financiera / Patrimonio", "Deuda financiera / Patrimonio",
     lambda b, y: _ratio(b["deuda_financiera"][y], b["b_patrimonio_total"][y])),
    (10, "Endeudamiento y solvencia", "Autonomia financiera", "Patrimonio / Activo total",
     lambda b, y: _ratio(b["b_patrimonio_total"][y], b["b_activo_total"][y])),
    (11, "Endeudamiento y solvencia", "Apalancamiento financiero", "Activo total / Patrimonio",
     lambda b, y: _ratio(b["b_activo_total"][y], b["b_patrimonio_total"][y])),
    (12, "Endeudamiento y solvencia", "Calidad de la deuda", "Pasivo corriente / Pasivo total",
     lambda b, y: _ratio(b["pasivo_corriente"][y], b["b_pasivo_total"][y])),
    (13, "Endeudamiento y solvencia", "Solvencia total", "Activo total / Pasivo total",
     lambda b, y: _ratio(b["b_activo_total"][y], b["b_pasivo_total"][y])),
    (14, "Endeudamiento y solvencia", "Pasivo / Capital",
     "Pasivo total / (Pasivo total + Patrimonio)",
     lambda b, y: _ratio(b["b_pasivo_total"][y], _sum(b["b_pasivo_total"][y], b["b_patrimonio_total"][y]))),
    (15, "Actividad y eficiencia", "Rotacion de activos totales",
     "Ingresos / ((Activo total actual + Activo total anterior) / 2)",
     lambda b, y: _ratio(b["ingresos"][y], _avg(b["b_activo_total"][y], b["b_activo_total"][y - 1]))),
    (16, "Actividad y eficiencia", "Rotacion de activos fijos",
     "Ingresos / ((Activo no corriente actual + anterior) / 2)",
     lambda b, y: _ratio(b["ingresos"][y], _avg(b["activo_no_corriente"][y], b["activo_no_corriente"][y - 1]))),
    (17, "Actividad y eficiencia", "Rotacion de cuentas por cobrar",
     "Ingresos / ((Cuentas por cobrar actual + anterior) / 2)",
     lambda b, y: _ratio(b["ingresos"][y], _avg(b["b_cuentas_por_cobrar"][y], b["b_cuentas_por_cobrar"][y - 1]))),
    (18, "Actividad y eficiencia", "Periodo medio de cobro", "365 / Rotacion de cuentas por cobrar",
     lambda b, y: _ratio(365, _ratio(b["ingresos"][y], _avg(b["b_cuentas_por_cobrar"][y], b["b_cuentas_por_cobrar"][y - 1])))),
    (19, "Actividad y eficiencia", "Rotacion de inventarios",
     "Costo de ventas / ((Inventarios actual + anterior) / 2)", lambda b, y: None),
    (20, "Actividad y eficiencia", "Dias de inventario", "365 / Rotacion de inventarios", lambda b, y: None),
    (21, "Actividad y eficiencia", "Rotacion de cuentas por pagar",
     "Compras a credito / ((Cuentas por pagar actual + anterior) / 2)", lambda b, y: None),
    (22, "Actividad y eficiencia", "Periodo medio de pago", "365 / Rotacion de cuentas por pagar", lambda b, y: None),
    (23, "Actividad y eficiencia", "Rotacion del capital de trabajo",
     "Ingresos / ((CT actual + CT anterior) / 2)",
     lambda b, y: _ratio(b["ingresos"][y], _avg(_ct(b, y), _ct(b, y - 1)))),
    (24, "Actividad y eficiencia", "EBITDA",
     "Resultado operativo antes de intereses e impuestos + Depreciacion + Amortizacion",
     lambda b, y: _ebitda(b, y)),
    (25, "Rentabilidad", "Resultado operativo antes de intereses e impuestos (EBIT)",
     "Ingresos - Costo de ventas - Gastos Generales - Otros gastos operacionales + Otros ingresos operacionales",
     lambda b, y: _ebit(b, y)),
    (26, "Rentabilidad", "Margen bruto", "Utilidad bruta / Ingresos",
     lambda b, y: _ratio(b["utilidad_bruta"][y], b["ingresos"][y])),
    (27, "Rentabilidad", "Margen operativo", "EBIT / Ingresos",
     lambda b, y: _ratio(_ebit(b, y), b["ingresos"][y])),
    (28, "Rentabilidad", "Margen EBITDA", "EBITDA / Ingresos",
     lambda b, y: _ratio(_ebitda(b, y), b["ingresos"][y])),
    (29, "Rentabilidad", "Margen antes de impuestos", "Utilidad antes de impuestos / Ingresos",
     lambda b, y: _ratio(b["i_resultado_antes_impuestos"][y], b["ingresos"][y])),
    (30, "Rentabilidad", "Margen neto", "Utilidad neta / Ingresos",
     lambda b, y: _ratio(b["i_resultado_del_ejercicio"][y], b["ingresos"][y])),
    (31, "Rentabilidad", "ROA",
     "Utilidad neta / ((Activo total actual + anterior) / 2)",
     lambda b, y: _ratio(b["i_resultado_del_ejercicio"][y], _avg(b["b_activo_total"][y], b["b_activo_total"][y - 1]))),
    (32, "Rentabilidad", "ROE",
     "Utilidad neta / ((Patrimonio actual + anterior) / 2)",
     lambda b, y: _ratio(b["i_resultado_del_ejercicio"][y], _avg(b["b_patrimonio_total"][y], b["b_patrimonio_total"][y - 1]))),
    (33, "Rentabilidad", "Capital invertido", "Capital Suscrito y Pagado + Obligaciones Financieras",
     lambda b, y: _sum(b["b_capital_suscrito"][y], b["obligaciones_financieras"][y])),
    (34, "Rentabilidad", "ROIC",
     "Utilidad operativa despues de impuestos / ((Capital invertido actual + anterior) / 2)",
     lambda b, y: _ratio(_ebit_op_total(b, y), _avg(_ci(b, y), _ci(b, y - 1)))),
    (35, "Rentabilidad", "Rendimiento sobre capital total",
     "UODI / ((Capital empleado actual + anterior) / 2)",
     lambda b, y: _ratio(_ebit_op_total(b, y), _avg(_capital_empleado(b, y), _capital_empleado(b, y - 1)))),
    (36, "Capital de trabajo y ciclo", "Ciclo operativo", "Dias de inventario + Dias de cartera", lambda b, y: None),
    (37, "Capital de trabajo y ciclo", "Ciclo de conversion de efectivo",
     "Dias de inventario + Dias de cartera - Dias de proveedores", lambda b, y: None),
    (38, "Capital de trabajo y ciclo", "Necesidad de capital de trabajo",
     "Activo corriente operativo - Pasivo corriente operativo",
     lambda b, y: _ct_operativo(b, y)),
    (39, "Capital de trabajo y ciclo", "Capital de trabajo / Ingresos Operacionales",
     "Capital de trabajo / Ingresos",
     lambda b, y: _ratio(_ct(b, y), b["ingresos"][y])),
    (40, "Cobertura y capacidad de pago", "Cobertura de intereses",
     "EBIT / Gastos financieros",
     lambda b, y: _ratio(_ebit(b, y), b["gastos_financieros"][y])),
    (41, "Cobertura y capacidad de pago", "Cobertura de intereses EBITDA",
     "EBITDA / Gastos financieros",
     lambda b, y: _ratio(_ebitda(b, y), b["gastos_financieros"][y])),
    (42, "Cobertura y capacidad de pago", "Variacion de cuentas por cobrar",
     "CxC actual / CxC anterior",
     lambda b, y: _var_ratio(b["b_cuentas_por_cobrar"], y)),
    (43, "Cobertura y capacidad de pago", "Variacion inventarios", "Inventarios actual / anterior", lambda b, y: None),
    (44, "Cobertura y capacidad de pago", "Variacion de cuentas por pagar",
     "CxP actual / CxP anterior",
     lambda b, y: _var_ratio(b["b_cuentas_por_pagar"], y)),
    (45, "Cobertura y capacidad de pago", "Variacion de otros activos corrientes operativos",
     "Otros activos corrientes operativos actual / anterior",
     lambda b, y: _var_ratio(b["b_otros_activos_no_financieros"], y)),
    (46, "Cobertura y capacidad de pago", "Variacion de otros pasivos corrientes operativos",
     "Otros pasivos corrientes operativos actual / anterior",
     lambda b, y: _var_ratio(b["b_otros_pasivos_no_financieros"], y)),
    (47, "Cobertura y capacidad de pago", "Variacion Propiedades, planta y equipo",
     "PyE actual / PyE anterior",
     lambda b, y: _var_ratio(b["b_propiedades_planta_equipo"], y)),
    (48, "Cobertura y capacidad de pago", "Variacion Activos intangibles",
     "Intangibles actual / anterior",
     lambda b, y: _var_ratio(b["b_activos_intangibles"], y)),
    (49, "Cobertura y capacidad de pago", "Variacion Otros activos no corrientes operativos",
     "Otros activos no corrientes operativos actual / anterior",
     lambda b, y: _var_ratio(b["otros_anc_operativos"], y)),
    (50, "Cobertura y capacidad de pago", "Flujo de caja operativo",
     "EBITDA - Impuesto de renta + Variacion capital de trabajo",
     lambda b, y: _fco(b, y)),
    (51, "Cobertura y capacidad de pago", "Flujo de caja disponible para deuda",
     "FCO - Variacion PyE - Variacion intangibles - Variacion Otros activos NC operativos",
     lambda b, y: _fc_disponible(b, y)),
    (52, "Cobertura y capacidad de pago", "Servicio de la deuda",
     "Gastos financieros + Amortizacion de deuda",
     lambda b, y: _sum(b["gastos_financieros"][y], b["amortizacion_deuda"][y])),
    (53, "Cobertura y capacidad de pago", "Indice de Cobertura del Servicio de la Deuda",
     "Flujo de caja disponible para deuda / Servicio total de la deuda",
     lambda b, y: _ratio(_fc_disponible(b, y), _sum(b["gastos_financieros"][y], b["amortizacion_deuda"][y]))),
    (54, "Cobertura y capacidad de pago", "Deuda financiera",
     "Obligaciones financieras corrientes + Obligaciones no corrientes",
     lambda b, y: b["deuda_financiera"][y]),
    (55, "Cobertura y capacidad de pago", "Deuda financiera / EBITDA",
     "Obligaciones Financieras / EBITDA",
     lambda b, y: _ratio(b["deuda_financiera"][y], _ebitda(b, y))),
    (56, "Cobertura y capacidad de pago", "Deuda financiera neta / EBITDA",
     "(Deuda financiera - Efectivo) / EBITDA",
     lambda b, y: _ratio(_sum(b["deuda_financiera"][y], _neg(b["efectivo"][y])), _ebitda(b, y))),
    (57, "Crecimiento", "Crecimiento de ingresos", "(Ingresos actual / Ingresos anterior) - 1",
     lambda b, y: _crec(b["ingresos"], y)),
    (58, "Crecimiento", "Crecimiento del EBITDA", "(EBITDA actual / EBITDA anterior) - 1",
     lambda b, y: _crec(_serie(b, _ebitda), y)),
    (59, "Crecimiento", "Crecimiento del resultado operativo", "(RO actual / RO anterior) - 1",
     lambda b, y: _crec(_serie(b, _ebit), y)),
    (60, "Crecimiento", "Crecimiento de utilidad neta", "(Utilidad neta actual / anterior) - 1",
     lambda b, y: _crec(b["i_resultado_del_ejercicio"], y)),
    (61, "Crecimiento", "Crecimiento de activos", "(Activo total actual / anterior) - 1",
     lambda b, y: _crec(b["b_activo_total"], y)),
    (62, "Calidad de resultados", "Calidad de resultados",
     "Flujo de efectivo de actividades operativas / Utilidad neta",
     lambda b, y: _ratio(b["c_flujo_operacion"][y], b["i_resultado_del_ejercicio"][y])),
    (63, "Calidad de resultados", "Rotacion de activos", "Ingresos operacionales / Activos totales",
     lambda b, y: _ratio(b["ingresos"][y], b["b_activo_total"][y])),
    (64, "Calidad de resultados", "Multiplicador de capital",
     "((Activo actual + Activo anterior)/2) / ((Patrimonio actual + Patrimonio anterior)/2)",
     lambda b, y: _ratio(_avg(b["b_activo_total"][y], b["b_activo_total"][y - 1]),
                          _avg(b["b_patrimonio_total"][y], b["b_patrimonio_total"][y - 1]))),
    (65, "Creacion de valor y DuPont", "ROE DuPont",
     "Margen neto x Rotacion de activos x Multiplicador de capital",
     lambda b, y: _roedupont(b, y)),
]


def _ebit_op_total(base, y):
    # UODI = resultado operacional ajustado por impuesto efectivo (proxy del EBIT compatible).
    # Metadato del indicador (id 34 ROIC / id 35 Rondamiento sobre capital total):
    #   - Tasa EFECTIVA = impuesto corriente / EBIT (desempeno operativo real, fuente estados).
    #   - Tasa ESTATUTARIA Art. 240 E.T. se mantiene como parametro de comparacion (ver 03_INDICADORES.md).
    ebit = _ebit(base, y)
    if ebit is None:
        return None
    tasa_efectiva = _ratio(base["i_gasto_impuesto_corriente"][y] or 0, _sum(ebit, 0))
    return _sum(ebit, -(ebit * (tasa_efectiva or 0)))


def _ci(base, y):
    return _sum(base["b_capital_suscrito"][y], base["obligaciones_financieras"][y])


def _capital_empleado(base, y):
    return _sum(base["obligaciones_financieras"][y], base["b_patrimonio_total"][y])


def _fco(base, y):
    dct = None
    if y - 1 in YEARS and _ct_operativo(base, y) is not None and _ct_operativo(base, y - 1) is not None:
        dct = _ct_operativo(base, y) - _ct_operativo(base, y - 1)
    return _sum(_ebitda(base, y), -(base["i_gasto_impuesto_corriente"][y] or 0), dct)


def _fc_disponible(base, y):
    fco = _fco(base, y)
    if fco is None:
        return None
    v = fco
    for ser in ["b_propiedades_planta_equipo", "b_activos_intangibles", "otros_anc_operativos"]:
        d = _var_abs(base[ser], y)
        if d is None:
            return None
        v = v - d
    return v


def _serie(base, fn):
    return {y: fn(base, y) for y in YEARS}


def _crec(serie, y):
    if y - 1 not in YEARS:
        return None
    return _ratio(serie[y], serie[y - 1]) - 1 if serie[y - 1] not in (None, 0) else None


def _roedupont(base, y):
    mn = _ratio(base["i_resultado_del_ejercicio"][y], base["ingresos"][y])
    rot = _ratio(base["ingresos"][y], base["b_activo_total"][y])
    mult = _ratio(_avg(base["b_activo_total"][y], base["b_activo_total"][y - 1]),
                  _avg(base["b_patrimonio_total"][y], base["b_patrimonio_total"][y - 1]))
    if mn is None or rot is None or mult is None:
        return None
    return mn * rot * mult


def calcular(csv_path=None):
    base = cargar_base(csv_path)
    motivos = {
        y: {19: NA_MOTIVOS["inventarios"], 20: NA_MOTIVOS["inventarios"],
            21: NA_MOTIVOS["compras_credito"], 22: NA_MOTIVOS["compras_credito"],
            36: NA_MOTIVOS["inventarios"], 37: NA_MOTIVOS["inventarios"],
            43: NA_MOTIVOS["inventarios"]}
        for y in YEARS
    }
    filas = []
    for idx, clasi, nombre, formula, fn in INDICADORES:
        row = {"#": idx, "clasificacion": clasi, "indicador": nombre, "formula": formula}
        for y in YEARS:
            v = fn(base, y)
            row[str(y)] = v
        filas.append(row)
    df = pd.DataFrame.from_records(filas).set_index("#")
    return df, base


def guardar(df, out_dir=None):
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "salidas")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "indicadores.csv")
    df.to_csv(path, index_label="#")
    return path


def main():
    df, _ = calcular()
    path = guardar(df)
    print(df.to_string(float_format=lambda x: "%.4f" % x))
    print("\nguardado en", path)


if __name__ == "__main__":
    main()