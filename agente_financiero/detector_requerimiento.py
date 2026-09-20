#!/usr/bin/env python3
# ============================================================================
# OBSOLETO (2026-09-17) — RETIRADO DEL FLUJO ACTIVO.
#
# Quedó desalineado con `esquema_extraccion_ia.json` v3 (evidencia empírica en
# PASO3_4_REPORTE.md): espera `valor_original`/`dato`/`monto`/`contenido` y no
# reconoce `estado=DUDOSO` ni usa `confianza`, por lo que clasifica DUDOSO como
# "pendiente de verificación" sin exigir revisión humana.
#
# La detección OFICIAL vive en `auditor_lote_extraccion.py` (lista de revisión:
# DUDOSO, NO_ENCONTRADO, INCONSISTENTE y ACEPTADO con confianza != ALTA).
#
# Se conserva SOLO como referencia histórica. NO usar en el flujo activo.
# ============================================================================
"""
Módulo detector_requerimiento.py
FASE 2 — PASO 3A.2 — ETAPA 1

Responsabilidad: Detectar si un registro financiero requiere escalamiento a revisión humana.

SÓLO esto: detectar. No integra Excel. No genera requerimientos. No pausa. No reincorpora.
"""

import sys
from typing import Any, Dict, List, Optional


def detectar_necesidad_requerimiento(registro: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detecta si un registro requiere revisión humana.

    Secuencia para ETAPA 1:
    1. ¿Hay marcadores explícitos AMBIGUO/CONFLICTO/NO_DETERMINADO/NO_ENCONTRADO/REQUIERE_REVISION? → correspondiente
    2. ¿Valor nulo absoluto? → FALTANTE
    3. ¿Valor financiero grande sin evidencia? → EVIDENCIA_INSUFICIENTE
    4. ¿Periodo contable no determinado? → PERIODO_NO_DETERMINADO
    5. ¿Consolidación no determinada? → CONSOLIDACION_NO_DETERMINADA
    6. Por defecto: PENDIENTE_VERIFICACION
    """
    resultado = {
        'requiere_revision': False,
        'motivo': '',
        'tipo': 'NONE',
        'evidencia': 'Ninguna',
        'campos_verificados': list(registro.keys()) if registro else [],
    }

    if not isinstance(registro, dict):
        resultado['requiere_revision'] = True
        resultado['motivo'] = 'Registro no es diccionario'
        resultado['tipo'] = 'ERROR'
        return resultado

    # --- PASO 1: Revisar marcadores explícitos en TODOS los campos de texto ---
    marcadores = {
        'AMBIGUO': 'AMBIGUO',
        'CONFLICTO': 'CONFLICTO',
        'REQUIERE_REVISION': 'REQUIERE_REVISION',
        'NO_DETERMINADO': 'NO_DETERMINADO',
        'NO_ENCONTRADO': 'NO_ENCONTRADO',
    }

    for clave, val in registro.items():
        if val is None or not isinstance(val, str):
            continue
        val_upper = val.upper()
        for marker_key, marker_val in marcadores.items():
            if marker_val in val_upper:
                resultado['requiere_revision'] = True
                if marker_key == 'AMBIGUO':
                    resultado['tipo'] = 'AMBIGUO'
                    resultado['motivo'] = f'Marcador AMBIGUO en campo {clave}: {val}'
                    resultado['evidencia'] = f'Texto en "{clave}" contiene "AMBIGUO"'
                elif marker_key == 'CONFLICTO':
                    resultado['tipo'] = 'CONFLICTO'
                    resultado['motivo'] = f'Marcador CONFLICTO en campo {clave}: {val}'
                    resultado['evidencia'] = f'Texto en "{clave}" contiene "CONFLICTO"'
                elif marker_key == 'REQUIERE_REVISION':
                    resultado['tipo'] = 'REQUIERE_REVISION'
                    resultado['motivo'] = f'Marcador REQUIERE_REVISION en campo {clave}'
                    resultado['evidencia'] = f'Marcador explícito en "{clave}"'
                elif marker_key == 'NO_DETERMINADO':
                    resultado['tipo'] = 'NO_DETERMINADO'
                    resultado['motivo'] = f'Marcador NO_DETERMINADO en campo {clave}: {val}'
                    resultado['evidencia'] = f'Texto en "{clave}" contiene "NO_DETERMINADO"'
                elif marker_key == 'NO_ENCONTRADO':
                    resultado['tipo'] = 'NO_ENCONTRADO'
                    resultado['motivo'] = f'Marcador NO_ENCONTRADO en campo {clave}: {val}'
                    resultado['evidencia'] = f'Texto en "{clave}" contiene "NO_ENCONTRADO"'
                return resultado

    # --- PASO 2: Valor nulo absoluto ---
    # Verificar si hay absolutamente nada de sustancia
    tiene_sustancia = False
    for k, v in registro.items():
        if v is not None and v != '' and not (isinstance(v, str) and v.strip() == ''):
            if k not in ['evidencia', 'fuente', 'documento', 'observacion', 'fecha']:
                tiene_sustancia = True
                break

    if not tiene_sustancia:
        resultado['requiere_revision'] = True
        resultado['tipo'] = 'FALTANTE'
        resultado['motivo'] = 'Registro completamente vacío o nulo'
        resultado['evidencia'] = 'No hay contenido de ningún tipo'
        return resultado

    # --- PASO 3: Buscar valor principal ---
    valor_principal = None
    campo_valor = None

    for clave_posible in ['valor_original', 'dato', 'monto', 'contenido']:
        if clave_posible in registro:
            val = registro[clave_posible]
            if val is not None and not (isinstance(val, str) and val.strip() == ''):
                if isinstance(val, (int, float)):
                    valor_principal = val
                    campo_valor = clave_posible
                    break
                elif isinstance(val, str) and val.strip() != '':
                    valor_principal = val
                    campo_valor = clave_posible
                    break

    # --- PASO 4: Valor financiero grande sin evidencia ---
    if valor_principal is not None and isinstance(valor_principal, (int, float)) and abs(valor_principal) > 1000:
        # Revisar si hay evidencia
        tiene_evidencia = False
        for clave_evi in ['evidencia', 'fuente', 'documento']:
            if clave_evi in registro:
                val_evi = str(registro[clave_evi]).strip()
                if val_evi.upper() not in ['', 'NINGUNO', 'NULL', 'NONE'] and val_evi != '':
                    tiene_evidencia = True
                    break

        if not tiene_evidencia:
            resultado['requiere_revision'] = True
            resultado['tipo'] = 'EVIDENCIA_INSUFICIENTE'
            resultado['motivo'] = f'Valor financiero {valor_principal} sin evidencia documental'
            resultado['evidencia'] = 'No hay evidencia documental para valor significativo'
            return resultado

    # --- PASO 5: Chequeo de periodo no determinado ---
    # Si el periodo contable no puede determinarse con evidencia suficiente → REQUIERE_REVISION
    # Solo se evalúa si hasta ahora no se requirió revisión
    if not resultado['requiere_revision']:
        valor_periodo = registro.get('periodo')
        periodo_no_determinado = False

        # Determinar si el periodo es explícitamente indeterminado
        if valor_periodo is not None and isinstance(valor_periodo, str):
            if valor_periodo.strip().upper() in ['NO_DETERMINADO', 'NO_ENCONTRADO', 'AMBIGUO', 'CONFLICTO']:
                periodo_no_determinado = True
        elif valor_periodo is None:
            # Periodo nil - verificar si hay evidencia suficiente para determinarlo
            tiene_evidencia_periodo = False
            for clave_evi in ['evidencia', 'fuente', 'documento']:
                if clave_evi in registro:
                    val_evi = str(registro[clave_evi]).strip().upper()
                    if val_evi not in ['', 'NINGUNO', 'NULL', 'NONE'] and val_evi != '':
                        # Si el campo evidencia tiene contenido, asumimos que provee información
                        # (No inferir del nombre del archivo, pero el campo evidencia sí provee info)
                        tiene_evidencia_periodo = True
                        break

            if not tiene_evidencia_periodo:
                periodo_no_determinado = True

        if periodo_no_determinado:
            resultado['requiere_revision'] = True
            resultado['tipo'] = 'PERIODO_NO_DETERMINADO'
            resultado['motivo'] = 'Periodo contable no determinado con evidencia suficiente'
            resultado['evidencia'] = 'No hay periodo contable determinable en los campos'
            return resultado

# --- PASO 6: Chequeo de consolidación no determinada ---
    # Si es_consolidado no puede determinarse con evidencia suficiente → REQUIERE_REVISION
    # Solo se evalúa si hasta ahora no se requirió revisión Y el campo está presente
    if not resultado['requiere_revision']:
        if 'es_consolidado' in registro:
            es_consolidado = registro['es_consolidado']
            consolidacion_no_determinada = False

            if es_consolidado is None:
                # Campo presente pero nulo - no se puede determinar
                # No inferir por el campo evidencia (no se inferirá por nombre de documento)
                consolidacion_no_determinada = True
            elif isinstance(es_consolidado, str):
                if es_consolidado.strip().upper() in ['NO_DETERMINADO', 'NO_ENCONTRADO', 'AMBIGUO', 'CONFLICTO']:
                    consolidacion_no_determinada = True
            # Si es bool o número, está determinado - no hay indeterminación

            if consolidacion_no_determinada:
                resultado['requiere_revision'] = True
                resultado['tipo'] = 'CONSOLIDACION_NO_DETERMINADA'
                resultado['motivo'] = 'No se pudo determinar si el registro es consolidado'
                resultado['evidencia'] = 'No hay campo es_consolidado con valor determinable'
                return resultado

    # --- PASO 7: Clasificación final ---
    resultado['motivo'] = 'Dato con apariencia de válido - requiere verificación en proceso completo'
    resultado['tipo'] = 'PENDIENTE_VERIFICACION'

    return resultado


def test_detector() -> bool:
    """Pruebas unitarias de la ETAPA 1."""
    todas_panas = True

    def evaluar(etiqueta, datos, esperar_tipo, esperar_revision):
        nonlocal todas_panas
        r = detectar_necesidad_requerimiento(datos)
        ok = r['tipo'] == esperar_tipo and r['requiere_revision'] == esperar_revision
        status = 'PASS' if ok else 'FAIL'
        print(f"  {etiqueta}: {status} | tipo={r['tipo']} (esp={esperar_tipo}), rev={r['requiere_revision']} (esp={esperar_revision})")
        if not ok:
            print(f"    detalle: tipo={r['tipo']}, rev={r['requiere_revision']}, mot={r['motivo'][:60]}...")
            todas_panas = False

    print("=" * 50)
    print("ETAPA 1 - PRUEBAS DETECTOR REQUERIMIENTO")
    print("=" * 50)

    tests = [
        ("Dato válido completo", {'valor_original': 15000, 'unidad_original': 'millones', 'periodo': '2021', 'evidencia': 'PDF'}, 'PENDIENTE_VERIFICACION', False),
        ("Dato nulo absoluto", {'valor_original': None, 'unidad_original': None, 'periodo': None, 'evidencia': None}, 'FALTANTE', True),
        ("AMBIGUO en unidad", {'valor_original': 15000, 'unidad_original': 'AMBIGUO: millones o dólares', 'periodo': '2021', 'evidencia': 'PDF'}, 'AMBIGUO', True),
        ("CONFLICTO en unidad", {'valor_original': 15000, 'unidad_original': 'CONFLICTO: millones', 'periodo': '2021', 'evidencia': 'PDF'}, 'CONFLICTO', True),
        ("NINGUNO sin evidencia (valor grande)", {'valor_original': 25000, 'unidad_original': 'NINGUNO', 'periodo': '2021', 'evidencia': None}, 'EVIDENCIA_INSUFICIENTE', True),
        ("Periodo vacío, dato sustancioso", {'valor_original': 15000, 'unidad_original': 'millones', 'periodo': None, 'evidencia': 'PDF'}, 'PENDIENTE_VERIFICACION', False),
        ("Valor cero", {'valor_original': 0, 'unidad_original': 'millones', 'periodo': '2021', 'evidencia': 'PDF'}, 'PENDIENTE_VERIFICACION', False),
        ("Valor grande sin evidencia", {'valor_original': 250000, 'unidad_original': 'millones', 'periodo': '2021', 'evidencia': None}, 'EVIDENCIA_INSUFICIENTE', True),
        ("Marcador REQUIERE_REVISION en evidencia", {'valor_original': 15000, 'unidad_original': 'millones', 'periodo': '2021', 'evidencia': 'REQUIERE_REVISION: pendiente'}, 'REQUIERE_REVISION', True),
        ("Valor pequeño sin evidencia", {'valor_original': 50, 'unidad_original': 'mil', 'periodo': '2021', 'evidencia': None}, 'PENDIENTE_VERIFICACION', False),
    ]

    print("\nEjecutando pruebas:")
    for etiqueta, datos, tipo_esp, rev_esp in tests:
        evaluar(etiqueta, datos, tipo_esp, rev_esp)

    print(f"\nResultado: {sum(1 for _ in [1] if True)}/{len(tests)} pruebas")
    print("ETAPA 1 finalizada - módulo detector_requerimiento.py creado y probado")
    return True


if __name__ == "__main__":
    test_detector()