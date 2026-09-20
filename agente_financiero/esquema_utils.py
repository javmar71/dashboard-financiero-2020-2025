#!/usr/bin/env python3
"""
Módulo esquema_utils.py
PASO 3.3 — Utilidades del esquema de extracción IA (PASO 4.7: cálculo IA)

Responsabilidad: preparar `esquema_extraccion_ia.json` (o `esquema_calculo_ia.json`)
para ser usado como `response_schema` de la llamada al modelo generativo (motor:
opencode; ver GUIA_MOTOR_IA.md).

Este es un sanitizador JSON Schema GENÉRICO: dependiendo del SDK/cliente de llamada,
un subconjunto de JSON Schema no se tolera y produce error. En particular, los
clientes que modelan su propio tipo `Schema` rechazan claves que no pertenecen a su
subconjunto:

- `$schema` produce `pydantic ValidationError: Extra inputs are not permitted`.
- `additionalProperties` no está soportado por `types.Schema`.

`sanear_schema_para_sdk()` devuelve una COPIA del esquema sin esas claves, lista
para pasarse como `response_schema`.

ADVERTENCIA: la copia saneada SOLO sirve para la llamada al modelo. La validación
oficial de la salida se hace contra el esquema ORIGINAL (sin sanear), con la capa
`nullable`-aware documentada en CONTRATO_DATOS.md (la clave `nullable` es una
convención de algunos SDK/extensiones, ajena a jsonschema draft-07 puro).
"""

from typing import Any

# Claves del JSON Schema que los SDK/cliente de llamada no aceptan en `response_schema`.
CLAVES_NO_SOPORTADAS_POR_SDK = ("$schema", "additionalProperties")


def sanear_schema_para_sdk(esquema: Any) -> Any:
    """
    Devuelve una copia recursiva del esquema apta para el SDK de llamada al modelo.

    Elimina, en todos los niveles (objetos y arrays), las claves de
    `CLAVES_NO_SOPORTADAS_POR_SDK` (`$schema`, `additionalProperties`).
    Cuando `type` es una lista de tipos (p. ej. `["number", "string"]` en
    `valor`), se omite el constraint en la copia del SDK porque este solo
    acepta un type unico; la validacion oficial sigue usando el esquema
    original.
    El esquema original NO se modifica.

    Args:
        esquema: Estructura cargada de `esquema_extraccion_ia.json`
                 (dict/list/str/int/...).

    Returns:
        Nueva estructura equivalente sin las claves no soportadas por el SDK.
    """
    if isinstance(esquema, dict):
        resultado = {}
        for clave, valor in esquema.items():
            if clave in CLAVES_NO_SOPORTADAS_POR_SDK:
                continue
            if clave == 'type' and isinstance(valor, list):
                # El SDK solo acepta un type unico. Para campos polimorficos validados en el
                # esquema OFICIAL (p. ej. `valor` numerico o string), se omite el constraint
                # en la copia del SDK: el tipo queda abierto y la validacion deterministica
                # se hace contra el esquema original.
                continue
            resultado[clave] = sanear_schema_para_sdk(valor)
        return resultado
    if isinstance(esquema, list):
        return [sanear_schema_para_sdk(item) for item in esquema]
    return esquema
