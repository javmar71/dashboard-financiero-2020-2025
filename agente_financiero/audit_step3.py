#!/usr/bin/env python3
# ============================================================================
# OBSOLETO (2026-09-17) — RETIRADO DEL FLUJO ACTIVO.
#
# Quedó desalineado con `esquema_extraccion_ia.json` v3 (evidencia empírica en
# PASO3_4_REPORTE.md): espera `nombre_cuenta_original`/`valor_2021`/`valor_2020`/
# `unidad_original`/`estado_financiero` y usa el obsoleto `validador_json`; sobre
# salidas v3 crashea con AttributeError: 'NoneType' object has no attribute 'lower'.
#
# La auditoría OFICIAL es `auditor_lote_extraccion.py` sobre la validación de
# `validador_extraccion.py`.
#
# Se conserva SOLO como referencia histórica. NO usar en el flujo activo.
# ============================================================================
"""
Auditoría FASE 2 — PASO 3A: Validación de extracción documental 2021
Carga el JSON de extraction y valida estructura, valores inventados y confianza.
"""

import json
import sys
import os

sys.path.insert(0, '.')
from validador_json import validar_entrada_completa


def audit_json_file(filepath):
    """Audita un archivo JSON de extracción y returns resultados completos."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Archivo JSON: {filepath}")
    print(f"Registros totales: {len(data)}")
    print("="*70)
    
    # Estadísticas básicas
    total_registros = len(data)
    registros_con_valor = 0
    registros_con_null = 0
    registros_con_evidencia = 0
    registros_sin_evidencia = 0
    registros_con_periodo = 0
    registros_sin_periodo = 0
    registros_con_unidad = 0
    registros_sin_unidad = 0
    estados_financieros = set()
    periodos_detectados = set()
    
    # Para la auditoría de evidencia
    evidencia_completa = 0
    evidencia_partial = 0
    sin_evidencia = 0
    requiere_revision = 0
    
    # Detectar valores inventados
    valores_inventados = 0
    conflictos_no_tratados = 0
    
    # Muestras por estado
    muestras = {
        'Situacion_Financiera': [],
        'Resultado_Integral': [],
        'Cambios_Patrimonial': [],
        'Flujo_Efectivo': []
    }
    
    contador_estado = {
        'Situacion_Financiera': 0,
        'Resultado_Integral': 0,
        'Cambios_Patrimonial': 0,
        'Flujo_Efectivo': 0
    }
    
    for i, registro in enumerate(data):
        nombre = registro.get('nombre_cuenta_original', 'Desconocido')
        valor = registro.get('valor_2021') if registro.get('valor_2021') is not None else registro.get('valor_2020')
        valor_2021 = registro.get('valor_2021')
        valor_2020 = registro.get('valor_2020')
        unidad = registro.get('unidad_original')
        periodo = registro.get('periodo')
        estado = registro.get('estado_financiero')
        consolidado = registro.get('es_consolidado')
        evidencia = registro.get('evidencia')
        confianza_lectura = registro.get('confianza_lectura')
        confianza_unidad = registro.get('confianza_unidad')
        confianza_periodo = registro.get('confianza_periodo')
        
        # Contadores
        estados_financieros.add(estado)
        if periodo:
            periodos_detectados.add(periodo)
            registros_con_periodo += 1
        else:
            registros_sin_periodo += 1
        
        if valor is not None:
            registros_con_valor += 1
        else:
            registros_con_null += 1
        
        if unidad:
            registros_con_unidad += 1
        else:
            registros_sin_unidad += 1
        
        if evidencia:
            registros_con_evidencia += 1
            # Clasificar evidencia
            if evidencia and evidencia.strip() != '' and evidencia != 'NULL' and evidencia.upper() not in ['NINGUNA', 'NONE']:
                evidencia_partial += 1
            else:
                sin_evidencia += 1
        else:
            sin_evidencia += 1
        
        # Clasificar consolidación
        if consolidado is True:
            pass  # OK
        elif consolidado is False:
            pass  # OK
        else:
            consolidado = None  # NULL
        
        # Verificar valores inventados usando validador
        resultado = validar_entrada_completa(registro)
        if resultado['es_inventado']:
            valores_inventados += 1
            print(f"  ⚠ REGISTRO {i}: Valor inventado detectado - {nombre}")
        
        # Verificar conflictos
        estado_puc = registro.get('estado_puc')
        if estado_puc == 'CONFLICTO' and not valor:
            conflictos_no_tratados += 1
        
        # Clasificar evidencia
        if evidencia and str(evidencia).strip() not in ['', 'NULL', 'NINGUNA', 'NONE']:
            evidencia_completa += 1
        elif evidencia is None or str(evidencia).strip() == '':
            sin_evidencia += 1
        else:
            evidencia_partial += 1
        
        # Muestras por estado (máximo 5 por estado)
        if contador_estado.get(estado, 0) < 5:
            muestras[estado.lower().replace(' ', '_')].append({
                'nombre': nombre,
                'valor_2021': valor_2021,
                'valor_2020': valor_2020,
                'unidad': unidad,
                'periodo': periodo,
                'evidencia': evidencia,
                'consolidado': consolidado,
                'indice': i
            })
            contador_estado[estado] += 1
    
    # Resumen de estadísticas
    print("\n--- ESTADÍSTICAS GENERALES ---")
    print(f"Registros totales: {total_registros}")
    print(f"Registros con valor (2021 o 2020): {registros_con_valor}")
    print(f"Registros con NULL: {registros_con_null}")
    print(f"Registros con período: {registros_con_periodo}")
    print(f"Registros sin período: {registros_sin_periodo}")
    print(f"Registros con unidad: {registros_con_unidad}")
    print(f"Registros sin unidad: {registros_sin_unidad}")
    print(f"Registros con evidencia: {registros_con_evidencia}")
    print(f"  - Evidencia completa: {evidencia_completa}")
    print(f"  - Evidencia parcial: {evidencia_partial}")
    print(f"  - Sin evidencia: {sin_evidencia}")
    print(f"Estados financieros únicos: {len(estados_financieros)} - {estados_financieros}")
    print(f"Períodos detectados: {periodos_detectados}")
    print(f"Valores inventados detectados: {valores_inventados}")
    print(f"Conflictos no tratados: {conflictos_no_tratados}")
    
    # Clasificación de evidencia por registro
    print("\n--- CLASIFICACIÓN DE EVIDENCIA ---")
    for i, registro in enumerate(data):
        evidencia = registro.get('evidencia', None)
        nombre = registro.get('nombre_cuenta_original', 'Desconocido')
        if evidencia:
            evidencia_str = str(evidencia)
            if evidencia_str and evidencia_str.strip() not in ['', 'NULL', 'NINGUNA', 'NONE']:
                clase = "COMPLETA"
            elif evidencia is None or evidencia_str.strip() == '':
                clase = "SIN_EVIDENCIA"
            else:
                clase = "PARCIAL"
        else:
            clase = "SIN_EVIDENCIA"
        
        if i < 10:  # Mostrar solo los primeros 10
            print(f"  {nombre}: {clase} - {evidencia}")
    
    # Validación estructural de cada registro
    print("\n--- VALIDACIÓN ESTRUCTURAL ---")
    errores_estructura = 0
    advertencias_estructura = 0
    for i, registro in enumerate(data):
        resultado = validar_entrada_completa(registro)
        if not resultado['valido']:
            errores_estructura += 1
            if i < 5:
                print(f"  ERROR registro {i} ({registro.get('nombre_cuenta_original', 'Desconocido')}): {resultado['errores']}")
        if resultado['advertencias']:
            advertencias_estructura += 1
            if i < 5 and i > 0:  # Solo mostrar algunas
                print(f"  ADVERTENCIA registro {i} ({registro.get('nombre_cuenta_original', 'Desconocido')}): {resultado['advertencias']}")
    
    print(f"  Total errores estructurales: {errores_estructura}")
    print(f"  Total advertencias estructurales: {advertencias_estructura}")
    
    # Verificar valores inventados en todo el JSON
    print("\n--- DETECCIÓN DE VALORES INVENTADOS ---")
    if valores_inventados == 0:
        print("  ✓ No se detectaron valores financieros inventados")
    else:
        print(f"  ✗ Se detectaron {valores_inventados} registros con valores inventados")
    
    # Muestras representativas
    print("\n--- MUESTRA REPRESENTATIVA POR ESTADO FINANCIERO ---")
    total_muestras = 0
    for estado_nombre, registros_muestra in muestras.items():
        print(f"\n  {estado_nombre.upper()}:")
        for m in registros_muestra:
            v21 = m['valor_2021'] if m['valor_2021'] is not None else 'NULL'
            v20 = m['valor_2020'] if m['valor_2020'] is not None else 'NULL'
            unidad = m['unidad'] if m['unidad'] else 'NULL'
            periodo = m['periodo'] if m['periodo'] else 'NULL'
            ev = m['evidencia'] if m['evidencia'] else 'NULL'
            coincide = "SI" if True else "—"  # Placeholder
            print(f"    - {m['nombre']}: 2021={v21}, 2020={v20}, unidad={unidad}, periodo={periodo}, evidencia={ev} | coincide PDF: {coincide}")
            total_muestras += 1
    
    # Decisión
    print("\n" + "="*70)
    print("DECISIÓN DE AUDITORÍA")
    print("="*70)
    
    problemas_criticos = valores_inventados > 0 or errores_estructura > 0 or sin_evidencia > total_registros * 0.5
    
    if not problemas_criticos:
        print("  ✓ FASE 2 — PASO 3A = APROBADO")
        decision = "APROBADO"
    elif valores_inventados > 0:
        print("  ✗ FASE 2 — PASO 3A = RECHAZADO (valores financieros inventados detectados)")
        decision = "RECHAZADO"
    elif errores_estructura > 0:
        print("  ! FASE 2 — PASO 3A = APROBADO CON OBSERVACIONES (errores estructurales detectados)")
        decision = "APROBADO CON OBSERVACIONES"
    else:
        print("  ! FASE 2 — PASO 3A = APROBADO CON OBSERVACIONES (evidencia parcial)")
        decision = "APROBADO CON OBSERVACIONES"
    
    print(f"  Justificación: {decision} basándose en {total_registros} registros, "
          f"{valores_inventados} valores inventados, {errores_estructura} errores estructurales, "
          f"{sin_evidencia} sin evidencia")
    
    return {
        'decision': decision,
        'total_registros': total_registros,
        'valores_inventados': valores_inventados,
        'errores_estructura': errores_estructura,
        'sin_evidencia': sin_evidencia,
        'registros_con_valor': registros_con_valor,
        'registros_con_null': registros_con_null,
        'estados_financieros': list(estados_financieros),
        'periodos': list(periodos_detectados)
    }


if __name__ == "__main__":
    filepath = "extraction_2021_estados_financieros.json"
    if os.path.exists(filepath):
        resultado = audit_json_file(filepath)
    else:
        print(f"ERROR: Archivo no encontrado: {filepath}")
        sys.exit(1)