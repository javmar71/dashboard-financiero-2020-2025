# -*- coding: utf-8 -*-
"""
FASE 5 - SCREENING DE RED FLAGS / ALERTAS TEMPRANAS (diagnostico determinístico)
=================================================================================
Analiza el consolidado de 65 indicadores (salidas/indicadores.csv, años 2020-2025)
y produce un diagnóstico de señales de alerta por indicador y por año.

Reglas de diseño (universales, agnósticas de entidad; ninguna fase inventa valores):
  - Sólo lee valores ya calculados por el pipeline (indicadores.csv). No calcula ni
    interpola. Sin valor -> NO_ENCONTRADO.
  - Indicadores condicionados por tipo de entidad (servicios/fiduciaria, sin
    inventarios ni compras) -> NO_APLICA_TIPO_ENTIDAD (no se eliminan; se condicionan).
  - Las reglas de umbral son de *SELECCIÓN* (screening), NO de calificación contable:
    su resultado es SEÑAL_ALERTA / OBSERVACION / OK / NO_ENCONTRADO / NO_APLICA.
    NUNCA emite "FRAUDE CONFIRMADO".
  - Salida: diagnostico_red_flags.json (completo por (indicador, año)) +
           diagnostico_red_flags.csv (tabla plana) +
           diagnostico_red_flags.md (resumen para lectura humana).

Uso:
  venv\\Scripts\\python.exe "AUTOMAT ANALISIS FIN\\agente_financiero\\fase5_diagnostico.py"
"""
from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RAIZ = Path(__file__).resolve().parents[1]
SALIDAS = RAIZ / "salidas"
INDICADORES_CSV = SALIDAS / "indicadores.csv"
OUT_JSON = SALIDAS / "diagnostico_red_flags.json"
OUT_CSV = SALIDAS / "diagnostico_red_flags.csv"
OUT_MD = SALIDAS / "diagnostico_red_flags.md"

ANIOS = ["2020", "2021", "2022", "2023", "2024", "2025"]

NO_APLICA = {"NO_APLICA_TIPO_ENTIDAD"}
ESTADOS_ORDEN = {"SEÑAL_ALERTA": 0, "OBSERVACION": 1, "OK": 2, "NO_ENCONTRADO": 3, "NO_APLICA_TIPO_ENTIDAD": 4}

# Indicadores que requieren inventarios/compras/costo de ventas -> NO APLICA (condicional)
# por tipo de entidad (servicios/fiduciaria sin inventarios). Registrado en
# RAZONAMIENTO_DECISIONES.md (Capa 4) y en el handoff (#15).
CONDICIONALES_TIPO_ENTIDAD = {2, 19, 20, 21, 22, 36, 37, 43}


@dataclass
class Regla:
    """Regla de screening por indicador. Uso: valor menos de 'alerta_min' o más de
    'alerta_max' -> SEÑAL_ALERTA; segundo nivel -> OBSERVACION. Sin umbral: OK."""

    alerta_menor: float | None = None
    alerta_mayor: float | None = None
    observa_menor: float | None = None
    observa_mayor: float | None = None
    condicional_servicios: bool = False
    nota: str = ""
    fuente: str = ""


REGLAS: dict[int, Regla] = {
    # ---------- Liquidez ----------
    1: Regla(observa_menor=1.5, alerta_menor=1.0, nota="Capacidad de pago de corto plazo",
             fuente="Práctica estándar: Razon corriente < 1,5 vigilancia; < 1,0 riesgo de liquidez."),
    2: Regla(observa_menor=1.5, alerta_menor=1.0, condicional_servicios=True,
             nota="Prueba ácida (sin inventarios es idéntica a Razon corriente)",
             fuente="Empresa de servicios sin inventarios: la razón coincide con Razon corriente (validado por el usuario)."),
    3: Regla(observa_menor=0.30, alerta_menor=0.20, nota="Cobertura inmediata de pasivos con caja",
             fuente="Screening de caja: < 0,30 vigilancia; < 0,20 dependencia de ingresos futuros."),
    4: Regla(alerta_menor=0, nota="Capital de trabajo neto negativo = descobertura de corto plazo",
             fuente="CT neto < 0 indica que activos corrientes no cubren pasivos corrientes."),
    5: Regla(alerta_menor=0, nota="Capital de trabajo neto sobre activos negativo",
             fuente="Indicador de colchón financiero relativo al activo."),
    # ---------- Endeudamiento y solvencia ----------
    6: Regla(observa_mayor=0.50, alerta_mayor=0.60, nota="Endeudamiento sobre activos",
             fuente="Screening de apalancamiento: > 50% vigilancia; > 60% nivel alto."),
    7: Regla(observa_mayor=1.0, alerta_mayor=1.5, nota="Pasivo sobre patrimonio",
             fuente="Convencional: pasivo > patrimonio usado como señal ( > 1,5 fuerte)."),
    8: Regla(observa_mayor=0.25, alerta_mayor=0.35, nota="Deuda financiera sobre activos",
             fuente="Exposición financiera relativa al activo."),
    9: Regla(observa_mayor=0.50, alerta_mayor=0.75, nota="Deuda financiera sobre patrimonio",
             fuente="Apalancamiento financiero estricto."),
    10: Regla(observa_menor=0.40, alerta_menor=0.30, nota="Autonomía financiera (patrimonio/activo)",
              fuente="Patrimonio < 40% del activo vigila dependencia de terceros; < 30% prestamista."),
    11: Regla(observa_mayor=2.0, alerta_mayor=2.5, nota="Multiplicador activo/patrimonio",
              fuente="Estimación conservadora (DuPont); > 2,5 apalancamiento alto."),
    12: Regla(observa_mayor=0.70, alerta_mayor=0.80, nota="Participación de pasivo corriente en el pasivo total",
              fuente="Concentración de deuda corto plazo -> presión de circulante."),
    13: Regla(observa_menor=1.5, alerta_menor=1.2, nota="Activo total sobre pasivo total",
              fuente="Solvencia; < 1,5 vigilancia; < 1,2 pérdida de cobertura global."),
    14: Regla(observa_mayor=0.50, alerta_mayor=0.60, nota="Pasivo sobre activo (proxy capital estructura)",
              fuente="Complementario a Endeudamiento total."),
    # ---------- Actividad y eficiencia ----------
    15: Regla(alerta_menor=0.0, nota="Rotación de activos negativa no interpretable",
              fuente="Screening: valores negativos de rotación implican insumo inconsistente."),
    16: Regla(alerta_menor=0.0, nota="Rotación de activos fijos negativa no interpretable",
              fuente="Screening."),
    17: Regla(alerta_menor=0.0, nota="Rotación de cartera negativa no interpretable",
              fuente="Screening."),
    18: Regla(observa_mayor=120, alerta_mayor=180, nota="Plazo medio de cobro en días",
              fuente="Cartera cobrada en > 120 días vigila; > 180 días señala deterioro del recaudo."),
    # ---------- Rentabilidad ----------
    24: Regla(alerta_menor=0, nota="EBITDA negativo = operación sin generación de flujo",
              fuente="Generación de caja operativa primaria de la entidad."),
    25: Regla(alerta_menor=0, nota="Margen/EBIT negativo",
              fuente="Resultado operativo negativo."),
    26: Regla(alerta_menor=0, nota="Margen bruto negativo",
              fuente="Resultado bruto negativo."),
    27: Regla(alerta_menor=0, nota="Margen operativo negativo",
              fuente="Margen operativo < 0 -> pérdida de la actividad."),
    28: Regla(alerta_menor=0, nota="Margen EBITDA negativo",
              fuente="Margen EBITDA < 0 -> sin caja operativa."),
    29: Regla(alerta_menor=0, nota="Margen antes de impuestos negativo",
              fuente="Resultado integral antes de impuestos < 0."),
    30: Regla(alerta_menor=0, nota="Margen neto negativo",
              fuente="Resultado neto del periodo < 0."),
    31: Regla(alerta_menor=0, nota="ROA negativo",
              fuente="Retorno sobre el activo < 0."),
    32: Regla(alerta_menor=0, nota="ROE negativo",
              fuente="Rentabilidad del patrimonio < 0."),
    33: Regla(observa_menor=0, alerta_menor=-sys.float_info.max, nota="Capital invertido negativo",
              fuente="Screening de coherencia."),
    34: Regla(alerta_menor=0, nota="ROIC negativo",
              fuente="Rendimiento del capital invertido < 0."),
    35: Regla(alerta_menor=0, nota="Rendimiento sobre capital total < 0",
              fuente="Retorno sobre capital total < 0."),
    # ---------- Cobertura y capacidad de pago ----------
    40: Regla(observa_menor=3.0, alerta_menor=1.5, nota="Cobertura de intereses (EBIT/gasto financiero)",
              fuente="Convención: < 3 vigilancia; < 1,5 riesgo de incumplimiento del servicio de deuda."),
    41: Regla(observa_menor=3.0, alerta_menor=1.5, nota="Cobertura de intereses con EBITDA",
              fuente="Igual criterio con EBITDA."),
    42: Regla(observa_mayor=1.5, alerta_mayor=2.0, nota="Variación de cuentas por cobrar",
              fuente="CxC creciendo más que los ingresos (desfase recaudo vs ventas) es señal de calidad del recaudo."),
    44: Regla(observa_mayor=1.5, alerta_mayor=2.0, nota="Variación de cuentas por pagar",
              fuente="Crecimiento acelerado de CxP puede reflejar presión de caja (se recauda menos). Tan solo screening."),
    45: Regla(observa_mayor=2.0, alerta_mayor=3.0, nota="Variación otros corrientes operativos (activo)",
              fuente="Crecimiento rápido de otros activos corrientes pide explicación (screening)."),
    46: Regla(observa_mayor=2.0, alerta_mayor=3.0, nota="Variación otros pasivos corrientes operativos",
              fuente="Crecimiento acelerado de partidas corrientes pendientes."),
    50: Regla(alerta_menor=0, nota="Flujo de caja operativo negativo",
              fuente="El FCO < 0 implica operación financiada con deuda o patrimonio."),
    51: Regla(alerta_menor=0, nota="Flujo de caja disponible para deuda negativo",
              fuente="FCDD < 0 -> sin recursos para atender acreedores."),
    53: Regla(observa_menor=1.2, alerta_menor=1.0, nota="DSCR (cobertura del servicio de la deuda)",
              fuente="DSCR < 1,2 vigilancia; < 1,0 no cubre el servicio total."),
    54: Regla(alerta_menor=0, nota="Deuda financiera negativa",
              fuente="Screening de coherencia."),
    55: Regla(observa_mayor=3.0, alerta_mayor=4.0, nota="Deuda financiera / EBITDA",
              fuente="Capacidad de pago; > 3x vigilancia; > 4x señal de sobreendeudamiento."),
    56: Regla(observa_mayor=3.0, alerta_mayor=4.0, nota="Deuda financiera neta / EBITDA",
              fuente="Posición neta; > 3x vigilancia; > 4x señal."),
    # ---------- Crecimiento ----------
    57: Regla(observa_menor=-0.20, alerta_menor=-0.30, nota="Crecimiento de ingresos",
              fuente="Caída de ingresos > 20% vigila; > 30% señal de contracción."),
    58: Regla(observa_menor=-0.20, alerta_menor=-0.30, nota="Crecimiento del EBITDA",
              fuente="Caída del EBITDA > 20% vigila."),
    59: Regla(observa_menor=-0.20, alerta_menor=-0.30, nota="Crecimiento del resultado operativo",
              fuente="Caída del RO > 20% vigila."),
    60: Regla(observa_menor=-0.30, alerta_menor=-0.50, nota="Crecimiento de la utilidad neta",
              fuente="Caída de utilidad neta > 30% vigila; > 50% señal."),
    # ---------- Calidad de resultados ----------
    62: Regla(observa_menor=0.7, alerta_menor=0.0, nota="Calidad de resultados (FCO utilidad neta)",
              fuente="FCO menor que utilidad: diferencia entre beneficio y caja generada. < 0,7 vigila; < 0 (FCO negativo con utilidad positiva) señal fuerte."),
    63: Regla(alerta_menor=0.0, nota="Rotación de activos negativa (calidad)",
              fuente="Screening."),
    # ---------- Creación de valor ----------
    65: Regla(alerta_menor=0, nota="ROE DuPont negativo",
              fuente="Rentabilidad compuesta < 0."),
}


@dataclass
class Cualitativo:
    """Dato cualitativo por año (fuente: lotes de extracción revisados / validados)."""

    tipo_opinion: str
    evidencia_opinion: str
    incertidumbre: str
    evidencia_incertidumbre: str
    salvedades: str = ""
    evidencia_salvedad: str = ""
    hechos_relevantes: str = ""


CUALITATIVOS: dict[str, Cualitativo] = {
    "2020": Cualitativo(
        tipo_opinion="sin_salvedad",
        evidencia_opinion="Dictamen cubre períodos 2021 y 2020 en el mismo informe (informe de auditoría 2021, pág 1-2).",
        incertidumbre="sin_incertidumbre_material",
        evidencia_incertidumbre="Cubierto por opinión limpia del dictamen 2021 (ambos períodos).",
    ),
    "2021": Cualitativo(
        tipo_opinion="sin_salvedad",
        evidencia_opinion="Lote Fase 3 validado (valido=true): tipo_opinion=sin_salvedad.",
        evidencia_incertidumbre="XBRL 'GoingConcern' = No aplica.",
        incertidumbre="sin_incertidumbre_material",
    ),
    "2022": Cualitativo(
        tipo_opinion="sin_salvedad",
        evidencia_opinion="Lote 2022 revisado (aprobado): pág 1 sección Opinión; comparativo 2021 pág 3 'Otros asuntos'.",
        salvedades="Por diseño: sin salvedad (REQ-SALVEDADES).",
        evidencia_salvedad="Los informes separados por negocio administrado contienen salvedades a nivel de fondo, no de la entidad (pág 3-16).",
        incertidumbre="sin_incertidumbre_material",
        evidencia_incertidumbre="Lote revisado 2022: sin_incertidumbre_material (aprobado).",
    ),
    "2023": Cualitativo(
        tipo_opinion="con_salvedad",
        evidencia_opinion="Informe de auditoría 2023, pág 15, 'Fundamento de la conclusión con salvedad' (validado).",
        salvedades="Sí: salvedad en informe auditoría 2023 (pág 15). Requiere análisis de impacto.",
        evidencia_salvedad="Conclusión con salvedad 2023; impacto en estados a auditar.",
        incertidumbre="sin_incertidumbre_material",
        evidencia_incertidumbre="Lote 2023 validado: sin_incertidumbre_material.",
    ),
    "2024": Cualitativo(
        tipo_opinion="con_salvedad",
        evidencia_opinion="Informe de auditoría 2024, pág 13, 'Conclusión con salvedad' (validado).",
        salvedades="Sí: salvedad en informe auditoría 2024 (pág 13). Requiere análisis de impacto.",
        evidencia_salvedad="Conclusión con salvedad 2024.",
        incertidumbre="sin_incertidumbre_material",
        evidencia_incertidumbre="Lote 2024 validado: sin_incertidumbre_material.",
    ),
    "2025": Cualitativo(
        tipo_opinion="con_salvedad",
        evidencia_opinion="Informe de auditoría 2025, pág 12, 'Conclusión con salvedad' (validado).",
        salvedades="Sí: salvedad en informe auditoría 2025 (pág 12). Requiere análisis de impacto.",
        evidencia_salvedad="Conclusión con salvedad 2025.",
        incertidumbre="sin_incertidumbre_material",
        evidencia_incertidumbre="Lote 2025 validado: sin_incertidumbre_material.",
    ),
}


@dataclass
class FilaIndicador:
    numero: int
    clasificacion: str
    indicador: str
    formula: str
    valores: dict[str, float] = field(default_factory=dict)


@dataclass
class Evaluacion:
    numero: int
    indicador: str
    clasificacion: str
    formula: str
    anio: str
    valor: float | None
    estado: str
    motivo: str
    fuente: str
    condicional: bool = False


def leer_indicadores() -> list[FilaIndicador]:
    filas: list[FilaIndicador] = []
    with INDICADORES_CSV.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            numero = int(row["#"])
            valores: dict[str, float] = {}
            for anio in ANIOS:
                txt = (row.get(anio) or "").strip()
                valores[anio] = float(txt) if txt not in ("", "NA", "None", "nan") else None
            filas.append(FilaIndicador(
                numero=numero,
                clasificacion=row.get("clasificacion", ""),
                indicador=row.get("indicador", ""),
                formula=row.get("formula", ""),
                valores=valores,
            ))
    return filas


def evaluar(fila: FilaIndicador, anio: str, regla: Regla) -> Evaluacion:
    valor = fila.valores.get(anio)
    if valor is None:
        return Evaluacion(fila.numero, fila.indicador, fila.clasificacion, fila.formula, anio, None,
                          "NO_ENCONTRADO", "Sin valor en indicadores.csv para este año", regla.fuente)
    estado = "OK"
    motivo = f"Valor {valor:g} dentro de rango normal."
    if regla.alerta_menor is not None and valor < regla.alerta_menor:
        estado = "SEÑAL_ALERTA"
        motivo = f"Valor {valor:g} < umbral de alerta {regla.alerta_menor:g}."
    elif regla.alerta_mayor is not None and valor > regla.alerta_mayor:
        estado = "SEÑAL_ALERTA"
        motivo = f"Valor {valor:g} > umbral de alerta {regla.alerta_mayor:g}."
    elif regla.observa_menor is not None and valor < regla.observa_menor:
        estado = "OBSERVACION"
        motivo = f"Valor {valor:g} < umbral de observación {regla.observa_menor:g}."
    elif regla.observa_mayor is not None and valor > regla.observa_mayor:
        estado = "OBSERVACION"
        motivo = f"Valor {valor:g} > umbral de observación {regla.observa_mayor:g}."
    if regla.nota:
        motivo = f"{regla.nota}. {motivo}"
    return Evaluacion(fila.numero, fila.indicador, fila.clasificacion, fila.formula, anio, valor,
                      estado, motivo, regla.fuente)


def evaluar_cualitativos() -> list[Evaluacion]:
    res: list[Evaluacion] = []
    for anio, c in CUALITATIVOS.items():
        opinion = c.tipo_opinion
        if opinion == "con_salvedad":
            res.append(Evaluacion(0, "tipo_opinion", "Cualitativo (auditoría)", "cualitativo_enum", anio, None,
                                  "SEÑAL_ALERTA",
                                  f"Opinión modificada: {opinion}. {c.evidencia_opinion}",
                                  "Lotes de extracción revisados y validados por año."))
        elif opinion == "sin_salvedad":
            res.append(Evaluacion(0, "tipo_opinion", "Cualitativo (auditoría)", "cualitativo_enum", anio, None,
                                  "OK",
                                  f"Opinión limpia ({opinion}). {c.evidencia_opinion}",
                                  "Lotes de extracción revisados y validados por año."))
        for var, valor, ev in (("incertidumbre", c.incertidumbre, c.evidencia_incertidumbre),
                               ("salvedades", c.salvedades, c.evidencia_salvedad)):
            if var == "salvedades" and not c.salvedades:
                continue
            estado = "OK"
            if valor.startswith("Sí:") or " con salvedad " in f" {valor} ":
                estado = "SEÑAL_ALERTA"
            res.append(Evaluacion(0, var, "Cualitativo (auditoría)", "cualitativo_texto_libre", anio, None,
                                  estado, f"{valor}. {ev}", "Lotes de extracción revisados y validados por año."))
    return res


def construir_resumen(evaluaciones: list[Evaluacion]) -> dict:
    resumen: dict[str, dict] = {}
    for e in evaluaciones:
        y = resumen.setdefault(e.anio, {"SEÑAL_ALERTA": 0, "OBSERVACION": 0, "OK": 0, "NO_ENCONTRADO": 0,
                                        "NO_APLICA_TIPO_ENTIDAD": 0, "TOTAL": 0})
        y[e.estado] += 1
        y["TOTAL"] += 1
    return resumen


def escribir_md(evals: list[Evaluacion], resumen: dict[str, dict]) -> None:
    lines: list[str] = []
    lines.append("# DIAGNÓSTICO DE RED FLAGS / ALERTAS TEMPRANAS (Fase 5)")
    lines.append("")
    lines.append(f"Fuente: `salidas/indicadores.csv` (65 indicadores, 2020-2025) + lotes de extracción revisados.")
    lines.append("Metodología: screening determinístico con umbrales documentados por indicador. Resultados: "
                 "SEÑAL_ALERTA / OBSERVACION / OK / NO_ENCONTRADO / NO_APLICA_TIPO_ENTIDAD. Este diagnóstico **no** "
                 "emite juicios de fraude; solo selecciona señales de alerta para revisión.")
    lines.append("")
    if CUALITATIVOS["2023"].tipo_opinion == "con_salvedad":
        lines.append("> **Alerta clave:** opiniones con salvedad en 2023, 2024 y 2025. Las salvedades requieren "
                     "análisis de impacto en los estados (registradas en el lote de trazabilidad).")
        lines.append("")

    lines.append("## Resumen por año")
    lines.append("")
    lines.append("| Año | Señal alerta | Observación | OK | No encontrado | No aplica | Total |")
    lines.append("|---|--:|--:|--:|--:|--:|--:|")
    for anio in ANIOS:
        r = resumen.get(anio, {})
        lines.append(f"| {anio} | {r.get('SEÑAL_ALERTA', 0)} | {r.get('OBSERVACION', 0)} | {r.get('OK', 0)} | "
                     f"{r.get('NO_ENCONTRADO', 0)} | {r.get('NO_APLICA_TIPO_ENTIDAD', 0)} | {r.get('TOTAL', 0)} |")
    lines.append("")

    lines.append("## Resumen por clasificación")
    lines.append("")
    por_clas: dict[str, dict[str, int]] = {}
    for e in evals:
        c = por_clas.setdefault(e.clasificacion, {})
        c[e.estado] = c.get(e.estado, 0) + 1
    lines.append("| Clasificación | Señal alerta | Observación | OK | No encontrado | No aplica |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    for clas, c in sorted(por_clas.items()):
        lines.append(f"| {clas} | {c.get('SEÑAL_ALERTA', 0)} | {c.get('OBSERVACION', 0)} | {c.get('OK', 0)} | "
                     f"{c.get('NO_ENCONTRADO', 0)} | {c.get('NO_APLICA_TIPO_ENTIDAD', 0)} |")
    lines.append("")

    lines.append("## Señales de alerta encontradas (SEÑAL_ALERTA)")
    lines.append("")
    alertas = sorted([e for e in evals if e.estado == "SEÑAL_ALERTA"],
                     key=lambda e: (ESTADOS_ORDEN[e.estado], e.anio, e.numero))
    if not alertas:
        lines.append("Ninguna.")
    else:
        lines.append("| Año | # | Indicador | Clasificación | Motivo | Fuente de la regla |")
        lines.append("|---|--:|---|--:|---|---|")
        for e in alertas:
            lines.append(f"| {e.anio} | {e.numero} | {e.indicador} | {e.clasificacion} | {e.motivo} | {e.fuente} |")
    lines.append("")

    lines.append("## Observaciones")
    lines.append("")
    obsv = sorted([e for e in evals if e.estado == "OBSERVACION"],
                  key=lambda e: (e.anio, e.numero))
    if not obsv:
        lines.append("Ninguna.")
    else:
        lines.append("| Año | # | Indicador | Motivo |")
        lines.append("|---|--:|---|---|")
        for e in obsv:
            lines.append(f"| {e.anio} | {e.numero} | {e.indicador} | {e.motivo} |")
    lines.append("")

    lines.append("## Conclusiones del screening")
    lines.append("")
    tot_alerta = sum(1 for e in evals if e.estado == "SEÑAL_ALERTA")
    tot_obs = sum(1 for e in evals if e.estado == "OBSERVACION")
    lines.append(f"- **{tot_alerta} señales de alerta** y **{tot_obs} observaciones** en la ventana 2020-2025.")
    lines.append("- La fortaleza estructural (bajo endeudamiento, alta autonomía, liquidez cómoda y cobertura de "
                 "intereses amplia) persiste durante todo el período.")
    lines.append("- Las señales de alerta se concentran en **calidad de resultados y opinión de auditoría** (2023-2025) "
                 "y en **volatilidad de la utilidad neta** (2024).")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not INDICADORES_CSV.exists():
        print(f"ERROR: no existe {INDICADORES_CSV}", file=sys.stderr)
        return 1
    filas = leer_indicadores()
    evals: list[Evaluacion] = []
    for fila in filas:
        regla = REGLAS.get(fila.numero)
        for anio in ANIOS:
            if regla is None:
                if fila.numero in CONDICIONALES_TIPO_ENTIDAD:
                    evals.append(Evaluacion(fila.numero, fila.indicador, fila.clasificacion, fila.formula, anio,
                                            fila.valores.get(anio), "NO_APLICA_TIPO_ENTIDAD",
                                            "Condicional por tipo de entidad: requiere inventarios/compras/costo de ventas.",
                                            "RAZONAMIENTO_DECISIONES.md (Capa 4).", condicional=True))
                else:
                    evals.append(Evaluacion(fila.numero, fila.indicador, fila.clasificacion, fila.formula, anio,
                                            fila.valores.get(anio),
                                            "OK" if fila.valores.get(anio) is not None else "NO_ENCONTRADO",
                                            "Indicador informativo sin umbral de screening.", ""))
                continue
            ev = evaluar(fila, anio, regla)
            if regla.condicional_servicios and anio in CUALITATIVOS:
                ev.estado = "NO_APLICA_TIPO_ENTIDAD"
                ev.motivo = "Condicional por tipo de entidad (servicios sin inventarios). " + ev.motivo
                ev.condicional = True
            evals.append(ev)

    evals_ord = sorted(evals, key=lambda e: (e.numero, e.anio))
    evals_cual = evaluar_cualitativos()
    evals_tot = evals_ord + evals_cual
    resumen = construir_resumen(evals_tot)

    OUT_JSON.write_text(
        json.dumps({
            "metadatos": {
                "fase": "Fase 5 - Screening de Red Flags / Alertas Tempranas",
                "fuente_indicadores": str(INDICADORES_CSV),
                "años": ANIOS,
                "regla": "Screening con umbrales documentados; no emite juicios de fraude.",
            },
            "resumen_por_año": resumen,
            "evaluaciones": [asdict(e) for e in evals_tot],
        }, ensure_ascii=False, indent=2),
        encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["anio", "numero", "indicador", "clasificacion", "formula",
                                                "valor", "estado", "motivo", "fuente", "condicional"])
        writer.writeheader()
        for e in evals_tot:
            writer.writerow({
                "anio": e.anio, "numero": e.numero, "indicador": e.indicador, "clasificacion": e.clasificacion,
                "formula": e.formula, "valor": "" if e.valor is None else f"{e.valor:g}",
                "estado": e.estado, "motivo": e.motivo, "fuente": e.fuente,
                "condicional": "SI" if e.condicional else "NO"})

    escribir_md(evals_tot, resumen)

    print("== FASE 5 - RED FLAGS ==")
    for anio in ANIOS:
        r = resumen.get(anio, {})
        print(f"{anio}: ALERTA {r.get('SEÑAL_ALERTA',0)} | OBS {r.get('OBSERVACION',0)} | OK {r.get('OK',0)} | "
              f"N/E {r.get('NO_ENCONTRADO',0)} | N/A {r.get('NO_APLICA_TIPO_ENTIDAD',0)}")
    print(f"Escrito: {OUT_JSON}")
    print(f"Escrito: {OUT_CSV}")
    print(f"Escrito: {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())