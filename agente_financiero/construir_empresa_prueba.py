# -*- coding: utf-8 -*-
r"""Generador determinista del workspace de empresa de prueba (empresa_prueba_2025).

Prueba de concepto multi-empresa (2026-09-20).

Crea un workspace totalmente aislado en ``almacen_empresas\empresa_prueba_2025\``:

* ``datos_origen\``: estados financieros SINTETICOS (semilla 2025) con identidad
  contable (activo = pasivo + patrimonio) verificada por asercion en cada periodo.
* ``salidas\``: insumos del Data Mart con el mismo esquema que la entidad ancla
  (raiz del repo): ``indicadores.csv``, ``datos_estados_financieros.csv``,
  ``fase7_wacc_roi\wacc_roi_2020_2025.csv`` y
  ``fase8_evidencia_formal\evidencia_formal_conceptos.csv``.

Reglas de aislamiento:

* NO escribe nada fuera de ``almacen_empresas\empresa_prueba_2025\``.
* SOLO LEE de la entidad ancla (raiz) el catalogo universal de definiciones de
  indicadores (``salidas\indicadores.csv``) para replicar ids/familias con
  valores SINTETICOS. No se copian valores reales de la entidad.

Despues de ejecutarlo, el Data Mart se genera de forma aislada con:

    venv\Scripts\python.exe agente_financiero\fase10_powerbi_data_mart.py --empresa empresa_prueba_2025

Los ECVs y reportes historicos de la entidad ancla no se modifican.
"""

from pathlib import Path
import random

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAIZ_SALIDAS = RAIZ / "salidas"
EMPRESA = "empresa_prueba_2025"
DESTINO = RAIZ / "almacen_empresas" / EMPRESA
ORIGEN = DESTINO / "datos_origen"
SALIDAS = DESTINO / "salidas"
DIR_F7 = SALIDAS / "fase7_wacc_roi"
DIR_F8 = SALIDAS / "fase8_evidencia_formal"

PERIODOS = [2020, 2021, 2022, 2023, 2024, 2025]

RANGOS_FAMILIA = {
    "Liquidez": (0.8, 6.0),
    "Capital de trabajo y ciclo": (0.0, 70.0),
    "Rentabilidad": (0.02, 0.28),
    "Crecimiento": (-0.08, 0.25),
    "Creacion de valor y DuPont": (-0.05, 0.35),
    "Actividad y eficiencia": (0.1, 3.0),
    "Endeudamiento y solvencia": (0.25, 0.85),
    "Cobertura y capacidad de pago": (0.8, 8.0),
    "Calidad de resultados": (-0.5, 1.5),
}


def _redondear(serie):
    return [round(float(v), 6) for v in serie]


def _estados_sinteticos(rng):
    """Balance con identidad activo = pasivo + patrimonio y lineas de resultado."""
    n = len(PERIODOS)
    ac = [round(rng.uniform(115000.0, 175000.0)) for _ in range(n)]
    an = [round(rng.uniform(75000.0, 120000.0)) for _ in range(n)]
    activo = [a + b for a, b in zip(ac, an)]
    pc = [round(rng.uniform(18000.0, 32000.0)) for _ in range(n)]
    pnc = [int(v * rng.uniform(0.25, 0.6)) for v in pc]
    pasivo = [p + q for p, q in zip(pc, pnc)]
    patrimonio = [a - p for a, p in zip(activo, pasivo)]

    ingresos = [round(a * rng.uniform(0.26, 0.34)) for a in activo]
    costo = [round(i * rng.uniform(0.55, 0.72)) for i in ingresos]
    utilidad_bruta = [i - c for i, c in zip(ingresos, costo)]
    gastos = [round(i * rng.uniform(0.10, 0.18)) for i in ingresos]
    impuestos = [round(g * rng.uniform(0.18, 0.30)) for g in gastos]
    utilidad_neta = [u - g for u, g in zip(utilidad_bruta, gastos)]

    for a, p, e in zip(activo, pasivo, patrimonio):
        assert a == p + e, "Identidad contable rota en el balance sintetico"

    filas = [
        ("b_activo_corriente", "Activo corriente", "balance", "activo_corriente", ac),
        ("b_activo_no_corriente", "Activo no corriente", "balance", "activo_no_corriente", an),
        ("b_activo_total", "Activo total", "balance", "activo_total", activo),
        ("b_pasivo_corriente", "Pasivo corriente", "balance", "pasivo_corriente", pc),
        ("b_pasivo_no_corriente", "Pasivo no corriente", "balance", "pasivo_no_corriente", pnc),
        ("b_pasivo_total", "Pasivo total", "balance", "pasivo_total", pasivo),
        ("b_patrimonio_total", "Patrimonio total", "balance", "patrimonio_total", patrimonio),
        ("r_ingresos_operacionales", "Ingresos operacionales", "resultados", "ingresos", ingresos),
        ("r_costo_de_ventas", "Costo de ventas", "resultados", "costo", costo),
        ("r_utilidad_bruta", "Utilidad bruta", "resultados", "utilidad_bruta", utilidad_bruta),
        ("r_gastos_operacionales", "Gastos operacionales", "resultados", "gastos", gastos),
        ("r_impuestos", "Impuestos", "resultados", "impuestos", impuestos),
        ("r_utilidad_neta", "Utilidad neta", "resultados", "utilidad_neta", utilidad_neta),
    ]

    registros = []
    for concepto, rotulo, estado, clasif, valores in filas:
        fila = {"concepto": concepto, "rotulo": rotulo, "estado": estado, "clasificacion": clasif}
        for p, v in zip(PERIODOS, _redondear(valores)):
            fila[str(p)] = v
        registros.append(fila)
    return pd.DataFrame(registros)


def _serie_indicador(row_idx, familia, rng):
    lo, hi = RANGOS_FAMILIA.get(familia, (0.0, 1.0))
    base = rng.uniform(lo, hi)
    rango = max(hi - lo, 1e-9)
    serie = []
    for k in range(len(PERIODOS)):
        drift = rng.uniform(-0.12, 0.12) * rango
        valor = base * (1.0 + 0.06 * k) + drift
        if familia in ("Liquidez", "Rentabilidad", "Cobertura y capacidad de pago"):
            valor = max(0.0, valor)
        serie.append(round(valor, 6))
    return serie


def _indicadores_sinteticos(rng):
    catalogo = pd.read_csv(RAIZ_SALIDAS / "indicadores.csv", encoding="utf-8-sig")
    for idx in range(catalogo.shape[0]):
        familia = catalogo.loc[idx, "clasificacion"]
        serie = _serie_indicador(idx, familia, rng)
        for p, v in zip(PERIODOS, serie):
            catalogo.loc[idx, str(p)] = v
    return catalogo


def _wacc_sintetico(rng):
    registros = []
    for k, p in enumerate(PERIODOS):
        deuda = round(rng.uniform(7000.0, 11000.0), 2)
        patrimonio = round(rng.uniform(250000.0, 310000.0), 2)
        intereses = round(rng.uniform(650.0, 950.0), 2)
        costo_bruto = round(intereses / deuda, 6)
        tasas = {2020: 0.32, 2021: 0.31, 2022: 0.35, 2023: 0.35, 2024: 0.35, 2025: 0.35}
        tasa = tasas[p]
        costo_neto = round(costo_bruto * (1.0 - tasa), 6)
        prop_d = round(deuda / (deuda + patrimonio), 6)
        prop_e = round(1.0 - prop_d, 6)
        if p == 2020:
            registro = dict(periodo=p, deuda_financiera_total=deuda, patrimonio_total=patrimonio,
                            intereses_pagados_abs=intereses, costo_deuda_bruto=costo_bruto,
                            tasa_estatutaria=tasa, costo_deuda_neto=costo_neto, proporcion_deuda=prop_d,
                            proporcion_patrimonio=prop_e, roi_ke_roic=None, wacc=None,
                            estado="NO_CALCULABLE",
                            nota="Ke indisponible (ROIC requiere promedio t y t-1; sin t-1 para 2020). Dato sintetico.")
        else:
            roic = round(rng.uniform(0.55, 0.90), 6)
            registro = dict(periodo=p, deuda_financiera_total=deuda, patrimonio_total=patrimonio,
                            intereses_pagados_abs=intereses, costo_deuda_bruto=costo_bruto,
                            tasa_estatutaria=tasa, costo_deuda_neto=costo_neto, proporcion_deuda=prop_d,
                            proporcion_patrimonio=prop_e, roi_ke_roic=roic,
                            wacc=round(roic * rng.uniform(0.86, 0.97), 6), estado="ACEPTADO",
                            nota="Ke=ROIC; Kd=|intereses pagados|/deuda (dato sintetico, sin parametros externos).")
        registros.append(registro)
    cols = ["periodo", "deuda_financiera_total", "patrimonio_total", "intereses_pagados_abs",
            "costo_deuda_bruto", "tasa_estatutaria", "costo_deuda_neto", "proporcion_deuda",
            "proporcion_patrimonio", "roi_ke_roic", "wacc", "estado", "nota"]
    return pd.DataFrame(registros, columns=cols)


def _evidencia_sintetica(estados):
    registros = []
    for _, fila in estados.iterrows():
        concepto = fila["concepto"]
        rotulo = fila["rotulo"]
        estado = fila["estado"]
        for p in PERIODOS:
            valor = float(fila[str(p)])
            registros.append(dict(
                anio=p, concepto=concepto, rotulo=rotulo,
                documento_origen="Estados Sinteticos.pdf", estado_financiero=estado,
                pagina=1, nota="", evidencia_linea=f"Sintetico $ {valor:.0f}",
                valor_pdf=round(valor, 2), valor_consolidado=round(valor, 2),
                coincide=True, estado="ACEPTADO", confianza="ALTA"))
    cols = ["anio", "concepto", "rotulo", "documento_origen", "estado_financiero", "pagina",
            "nota", "evidencia_linea", "valor_pdf", "valor_consolidado", "coincide", "estado", "confianza"]
    return pd.DataFrame(registros, columns=cols)


def _escribir_readme():
    contenido = f"""# Workspace de empresa de prueba: {EMPRESA}

Prueba de concepto multi-empresa (2026-09-20). Datos 100 % SINTETICOS
(semilla 2025) generados por `agente_financiero\\construir_empresa_prueba.py`.

## Estructura

- `datos_origen\\estados_financieros_sinteticos.csv` -- estados SINTETICOS
  2020-2025 con identidad contable verificada (activo = pasivo + patrimonio).
- `salidas\\` -- insumos del Data Mart con el mismo esquema que la entidad
  ancla: `indicadores.csv`, `datos_estados_financieros.csv`,
  `fase7_wacc_roi\\wacc_roi_2020_2025.csv`,
  `fase8_evidencia_formal\\evidencia_formal_conceptos.csv`.

## Aislamiento

- Ningun archivo de la entidad ancla (raiz `salidas\\`) se modifica.
- El Data Mart se genera en `salidas\\power_bi\\` de ESTE workspace:

  ```
  venv\\Scripts\\python.exe agente_financiero\\fase10_powerbi_data_mart.py --empresa {EMPRESA}
  ```

## Trazabilidad

- Origen: generador deterministico (semilla 2025).
- Estado: SINTETICO / prueba. No corresponde a ninguna entidad real.
"""
    (ORIGEN / "README_EMPRESA_PRUEBA.md").write_text(contenido, encoding="utf-8")


def main():
    ORIGEN.mkdir(parents=True, exist_ok=True)
    SALIDAS.mkdir(parents=True, exist_ok=True)
    DIR_F7.mkdir(parents=True, exist_ok=True)
    DIR_F8.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2025)

    estados = _estados_sinteticos(rng)
    estados.to_csv(ORIGEN / "estados_financieros_sinteticos.csv", index=False, encoding="utf-8-sig")
    estados.to_csv(SALIDAS / "datos_estados_financieros.csv", index=False, encoding="utf-8-sig")

    indicadores = _indicadores_sinteticos(rng)
    indicadores.to_csv(SALIDAS / "indicadores.csv", index=False, encoding="utf-8-sig")

    wacc = _wacc_sintetico(rng)
    wacc.to_csv(DIR_F7 / "wacc_roi_2020_2025.csv", index=False, encoding="utf-8-sig")

    evidencia = _evidencia_sintetica(estados)
    evidencia.to_csv(DIR_F8 / "evidencia_formal_conceptos.csv", index=False, encoding="utf-8-sig")

    _escribir_readme()

    print(f"== WORKSPACE SINTETICO GENERADO: {DESTINO} ==")
    print(f"estados filas: {estados.shape[0]} x periodos {PERIODOS}")
    print(f"indicadores: {indicadores.shape[0]} (catalogo id 1-{indicadores.shape[0]})")
    print(f"wacc filas: {wacc.shape[0]}; evidencia filas: {evidencia.shape[0]}")
    print("identidad contable: OK (assert)")


if __name__ == "__main__":
    main()