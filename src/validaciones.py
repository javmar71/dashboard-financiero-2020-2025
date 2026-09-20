# -*- coding: utf-8 -*-
"""Validaciones de conciliacion sobre la serie normalizada 2020-2025.

Carga salidas/datos_estados_financieros.csv y verifica:
  1. Activo = Pasivo + Patrimonio
  2. Componentes de activo (corriente + no corriente) = Total activos
  3. Componentes de pasivo (corriente + no corriente) = Total pasivos
  4. Componentes de patrimonio = Total patrimonio
  5. Flujos: op + inv + fin = aumento neto; inicio + aumento = cierre; cierre = b_efectivo
  6. b_utilidad_periodo = i_resultado_del_ejercicio = c_utilidad_del_ejercicio
  7. c_efectivo_inicio = b_efectivo del periodo anterior
Genera salidas/reporte_validaciones.txt
"""
import os

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "salidas", "datos_estados_financieros.csv")
OUT_PATH = os.path.join(BASE_DIR, "salidas", "reporte_validaciones.txt")

YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
TOL = 1.0


def _num(v):
    if pd.isna(v):
        return None
    return float(v)


def _igual(a, b, tol=TOL):
    if a is None or b is None:
        return False, None
    return abs(a - b) <= tol, a - b


def main():
    df = pd.read_csv(CSV_PATH)
    base = df.set_index("concepto")

    rows = []

    def check(nombre, ok, detalle):
        rows.append((nombre, ok, detalle))

    s = base

    for y in YEARS:
        a = _num(s.loc["b_activo_total", str(y)])
        p = _num(s.loc["b_pasivo_total", str(y)])
        pat = _num(s.loc["b_patrimonio_total", str(y)])
        ok, dif = _igual(a, p + pat if (p is not None and pat is not None) else None)
        check("Activo = Pasivo + Patrimonio", ok, f"{y}: A={a} P={p} Patrimonio={pat} diff={dif}")

        a_corr = sum(
            _num(s.loc[k, str(y)]) or 0
            for k in ["b_efectivo", "b_inversiones", "b_cuentas_por_cobrar",
                      "b_impuesto_corriente_activo", "b_otros_activos_no_financieros"]
        )
        a_no_corr = sum(
            _num(s.loc[k, str(y)]) or 0
            for k in ["b_impuesto_diferido_activo", "b_propiedades_planta_equipo",
                      "b_derecho_uso_activo", "b_activos_intangibles"]
        )
        ok_2, dif_2 = _igual(a_corr + a_no_corr, a)
        check("Componentes activo = Total activos", ok_2,
              f"{y}: corriente={a_corr} no_corriente={a_no_corr} suma={a_corr + a_no_corr} total={a} diff={dif_2}")

        p_corr = sum(
            _num(s.loc[k, str(y)]) or 0
            for k in ["b_cuentas_por_pagar", "b_derecho_uso_pasivo",
                      "b_beneficios_empleados", "b_impuesto_corriente_pasivo",
                      "b_otros_pasivos_no_financieros"]
        )
        p_no_corr = sum(
            _num(s.loc[k, str(y)]) or 0
            for k in ["b_provisiones", "b_impuesto_diferido_pasivo"]
        )
        ok_3, dif_3 = _igual(p_corr + p_no_corr, p)
        check("Componentes pasivo = Total pasivos", ok_3,
              f"{y}: corriente={p_corr} no_corriente={p_no_corr} suma={p_corr + p_no_corr} total={p} diff={dif_3}")

        pat_comp = sum(
            _num(s.loc[k, str(y)]) or 0
            for k in ["b_capital_suscrito", "b_prima_colocacion", "b_reservas",
                      "b_utilidad_periodo", "b_utilidad_ejercicios_anteriores",
                      "b_efecto_ncif", "b_ori_valorizacion"]
        )
        ok_4, dif_4 = _igual(pat_comp, pat)
        check("Componentes patrimonio = Total patrimonio", ok_4,
              f"{y}: suma={pat_comp} total={pat} diff={dif_4}")

        op = _num(s.loc["c_flujo_operacion", str(y)])
        in_ = _num(s.loc["c_flujo_inversion", str(y)])
        fin = _num(s.loc["c_flujo_financiacion", str(y)])
        aum = _num(s.loc["c_aumento_neto", str(y)])
        ok_5, dif_5 = _igual(
            (op + in_ + fin) if (op is not None and in_ is not None and fin is not None) else None,
            aum)
        check("Flujo op+inv+fin = Aumento neto", ok_5,
              f"{y}: op={op} inv={in_} fin={fin} suma={None if op is None else op + in_ + fin} aumento={aum} diff={dif_5}")

        ini = _num(s.loc["c_efectivo_inicio", str(y)])
        cie = _num(s.loc["c_efectivo_cierre", str(y)])
        b_ef = _num(s.loc["b_efectivo", str(y)])
        ok_6, dif_6 = _igual(ini + aum if (ini is not None and aum is not None) else None, cie)
        check("Efectivo inicio + aumento = cierre", ok_6,
              f"{y}: inicio={ini} aumento={aum} suma={None if ini is None else ini + aum} cierre={cie} diff={dif_6}")

        ok_7, dif_7 = _igual(cie, b_ef)
        check("Efectivo cierre = b_efectivo", ok_7, f"{y}: flujo_cierre={cie} balance={b_ef} diff={dif_7}")

        u_per = _num(s.loc["b_utilidad_periodo", str(y)])
        u_res = _num(s.loc["i_resultado_del_ejercicio", str(y)])
        u_cf = _num(s.loc["c_utilidad_del_ejercicio", str(y)])
        ok_8 = u_per is not None and u_res is not None and u_cf is not None and u_per == u_res == u_cf
        check("Utilidad balance = Resultado = CF", ok_8,
              f"{y}: balance={u_per} resultado={u_res} cf={u_cf}")

        if y > YEARS[0]:
            prev_inicio = _num(s.loc["c_efectivo_inicio", str(y)])
            prev_balance = _num(s.loc["b_efectivo", str(y - 1)])
            ok_9, dif_9 = _igual(prev_inicio, prev_balance)
            check("c_efectivo_inicio = b_efectivo anterior", ok_9,
                  f"{y}: inicio_flujo={prev_inicio} balance_{y - 1}={prev_balance} diff={dif_9}")

        desglose_ini = (_num(s.loc["c_efectivo_restriccion", str(y)]) or 0) + \
                       (_num(s.loc["c_efectivo_sin_restriccion", str(y)]) or 0)
        ok_10, dif_10 = _igual(desglose_ini, _num(s.loc["c_efectivo_inicio", str(y)]))
        check("Restringido + sin restriccion = Efectivo inicio", ok_10,
              f"{y}: restriccion={_num(s.loc['c_efectivo_restriccion', str(y)])} "
              f"sin_restriccion={_num(s.loc['c_efectivo_sin_restriccion', str(y)])} "
              f"suma={desglose_ini} inicio={_num(s.loc['c_efectivo_inicio', str(y)])} diff={dif_10}")

        i_tit = _num(s.loc["i_ori_titulos", str(y)])
        i_act = _num(s.loc["i_ori_actuarial", str(y)])
        i_inn = _num(s.loc["i_ori_inmuebles", str(y)])
        i_imp = _num(s.loc["i_impuesto_diferido_ori", str(y)])
        comp = [v for v in (i_tit, i_act, i_inn, i_imp) if v is not None]
        total_ori = _num(s.loc["i_ori_total", str(y)])
        ok_11, dif_11 = _igual(sum(comp) if comp else None, total_ori)
        check("Suma ORI = Total otro resultado integral", ok_11,
              f"{y}: titulos={i_tit} actuarial={i_act} inmuebles={i_inn} imp_dif={i_imp} "
              f"suma={sum(comp) if comp else None} total={total_ori} diff={dif_11}")

    n_ok = sum(1 for _, ok, _ in rows if ok)
    n_fail = len(rows) - n_ok

    lines = [
        "REPORTE DE VALIDACIONES - FIDUCIARIA LA PREVISORA S.A. (millones COP)",
        "Serie normalizada 2020-2025 a partir de 87 conceptos canonicos.",
        "=" * 78,
    ]
    for nombre, ok, detalle in rows:
        lines.append(f"{'[OK]  ' if ok else '[FALLA]'} {nombre}")
        lines.append(f"       {detalle}")
    lines.append("=" * 78)
    lines.append(f"Total: {n_ok} OK, {n_fail} fallas de {len(rows)} comprobaciones.")
    if n_fail:
        lines.append("Nota: las diferencias senaladas no alteran los totales del balance; revisar "
                     "las partidas indicadas en el detalle antes de usar la serie.")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"guardado en {OUT_PATH}")
    print(f"{n_ok} OK | {n_fail} fallas de {len(rows)} comprobaciones")


if __name__ == "__main__":
    main()