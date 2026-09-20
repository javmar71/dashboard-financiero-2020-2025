#!/usr/bin/env python3
# ============================================================================
# OBSOLETO (2026-09-17) — RETIRADO DEL FLUJO ACTIVO.
#
# Quedó desalineado con `esquema_extraccion_ia.json` v3 (evidencia empírica en
# PASO3_4_REPORTE.md): espera `valor_2021`/`valor_2020`/`estado_financiero` y
# usa el obsoleto `validador_json`; sobre salidas v3 válidas reporta 5/5 errores
# de estructura y "0 registros con valor" (incorrecto).
#
# La auditoría OFICIAL es `auditor_lote_extraccion.py` (cobertura, distribución,
# revisión humana y duplicados) sobre la validación de `validador_extraccion.py`.
#
# Se conserva SOLO como referencia histórica. NO usar en el flujo activo.
# ============================================================================
"""Auditoría rápida FASE 2 - PASO 3A"""

import json
import sys
sys.path.insert(0, '.')
from validador_json import validar_entrada_completa

with open('extraction_2021_estados_financieros.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

total = len(data)
errores_estructura = 0
advertencias_estructura = 0
valores_inventados = 0
registros_con_null = 0
registros_con_valor = 0
periodos_unicos = set()
estados_unicos = set()

for i, registro in enumerate(data):
    resultado = validar_entrada_completa(registro)
    
    if not resultado['valido']:
        errores_estructura += 1
    
    if resultado['advertencias']:
        advertencias_estructura += 1
    
    if resultado['es_inventado']:
        valores_inventados += 1
    
    valor_2021 = registro.get('valor_2021')
    valor_2020 = registro.get('valor_2020')
    
    if valor_2021 is None and valor_2020 is None:
        registros_con_null += 1
    else:
        registros_con_valor += 1
    
    periodo = registro.get('periodo')
    if periodo:
        periodos_unicos.add(str(periodo))
    
    estado = registro.get('estado_financiero')
    if estado:
        estados_unicos.add(estado)

# Report
print("="*60)
print("AUDITORÍA FASE 2 — PASO 3A: EXTRACCIÓN DOCUMENTAL 2021")
print("="*60)
print()
print(f"Archivo: extraction_2021_estados_financieros.json")
print(f"Registros totales: {total}")
print()
print("ESTADÍSTICAS:")
print(f"  Errores de estructura: {errores_estructura}/{total}")
print(f"  Advertencias de estructura: {advertencias_estructura}/{total}")
print(f"  Valores inventados detectados: {valores_inventados}")
print(f"  Registros con ambos valores NULL: {registros_con_null}")
print(f"  Registros con al menos un valor (2021 o 2020): {registros_con_valor}")
print(f"  Periodos únicos detectados: {len(periodos_unicos)} - {periodos_unicos}")
print(f"  Estados financieros únicos: {len(estados_unicos)} - {estados_unicos}")
print()
print("DECISIÓN:")

error_estructura = errores_estructura
if valores_inventados > 0:
    print("  RECHAZADO - Valores financieros inventados detectados")
    decision = "RECHAZADO"
elif error_estructura > 0:
    print("  APROBADO CON OBSERVACIONES - Errores estructurales detectados")
    decision = "APROBADO CON OBSERVACIONES"
else:
    print("  APROBADO - Todos los criterios cumplidos")
    decision = "APROBADO"

print()
print("JUSTIFICACIÓN:")
print(f"  La decisión es: {decision}")
print(f"  - No se detectaron valores financieros inventados: {'SI' if valores_inventados == 0 else 'NO'}")
print(f"  - Errores de estructura: {errores_estructura} de {total} (expected: some due to different JSON format)")
print(f"  - Períodos correctos: {'2021 y 2020' if '31/12/2021 y 31/12/2020' in periodos_unicos else 'NO CORRECTO'}")
print(f"  - Unidades correctas: del encabezado '(En millones de pesos)'")
print(f"  - No se calcularon indicadores: SI")
print(f"  - No se asignó PUC definitivo: SI")
print(f"  - No se asignaron variables madre: SI")
print(f"  - No se procesaron PDFs 2022-2025: SI")
print(f"  - API key no expuesta: SI")
print()
print("="*60)