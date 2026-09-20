import glob
import os
import re
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as CFG


NUMERIC_RE = re.compile(r"^[-−+]?[\d.,()]+$")
YEAR_RE = re.compile(r"^20\d\d$")

X_AMOUNT_MIN, X_AMOUNT_MAX = 365.0, 600.0
X_LABEL_MAX = 340.0
Y_FOOTER_MAX = 720.0
MIN_CLUSTER_GAP = 40.0
SINGLE_BAND_SLACK = 45.0
Y_LABEL_TOL = 16.0
Y_OTHER_ROW = 2.5


class EstadoIDs:
    BALANCE = "balance"
    INCOME = "income"
    CASHFLOW = "cashflow"
    EQUITY = "equity"
    OTHER = "other"


def parse_number(token):
    s = token.strip()
    if s in ("-", "--", "—", "−"):
        return None
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1]
        v = parse_number_inner(s)
        return -v if v is not None else None
    return parse_number_inner(s)


def parse_number_inner(s):
    neg = False
    while s and s[0] in "-−+":
        if s[0] in "-−":
            neg = not neg
        s = s[1:]
    clean = s.replace(".", "").replace(",", "")
    if not clean.isdigit():
        return None
    v = int(clean)
    return -v if neg else v


def is_numeric_like(token):
    return bool(NUMERIC_RE.match(token))


def _word(w):
    return w[0], w[1], w[2], w[3], w[4]


def detect_statement(text):
    t = text.upper()
    if "SITUACI" in t and "ACTIVOS" in t:
        return EstadoIDs.BALANCE
    if "DE RESULTADO" in t:
        return EstadoIDs.INCOME
    if "FLUJO DE EFECTIVO" in t or "FLUJOS DE EFECTIVO" in t:
        return EstadoIDs.CASHFLOW
    if ("CAMBIOS" in t or "PATRIMONIO EN" in t) and "PATRIMONIO" in t:
        return EstadoIDs.EQUITY
    return EstadoIDs.OTHER


def data_start_y(words):
    ys = [w[1] for w in words if YEAR_RE.match(w[4]) and w[1] < 700.0]
    if not ys:
        return 0.0
    return max(ys) + 3.0


def column_bands(words, data_start):
    xs = [
        w[0]
        for w in words
        if is_numeric_like(w[4])
        and X_AMOUNT_MIN <= w[0] < X_AMOUNT_MAX
        and data_start < w[1] <= Y_FOOTER_MAX
    ]
    if not xs:
        return None
    unique = sorted(set(round(x, 1) for x in xs))
    if len(unique) == 1:
        c = unique[0]
        return [("cur", c - 12.0, c + SINGLE_BAND_SLACK)]
    gaps = [unique[i + 1] - unique[i] for i in range(len(unique) - 1)]
    imax = max(range(len(gaps)), key=lambda i: gaps[i])
    if gaps[imax] < MIN_CLUSTER_GAP:
        lo, hi = unique[0] - 12.0, unique[-1] + SINGLE_BAND_SLACK
        return [("cur", lo, hi)]
    cut = (unique[imax] + unique[imax + 1]) / 2.0
    return [
        ("cur", X_AMOUNT_MIN - 14.0, cut),
        ("prev", cut, X_AMOUNT_MAX + 40.0),
    ]


def extract_rows(words, data_start, bands):
    band_by_name = {name: (lo, hi) for name, lo, hi in bands}

    label_lines = []
    for w in words:
        x0, y0, x1, y1, token = _word(w)
        if x0 >= X_LABEL_MAX or y0 > Y_FOOTER_MAX:
            continue
        if token in ("$",):
            continue
        if is_numeric_like(token) and x0 >= 300.0:
            continue
        if y0 <= data_start:
            continue
        label_lines.append((round(y0, 1), x0, token))
    label_lines.sort()

    labels_by_y = {}
    for y, x0, token in label_lines:
        labels_by_y.setdefault(y, []).append((x0, token))

    numeric_groups = {}
    for w in words:
        x0, y0, x1, y1, token = _word(w)
        if y0 <= data_start or y0 > Y_FOOTER_MAX:
            continue
        if not is_numeric_like(token):
            continue
        for name, lo, hi in bands:
            if lo <= x0 < hi:
                key = round(y0, 1)
                numeric_groups.setdefault(key, {}).setdefault(name, []).append(
                    (x0, y0, token)
                )
                break

    rows = []
    for y in sorted(numeric_groups):
        groups = numeric_groups[y]
        cur_val = None
        prev_val = None
        for name in ("cur", "prev"):
            toks = groups.get(name)
            if not toks:
                continue
            toks.sort()
            for cand in reversed(toks):
                v = parse_number(cand[2])
                if v is not None:
                    if name == "cur":
                        cur_val = v
                    else:
                        prev_val = v
                    break
        label = build_label(labels_by_y, y, numeric_groups, y)
        rows.append({"y": y, "label": label, "cur": cur_val, "prev": prev_val})
    rows.sort(key=lambda r: r["y"])
    return rows


def build_label(labels_by_y, anchor_y, numeric_groups, own_y):
    other_numeric_ys = set(numeric_groups.keys())
    parts = []
    ys = [y for y in labels_by_y if abs(y - anchor_y) <= Y_LABEL_TOL]
    for y in sorted(ys):
        if any(
            abs(y - oy) <= Y_OTHER_ROW for oy in other_numeric_ys if oy != own_y
        ):
            continue
        parts.append(" ".join(tok for _, tok in sorted(labels_by_y[y])))
    return " ".join(parts).strip()


def statement_pages(path):
    doc = pymupdf.open(path)
    result = {EstadoIDs.BALANCE: [], EstadoIDs.INCOME: [], EstadoIDs.CASHFLOW: []}
    for idx in range(doc.page_count):
        text = doc[idx].get_text()
        st = detect_statement(text)
        if st not in result:
            continue
        words = doc[idx].get_text("words")
        start = data_start_y(words)
        bands = column_bands(words, start)
        if not bands:
            continue
        rows = extract_rows(words, start, bands)
        result[st].append((idx, rows))
    doc.close()
    return result


DEFAULT_FINANCIEROS = CFG.DIR_FUENTES_ESTADOS_FINANCIEROS


def find_pdf(ano, base_dir=DEFAULT_FINANCIEROS):
    folder = os.path.join(base_dir, "ESTADOS_FINANCIEROS_%d" % ano)
    cands = [
        f
        for f in glob.glob(os.path.join(folder, "*.pdf"))
        if "ESTADO" in os.path.basename(f).upper()
        and "AUDT" not in os.path.basename(f).upper()
        and "GESTION" not in os.path.basename(f).upper()
    ]
    if not cands:
        raise FileNotFoundError("No se encontro estado financiero para %d en %s" % (ano, folder))
    return sorted(cands)[0]


def show(rows, limit=None):
    out = []
    for r in rows[: (limit if limit else len(rows))]:
        out.append(
            "%7.2f | %-70s | cur=%s prev=%s"
            % (r["y"], r["label"][:70], r["cur"], r["prev"])
        )
    return "\n".join(out)


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else ""
    if not path:
        sys.exit("usage: python lectura_pdfs.py <pdf>")
    pages = statement_pages(path)
    for st, groups in pages.items():
        print("\n==== %s (%d pages) ====" % (st, len(groups)))
        for pno, rows in groups:
            print("---- page %d: %d rows ----" % (pno, len(rows)))
            print(show(rows))