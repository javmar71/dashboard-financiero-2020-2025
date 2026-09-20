#!/usr/bin/env python3
"""
Módulo auditor_lote_extraccion.py
PASO 3.4 — Auditoría del JSON de extracción IA (por LOTE)

Responsabilidad: auditar un LOTE de registros de extracción (salidas del esquema
`esquema_extraccion_ia.json` v3) y reportar:

  1. Cobertura: de las N variables IA-searchable × P periodos esperados, cuántos
     objetivos (variable, periodo) tienen resultado y cuántos faltan.
  2. Distribución de `estado` (ACEPTADO/DUDOSO/NO_ENCONTRADO/INCONSISTENTE) y de
     `confianza`.
  3. Registros que requieren revisión humana: todo DUDOSO, todo NO_ENCONTRADO,
     todo INCONSISTENTE, y ACEPTADO con confianza distinta de ALTA.
  4. Duplicados e inconsistencias en la pareja `(variable_madre_id, periodo)`.

Reutiliza la validación oficial (`validador_extraccion.py`) para reportar errores
de esquema y determinísticos del lote. No genera extracción ni modifica datos.

Uso CLI:
    python auditor_lote_extraccion.py archivo1.json [archivo2.json ...]
        [--periodos 2021 2020] [--csv taxonomia_variable_madre.csv] [--json salida.json]
"""

import argparse
import csv
import json
import pathlib
from typing import Any, Dict, List, Optional, Sequence, Set

import validador_extraccion

DIRECTORIO = pathlib.Path(__file__).parent
CSV_POR_DEFECTO = DIRECTORIO / 'taxonomia_variable_madre.csv'
PERIODOS_POR_DEFECTO = ('2021', '2020')
FUENTES_IA = {'notas', 'informe_gestion', 'informe_auditoria'}
ESTADOS = ('ACEPTADO', 'DUDOSO', 'NO_ENCONTRADO', 'INCONSISTENTE')
CONFIANZAS = ('ALTA', 'MEDIA', 'BAJA', 'NO_DETERMINADA')


def cargar_variables_ia(ruta_csv: Optional[Any] = None) -> List[str]:
    """Devuelve los `variable_madre_id` IA-searchable (tipo_variable primaria y fuente IA)."""
    ruta = pathlib.Path(ruta_csv) if ruta_csv else CSV_POR_DEFECTO
    variables = []
    with open(ruta, encoding='utf-8-sig') as f:
        for fila in csv.DictReader(f):
            if fila['tipo_variable'] == 'primaria' and fila['fuente_esperada'] in FUENTES_IA:
                variables.append(fila['variable_madre_id'])
    return sorted(set(variables))


def cargar_reglas_diseno(ruta_csv: Optional[Any] = None) -> Dict[str, Dict[str, str]]:
    """
    Devuelve {variable: {campo_condicion, valor_condicion}} desde la columna
    `regla_diseno` de la taxonomía. Formato: "condicion:<variable>=<valor>".

    Ejemplo: salvedades → condicion:tipo_opinion=sin_salvedad  (significa: para esa
    variable, NO_ENCONTRADO es el resultado esperado cuando `tipo_opinion` tiene ese
    valor; solo alerta si la condición documentada se viola).
    """
    ruta = pathlib.Path(ruta_csv) if ruta_csv else CSV_POR_DEFECTO
    reglas: Dict[str, Dict[str, str]] = {}
    if not ruta.exists():
        return reglas
    with open(ruta, encoding='utf-8-sig') as f:
        for fila in csv.DictReader(f):
            regla = (fila.get('regla_diseno') or '').strip()
            if regla.startswith('condicion:'):
                expr = regla[len('condicion:'):]
                if '=' in expr:
                    campo, valor = expr.split('=', 1)
                    reglas[fila['variable_madre_id']] = {
                        'campo_condicion': campo.strip(),
                        'valor_condicion': valor.strip(),
                    }
    return reglas


def cargar_registros(rutas: Sequence[Any]) -> List[Dict[str, Any]]:
    """Carga y concatena registros desde varios JSON (lista directa o `{"datos":[...]}`)."""
    registros: List[Dict[str, Any]] = []
    for ruta in rutas:
        with open(ruta, encoding='utf-8') as f:
            contenido = json.load(f)
        if isinstance(contenido, dict) and isinstance(contenido.get('datos'), list):
            registros.extend(contenido['datos'])
        elif isinstance(contenido, list):
            registros.extend(contenido)
        else:
            registros.append(contenido)
    return registros


def _clave(registro: Dict[str, Any]):
    return (registro.get('variable_madre_id'), registro.get('periodo'))


def auditar(
    registros: List[Dict[str, Any]],
    variables_esperadas: Sequence[str],
    periodos_esperados: Sequence[str] = PERIODOS_POR_DEFECTO,
    esquema: Optional[Dict[str, Any]] = None,
    reglas_diseno: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Ejecuta la auditoría del lote y devuelve el reporte como diccionario."""
    variables_esperadas = list(variables_esperadas)
    periodos_esperados = [str(p) for p in periodos_esperados]
    esperados = {(v, p) for v in variables_esperadas for p in periodos_esperados}

    con_periodo = [r for r in registros if r.get('periodo') is not None]
    sin_periodo = [r for r in registros if r.get('periodo') is None]
    presentes = {(r.get('variable_madre_id'), str(r.get('periodo'))) for r in con_periodo}
    cubiertos = esperados & presentes
    faltantes = esperados - presentes

    distribucion_estado = {e: 0 for e in ESTADOS}
    distribucion_confianza = {c: 0 for c in CONFIANZAS}
    extra: Dict[str, int] = {}
    for r in registros:
        est = r.get('estado')
        if est in distribucion_estado:
            distribucion_estado[est] += 1
        else:
            extra[str(est)] = extra.get(str(est), 0) + 1
        conf = r.get('confianza')
        if conf in distribucion_confianza:
            distribucion_confianza[conf] += 1
        else:
            extra[str(conf)] = extra.get(str(conf), 0) + 1

    reglas_diseno = reglas_diseno if reglas_diseno is not None else cargar_reglas_diseno()
    # valores efectivos de las variables condicionantes para evaluar reglas de diseño
    valores_por_variable: Dict[str, List[Any]] = {}
    for r in registros:
        valores_por_variable.setdefault(r.get('variable_madre_id'), []).append(r.get('valor'))

    def condicion_diseno_satisfecha(r, regla):
        """True si la condición documentada (NO_ENCONTRADO esperado por diseño) se cumple."""
        campo = regla['campo_condicion']
        valor = regla['valor_condicion']
        candidatos = [v for v in valores_por_variable.get(campo, []) if v is not None]
        return valor in candidatos

    # mapa {indice: motivo} con reglas de diseño aplicadas
    confirmados_diseno: List[Dict[str, Any]] = []
    motivo_final: Dict[int, Optional[str]] = {}
    for i, r in enumerate(registros):
        est = r.get('estado')
        base = None
        if est == 'DUDOSO':
            base = 'DUDOSO'
        elif est == 'NO_ENCONTRADO':
            regla = reglas_diseno.get(r.get('variable_madre_id'))
            if regla is not None and condicion_diseno_satisfecha(r, regla):
                confirmados_diseno.append({
                    'indice': i, 'variable_madre_id': r.get('variable_madre_id'),
                    'periodo': r.get('periodo'), 'pagina': r.get('pagina'),
                    'documento_origen': r.get('documento_origen'),
                    'condicion': f"{regla['campo_condicion']}={regla['valor_condicion']}",
                })
                base = None  # esperado por diseño → fuera de revisión humana
            else:
                base = 'NO_ENCONTRADO'
                if regla is not None:
                    base = f'NO_ENCONTRADO pero viola la condicion documentada ({regla["campo_condicion"]}={regla["valor_condicion"]})'
        elif est == 'INCONSISTENTE':
            base = 'INCONSISTENTE'
        elif est == 'ACEPTADO':
            regla = reglas_diseno.get(r.get('variable_madre_id'))
            if regla is not None and condicion_diseno_satisfecha(r, regla):
                # la condición documentada exigía NO_ENCONTRADO; tener ACEPTADO es la violación
                base = f'ACEPTADO cuando la regla de diseno esperaba NO_ENCONTRADO (condicion cumplida: {regla["campo_condicion"]}={regla["valor_condicion"]})'
            elif r.get('confianza') != 'ALTA':
                base = 'ACEPTADO con confianza != ALTA'
        motivo_final[i] = base

    revision = [
        {'indice': i, 'variable_madre_id': r.get('variable_madre_id'), 'periodo': r.get('periodo'),
         'estado': r.get('estado'), 'confianza': r.get('confianza'), 'pagina': r.get('pagina'),
         'documento_origen': r.get('documento_origen'), 'motivo': motivo_final[i]}
        for i, r in enumerate(registros) if motivo_final[i]
    ]

    grupos: Dict[Any, List[int]] = {}
    for i, r in enumerate(registros):
        grupos.setdefault(_clave(r), []).append(i)
    duplicados = [
        {'clave': list(k), 'indices': idx,
         'valores': [registros[i].get('valor') for i in idx],
         'conflictivo': len({json.dumps(registros[i].get('valor')) for i in idx}) > 1}
        for k, idx in grupos.items() if len(idx) > 1
    ]

    variables_con_resultado = sorted({r.get('variable_madre_id') for r in registros})
    variables_sin_resultado = sorted(set(variables_esperadas) - set(variables_con_resultado))

    validacion = validador_extraccion.validar_salida({'datos': registros}, esquema=esquema)

    return {
        'resumen': {
            'registros_totales': len(registros),
            'registros_con_periodo': len(con_periodo),
            'registros_sin_periodo': len(sin_periodo),
            'variables_esperadas': len(variables_esperadas),
            'periodos_esperados': periodos_esperados,
            'objetivos_esperados': len(esperados),
            'objetivos_cubiertos': len(cubiertos),
            'objetivos_faltantes': len(faltantes),
            'variables_con_resultado': len(variables_con_resultado),
            'variables_sin_resultado': len(variables_sin_resultado),
        },
        'distribucion_estado': distribucion_estado,
        'distribucion_confianza': distribucion_confianza,
        'valores_fuera_de_enum': extra,
        'requieren_revision': {
            'total': len(revision),
            'registros': revision,
        },
        'confirmados_por_diseno': confirmados_diseno,
        'duplicados': duplicados,
        'registros_sin_periodo': [
            {'variable_madre_id': r.get('variable_madre_id'), 'estado': r.get('estado'),
             'confianza': r.get('confianza'), 'pagina': r.get('pagina')} for r in sin_periodo
        ],
        'objetivos_faltantes': sorted(f'{v}|{p}' for v, p in faltantes),
        'variables_sin_resultado': variables_sin_resultado,
        'validacion': validacion,
    }


def imprimir_reporte(reporte: Dict[str, Any]) -> None:
    """Imprime el reporte legible por humanos."""
    r = reporte['resumen']
    print('=' * 72)
    print('AUDITORÍA DE LOTE — EXTRACCIÓN IA (esquema v3)')
    print('=' * 72)
    print(f"Registros totales: {r['registros_totales']} "
          f"(con periodo: {r['registros_con_periodo']}, sin periodo: {r['registros_sin_periodo']})")
    print(f"Objetivos esperados: {r['objetivos_esperados']} "
          f"({r['variables_esperadas']} variables IA-searchable × {len(r['periodos_esperados'])} periodos "
          f"{r['periodos_esperados']})")
    print(f"  Cubiertos: {r['objetivos_cubiertos']} | Faltantes: {r['objetivos_faltantes']}")
    print(f"Variables con algún resultado: {r['variables_con_resultado']}/{r['variables_esperadas']}")
    print('\nDISTRIBUCIÓN DE ESTADO:')
    for k, v in reporte['distribucion_estado'].items():
        print(f"  {k}: {v}")
    print('DISTRIBUCIÓN DE CONFIANZA:')
    for k, v in reporte['distribucion_confianza'].items():
        print(f"  {k}: {v}")
    if reporte['valores_fuera_de_enum']:
        print(f"VALORES FUERA DE ENUM: {reporte['valores_fuera_de_enum']}")
    print(f"\nCONFIRMADOS POR DISENO (NO_ENCONTRADO esperado segun taxonomia): {len(reporte['confirmados_por_diseno'])}")
    for x in reporte['confirmados_por_diseno']:
        print(f"  - [{x['indice']}] {x['variable_madre_id']}/{x['periodo']} pag={x['pagina']} -> {x['condicion']}")
    print(f"\nREQUIEREN REVISIÓN HUMANA: {reporte['requieren_revision']['total']}")
    for x in reporte['requieren_revision']['registros']:
        print(f"  - [{x['indice']}] {x['variable_madre_id']}/{x['periodo']} "
              f"estado={x['estado']} conf={x['confianza']} pag={x['pagina']} -> {x['motivo']}")
    print(f"\nDUPLICADOS (variable_madre_id, periodo): {len(reporte['duplicados'])}")
    for d in reporte['duplicados']:
        print(f"  - {d['clave']} indices={d['indices']} valores={d['valores']} conflictivo={d['conflictivo']}")
    if reporte['registros_sin_periodo']:
        print('REGISTROS SIN PERIODO (no cubren un objetivo variable×periodo):')
        for x in reporte['registros_sin_periodo']:
            print(f"  - {x['variable_madre_id']} estado={x['estado']} pag={x['pagina']}")
    v = reporte['validacion']
    print(f"\nVALIDACIÓN OFICIAL: valido={v['valido']} | errores esquema={len(v['errores_esquema'])} "
          f"| errores determinísticos={len(v['errores_deterministicos'])} | advertencias={len(v['advertencias'])}")


def _main() -> int:
    parser = argparse.ArgumentParser(description='Auditoría de lote de extracción IA (esquema v3).')
    parser.add_argument('registros', nargs='+', help='Uno o más JSON de registros.')
    parser.add_argument('--periodos', nargs='*', default=list(PERIODOS_POR_DEFECTO))
    parser.add_argument('--csv', default=None, help='Taxonomía (por defecto taxonomia_variable_madre.csv).')
    parser.add_argument('--json', default=None, help='Ruta donde volcar el reporte JSON.')
    args = parser.parse_args()

    registros = cargar_registros(args.registros)
    reporte = auditar(registros, cargar_variables_ia(args.csv), args.periodos,
                      esquema=validador_extraccion.cargar_esquema(),
                      reglas_diseno=cargar_reglas_diseno(args.csv))
    imprimir_reporte(reporte)
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
