#!/usr/bin/env python3
"""
Módulo validador_extraccion.py
PASO 3.3 — Validación OFICIAL de la salida de extracción IA

Responsabilidad: validar la salida del modelo contra `esquema_extraccion_ia.json`
(v3) en dos capas:

  1. jsonschema `nullable`-aware. La clave `nullable` es una extensión de Google,
     ajena a JSON Schema draft-07. Draft-07 puro la ignora y marca como inválido
     cualquier campo `nullable` que venga en `null` (p. ej. `codigo_puc: null`),
     produciendo un falso positivo. Aquí se extiende `Draft7Validator` para
     aceptar `null` cuando el sub-esquema declara `nullable: true`.

  2. Capa determinística propia: no invención, `evidencia` no vacía, enums de
     `estado`/`confianza`, `pagina` y `documento_origen` presentes y no nulos,
     unicidad de `(variable_madre_id, periodo)` y coherencia de
     `estado = NO_ENCONTRADO` (los campos de valor deben venir en `null`).

Es la validación OFICIAL del proyecto; reemplaza a `validador_json.py` (obsoleto).
No modifica el esquema ni la salida.

Uso CLI:
    python validador_extraccion.py salida.json [--variable proveedores]
        [--periodos 2021 2020] [--esquema ruta_al_esquema.json]
"""

import argparse
import csv
import json
import pathlib
from typing import Any, Dict, List, Optional, Set

from jsonschema import Draft7Validator, validators

ESQUEMA_POR_DEFECTO = pathlib.Path(__file__).with_name('esquema_extraccion_ia.json')
CSV_POR_DEFECTO = pathlib.Path(__file__).with_name('taxonomia_variable_madre.csv')

ESTADOS_VALIDOS = {'ACEPTADO', 'DUDOSO', 'NO_ENCONTRADO', 'INCONSISTENTE'}
CONFIANZAS_VALIDAS = {'ALTA', 'MEDIA', 'BAJA', 'NO_DETERMINADA'}
ESTADOS_CON_VALOR_OBLIGATORIO = {'ACEPTADO', 'INCONSISTENTE'}
CAMPOS_NULOS_SI_NO_ENCONTRADO = ('valor', 'periodo', 'unidad', 'cuenta_original')


TIPOS_DATO_CUALITATIVOS = {'cualitativo', 'cualitativo_enum', 'cualitativo_texto_libre'}


def cargar_tipos_dato(ruta: Optional[Any] = None) -> Dict[str, str]:
    """
    Carga `{variable_madre_id: tipo_dato}` desde la taxonomía.

    `tipo_dato` ∈ {cuantitativo, cualitativo_enum, cualitativo_texto_libre}.
    """
    ruta = pathlib.Path(ruta) if ruta else CSV_POR_DEFECTO
    tipos: Dict[str, str] = {}
    if not ruta.exists():
        return tipos
    with open(ruta, encoding='utf-8-sig') as f:
        for fila in csv.DictReader(f):
            tipos[fila['variable_madre_id']] = (fila.get('tipo_dato') or '').strip()
    return tipos


def cargar_cualitativas(ruta: Optional[Any] = None) -> Set[str]:
    """
    Carga los `variable_madre_id` con un `tipo_dato` cualitativo (cualquier variante)
    desde la taxonomía. Mantiene la firma usada por otros módulos.
    """
    ruta = pathlib.Path(ruta) if ruta else CSV_POR_DEFECTO
    cualitativas: Set[str] = set()
    tipos = cargar_tipos_dato(ruta)
    for vid, td in tipos.items():
        if td in TIPOS_DATO_CUALITATIVOS:
            cualitativas.add(vid)
    return cualitativas


def cargar_esquema(ruta: Optional[Any] = None) -> Dict[str, Any]:
    """Carga el esquema desde `ruta` o desde `esquema_extraccion_ia.json` (por defecto)."""
    ruta = pathlib.Path(ruta) if ruta else ESQUEMA_POR_DEFECTO
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def _validador_nullable_aware(esquema: Dict[str, Any]):
    """Devuelve un `Draft7Validator` que acepta `null` cuando el sub-esquema es `nullable`."""

    def tipo_nullable(validator, tipos, instancia, subesquema):
        if instancia is None and subesquema.get('nullable') is True:
            return
        yield from Draft7Validator.VALIDATORS['type'](validator, tipos, instancia, subesquema)

    return validators.extend(Draft7Validator, {'type': tipo_nullable})(esquema)


def validar_esquema(salida: Any, esquema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Valida `salida` contra `esquema` con la capa `nullable`-aware. Devuelve lista de errores."""
    validador = _validador_nullable_aware(esquema)
    return [
        {'ruta': list(error.absolute_path), 'mensaje': error.message}
        for error in sorted(validador.iter_errors(salida), key=lambda e: list(e.absolute_path))
    ]


def validar_entrada(
    entrada: Any,
    indice: int,
    variable_objetivo: Optional[str] = None,
    periodos_esperados: Optional[Set[str]] = None,
    variables_cualitativas: Optional[Set[str]] = None,
    tipos_dato: Optional[Dict[str, str]] = None,
) -> Dict[str, List[str]]:
    """Valida una entrada `datos[i]` con las reglas determinísticas. Devuelve errores y advertencias."""
    errores: List[str] = []
    advertencias: List[str] = []
    variables_cualitativas = variables_cualitativas or set()
    tipos_dato = tipos_dato if tipos_dato is not None else cargar_tipos_dato()
    p = f'datos[{indice}]'
    vid = entrada.get('variable_madre_id') if isinstance(entrada, dict) else None
    tipo_dato = (tipos_dato or {}).get(vid) if isinstance(vid, str) else None

    if not isinstance(entrada, dict):
        return {'errores': [f'{p}: la entrada no es un objeto'], 'advertencias': []}

    if variable_objetivo is not None and entrada.get('variable_madre_id') != variable_objetivo:
        errores.append(
            f'{p}: variable_madre_id={entrada.get("variable_madre_id")!r} != objetivo {variable_objetivo!r}')

    if not isinstance(entrada.get('documento_origen'), str) or not entrada['documento_origen'].strip():
        errores.append(f'{p}: documento_origen ausente/vacio')

    pagina = entrada.get('pagina')
    if not isinstance(pagina, int) or isinstance(pagina, bool) or pagina < 1:
        errores.append(
            f'{p}: pagina ausente o no entero >=1: {pagina!r} (obligatoria siempre, incluso NO_ENCONTRADO)')

    estado = entrada.get('estado')
    if estado not in ESTADOS_VALIDOS:
        errores.append(f'{p}: estado fuera de enum: {estado!r}')
    if entrada.get('confianza') not in CONFIANZAS_VALIDAS:
        errores.append(f'{p}: confianza fuera de enum: {entrada.get("confianza")!r}')

    if not isinstance(entrada.get('evidencia'), str) or not entrada['evidencia'].strip():
        errores.append(f'{p}: evidencia vacia (prohibida)')

    es_cualitativa = (vid in variables_cualitativas) or (tipo_dato in TIPOS_DATO_CUALITATIVOS)
    es_enum = tipo_dato == 'cualitativo_enum'
    es_texto_libre = tipo_dato == 'cualitativo_texto_libre'
    valor = entrada.get('valor')
    valor_numerico = isinstance(valor, (int, float)) and not isinstance(valor, bool)
    valor_string = isinstance(valor, str) and bool(valor.strip())

    if estado == 'NO_ENCONTRADO':
        for campo in CAMPOS_NULOS_SI_NO_ENCONTRADO:
            if entrada.get(campo) is not None:
                errores.append(
                    f'{p}: estado=NO_ENCONTRADO pero {campo}={entrada.get(campo)!r} (debe ser null)')
    elif es_texto_libre:
        if estado in ESTADOS_CON_VALOR_OBLIGATORIO:
            if not valor_string:
                errores.append(f'{p}: estado={estado} texto_libre exige valor string no vacio')
        elif estado == 'DUDOSO':
            if valor is not None and not valor_string:
                errores.append(f'{p}: estado=DUDOSO con valor no string: {valor!r}')
            if valor is None:
                advertencias.append(
                    f'{p}: estado=DUDOSO sin valor unico (valido si los candidatos estan detallados en evidencia)')
    elif es_enum:
        if estado in ESTADOS_CON_VALOR_OBLIGATORIO:
            if not valor_string:
                errores.append(f'{p}: estado={estado} enum exige valor string (miembro del enum)')
        elif estado == 'DUDOSO':
            if valor is not None and not valor_string:
                errores.append(f'{p}: estado=DUDOSO con valor no string: {valor!r}')
            if valor is None:
                advertencias.append(
                    f'{p}: estado=DUDOSO sin valor unico (valido si los candidatos estan detallados en evidencia)')
    elif es_cualitativa:
        if estado in ESTADOS_CON_VALOR_OBLIGATORIO:
            if valor is not None and not valor_string:
                errores.append(f'{p}: estado={estado} cualitativo con valor no string: {valor!r}')
            if valor is None:
                advertencias.append(
                    f'{p}: estado={estado} cualitativo sin valor string (valido si la evidencia es documental)')
        elif estado == 'DUDOSO':
            if valor is not None and not valor_string and not valor_numerico:
                errores.append(f'{p}: estado=DUDOSO con valor no numerico: {valor!r}')
            if valor is None:
                advertencias.append(
                    f'{p}: estado=DUDOSO sin valor unico (valido si los candidatos estan detallados en evidencia)')
    else:
        if estado in ESTADOS_CON_VALOR_OBLIGATORIO and not valor_numerico:
            errores.append(f'{p}: estado={estado} sin valor numerico')
        elif estado == 'DUDOSO':
            if valor is not None and not valor_numerico:
                errores.append(f'{p}: estado=DUDOSO con valor no numerico: {valor!r}')
            if valor is None:
                advertencias.append(
                    f'{p}: estado=DUDOSO sin valor unico (valido si los candidatos estan detallados en evidencia)')

    if periodos_esperados is not None and entrada.get('periodo') not in periodos_esperados:
        errores.append(
            f'{p}: periodo={entrada.get("periodo")!r} fuera de los esperados {sorted(periodos_esperados)}')

    return {'errores': errores, 'advertencias': advertencias}


def validar_salida(
    salida: Any,
    esquema: Optional[Dict[str, Any]] = None,
    variable_objetivo: Optional[str] = None,
    periodos_esperados: Optional[Set[str]] = None,
    variables_cualitativas: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Ejecuta la validación oficial completa (esquema + determinística) sobre una salida.

    Returns:
        Dict con {valido, errores_esquema, errores_deterministicos, advertencias, n_entradas}.
    """
    esquema = esquema if esquema is not None else cargar_esquema()
    variables_cualitativas = variables_cualitativas if variables_cualitativas is not None else cargar_cualitativas()
    errores_esquema = validar_esquema(salida, esquema)
    errores_det: List[str] = []
    advertencias: List[str] = []

    entradas = salida.get('datos', []) if isinstance(salida, dict) else []
    if not isinstance(entradas, list):
        entradas = []
    vistos: Set[Any] = set()
    for i, entrada in enumerate(entradas):
        r = validar_entrada(entrada, i, variable_objetivo, periodos_esperados, variables_cualitativas)
        errores_det.extend(r['errores'])
        advertencias.extend(r['advertencias'])
        clave = (entrada.get('variable_madre_id'), entrada.get('periodo')) if isinstance(entrada, dict) else None
        if clave in vistos:
            errores_det.append(f'datos[{i}]: duplicado (variable_madre_id, periodo)={clave}')
        vistos.add(clave)

    return {
        'valido': not errores_esquema and not errores_det,
        'errores_esquema': errores_esquema,
        'errores_deterministicos': errores_det,
        'advertencias': advertencias,
        'n_entradas': len(entradas),
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description='Validador oficial de la extracción IA (esquema v3).')
    parser.add_argument('salida', help='Ruta del JSON de salida a validar.')
    parser.add_argument('--esquema', default=None, help='Ruta del esquema (por defecto esquema_extraccion_ia.json).')
    parser.add_argument('--variable', default=None, help='variable_madre_id esperado en todas las entradas.')
    parser.add_argument('--periodos', nargs='*', default=None, help='Periodos esperados, ej: --periodos 2021 2020.')
    args = parser.parse_args()

    with open(args.salida, encoding='utf-8') as f:
        salida = json.load(f)
    resultado = validar_salida(
        salida,
        esquema=cargar_esquema(args.esquema),
        variable_objetivo=args.variable,
        periodos_esperados=set(args.periodos) if args.periodos else None,
    )
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0 if resultado['valido'] else 1


if __name__ == '__main__':
    raise SystemExit(_main())
