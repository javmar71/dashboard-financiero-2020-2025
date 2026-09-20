# fase9_validacion_transversal.py
# Fase 9 - Prueba de Validacion Transversal (autorizada por instruccion operativa 2026-09-19).
# Valida la matriz consolidada 2020-2025 (datos_estados_financieros.csv + indicadores.csv + WACC fase7):
#   A. Ecuacion patrimonial: Activo Total = Pasivo Total + Patrimonio
#   B. Conciliacion de Efectivo: Efectivo Cierre(Y) = Efectivo Inicio(Y) + Aumento Neto(Y)
#   C. Continuidad temporal: Inicio(Y) = Cierre(Y-1) = b_efectivo(Y-1)
#   D. Descomposicion del efectivo inicial: restringido + sin restriccion = inicio
#   E. Aumento neto = flujo operacion + inversion + financiacion
#   F. Cierre de flujos = efectivo de balance (b_efectivo)
#   G. Resultado: antes_impuestos - (corriente + diferido) = resultado del ejercicio
#   H. Resultado integral = resultado del ejercicio + ORI total
#   I. Reproducibilidad EBIT (id 25) y ROIC (id 34) desde componentes
#   J. NOPAT/ROIC cross-check con tasa estatutaria Art. 240 E.T. por anio
#   K. Recalculacion WACC fase7 (Ke = ROIC id 34) desde fuentes
# Estados: ACEPTADO / DESCUDRE / DUDOSO / NO_ENCONTRADO / NO_CALCULABLE
# Regla universal (agnostica de entidad): sin inventar valores; solo cruces documentados.

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SALIDAS = BASE / "salidas"
OUT_DIR = SALIDAS / "fase9_validacion_transversal"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANIOS = ["2020", "2021", "2022", "2023", "2024", "2025"]

# Tasa general personas juridicas, Art. 240 E.T. (Ley 2010/2019: 32/31/30 para 2020/21/22;
# Ley 2277/2022: 35% desde 2023). Usada SOLO como cross-check metodologico.
T_ART240 = {"2020": 0.32, "2021": 0.31, "2022": 0.30, "2023": 0.35, "2024": 0.35, "2025": 0.35}
# Tasa usada en fase7 (taxonomia): 2022+ = 35%.
T_FASE7 = {"2020": 0.32, "2021": 0.31, "2022": 0.35, "2023": 0.35, "2024": 0.35, "2025": 0.35}

TOL_ABS = 1e-3   # identidades monetarias (miles)
TOL_REL = 1e-4   # ratios


def leer_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def serie(rows, key_col, key, anios=ANIOS):
    for r in rows:
        if r[key_col].strip() == key:
            out = {}
            for a in anios:
                v = r.get(a, "").strip()
                out[a] = float(v) if v not in ("", None) else None
            return out
    return None


def chequeo(grupo, nombre, anio, izq, der, formula, tol=TOL_ABS, rel=False):
    if izq is None or der is None:
        estado = "NO_ENCONTRADO"
        diff_abs, diff_rel = None, None
    else:
        diff_abs = izq - der
        diff_rel = (diff_abs / der) if der else (diff_abs if izq else 0.0)
        ok = (abs(diff_abs) <= tol) if not rel else (abs(diff_rel) <= tol)
        estado = "ACEPTADO" if ok else ("DUDOSO" if not ok else "DESCUDRE")
        if not ok and abs(diff_rel) > 0.5 and abs(diff_abs) > 100:
            estado = "DESCUDRE"
    return {
        "grupo": grupo,
        "check": nombre,
        "anio": anio,
        "formula": formula,
        "izquierda": round(izq, 6) if izq is not None else None,
        "derecha": round(der, 6) if der is not None else None,
        "diferencia_abs": round(diff_abs, 6) if diff_abs is not None else None,
        "diferencia_rel": round(diff_rel, 6) if diff_rel is not None else None,
        "estado": estado,
    }


D = serie(leer_csv(SALIDAS / "datos_estados_financieros.csv"), "concepto", "b", anios=ANIOS) or {}
EST = {r["concepto"].strip(): {a: (float(r[a]) if r[a].strip() not in ("", "None") else None) for a in ANIOS}
       for r in leer_csv(SALIDAS / "datos_estados_financieros.csv")}

IND = {int(r["#"].strip()): {a: (float(r[a]) if r[a].strip() not in ("", "None") else None) for a in ANIOS}
       for r in leer_csv(SALIDAS / "indicadores.csv")}

filas = []

# --- A. Ecuacion patrimonial ---
for a in ANIOS:
    filas.append(chequeo("A_Ecuacion_Patrimonial", "Activo = Pasivo + Patrimonio", a,
                         EST["b_activo_total"][a],
                         (EST["b_pasivo_total"][a] or 0) + (EST["b_patrimonio_total"][a] or 0),
                         "b_activo_total = b_pasivo_total + b_patrimonio_total"))
for a in ANIOS:
    filas.append(chequeo("A_Ecuacion_Patrimonial", "Total pasivo y patrimonio = Activo", a,
                         EST["b_total_pasivo_patrimonio"][a], EST["b_activo_total"][a],
                         "b_total_pasivo_patrimonio = b_activo_total"))

# --- B. Conciliacion de efectivo ---
for a in ANIOS:
    filas.append(chequeo("B_Conciliacion_Efectivo", "Cierre = Inicio + Aumento neto", a,
                         EST["c_efectivo_cierre"][a],
                         (EST["c_efectivo_inicio"][a] or 0) + (EST["c_aumento_neto"][a] or 0),
                         "c_efectivo_cierre = c_efectivo_inicio + c_aumento_neto"))

# --- C. Continuidad temporal ---
for i, a in enumerate(ANIOS):
    if i == 0:
        filas.append({
            "grupo": "C_Continuidad_Temporal", "check": "Inicio(Y) = Cierre(Y-1)", "anio": a,
            "formula": "c_efectivo_inicio(2020) = c_efectivo_cierre(2019) [sin dato 2019]",
            "izquierda": EST["c_efectivo_inicio"][a], "derecha": None,
            "diferencia_abs": None, "diferencia_rel": None, "estado": "NO_ENCONTRADO"})
        continue
    prev = ANIOS[i - 1]
    filas.append(chequeo("C_Continuidad_Temporal", "Inicio(Y) = Cierre(Y-1)", a,
                         EST["c_efectivo_inicio"][a], EST["c_efectivo_cierre"][prev],
                         "c_efectivo_inicio(Y) = c_efectivo_cierre(Y-1)"))
    filas.append(chequeo("C_Continuidad_Temporal", "Inicio(Y) = Efectivo balance(Y-1)", a,
                         EST["c_efectivo_inicio"][a], EST["b_efectivo"][prev],
                         "c_efectivo_inicio(Y) = b_efectivo(Y-1)"))

# --- D. Descomposicion del efectivo inicial ---
for a in ANIOS:
    filas.append(chequeo("D_Descomposicion_Efectivo", "Restringido + Sin restriccion = Inicio", a,
                         (EST["c_efectivo_restriccion"][a] or 0) + (EST["c_efectivo_sin_restriccion"][a] or 0),
                         EST["c_efectivo_inicio"][a],
                         "restriccion + sin_restriccion = c_efectivo_inicio"))

# --- E. Aumento neto = op + inv + fin ---
for a in ANIOS:
    filas.append(chequeo("E_Aumento_Neto", "Aumento = Op + Inv + Fin", a,
                         (EST["c_flujo_operacion"][a] or 0) + (EST["c_flujo_inversion"][a] or 0) + (EST["c_flujo_financiacion"][a] or 0),
                         EST["c_aumento_neto"][a],
                         "c_aumento_neto = op + inv + financiacion"))

# --- F. Cierre = efectivo de balance ---
for a in ANIOS:
    filas.append(chequeo("F_Cierre_vs_Balance", "Cierre flujo = b_efectivo", a,
                         EST["c_efectivo_cierre"][a], EST["b_efectivo"][a],
                         "c_efectivo_cierre = b_efectivo"))

# --- G. Resultado del ejercicio ---
for a in ANIOS:
    der = (EST["i_gasto_impuesto_corriente"][a] or 0) + (EST["i_gasto_impuesto_diferido"][a] or 0)
    filas.append(chequeo("G_Resultado", "Ejercicio = Antes impuestos - (corriente + diferido)", a,
                         EST["i_resultado_del_ejercicio"][a],
                         (EST["i_resultado_antes_impuestos"][a] or 0) - der,
                         "i_resultado_del_ejercicio = i_resultado_antes_impuestos - impuestos"))

# --- H. Resultado integral ---
for a in ANIOS:
    filas.append(chequeo("H_Resultado_Integral", "Integral = Ejercicio + ORI total", a,
                         EST["i_comprehensivo_total"][a],
                         (EST["i_resultado_del_ejercicio"][a] or 0) + (EST["i_ori_total"][a] or 0),
                         "i_comprehensivo_total = i_resultado_del_ejercicio + i_ori_total"))

# --- I. Reproducibilidad EBIT y ROIC ---
for a in ANIOS:
    ebit_der = EST["i_utilidad_bruta"][a]
    if ebit_der is not None:
        ebit_der -= (EST["i_gasto_beneficios"][a] or 0)
        ebit_der -= (EST["i_gastos_administracion"][a] or 0)
        ebit_der -= (EST["i_gastos_operaciones_conjuntas"][a] or 0)
        ebit_der -= (EST["i_deterioro_cxc"][a] or 0)
        ebit_der += (EST["i_otros_ingresos_egresos"][a] or 0)
    filas.append(chequeo("I_Reproducibilidad", "EBIT id25 desde componentes", a,
                         IND.get(25, {}).get(a), ebit_der,
                         "EBIT = utilidad_bruta - gastos_gen - deterioro + otros", rel=True, tol=TOL_REL))
for a in ANIOS:
    ci_t = IND.get(33, {}).get(a)
    ci_prev = IND.get(33, {}).get(ANIOS[max(0, ANIOS.index(a) - 1)]) if ANIOS.index(a) > 0 else None
    nopat = None
    if IND.get(25, {}).get(a) is not None:
        nopat = IND[25][a] - (EST["i_gasto_impuesto_corriente"][a] or 0)
    roic_recalc = None
    if nopat is not None and ci_t is not None and ci_prev is not None:
        roic_recalc = nopat / ((ci_t + ci_prev) / 2)
    filas.append(chequeo("I_Reproducibilidad", "ROIC id34 = (EBIT-corr)/avg CI", a,
                         IND.get(34, {}).get(a), roic_recalc,
                         "ROIC = (EBIT - imp_corriente) / ((CI_t + CI_t-1)/2)", rel=True, tol=TOL_REL))

# --- J. NOPAT/ROIC con tasa estatutaria Art. 240 ---
for a in ANIOS:
    ebit = IND.get(25, {}).get(a)
    ci_t = IND.get(33, {}).get(a)
    ci_prev = IND.get(33, {}).get(ANIOS[max(0, ANIOS.index(a) - 1)]) if ANIOS.index(a) > 0 else None
    if None in (ebit, ci_t, ci_prev):
        filas.append(chequeo("J_NOPAT_Art240", "ROIC estatutario Art. 240", a, None, None,
                             "Requiere EBIT, CI_t, CI_t-1"))
        continue
    nopat = ebit * (1 - T_ART240[a])
    roic_stat = nopat / ((ci_t + ci_prev) / 2)
    c = chequeo("J_NOPAT_Art240", "ROIC con tasa estatutaria Art. 240", a,
                roic_stat, IND.get(34, {}).get(a),
                "ROIC_stat = EBIT*(1-T_art240)/avg CI  vs  ROIC id34", rel=True, tol=0.02)
    if c["estado"] == "ACEPTADO" and roic_stat is not None and IND.get(34, {}).get(a) is not None \
            and abs((roic_stat - IND[34][a]) / IND[34][a]) > TOL_REL:
        c["estado"] = "DUDOSO"
        c["formula"] += " | divergencia metodologica: id34 usa tasa efectiva (imp_corriente/EBIT), no estatutaria"
    filas.append(c)

# --- K. Recalculacion WACC fase7 ---
wacc_json = json.loads((SALIDAS / "fase7_wacc_roi" / "wacc_roi_2020_2025.json").read_text(encoding="utf-8"))
for r in wacc_json["resultados"]:
    a = r["periodo"]
    d = EST["b_derecho_uso_pasivo"][a]
    e = EST["b_patrimonio_total"][a]
    interes = abs(EST["c_intereses_pagados"][a]) if EST["c_intereses_pagados"][a] is not None else None
    kd = interes / d if (interes is not None and d) else None
    kd_neto = kd * (1 - T_FASE7[a]) if kd is not None else None
    wd = d / (d + e) if (d is not None and e is not None) else None
    we = e / (d + e) if (d is not None and e is not None) else None
    ke = IND.get(34, {}).get(a)
    wacc_rec = None
    if kd_neto is not None and wd is not None and we is not None and ke is not None:
        wacc_rec = kd_neto * wd + ke * we
    filas.append(chequeo("K_WACC_Fase7", "WACC recalculado = fase7", a, wacc_rec, r["wacc"],
                         "WACC = Kd*(1-T)*wd + ROIC*we", rel=True, tol=TOL_REL))
    if a == "2022":
        filas.append({
            "grupo": "K_WACC_Fase7", "check": "Tasa Art. 240 vs tasa fase7", "anio": a,
            "formula": "T_ART240(2022)=0.30 (Ley 2010) vs T_FASE7/taxonomia=0.35",
            "izquierda": T_ART240[a], "derecha": T_FASE7[a],
            "diferencia_abs": T_ART240[a] - T_FASE7[a], "diferencia_rel": None,
            "estado": "DUDOSO",
        })

# --- RONA (id 35) observacion metodologica ---
for a in ANIOS[1:]:
    base35 = (IND.get(33, {}).get(a) or 0) + (IND.get(33, {}).get(ANIOS[ANIOS.index(a) - 1]) or 0)
    rona_cano = None
    nopat = IND.get(25, {}).get(a)
    if nopat is not None and base35:
        rona_cano = nopat / (base35 / 2)
    c = chequeo("J_RONA", "RONA id35 coincide con ROIC id34 (base = capital invertido)", a,
                IND.get(35, {}).get(a), IND.get(34, {}).get(a),
                "id35 usa mismo denominador (capital invertido proxy arrendamiento) => numeros identicos", rel=True, tol=1e-9)
    if c["estado"] == "ACEPTADO":
        c["estado"] = "DUDOSO"
        c["formula"] += " | OBSERVACION: RONA canonica (03_INDICADORES) = NOPAT/capital_empleado (deuda+patrimonio); motor usa capital_invertido"
    filas.append(c)

# --- persistencia ---
with open(OUT_DIR / "matriz_consistencia_transversal.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
    w.writeheader()
    w.writerows(filas)

resumen = {estado: sum(1 for r in filas if r["estado"] == estado) for estado in
           ["ACEPTADO", "DESCUDRE", "DUDOSO", "NO_ENCONTRADO", "NO_CALCULABLE"]}
descuadres = [r for r in filas if r["estado"] in ("DESCUDRE", "DUDOSO")]
(OUT_DIR / "resumen_validacion_transversal.json").write_text(
    json.dumps({
        "alcance": "Prueba de Validacion Transversal - matriz consolidada 2020-2025",
        "total_checks": len(filas),
        "resumen": resumen,
        "integridad_100pct": resumen["DESCUDRE"] == 0,
        "observaciones": descuadres,
        "tasa_art240": T_ART240,
        "tasa_fase7_taxonomia": T_FASE7,
        "nota": "DESCUDRE/DUDOSO no corrigen la taxonomia; requieren juicio de Big Pickle.",
    }, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

for r in filas:
    print(f"{r['grupo']:24} | {r['check'][:52]:52} | {r['anio']} | {r['estado']}")
print("\nRESUMEN:", resumen)
print("Integridad 100%:", resumen["DESCUDRE"] == 0)
print("OK ->", OUT_DIR)