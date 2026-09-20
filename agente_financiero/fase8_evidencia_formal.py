# fase8_evidencia_formal.py
# Fase 8 - Modulo de Evidencia Formal (2026-09-19).
# Cruza cada concepto del consolidado (datos_estados_financieros.csv, 87 conceptos x 6 anos)
# con su origen documental en los PDF (documento -> estado -> seccion -> pagina -> nota -> linea).
# Reglas: no inventar ni interpolar (sin match textual -> NO_ENCONTRADO); validacion por coherencia
# numerica contra los valores impresos en los estados financieros (separador de miles '.', negativos en parentesis).
#
# Fuente de verdad del texto: segmentacion_YYYY.json (documento "Estados Financieros_YYYY.pdf").
# Para el ano 2020 se usa el comparativo del documento 2021 (columna 2020).
#
# Matcher: se restringe por segmento segun el prefijo del concepto (b_ -> ESF, i_ -> ERI, c_ -> Flujo),
# con coincidencia tolerante a pluralizacion (prefijo) y mapa de alias por concepto a las frases
# reales del PDF (no se inventa: las frases provienen de extraction/segmentacion verificadas).

import csv
import json
import re
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SALIDAS = BASE / "salidas"
AGENTE = Path(__file__).resolve().parent
OUT_DIR = SALIDAS / "fase8_evidencia_formal"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANIOS = ["2020", "2021", "2022", "2023", "2024", "2025"]
DOC_POR_ANIO = {  # ano objetivo -> (documento de texto origen, indice de columna dentro de la linea)
    "2020": ("Estados Financieros_2021.pdf", 1),
    "2021": ("Estados Financieros_2021.pdf", 0),
    "2022": ("Estados Financieros_2022.pdf", 0),
    "2023": ("Estados Financieros_2023.pdf", 0),
    "2024": ("Estados Financieros_2024.pdf", 0),
    "2025": ("Estados Financieros_2025.pdf", 0),
}
SEG_POR_DOC = {}  # ano documento -> lista de segmentos {titulo,pagina,texto,doc_anio}

SEG_RESTRICCION = {
    "b_": "SITUACION",
    "i_": "RESULTADO",
    "c_": "FLUJO",
}

STOPW = {
    "de", "en", "el", "la", "los", "las", "y", "a", "al", "del", "o", "por", "para",
    "un", "una", "unos", "unas", "con", "sin", "entre", ",", "cf",
}

ALIAS = {
    "i_gasto_impuesto_corriente": ["gasto por impuestos a las ganancias"],
    "i_gasto_impuesto_diferido": ["gasto ingreso por impuesto diferido"],
    "i_resultado_del_ejercicio": ["resultado del ejercicio", "utilidad del periodo"],
    "i_comprehensivo_total": ["total utilidad del ejercicio y otro resultado integral"],
    "i_ori_total": ["total otro resultado integral del periodo"],
    "i_ori_titulos": ["valorizacion titulos participativos"],
    "i_ori_actuarial": ["valorizacion actuarial pensionados"],
    "i_ori_inmuebles": ["valorizacion bienes inmuebles"],
    "i_impuesto_diferido_ori": ["impuesto diferido"],
    "c_gasto_impuesto_corriente": ["gasto por impuestos a las ganancias"],
    "c_gasto_impuesto_diferido": ["gasto por impuesto diferido"],
    "c_utilidad_del_ejercicio": ["utilidad del periodo"],
    "c_provisiones": ["provisiones multas litigios"],
    "c_depreciacion": ["depreciacion"],
    "c_depreciacion_derecho_uso": ["depreciacion derechos de uso"],
    "c_valoracion_inversiones": ["valoracion de inversiones"],
    "c_beneficios_empleados": ["pasivo por beneficios"],
    "c_deterioro_cxc": ["deterioro cuentas por cobrar"],
    "c_reintegro_provisiones": ["reintegro de otras provisiones"],
    "c_amortizacion_intangibles": ["amortizacion de intangibles"],
    "c_amortizacion_otros": ["amortizacion de otros activos"],
    "c_intereses_arrendamiento": ["intereses sobre pasivos por arrendamiento"],
    "c_baja_ppye": ["baja en propiedades y equipo", "baja propiedades y equipo"],
    "c_baja_depreciacion_ppye": ["baja depreciacion en propiedades y equipo"],
    "c_baja_intangibles": ["baja en activos intangibles", "baja activos intangibles"],
    "c_baja_amortizacion_intangibles": ["baja amortizacion en activos intangibles"],
    "c_cuentas_por_cobrar": ["cuentas por cobrar"],
    "c_cuentas_por_pagar": ["cuentas por pagar"],
    "c_impuestos_neto": ["impuestos neto"],
    "c_pasivos_provisiones": ["pasivos por provisiones"],
    "c_intereses_pagados": ["intereses pagados"],
    "c_impuestos_pagados": ["impuestos pagados"],
    "c_flujo_operacion": ["flujo neto de efectivo actividades de operacion", "flujo neto de efectivo operacion"],
    "c_inversiones": ["inversiones"],
    "c_adquisicion_ppye": ["adquisicion propiedades y equipo"],
    "c_adquisicion_intangibles": ["adquisicion de activos intangibles"],
    "c_flujo_inversion": ["flujo neto de efectivo inversion", "flujo neto de efectivo inversiones"],
    "c_pagos_arrendamiento": ["pagos parte principal arrendamiento"],
    "c_dividendos": ["dividendos decretados"],
    "c_flujo_financiacion": ["flujo neto de efectivo financiacion"],
    "c_otros_activos": ["otros activos"],
    "c_efectivo_restriccion": ["efectivo restringido"],
    "c_efectivo_sin_restriccion": ["efectivo sin restriccion"],
    "c_efectivo_inicio": ["total efectivo al inicio de periodo"],
    "c_efectivo_cierre": ["efectivo al cierre del periodo"],
    "c_aumento_neto": ["aumento neto"],
    "b_impuesto_corriente_activo": ["activo por impuesto a las ganancias corrientes", "activo por impuesto corriente"],
    "b_impuesto_corriente_pasivo": ["pasivo por impuesto a las ganancias corrientes", "pasivo por impuesto corriente"],
    "b_impuesto_diferido_activo": ["activo por impuesto diferido"],
    "b_impuesto_diferido_pasivo": ["pasivo por impuesto diferido"],
    "b_ori_valorizacion": ["ganancias o perdidas no realizadas"],
    "b_efecto_ncif": ["normas de contabilidad y de informacion financiera", "ncif"],
    "b_derecho_uso_activo": ["derecho en uso activo", "derecho de uso activo"],
    "b_derecho_uso_pasivo": ["derecho en uso pasivo", "derecho de uso pasivo"],
    "b_provisiones": ["procesos judiciales", "provisiones"],
    "b_activo_total": ["total de activos"],
    "b_pasivo_total": ["total de pasivos"],
    "b_total_pasivo_patrimonio": ["total de pasivos y patrimonio"],
    "b_beneficios_empleados": ["pasivo por beneficios a los empleados"],
    "b_otros_pasivos_no_financieros": ["otros pasivos no financieros"],
    "b_otros_activos_no_financieros": ["otros activos no financieros"],
    "b_cuentas_por_cobrar": ["cuentas comerciales por cobrar", "cuentas por cobrar"],
    "b_cuentas_por_pagar": ["cuentas comerciales por pagar", "cuentas por pagar"],
    "b_efectivo": ["efectivo y equivalentes de efectivo", "efectivo"],
    "b_inversiones": ["inversiones"],
    "b_propiedades_planta_equipo": ["propiedades y equipo"],
    "b_activos_intangibles": ["activos intangibles"],
    "b_capital_suscrito": ["capital suscrito y pagado"],
    "b_prima_colocacion": ["prima en colocacion de acciones"],
    "b_reservas": ["reservas"],
    "b_utilidad_periodo": ["utilidad del periodo"],
    "b_utilidad_ejercicios_anteriores": ["utilidad de ejercicios anteriores"],
    "b_patrimonio_total": ["total patrimonio"],
    "i_comisiones": ["comisiones y honorarios"],
    "i_ingresos_operaciones_conjuntas": ["ingresos de actividades en operaciones conjuntas", "ingresos de operaciones conjuntas"],
    "i_utilidad_bruta": ["resultado antes de gastos de operacion"],
    "i_gasto_beneficios": ["beneficios a empleados"],
    "i_gastos_administracion": ["gastos de administracion"],
    "i_gastos_operaciones_conjuntas": ["gastos de actividades en operaciones conjuntas"],
    "i_deterioro_cxc": ["deterioro cuentas por cobrar"],
    "i_depreciaciones": ["depreciacion"],
    "i_amortizaciones": ["amortizacion"],
    "i_resultado_despues_gastos": ["resultado despues de gastos operacion", "resultado despues de gastos de operacion"],
    "i_resultado_financiero_neto": ["resultado financiero neto", "resultado financiero"],
    "i_resultado_operacional": ["resultado operacional"],
    "i_otros_ingresos_egresos": ["otros ingresos egresos", "otros ingresos"],
    "i_resultado_antes_impuestos": ["resultado antes de impuestos a las ganancias"],
}

MIN_RECALL = 0.55  # rechaza coincidencias espurias de bajo recuerdo (frases parcialmente presentes)

ORDEN_FLUJO = {  # los totales del EFE aparecen siempre en este orden: operacion, inversion, financiacion
    "c_flujo_operacion": 1,
    "c_flujo_inversion": 2,
    "c_flujo_financiacion": 3,
}

REQUERIDO = {  # tokens discriminadores que DEBEN aparecer en la linea del PDF para considerar el match
    "b_impuesto_corriente_activo": {"activo", "corriente"},
    "b_impuesto_corriente_pasivo": {"pasivo", "corriente"},
    "b_impuesto_diferido_activo": {"activo", "diferido"},
    "b_impuesto_diferido_pasivo": {"pasivo", "diferido"},
    "i_ori_inmuebles": {"inmuebles"},
    "c_baja_amortizacion_intangibles": {"amortizacion"},
    "c_aumento_neto": {"aumento", "neto"},
    "c_efectivo_cierre": {"cierre"},
}


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def toks(s):
    return {t for t in norm(s).split() if t not in STOPW and not t.isdigit()}


def tok_equiv(t1, t2):
    if t1 == t2:
        return True
    if min(len(t1), len(t2)) >= 5:
        if t1.startswith(t2) or t2.startswith(t1):
            return True
    if len(t1) <= 4 and len(t2) <= 4:
        return False
    return False


def cargar_segmentaciones():
    for anio in ["2021", "2022", "2023", "2024", "2025"]:
        p = AGENTE / f"segmentacion_{anio}.json"
        if not p.exists():
            continue
        d = json.load(open(p, encoding="utf-8"))
        for doc in d.get("documentos", []):
            nom = doc["documento_origen"]
            segs = []
            for s in doc.get("segmentos", []):
                texto = s.get("texto", "")
                segs.append(
                    {
                        "titulo": s.get("titulo_seccion") or s.get("titulo_resumen") or "",
                        "pagina": s.get("pagina_inicio"),
                        "texto": texto,
                        "doc_anio": anio,
                    }
                )
            if "estados financieros" in norm(nom):
                SEG_POR_DOC[anio] = segs
                for s in segs:
                    s["_lineas"] = s["texto"].split("\n")


def pockets(linea):
    vals = ["-", "(", ")", "$"]
    out = []
    for t in re.split(r"\s+", linea.strip()):
        tk = t.strip()
        if not tk:
            continue
        limpio = tk.replace("$", "")
        if limpio in vals:
            out.append(("dash", None) if limpio == "-" else ("txt", None))
            continue
        if limpio.startswith("(") and limpio.endswith(")"):
            limpio = limpio[1:-1]
            sign = -1
        else:
            sign = 1
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", limpio):
            out.append(("num", sign * int(limpio.replace(".", ""))))
        elif re.fullmatch(r"\d+", limpio):
            out.append(("num", sign * int(limpio)))
        elif re.fullmatch(r"\d{1,2}\.\d{1,2}", limpio):
            out.append(("nota", limpio))
        else:
            out.append(("txt", None))
    return out


def extraer(linea):
    ps = pockets(linea)
    numericos = [p for p in ps if p[0] in ("num", "dash")]
    if not numericos:
        return None, None, None
    slots = numericos[-2:]
    nota = None
    num_nota = [p[1] for p in ps if p[0] == "nota"]
    if num_nota:
        nota = num_nota[0]
    col0 = None if slots[0][0] == "dash" else slots[0][1]
    col1 = None
    if len(slots) == 2:
        col1 = None if slots[1][0] == "dash" else slots[1][1]
    return nota, col0, col1


def fusionar(seg, ln):
    """Une la linea con las de continuacion (salto de renglon del PDF) hasta obtener 2 valores.
    Se detiene si la continuacion es una linea independiente de datos (>=4 palabras) o si la linea
    ya contiene un valor real (1 numero + guion significa anio vacio, no continuacion truncada)."""
    merged = ln.strip()
    idx = seg["_lineas"].index(ln)
    add = 0
    while add < 3:
        numericos = [p for p in pockets(merged) if p[0] == "num"]
        if len(numericos) >= 2:
            break
        if len(numericos) == 1 and any(p[0] == "dash" for p in pockets(merged)):
            break
        idx += 1
        if idx >= len(seg["_lineas"]):
            break
        prox = seg["_lineas"][idx].strip()
        if not prox or prox.endswith(":"):
            break
        if len(numericos) == 0 and len(toks(prox)) >= 4:
            break
        merged = merged + " " + prox
        add += 1
    return merged


def buscar(concepto, rotulo, prefijo, doc_nom):
    frases = ALIAS.get(concepto, [rotulo])
    mejor = None
    anio_doc = None
    for anio in SEG_POR_DOC:
        if anio in doc_nom:
            anio_doc = anio
            break
    if anio_doc is None:
        return None
    pref_titulo = SEG_RESTRICCION.get(prefijo, "")
    segs = SEG_POR_DOC.get(anio_doc, [])
    candidatos = []

    orden = ORDEN_FLUJO.get(concepto)
    if orden:
        for seg in segs:
            tn = norm(seg["titulo"]) if seg["titulo"] else ""
            if "flujo" not in tn:
                continue
            cont = 0
            for ln in seg["_lineas"]:
                if "flujo neto de efectivo" not in norm(ln):
                    continue
                cont += 1
                if cont != orden:
                    continue
                linea = ln.strip()
                idx = seg["_lineas"].index(ln)
                prox = seg["_lineas"][idx + 1].strip() if idx + 1 < len(seg["_lineas"]) else ""
                if extraer(linea) == (None, None, None) and prox and any(p[0] == "num" for p in pockets(prox)):
                    linea = linea + " " + prox
                if extraer(linea) != (None, None, None):
                    candidatos.append((10.0, linea, 0, seg["titulo"], seg["pagina"], anio_doc))
        if candidatos:
            candidatos.sort(key=lambda x: (-x[0], x[1]))
            return candidatos[0]

    for seg in segs:
        tit = seg["titulo"]
        if pref_titulo:
            tn = norm(tit) if tit else ""
            if pref_titulo.lower() not in tn:
                continue
            req = REQUERIDO.get(concepto) or set()
        for ln in seg["_lineas"]:
            lt = toks(ln)
            if not lt:
                continue
            for frase in frases:
                objetivo = toks(frase)
                if not objetivo:
                    continue
                if req and not all(any(tok_equiv(rq, x) for x in lt) for rq in req):
                    continue
                match_t = [t for t in objetivo if any(tok_equiv(t, x) for x in lt)]
                if not match_t:
                    continue
                recall = len(match_t) / len(objetivo)
                if recall < MIN_RECALL:
                    continue
                linea = fusionar(seg, ln)
                dice = 2 * len(match_t) / (len(objetivo) + len(lt))
                score = recall + 0.5 * dice
                candidatos.append((score, linea, len(lt), seg["titulo"], seg["pagina"], anio_doc))
    if not candidatos:
        return None
    candidatos.sort(key=lambda x: (-x[0], x[2], x[1][:3]))
    return candidatos[0]


def main():
    cargar_segmentaciones()
    filas = list(csv.DictReader(open(SALIDAS / "datos_estados_financieros.csv", newline="", encoding="utf-8-sig")))
    registros = []
    for fila in filas:
        concepto = fila["concepto"]
        rotulo = fila["rotulo"]
        prefijo = concepto.split("_", 1)[0] + "_"
        for anio in ANIOS:
            consol = fila.get(anio, "").strip()
            consol_val = float(consol) if consol not in ("", None) else None
            doc_nom, col_idx = DOC_POR_ANIO[anio]
            hit = buscar(concepto, rotulo, prefijo, doc_nom)
            if hit is None:
                registros.append(
                    {
                        "anio": anio,
                        "concepto": concepto,
                        "rotulo": rotulo,
                        "documento_origen": doc_nom,
                        "estado_financiero": None,
                        "pagina": None,
                        "nota": None,
                        "evidencia_linea": None,
                        "valor_pdf": None,
                        "valor_consolidado": consol_val,
                        "coincide": None,
                        "estado": "NO_ENCONTRADO",
                        "confianza": None,
                    }
                )
                continue
            score, linea, _len_lt, titulo, pagina, _anio_doc = hit
            nota, col0, col1 = extraer(linea)
            valor_pdf = col0 if col_idx == 0 else col1
            if valor_pdf is None and consol_val is None:
                estado = "ACEPTADO"
                coincide = True
                conf = "ALTA"
            elif valor_pdf is None or consol_val is None:
                if valor_pdf is None and consol_val is not None:
                    estado = "NO_CALCULABLE"
                else:
                    estado = "DUDOSO"
                coincide = valor_pdf is not None and consol_val is not None and abs(valor_pdf - consol_val) <= 0.5
                conf = "MEDIA"
            else:
                coincide = abs(valor_pdf - consol_val) <= 0.5
                estado = "ACEPTADO" if coincide else "DUDOSO"
                conf = "ALTA" if coincide else "MEDIA"
            registros.append(
                {
                    "anio": anio,
                    "concepto": concepto,
                    "rotulo": rotulo,
                    "documento_origen": doc_nom,
                    "estado_financiero": titulo,
                    "pagina": pagina,
                    "nota": nota,
                    "evidencia_linea": linea,
                    "valor_pdf": valor_pdf,
                    "valor_consolidado": consol_val,
                    "coincide": coincide,
                    "estado": estado,
                    "confianza": conf,
                }
            )

    with open(OUT_DIR / "evidencia_formal_conceptos.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
        w.writeheader()
        w.writerows(registros)

    resumen = {
        "metodologia": "Módulo de Evidencia Formal - cruce consolidado vs estados financieros (segmentacion_YYYY.json)",
        "fuentes": "datos_estados_financieros.csv + segmentacion_2021..2025.json (Estados Financieros_YYYY.pdf)",
        "regla": "Sin match textual -> NO_ENCONTRADO; coherencia numerica (tolerancia 0.5 M) -> ACEPTADO/DUDOSO",
        "por_estado": {},
        "por_anio": {},
    }
    for anio in ANIOS:
        sub = [r for r in registros if r["anio"] == anio]
        resumen["por_anio"][anio] = {}
        for r in sub:
            resumen["por_anio"][anio][r["estado"]] = resumen["por_anio"][anio].get(r["estado"], 0) + 1
            resumen["por_estado"][r["estado"]] = resumen["por_estado"].get(r["estado"], 0) + 1
    no_enc = [r for r in registros if r["estado"] == "NO_ENCONTRADO"]
    resumen["total_registros"] = len(registros)
    resumen["no_encontrados_conceptos"] = sorted({r["concepto"] for r in no_enc})

    (OUT_DIR / "resumen_evidencia_formal.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    for anio in ANIOS:
        print(f"{anio}:", resumen["por_anio"][anio])
    print("ESTADOS:", resumen["por_estado"])
    print("NO_ENCONTRADOS:", resumen["no_encontrados_conceptos"])
    print("OK ->", OUT_DIR)
    return resumen


if __name__ == "__main__":
    main()