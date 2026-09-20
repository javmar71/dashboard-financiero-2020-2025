# fase7_wacc_roi.py
# Fase 7 - WACC con Kep = ROI (ke = ROIC id 34). Sustituye CAPM (2026-09-19).
# Regla universal (agnostica de entidad): sin insumos externos manuales.
#
# Formula (instruccion ejecutiva 2026-09-19):
#   WACC = (Kd * (1 - T_estatutaria) * wd) + (Ke * we)
#   Ke   = ROIC (id 34)  -> rentabilidad operativa interna (Return on Invested Capital)
#   Kd   = |c_intereses_pagados| / deuda_financiera_total
#   wd   = deuda_financiera_total / (deuda_financiera_total + patrimonio_total)
#   we   = patrimonio_total / (deuda_financiera_total + patrimonio_total)
#
# Fuentes de verdad (no se inventan valores):
#   - salidas/indicadores.csv  (ROIC id 34)
#   - salidas/datos_estados_financieros.csv (deuda proxy pasivo derecho de uso, patrimonio, intereses pagados)
#   - T_estatutaria: tarifa general Art. 240 E.T.: 2020=32%, 2021=31%, 2022+=35% (taxonomia)

import csv
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]  # AUTOMAT ANALISIS FIN (contiene salidas)
SALIDAS = BASE / "salidas"
AGENTE = Path(__file__).resolve().parent
OUT_DIR = SALIDAS / "fase7_wacc_roi"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANIOS = ["2020", "2021", "2022", "2023", "2024", "2025"]
T_ESTATUTARIA = {"2020": 0.32, "2021": 0.31, "2022": 0.35, "2023": 0.35, "2024": 0.35, "2025": 0.35}


def leer_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def leer_valores(row, anios):
    out = {}
    for anio in anios:
        v = row.get(anio, "").strip()
        out[anio] = float(v) if v not in ("", None) else None
    return out


panorama = []
for r in leer_csv(SALIDAS / "datos_estados_financieros.csv"):
    if r["concepto"] in ("b_derecho_uso_pasivo", "b_patrimonio_total", "c_intereses_pagados"):
        panorama.append((r["concepto"], leer_valores(r, ANIOS)))

DEUDA = dict(next(v for k, v in panorama if k == "b_derecho_uso_pasivo"))
PATRIM = dict(next(v for k, v in panorama if k == "b_patrimonio_total"))
INT_PAG = dict(next(v for k, v in panorama if k == "c_intereses_pagados"))

roic = None
for r in leer_csv(SALIDAS / "indicadores.csv"):
    if r["#"].strip() == "34":
        roic = leer_valores(r, ANIOS)
        break
if roic is None:
    raise SystemExit("ROIC id 34 no encontrado en indicadores.csv")

resultados = []
for anio in ANIOS:
    d = DEUDA[anio]
    e = PATRIM[anio]
    interes = abs(INT_PAG[anio]) if INT_PAG[anio] is not None else None
    kd = None
    if interes is not None and d:
        kd = interes / d
    kd_neto = kd * (1 - T_ESTATUTARIA[anio]) if kd is not None else None
    wd = d / (d + e) if (d is not None and e is not None) else None
    we = e / (d + e) if (d is not None and e is not None) else None
    kd_term = kd_neto * wd if (kd_neto is not None and wd is not None) else None
    ke_term = roic[anio] * we if (roic[anio] is not None and we is not None) else None
    if kd_term is not None and ke_term is not None:
        wacc = kd_term + ke_term
        estado = "ACEPTADO"
    else:
        wacc = None
        estado = "NO_CALCULABLE"
    resultados.append(
        {
            "periodo": anio,
            "deuda_financiera_total": d,
            "patrimonio_total": e,
            "intereses_pagados_abs": interes,
            "costo_deuda_bruto": round(kd, 6) if kd is not None else None,
            "tasa_estatutaria": T_ESTATUTARIA[anio],
            "costo_deuda_neto": round(kd_neto, 6) if kd_neto is not None else None,
            "proporcion_deuda": round(wd, 6) if wd is not None else None,
            "proporcion_patrimonio": round(we, 6) if we is not None else None,
            "roi_ke_roic": round(roic[anio], 6) if roic[anio] is not None else None,
            "wacc": round(wacc, 6) if wacc is not None else None,
            "estado": estado,
            "nota": "Ke=ROIC(id34); Kd=|intereses pagados|/deuda; wd/we segun taxonomia; sin parametros externos"
            if estado == "ACEPTADO"
            else "Ke indisponible (ROIC requiere promedio t y t-1; sin t-1 para 2020)",
        }
    )

(OUT_DIR / "wacc_roi_2020_2025.json").write_text(
    json.dumps({"metodologia": "WACC_Kp=ROI", "ke": "ROIC id 34", "kd": "abs(intereses_pagados)/deuda", "resultados": resultados}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

with open(OUT_DIR / "wacc_roi_2020_2025.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(list(resultados[0].keys()))
    for r in resultados:
        w.writerow(list(r.values()))

for r in resultados:
    print(f"{r['periodo']} | Kd_neto={r['costo_deuda_neto']} wd={r['proporcion_deuda']} we={r['proporcion_patrimonio']} Ke(ROIC)={r['roi_ke_roic']} WACC={r['wacc']} [{r['estado']}]")

print("OK ->", OUT_DIR)