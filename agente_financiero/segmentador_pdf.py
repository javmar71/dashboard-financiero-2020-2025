#!/usr/bin/env python3
"""
segmentador_pdf.py — Fase 3 / Paso 3.2

Segmentador DETERMINISTICO de PDF: PDF -> paginas -> secciones/fragmentos
textuales delimitados + metadatos de origen.

QUE HACE:
  - Lee cada pagina y reconstruye filas de texto (fusionando spans/lineas con la
    misma coordenada vertical).
  - Detecta encabezados de seccion mediante reglas puramente deterministas
    (patrones estructurales, numeracion, mayusculas y aislamiento por espaciado).
  - Construye segmentos continuos que atraviesan paginas sin cortar tablas ni
    bloques por cambio de pagina.
  - Excluye ruido tecnico repetitivo (marca de agua "VERIFIED", pies de pagina,
    numeracion de pagina) detectado de forma deterministica.

QUE NO HACE (limites explicitos del Paso 3.2):
  - NO llama a Gemini ni a ningun proveedor de IA.
  - NO interpreta cuentas.
  - NO asigna variable_madre_id, ni indicadores, ni codigo PUC.
  - NO infiere valores.
  - NO decide que fuente semantica es correcta.
  - NO genera JSON de extraccion IA.
  - NO clasifica el archivo "Informe de Gestion_2021.pdf" como
    fuente_esperada="informe_gestion": el nombre del archivo y el contenido se
    conservan como hechos independientes.

Uso:
  python segmentador_pdf.py "ruta\\al.pdf" [--out salida.json] [--sin-heuristica] [--debug]
  python segmentador_pdf.py --dir "carpeta" [--out salida.json] [--sin-heuristica]
  (sin argumentos: procesa los 3 PDF de ESTADOS_FINANCIEROS_2021)
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

import pymupdf

# --------------------------------------------------------------------------- #
# Parametros deterministas (documentados en PASO3_2_REPORTE.md)
# --------------------------------------------------------------------------- #

TOL_FILA = 2.5              # px: filas con centro y a menos de esta distancia se fusionan
BANDA_SUP_FRAC = 0.13      # fraccion superior de la pagina considerada "borde"
BANDA_INF_FRAC = 0.85      # fraccion inferior de la pagina considerada "borde"
RUIDO_MIN_PAGINAS = 4      # un texto repetido solo puede ser ruido si el PDF tiene >= 4 paginas
RUIDO_MIN_REP = 0.5        # y aparece en al menos el 50% de las paginas
RUIDO_MAX_LEN = 90         # y su longitud (normalizada) no supera este valor
MAYUS_MIN_ALPHA = 8        # letras minimas para considerar un titulo en mayusculas
MAYUS_MIN_TAM = 10.5       # tamano de fuente minimo para titulo en mayusculas
MAYUS_MIN_RATIO = 0.85     # proporcion minima de mayusculas
TITULO_MAX_LEN = 90        # longitud maxima de un encabezado
PATRON_MIN_RATIO = 0.8     # un patron estructural solo cuenta si el texto es casi todo mayusculas
HEUR_MIN_ALPHA = 6         # letras minimas para el titulo heuristico
HEUR_MAX_LEN = 85          # longitud maxima para el titulo heuristico
HEUR_FACTOR_GAP = 1.5      # el hueco debe ser >= 1.5x la mediana de huecos de la pagina
HEUR_MIN_SIGUIENTE = 55    # la linea siguiente debe ser prosa (>= 55 caracteres)
HEUR_MAX_RATIO_SIG = 0.6   # y la linea siguiente no debe ser un titulo
HEUR_MAX_PALABRAS = 8      # un titulo heuristico tiene como maximo 8 palabras

RE_NUM_SUB = re.compile(r"^(\d{1,2}(?:\.\d{1,2})+)\s+[A-Za-zÁÉÍÓÚÜÑ]")
RE_NUM_PRINCIPAL = re.compile(r"^(\d{1,2})\.\s+\S")
RE_NUMERACION = re.compile(r"^\d+(?:\.\d+)*\.?\s+")
RE_TERMINAL = re.compile(r"[.;:,]$")

# Titulos estructurales de estados financieros (regla deterministica, documentada).
# Se comparan sobre el texto en MAYUSCULAS y sin tildes.
PATRONES_TITULO = [
    r"^NOTAS A LOS ESTADOS FINANCIEROS",
    r"^INFORME DEL REVISOR FISCAL",
    r"^INFORME SOBRE LA AUDITOR[I]A DE LOS ESTADOS FINANCIEROS",
    r"^INFORME SOBRE OTROS REQUERIMIENTOS LEGALES Y REGLAMENTARIOS",
    r"^CERTIFICACION DE LOS ESTADOS FINANCIEROS",
    r"^ESTADO DE SITUACION FINANCIERA",
    r"^ESTADO DE RESULTADO INTEGRAL",
    r"^ESTADO DE CAMBIOS EN EL PATRIMONIO",
    r"^ESTADO DE FLUJOS? DE EFECTIVO",
    r"^ESTADO DE FLUJO DE EFECTIVO",
]
PATRONES_TITULO = [re.compile(p) for p in PATRONES_TITULO]

TIPO = {
    "PATRON": "titulo_patron",
    "NUM_PRINCIPAL": "seccion_numerada",
    "NUM_SUB": "subseccion_numerada",
    "MAYUS": "titulo_mayusculas",
    "HEUR": "titulo_heuristica",
    "PREAMBULO": "preambulo",
}


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #

def sin_tildes(texto):
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def ratio_mayusculas(texto):
    letras = [c for c in texto if c.isalpha()]
    if not letras:
        return 0.0
    return sum(1 for c in letras if c.isupper()) / len(letras)


def normaliza_ruido(texto):
    return re.sub(r"\d+", "#", texto).strip().upper()


def normaliza_titulo(texto):
    plano = sin_tildes(texto).upper()
    plano = RE_NUMERACION.sub("", plano)
    return re.sub(r"\s+", " ", plano).strip()


def titulo_corto(texto):
    corte = len(texto)
    for delim in (" - ", " – ", ": ", ". "):
        pos = texto.find(delim)
        if pos >= 4:
            corte = min(corte, pos)
    return texto[:corte].strip()


def _lineas_pagina(page):
    data = page.get_text("dict")
    lineas = []
    for bloque in data.get("blocks", []):
        for linea in bloque.get("lines", []):
            spans = [s for s in linea.get("spans", []) if s["text"].strip()]
            if not spans:
                continue
            x0 = min(s["bbox"][0] for s in spans)
            y0 = min(s["bbox"][1] for s in spans)
            x1 = max(s["bbox"][2] for s in spans)
            y1 = max(s["bbox"][3] for s in spans)
            lineas.append(
                {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "yc": (y0 + y1) / 2.0,
                 "spans": spans}
            )
    lineas.sort(key=lambda l: (round(l["yc"], 1), l["x0"]))
    return lineas


def extraer_filas(page):
    """Reconstruye filas de texto, fusionando lineas con igual coordenada vertical."""
    lineas = _lineas_pagina(page)
    filas = []
    for linea in lineas:
        if filas and abs(linea["yc"] - filas[-1]["yc"]) <= TOL_FILA:
            grupo = filas[-1]
            grupo["_lineas"].append(linea)
            grupo["yc"] = statistics.mean(l["yc"] for l in grupo["_lineas"])
            grupo["y0"] = min(l["y0"] for l in grupo["_lineas"])
            grupo["y1"] = max(l["y1"] for l in grupo["_lineas"])
            grupo["x0"] = min(l["x0"] for l in grupo["_lineas"])
            grupo["x1"] = max(l["x1"] for l in grupo["_lineas"])
        else:
            filas.append(
                {"yc": linea["yc"], "y0": linea["y0"], "y1": linea["y1"],
                 "x0": linea["x0"], "x1": linea["x1"], "_lineas": [linea]}
            )
    for fila in filas:
        piezas = []
        for linea in sorted(fila["_lineas"], key=lambda l: l["x0"]):
            for span in sorted(linea["spans"], key=lambda s: s["bbox"][0]):
                piezas.append(span["text"])
        fila["texto"] = re.sub(r"\s+", " ", " ".join(piezas)).strip()
        fila["tamano"] = round(
            max((s["size"] for l in fila["_lineas"] for s in l["spans"]), default=0.0), 2
        )
        fila["fuentes"] = sorted({s["font"] for l in fila["_lineas"] for s in l["spans"]})
        del fila["_lineas"]
    filas.sort(key=lambda f: (f["yc"], f["x0"]))
    return filas


# --------------------------------------------------------------------------- #
# Ruido repetitivo
# --------------------------------------------------------------------------- #

def detectar_ruido(paginas):
    """Devuelve (conjunto de textos normalizados ruidosos, registros de ruido)."""
    total = len(paginas)
    registros = []
    if total < RUIDO_MIN_PAGINAS:
        return set(), registros
    apariciones = {}
    for idx, pagina in enumerate(paginas):
        alto = pagina["_page"].rect.height
        for fila in pagina["filas"]:
            texto = fila["texto"]
            if not texto or len(texto) > RUIDO_MAX_LEN:
                continue
            en_borde = (
                fila["yc"] < alto * BANDA_SUP_FRAC or fila["yc"] > alto * BANDA_INF_FRAC
            )
            if not en_borde:
                continue
            apariciones.setdefault(normaliza_ruido(texto), set()).add(idx)
    ruido = {n for n, pgs in apariciones.items() if len(pgs) / total >= RUIDO_MIN_REP}
    for idx, pagina in enumerate(paginas):
        for fila in pagina["filas"]:
            if normaliza_ruido(fila["texto"]) in ruido:
                registros.append(
                    {"pagina": idx + 1, "texto": fila["texto"],
                     "texto_normalizado": normaliza_ruido(fila["texto"]),
                     "y": round(fila["yc"], 1)}
                )
    return ruido, registros


# --------------------------------------------------------------------------- #
# Clasificacion de encabezados
# --------------------------------------------------------------------------- #

def mediana_huecos(filas):
    huecos = [
        filas[i + 1]["yc"] - filas[i]["yc"]
        for i in range(len(filas) - 1)
        if filas[i + 1]["yc"] - filas[i]["yc"] > 0
    ]
    return statistics.median(huecos) if huecos else None


def clasificar_encabezado(fila, anteriores, posteriores, mediana, usar_heuristica):
    """Devuelve (nivel, tipo) o None. Reglas deterministas, en orden de prioridad."""
    texto = fila["texto"]
    if not texto:
        return None
    letras = [c for c in texto if c.isalpha()]
    plano = sin_tildes(texto).upper()
    ratio = ratio_mayusculas(texto)

    # 1) Titulos estructurales conocidos (deben ser casi todo mayusculas).
    if ratio >= PATRON_MIN_RATIO and len(texto) <= TITULO_MAX_LEN:
        for patron in PATRONES_TITULO:
            if patron.match(plano):
                return 1, TIPO["PATRON"]

    # 2) Subsecciones numeradas (x.y...). Cada componente 1-2 digitos evita
    #    confundir miles separados con punto (ej. 81.254).
    if RE_NUM_SUB.match(texto) and len(texto) <= TITULO_MAX_LEN * 2:
        puntos = texto.split()[0].count(".") + 1
        return min(puntos, 3), TIPO["NUM_SUB"]

    # 3) Secciones numeradas principales (N. TITULO).
    if RE_NUM_PRINCIPAL.match(texto) and len(texto) <= TITULO_MAX_LEN and ratio >= 0.4:
        return 1, TIPO["NUM_PRINCIPAL"]

    # 4) Titulos en mayusculas con fuente mayor que el cuerpo.
    if (
        fila["tamano"] >= MAYUS_MIN_TAM
        and len(texto) <= TITULO_MAX_LEN
        and len(letras) >= MAYUS_MIN_ALPHA
        and ratio >= MAYUS_MIN_RATIO
        and not RE_TERMINAL.search(texto)
    ):
        return 1, TIPO["MAYUS"]

    # 5) Heuristica de aislamiento (opcional): linea corta, sin cifras, aislada
    #    por espaciado y seguida de prosa.
    if usar_heuristica and mediana and anteriores and posteriores:
        siguiente = posteriores[0]
        if (
            len(texto) <= HEUR_MAX_LEN
            and len(letras) >= HEUR_MIN_ALPHA
            and len(texto.split()) <= HEUR_MAX_PALABRAS
            and texto[0].isupper()
            and ratio <= MAYUS_MIN_RATIO
            and not RE_TERMINAL.search(texto)
            and not any(c.isdigit() for c in texto)
            and len(siguiente["texto"]) >= HEUR_MIN_SIGUIENTE
            and ratio_mayusculas(siguiente["texto"]) <= HEUR_MAX_RATIO_SIG
        ):
            gap_prev = fila["yc"] - anteriores[-1]["yc"]
            gap_next = siguiente["yc"] - fila["yc"]
            if gap_prev >= HEUR_FACTOR_GAP * mediana and gap_next >= HEUR_FACTOR_GAP * mediana:
                return 1, TIPO["HEUR"]

    return None


# --------------------------------------------------------------------------- #
# Segmentacion
# --------------------------------------------------------------------------- #

def segmentar_pdf(path, usar_heuristica=True):
    doc = pymupdf.open(path)
    nombre = os.path.basename(path)
    paginas = [
        {"_page": doc[i], "filas": extraer_filas(doc[i])} for i in range(doc.page_count)
    ]

    ruido, registros_ruido = detectar_ruido(paginas)

    segmentos = []
    estado = {"actual": None, "orden": 0}

    def abrir(titulo, nivel, tipo, fila, pagina):
        estado["orden"] += 1
        estado["actual"] = {
            "orden_documento": estado["orden"],
            "documento_origen": nombre,
            "tipo_segmento": tipo,
            "nivel": nivel,
            "titulo_seccion": titulo,
            "titulo_resumen": titulo_corto(titulo) if titulo else None,
            "pagina_inicio": pagina,
            "pagina_fin": pagina,
            "bloques_por_pagina": [],
            "num_filas": 0,
            "encabezado_origen": {
                "pagina": pagina,
                "y": round(fila["yc"], 1) if fila else None,
                "tamano": fila["tamano"] if fila else None,
                "fuentes": fila["fuentes"] if fila else [],
            },
            "_contenido": 0,
            "_titulo_norm": normaliza_titulo(titulo) if titulo else None,
        }
        segmentos.append(estado["actual"])

    def agregar(fila, pagina, es_titulo=False):
        if estado["actual"] is None:
            abrir(None, None, TIPO["PREAMBULO"], None, pagina)
        seg = estado["actual"]
        if not seg["bloques_por_pagina"] or seg["bloques_por_pagina"][-1]["pagina"] != pagina:
            seg["bloques_por_pagina"].append({"pagina": pagina, "lineas": []})
        seg["bloques_por_pagina"][-1]["lineas"].append(fila["texto"])
        seg["pagina_fin"] = pagina
        seg["num_filas"] += 1
        if not es_titulo:
            seg["_contenido"] += 1

    for idx in range(doc.page_count):
        filas = paginas[idx]["filas"]
        visibles = [f for f in filas if normaliza_ruido(f["texto"]) not in ruido]
        mediana = mediana_huecos(visibles)
        for j, fila in enumerate(visibles):
            if not fila["texto"]:
                continue
            clase = clasificar_encabezado(
                fila, visibles[:j], visibles[j + 1 :], mediana, usar_heuristica
            )
            if clase is not None:
                nivel, tipo = clase
                norm = normaliza_titulo(fila["texto"])
                seg = estado["actual"]
                titulos_bloque = (TIPO["MAYUS"], TIPO["PATRON"])
                subtitulo = (
                    seg is not None
                    and seg["_contenido"] == 0
                    and tipo in titulos_bloque
                    and seg["tipo_segmento"] in titulos_bloque
                )
                continuacion = seg is not None and (norm == seg["_titulo_norm"] or subtitulo)
                if continuacion:
                    agregar(fila, idx + 1, es_titulo=True)
                else:
                    abrir(fila["texto"], nivel, tipo, fila, idx + 1)
                    agregar(fila, idx + 1, es_titulo=True)
            else:
                agregar(fila, idx + 1)

    for seg in segmentos:
        seg["texto"] = "\n".join(
            "\n".join(b["lineas"]) for b in seg["bloques_por_pagina"]
        ).strip()
        seg["bloques_por_pagina"] = [
            {"pagina": b["pagina"], "texto": "\n".join(b["lineas"])}
            for b in seg["bloques_por_pagina"]
        ]
        del seg["_contenido"]
        del seg["_titulo_norm"]

    resultado = {
        "documento_origen": nombre,
        "ruta": os.path.abspath(path),
        "num_paginas": doc.page_count,
        "num_segmentos": len(segmentos),
        "ruido_repetitivo_detectado": sorted(
            {r["texto_normalizado"] for r in registros_ruido}
        ),
        "num_filas_ruido_excluidas": len(registros_ruido),
        "segmentos": segmentos,
    }
    doc.close()
    return resultado


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

DIR_2021 = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Estados Financieros",
    "ESTADOS_FINANCIEROS_2021",
)
PDFS_DEFECTO = [
    "Estados Financieros_2021.pdf",
    "Informe de Gestion_2021.pdf",
    "Informe de Audtoria_2021.pdf",
]


def _rutas_entrada(args):
    if args.archivos:
        return [os.path.abspath(p) for p in args.archivos]
    if args.dir:
        base = os.path.abspath(args.dir)
        return [
            os.path.join(base, f)
            for f in sorted(os.listdir(base))
            if f.lower().endswith(".pdf")
        ]
    return [os.path.join(DIR_2021, f) for f in PDFS_DEFECTO]


def _resumen(res):
    print("=" * 78)
    print("%s  (paginas=%d, segmentos=%d, filas_ruido=%d)"
          % (res["documento_origen"], res["num_paginas"], res["num_segmentos"],
             res["num_filas_ruido_excluidas"]))
    print("  ruido repetitivo:", res["ruido_repetitivo_detectado"])
    for seg in res["segmentos"]:
        titulo = seg["titulo_resumen"] or "(sin titulo)"
        print("  #%02d  p.%d-%d  [%s]  %s"
              % (seg["orden_documento"], seg["pagina_inicio"], seg["pagina_fin"],
                 seg["tipo_segmento"], titulo[:80]))


def main():
    ap = argparse.ArgumentParser(description="Segmentador deterministico de PDF (Paso 3.2)")
    ap.add_argument("archivos", nargs="*", help="PDF(s) a segmentar")
    ap.add_argument("--dir", help="carpeta con PDFs a segmentar")
    ap.add_argument("--out", help="ruta del JSON de salida")
    ap.add_argument("--sin-heuristica", action="store_true",
                    help="desactiva la regla heuristica de titulo por aislamiento")
    ap.add_argument("--debug", action="store_true", help="imprime el resumen por documento")
    args = ap.parse_args()

    usar_heuristica = not args.sin_heuristica
    resultados = []
    for ruta in _rutas_entrada(args):
        if not os.path.isfile(ruta):
            print("AVISO: no existe %s" % ruta, file=sys.stderr)
            continue
        res = segmentar_pdf(ruta, usar_heuristica=usar_heuristica)
        resultados.append(res)
        _resumen(res)

    if args.out:
        payload = {
            "generador": "segmentador_pdf.py",
            "paso": "3.2",
            "usa_ia": False,
            "regla_heuristica_activa": usar_heuristica,
            "documentos": resultados,
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print("\nJSON escrito en: %s" % os.path.abspath(args.out))


if __name__ == "__main__":
    main()
