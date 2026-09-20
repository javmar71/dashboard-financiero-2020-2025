import re
import unicodedata

from lectura_pdfs import EstadoIDs


BALANCE_ORDER = [
    ("b_efectivo", {"includes": ["efectivo"], "excludes": ["inicio de periodo", "31 de diciembre"]}),
    ("b_inversiones", {"includes": ["inversiones"]}),
    ("b_cuentas_por_cobrar", {"includes": ["cuentas comerciales por cobrar y otras cuentas por cobrar", "cuentas por cobrar y otras cuentas por cobrar"], "excludes": ["deterioro"]}),
    ("b_impuesto_corriente_activo", {"includes": ["activo por impuesto a las ganancias corrientes"], "excludes": ["diferido"]}),
    ("b_impuesto_diferido_activo", {"includes": ["activo por impuesto diferido"], "excludes": ["corrientes"]}),
    ("b_otros_activos_no_financieros", {"includes": ["otros activos no financieros"]}),
    ("b_propiedades_planta_equipo", {"includes": ["propiedades y equipo", "propiedad planta y equipo"], "excludes": ["baja"]}),
    ("b_derecho_uso_activo", {"includes": ["derecho en uso activo", "derecho de uso activo"]}),
    ("b_activos_intangibles", {"includes": ["activos intangibles"], "excludes": ["baja"]}),
    ("b_activo_total", {"includes": ["total de activos", "total activos"], "excludes": ["baja"]}),
    ("b_cuentas_por_pagar", {"includes": ["cuentas comerciales por pagar y otras cuentas por pagar", "cuentas por pagar"], "excludes": ["derecho"]}),
    ("b_derecho_uso_pasivo", {"includes": ["derecho en uso pasivo", "derecho de uso pasivo"]}),
    ("b_beneficios_empleados", {"includes": ["pasivo por beneficios a los empleados", "beneficios a los empleados"]}),
    ("b_provisiones", {"includes": ["procesos judiciales", "provisiones"], "excludes": ["reintegro", "pasivos por provisiones", "or provisiones", "otras provisiones"]}),
    ("b_impuesto_corriente_pasivo", {"includes": ["pasivo por impuesto a las ganancias corrientes"]}),
    ("b_impuesto_diferido_pasivo", {"includes": ["pasivo por impuesto diferido"], "excludes": ["corrientes", "otros pasivos"]}),
    ("b_otros_pasivos_no_financieros", {"includes": ["otros pasivos no financieros"]}),
    ("b_pasivo_total", {"includes": ["total de pasivos"], "excludes": ["y patrimonio"]}),
    ("b_capital_suscrito", {"includes": ["capital suscrito y pagado", "capital suscrito"]}),
    ("b_prima_colocacion", {"includes": ["prima en colocacion de acciones", "prima en colocacion"]}),
    ("b_reservas", {"includes": ["reservas"]}),
    ("b_utilidad_periodo", {"includes": ["utilidad del periodo"]}),
    ("b_utilidad_ejercicios_anteriores", {"includes": ["utilidad de ejercicios anteriores"]}),
    ("b_efecto_ncif", {"includes": ["normas de contabilidad y de informacion financiera", "ncif", "efecto aplicacion"], "excludes": ["total", "utilidad"]}),
    ("b_ori_valorizacion", {"includes": ["resultado por valorizacion", "ganancias o perdidas no realizadas"]}),
    ("b_patrimonio_total", {"includes": ["total patrimonio"], "excludes": ["pasivos"]}),
    ("b_total_pasivo_patrimonio", {"includes": ["total de pasivos y patrimonio", "total pasivos patrimonio"]}),
]

INCOME_ORDER = [
    ("i_comisiones", {"includes": ["comisiones y honorarios"]}),
    ("i_ingresos_operaciones_conjuntas", {"includes": ["ingresos de actividades en operaciones conjuntas"]}),
    ("i_utilidad_bruta", {"includes": ["resultado antes de gastos de operacion"]}),
    ("i_gasto_beneficios", {"includes": ["beneficios a empleados"]}),
    ("i_gastos_administracion", {"includes": ["gastos de administracion"]}),
    ("i_gastos_operaciones_conjuntas", {"includes": ["gastos de actividades en operaciones conjuntas"]}),
    ("i_deterioro_cxc", {"includes": ["deterioro cuentas por cobrar"]}),
    ("i_depreciaciones", {"includes": ["depreciaciones", "depreciacion"], "excludes": ["derechos de uso", "baja"]}),
    ("i_amortizaciones", {"includes": ["amortizaciones", "amortizacion"], "excludes": ["baja"]}),
    ("i_resultado_despues_gastos", {"includes": ["resultado despues de gastos"]}),
    ("i_resultado_financiero_neto", {"includes": ["resultado financiero neto", "resultado financiero"]}),
    ("i_resultado_operacional", {"includes": ["resultado operacional"]}),
    ("i_otros_ingresos_egresos", {"includes": ["otros ingresos egresos", "otros ingresos (egresos)", "otros ingresos"]}),
    ("i_resultado_antes_impuestos", {"includes": ["resultado antes de impuestos"]}),
    ("i_gasto_impuesto_corriente", {"includes": ["gasto por impuestos a las ganancias"]}),
    ("i_gasto_impuesto_diferido", {"includes": ["gasto ingreso por impuesto diferido", "gasto por impuesto diferido"], "excludes": ["corrientes"]}),
    ("i_resultado_del_ejercicio", {"includes": ["resultado del ejercicio", "utilidad del periodo"], "excludes": ["total"]}),
    ("i_ori_titulos", {"includes": ["resultado por valorizacion de titulos", "resultado por valorizacion titulos participativos", "titulos participativos"], "excludes": ["actuarial"]}),
    ("i_ori_actuarial", {"includes": ["resultado por valorizacion actuarial de pensionados", "actuarial de pensionados"]}),
    ("i_ori_inmuebles", {"includes": ["resultado por valorizacion de bienes inmuebles", "valorizacion de bienes inmuebles", "bienes inmubles"]}),
    ("i_impuesto_diferido_ori", {"includes": ["impuesto diferido"], "excludes": ["gasto", "ingreso"]}),
    ("i_ori_total", {"includes": ["total otro resultado integral"]}),
    ("i_comprehensivo_total", {"includes": ["total utilidad del ejercicio y otro resultado integral", "total utilidad y otro resultado integral"]}),
]

CFLOW_ORDER = [
    ("c_utilidad_del_ejercicio", {"includes": ["utilidad del periodo", "utilidad del ejercicio"], "excludes": ["total"]}),
    ("c_depreciacion", {"includes": ["depreciacion"], "excludes": ["derechos de uso", "baja"]}),
    ("c_depreciacion_derecho_uso", {"includes": ["depreciacion derechos de uso", "depreciacion de derechos de uso", "depreciacionder"]}),
    ("c_provisiones", {"includes": ["provisiones multas y litigios", "provisiones"], "excludes": ["reintegro", "pasivos por provisiones"]}),
    ("c_deterioro_cxc", {"includes": ["deterioro cuentas por cobrar", "deterioro de cuentas por cobrar", "comision fiduciaria y otras cuentas por cobrar"]}),
    ("c_reintegro_provisiones", {"includes": ["reintegro de otras provisiones", "reintegro"]}),
    ("c_valoracion_inversiones", {"includes": ["valoracion de inversiones", "valoracion de inversiones y"]}),
    ("c_amortizacion_intangibles", {"includes": ["amortizacion de intangibles", "amortizacion de activos intangibles"], "excludes": ["baja"]}),
    ("c_amortizacion_otros", {"includes": ["amortizacion de otros activos no financieros", "amortizacion de otros"]}),
    ("c_intereses_arrendamiento", {"includes": ["gastos por intereses sobre pasivos por arrendamiento", "intereses sobre pasivos por arrendamiento"]}),
    ("c_gasto_impuesto_corriente", {"includes": ["gasto por impuestos a las ganancias"], "excludes": ["diferido"]}),
    ("c_gasto_impuesto_diferido", {"includes": ["gasto ingreso por impuesto diferido", "gasto por impuesto diferido", "impuesto diferido"], "excludes": ["corriente", "impuestos pagados", "total"]}),
    ("c_baja_ppye", {"includes": ["baja en propiedades y equipo", "baja propiedades y equipo", "baja sistemas"], "excludes": ["depreciacion"]}),
    ("c_baja_depreciacion_ppye", {"includes": ["baja depreciacion en propiedades y equipo", "baja depreciacion en propiedades"]}),
    ("c_baja_intangibles", {"includes": ["baja en activos intangibles"], "excludes": ["amortizacion"]}),
    ("c_baja_amortizacion_intangibles", {"includes": ["baja amortizacion en activos intangibles", "baja amortizacion"]}),
    ("c_cuentas_por_cobrar", {"includes": ["cuentas por cobrar"], "excludes": ["deterioro", "reintegro", "otras"]}),
    ("c_otros_activos", {"includes": ["otros activos"], "excludes": ["no financieros", "intangibles", "deterioro"]}),
    ("c_cuentas_por_pagar", {"includes": ["cuentas por pagar"]}),
    ("c_impuestos_neto", {"includes": ["impuestos neto", "impuestos netos"]}),
    ("c_beneficios_empleados", {"includes": ["pasivo por beneficios a los empleados", "beneficios a los empleados", "pasivo por beneficios a empleados", "beneficios a empleados"]}),
    ("c_pasivos_provisiones", {"includes": ["pasivos por provisiones", "pasivos por provisiones"], "excludes": ["reintegro"]}),
    ("c_intereses_pagados", {"includes": ["intereses pagados"]}),
    ("c_impuestos_pagados", {"includes": ["impuestos pagados"]}),
    ("c_flujo_operacion", {"includes": ["flujo neto de efectivo", "flujo neto"], "excludes": ["inversion", "financiacion", "impuestos", "dividendos"]}),
    ("c_inversiones", {"includes": ["inversiones"], "excludes": ["valoracion", "amortizacion"]}),
    ("c_adquisicion_ppye", {"includes": ["adquisicion propiedades y equipo", "adquisicion de propiedades y equipo"]}),
    ("c_adquisicion_intangibles", {"includes": ["adquisicion de activos intangibles", "adquisicion de intangibles"]}),
    ("c_flujo_inversion", {"includes": ["flujo neto", "flujo de efectivo"], "excludes": ["operacion", "financiacion", "impuestos", "dividendos"]}),
    ("c_pagos_arrendamiento", {"includes": ["pagos parte principal del pasivo por arrendamiento", "pasivo por arrendamiento"]}),
    ("c_dividendos", {"includes": ["dividendos"]}),
    ("c_flujo_financiacion", {"includes": ["flujo neto", "flujo de efectivo"], "excludes": ["operacion", "inversion", "impuestos", "dividendos"]}),
    ("c_aumento_neto", {"includes": ["aumento neto de efectivo", "aumento (disminucion) neto de efectivo", "aumento neto", "disminucion neto de efectivo"]}),
    ("c_efectivo_restriccion", {"includes": ["efectivo restringido"], "excludes": ["sin restriccion", "total"]}),
    ("c_efectivo_sin_restriccion", {"includes": ["efectivo sin restriccion"]}),
    ("c_efectivo_inicio", {"includes": ["total efectivo al inicio de periodo", "efectivo al inicio de periodo", "efectivo al inicio"]}),
    ("c_efectivo_cierre", {"includes": ["efectivo al 31 de diciembre", "al 31 de diciembre"], "excludes": ["inicio"]}),
]

ORDER = {
    EstadoIDs.BALANCE: BALANCE_ORDER,
    EstadoIDs.INCOME: INCOME_ORDER,
    EstadoIDs.CASHFLOW: CFLOW_ORDER,
}


def normalize_text(text):
    s = text.lower().strip()
    toks = s.split()
    while toks and re.fullmatch(r"\d+(\.\d+)?", toks[-1]):
        toks.pop()
    s = " ".join(toks)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def best_phrase_len(norm_label, spec):
    best = 0
    for inc in spec.get("includes", []):
        if inc in norm_label:
            best = max(best, len(inc))
    return best


def matches_spec(norm_label, spec):
    if spec.get("excludes"):
        if any(x in norm_label for x in spec["excludes"]):
            return False
    return best_phrase_len(norm_label, spec) > 0


def map_statement(rows, statement_id):
    order = ORDER[statement_id]
    out = {}
    for key, spec in order:
        candidates = []
        for r in rows:
            norm = normalize_text(r["label"])
            if matches_spec(norm, spec):
                candidates.append((best_phrase_len(norm, spec), r))
        if not candidates:
            continue
        candidates.sort(key=lambda c: (-c[0], c[1]["y"]))
        best = candidates[0][1]
        out[key] = {
            "cur": best["cur"],
            "prev": best["prev"],
            "y": best["y"],
            "label": best["label"],
            "norm": normalize_text(best["label"]),
            "matched": len(candidates),
        }
    return out


def classify_all(pages):
    result = {}
    for st in (EstadoIDs.BALANCE, EstadoIDs.INCOME, EstadoIDs.CASHFLOW):
        flat = []
        for _pno, rows in pages.get(st, []):
            flat.extend(rows)
        flat.sort(key=lambda r: r["y"])
        result[st] = map_statement(flat, st)
    return result


def coverage_report(mapped):
    lines = []
    for st in (EstadoIDs.BALANCE, EstadoIDs.INCOME, EstadoIDs.CASHFLOW):
        m = mapped.get(st, {})
        n_keys = len(ORDER[st])
        lines.append("%s: %d/%d claves mapeadas" % (st, len(m), n_keys))
        missing = [k for k, _ in ORDER[st] if k not in m]
        if missing:
            lines.append("   faltan: %s" % ", ".join(missing))
    return "\n".join(lines)


CORRIENTE_RULES = {
    "activo_corriente": [
        "b_efectivo",
        "b_inversiones",
        "b_cuentas_por_cobrar",
        "b_impuesto_corriente_activo",
        "b_otros_activos_no_financieros",
    ],
    "activo_no_corriente": [
        "b_impuesto_diferido_activo",
        "b_propiedades_planta_equipo",
        "b_derecho_uso_activo",
        "b_activos_intangibles",
    ],
    "pasivo_corriente": [
        "b_cuentas_por_pagar",
        "b_beneficios_empleados",
        "b_impuesto_corriente_pasivo",
        "b_otros_pasivos_no_financieros",
    ],
    "pasivo_no_corriente": [
        "b_provisiones",
        "b_impuesto_diferido_pasivo",
        "b_derecho_uso_pasivo",
    ],
}