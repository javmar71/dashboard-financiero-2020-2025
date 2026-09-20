#!/usr/bin/env python3
"""
Módulo mapeo_variables_secciones.py
PASO 3.5 (parte 1) — Mapeo determinístico variable_madre_id -> sección(es) candidata(s).

Es un paso de REGLAS (coincidencia de título/palabras clave), NO de modelo.
No llama a la IA. No extrae valores.

Fuentes:
  - `taxonomia_variable_madre.csv`: las 26 variables IA-searchable y su `fuente_esperada`.
  - `segmentacion_2021.json`: secciones (título + texto) por documento.

Salida: `mapeo_variables_secciones_2021.json` con, por variable:
  - `documento_origen` y `fuente_esperada`.
  - `candidatas`: secciones ordenadas por coincidencia (con `orden_documento`,
    `titulo_seccion`, `pagina_inicio`, `pagina_fin`, `coincidencias_titulo`, `menciones_cuerpo`).
  - `seccion_principal`: la mejor candidata con coincidencia de título, o
    `sin_seccion_candidata` si no hay ninguna clara.
  - `grupo_seccion`: clave de agrupación para pedir en una sola llamada.

Donde no hay sección clara se marca `sin_seccion_candidata` (no se fuerza).
"""

import csv
import json
import pathlib
import re
import sys
import unicodedata

DIRECTORIO = pathlib.Path(__file__).parent
SEGMENTACION = DIRECTORIO / 'segmentacion_2021.json'
CSV_TAXONOMIA = DIRECTORIO / 'taxonomia_variable_madre.csv'
SALIDA = DIRECTORIO / 'mapeo_variables_secciones_2021.json'

FUENTES_IA = {'notas', 'informe_gestion', 'informe_auditoria'}
DOC_POR_FUENTE = {
    'notas': 'Informe de Gestion_2021.pdf',
    'informe_gestion': 'Informe de Gestion_2021.pdf',
    'informe_auditoria': 'Informe de Audtoria_2021.pdf',
}

PALABRAS_CLAVE = {
    # --- notas ---
    'proveedores': ['proveedores', 'cuentas comerciales por pagar', 'cuentas por pagar'],
    'composicion_deuda': ['composicion de la deuda', 'composicion deuda', 'estructura de la deuda',
                          'obligaciones financieras', 'deuda financiera'],
    'deuda_financiera_corriente': ['deuda financiera corriente', 'obligaciones financieras corrientes',
                                   'obligaciones financieras'],
    'deuda_financiera_no_corriente': ['deuda financiera no corriente', 'obligaciones financieras no corrientes',
                                      'largo plazo'],
    'tasas_interes': ['tasas de interes', 'tasa de interes', 'tasa efectiva', 'tasas efectivas'],
    'composicion_inventarios': ['inventarios', 'inventario'],
    'inversiones_detalle': ['inversiones', 'instrumentos financieros', 'valor razonable'],
    'adquisiciones_activos': ['propiedades y equipo', 'adquisiciones', 'adiciones', 'derecho de uso',
                              'activos intangibles'],
    'contingencias': ['contingencias', 'contingente', 'provisiones'],
    'partes_relacionadas': ['partes relacionadas', 'vinculados', 'transacciones con partes relacionadas'],
    # --- informe_gestion ---
    'crecimiento_adquisiciones': ['crecimiento', 'adquisiciones', 'expansion'],
    'participacion_mercado': ['participacion de mercado', 'participacion'],
    'ventas_por_segmento': ['ventas por segmento', 'ingresos por segmento', 'ingresos de operaciones', 'segmento'],
    'desempeno_por_segmento': ['desempeno', 'resultado por segmento', 'segmentos'],
    'eficiencia_operativa': ['eficiencia', 'gastos de administracion'],
    'numero_empleados': ['numero de empleados', 'empleados', 'beneficios a empleados', 'colaboradores'],
    'perspectivas': ['perspectivas', 'proyecciones', 'expectativas'],
    'riesgos': ['riesgo', 'riesgos', 'politicas de riesgo'],
    'hechos_relevantes': ['hechos relevantes', 'hechos posteriores', 'eventos subsecuentes'],
    'cumplimiento_covenants': ['covenant', 'covenants', 'relacion de solvencia', 'patrimonio tecnico', 'solvencia'],
    # --- informe_auditoria ---
    'tipo_opinion': ['opinion'],
    'salvedades': ['salvedad', 'salvedades', 'excepto por'],
    'enfasis': ['enfasis'],
    'cuestiones_key': ['cuestiones clave', 'asuntos clave', 'cuestiones'],
    'incertidumbre': ['incertidumbre', 'empresa en marcha', 'negocio en marcha'],
}


# Decisión revisada (2026-09-17): tras inspeccionar el contexto de cada coincidencia.
# Valor = `orden_documento` de la sección principal; None = `sin_seccion_candidata`.
# Las reglas de palabras clave siguen siendo la evidencia; esta capa fija la conclusión
# (el keyword crudo asignaba mal, p. ej., `numero_empleados`->Beneficios a empleados).
DECISION_REVISADA = {
    'proveedores': 44,
    'composicion_deuda': None,
    'deuda_financiera_corriente': None,
    'deuda_financiera_no_corriente': None,
    'tasas_interes': None,
    'composicion_inventarios': None,
    'inversiones_detalle': 34,
    'adquisiciones_activos': 42,
    'contingencias': 50,
    'partes_relacionadas': 70,
    'crecimiento_adquisiciones': None,
    'participacion_mercado': None,
    'ventas_por_segmento': None,
    'desempeno_por_segmento': None,
    'eficiencia_operativa': None,
    'numero_empleados': None,
    'perspectivas': None,
    'riesgos': 73,
    'hechos_relevantes': 74,
    'cumplimiento_covenants': 71,
    'tipo_opinion': 4,
    'salvedades': 4,
    'enfasis': None,
    'cuestiones_key': None,
    'incertidumbre': 5,
}

# Tratamiento en la extracción (PASO 3.5):
#   extraccion_ia            -> se pide al modelo (una llamada por sección).
#   no_encontrado_estructural-> estado=NO_ENCONTRADO sin llamada: no existe informe de
#                              gestión narrativo en el conjunto documental 2021.
#   pendiente_decision       -> cadena deuda: espera resultado de la 2ª búsqueda (términos ampliados).
# Las variables `no_aplica_tipo_entidad` ya se excluyen de la taxonomía (CSV).
NO_ENCONTRADO_ESTRUCTURAL = ['crecimiento_adquisiciones', 'participacion_mercado',
                             'ventas_por_segmento', 'desempeno_por_segmento',
                             'eficiencia_operativa', 'numero_empleados', 'perspectivas']
CADENA_DEUDA = ['composicion_deuda', 'deuda_financiera_corriente',
                'deuda_financiera_no_corriente', 'tasas_interes']

NOTAS_REVISION = {
    'proveedores': 'Nota 16 "Cuentas comerciales por pagar y otras cuentas por pagar": es donde se revelan proveedores.',
    'composicion_deuda': 'No hay nota de obligaciones/deuda financiera; las menciones a "deuda"/"obligación" son políticas contables, inversiones (TES) o litigios.',
    'deuda_financiera_corriente': 'Igual que composicion_deuda: no existe nota de obligaciones financieras.',
    'deuda_financiera_no_corriente': 'Igual que composicion_deuda: no existe nota de obligaciones financieras.',
    'tasas_interes': 'La única coincidencia de título es la Reforma de la tasa de interés (norma contable 2.2.7), no tasas de la entidad.',
    'composicion_inventarios': 'No hay nota de inventarios (solo menciones genéricas: acta de asamblea / NIC 2).',
    'inversiones_detalle': 'Nota 8 "Inversiones, neto" (detalle por tipo); apoyo en política [19] Instrumentos financieros y [30] Valor razonable.',
    'adquisiciones_activos': 'Nota 14 "Propiedades y equipo, neto" (adiciones); relacionadas [43] intangibles, [45]/[46] derecho de uso.',
    'contingencias': 'Nota 22 "Provisiones"; litigios en [51]-[56]; política NIC 37 [13].',
    'partes_relacionadas': 'Nota 36 "Transacciones con partes relacionadas".',
    'crecimiento_adquisiciones': 'No hay informe de gestión narrativo ni sección de crecimiento/expansión.',
    'participacion_mercado': 'No hay informe de gestión narrativo (las menciones a "participación" son de instrumentos/operaciones conjuntas).',
    'ventas_por_segmento': 'No hay desglose de ventas por segmento; "segmento" refiere a cartera de inversiones/mora.',
    'desempeno_por_segmento': 'No hay sección de desempeño por segmento.',
    'eficiencia_operativa': 'No se publican indicadores de eficiencia operativa.',
    'numero_empleados': 'No se revela número de empleados ni planta de personal (Beneficios a empleados es sobre pasivos laborales).',
    'perspectivas': 'No hay sección de perspectivas/proyecciones.',
    'riesgos': 'Nota 39 "Políticas de riesgo".',
    'hechos_relevantes': 'Nota 40 "Eventos subsecuentes".',
    'cumplimiento_covenants': 'No se usa la palabra "covenant"; nota 37 "Patrimonio técnico y relación de solvencia" es lo más cercano (exigencias regulatorias).',
    'tipo_opinion': 'Sección "Opinión" [4]; apoyo en "Fundamento de la Opinión" [5].',
    'salvedades': 'Sección "Opinión" [4] (donde constarían las salvedades); en [6] se alude a una opinión previa "sin salvedades".',
    'enfasis': 'No hay párrafo de énfasis ("enfasis" sin coincidencias).',
    'cuestiones_key': 'No hay cuestiones clave / KAM ("cuestiones clave" sin coincidencias).',
    'incertidumbre': 'Mención de "incertidumbre material" en "Fundamento de la Opinión" [5]; no hay incertidumbre material específica de la entidad.',
}


def normalizar(texto: str) -> str:
    """Minúsculas y sin acentos, para coincidencia robusta."""
    if not texto:
        return ''
    descompuesto = unicodedata.normalize('NFKD', texto)
    plano = ''.join(c for c in descompuesto if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', plano.lower())


def cargar_variables_ia() -> list:
    variables = []
    with open(CSV_TAXONOMIA, encoding='utf-8-sig') as f:
        for fila in csv.DictReader(f):
            if fila['tipo_variable'] == 'primaria' and fila['fuente_esperada'] in FUENTES_IA:
                variables.append({'variable_madre_id': fila['variable_madre_id'],
                                  'fuente_esperada': fila['fuente_esperada']})
    return variables


def cargar_segmentos(documento: str) -> list:
    datos = json.loads(SEGMENTACION.read_text(encoding='utf-8'))
    for doc in datos['documentos']:
        if doc['documento_origen'] == documento:
            segmentos = []
            for s in doc['segmentos']:
                texto = '\n'.join(b['texto'] for b in s.get('bloques_por_pagina', []))
                segmentos.append({
                    'orden_documento': s['orden_documento'],
                    'titulo_seccion': s['titulo_seccion'],
                    'pagina_inicio': s['pagina_inicio'],
                    'pagina_fin': s['pagina_fin'],
                    'bloques': s.get('bloques_por_pagina', []),
                    '_titulo_norm': normalizar(s['titulo_seccion'] or ''),
                    '_cuerpo_norm': normalizar(texto),
                })
            return segmentos
    return []


def buscar_candidatas(variable: dict, palabras: list, segmentos: list) -> list:
    candidatas = []
    for s in segmentos:
        titulo_hits = [p for p in palabras if normalizar(p) in s['_titulo_norm']]
        cuerpo_hits = {p: s['_cuerpo_norm'].count(normalizar(p)) for p in palabras
                       if s['_cuerpo_norm'].count(normalizar(p)) > 0}
        if not titulo_hits and not cuerpo_hits:
            continue
        score = 10 * len(titulo_hits) + sum(cuerpo_hits.values())
        candidatas.append({
            'orden_documento': s['orden_documento'],
            'titulo_seccion': s['titulo_seccion'],
            'pagina_inicio': s['pagina_inicio'],
            'pagina_fin': s['pagina_fin'],
            'coincidencias_titulo': titulo_hits,
            'menciones_cuerpo': cuerpo_hits,
            '_score': score,
            '_tiene_titulo': bool(titulo_hits),
        })
    candidatas.sort(key=lambda c: (c['_tiene_titulo'], c['_score']), reverse=True)
    return candidatas


def construir_mapeo() -> dict:
    variables = cargar_variables_ia()
    cache_segmentos = {}
    registros = []
    for var in variables:
        doc = DOC_POR_FUENTE[var['fuente_esperada']]
        if doc not in cache_segmentos:
            cache_segmentos[doc] = cargar_segmentos(doc)
        palabras = PALABRAS_CLAVE.get(var['variable_madre_id'], [])
        candidatas = buscar_candidatas(var, palabras, cache_segmentos[doc])

        principal = DECISION_REVISADA.get(var['variable_madre_id'])
        if principal is None:
            principal = 'sin_seccion_candidata'
        if var['variable_madre_id'] in NO_ENCONTRADO_ESTRUCTURAL:
            tratamiento = 'no_encontrado_estructural'
        elif var['variable_madre_id'] in CADENA_DEUDA:
            tratamiento = 'pendiente_decision'
        elif principal != 'sin_seccion_candidata':
            tratamiento = 'extraccion_ia'
        else:
            tratamiento = 'sin_seccion_candidata'

        for c in candidatas:
            c.pop('_score', None)
            c.pop('_tiene_titulo', None)

        registros.append({
            'variable_madre_id': var['variable_madre_id'],
            'fuente_esperada': var['fuente_esperada'],
            'documento_origen': doc,
            'palabras_clave': palabras,
            'seccion_principal': principal,
            'grupo_seccion': principal,
            'tratamiento': tratamiento,
            'nota_revision': NOTAS_REVISION.get(var['variable_madre_id'], ''),
            'candidatas': candidatas,
        })
    return {'generado_por': 'mapeo_variables_secciones.py', 'paso': '3.5-parte1', 'usa_ia': False,
            'total_variables': len(registros), 'registros': registros}


def _imprimir(mapeo: dict) -> None:
    for r in mapeo['registros']:
        print(f"\n{r['variable_madre_id']}  (fuente={r['fuente_esperada']}, doc={r['documento_origen']})")
        print(f"  palabras_clave: {r['palabras_clave']}")
        print(f"  seccion_principal: {r['seccion_principal']}")
        if r['candidatas']:
            for c in r['candidatas'][:4]:
                print(f"    [{c['orden_documento']:>3}] p{c['pagina_inicio']}-{c['pagina_fin']} "
                      f"T={c['coincidencias_titulo']} B={c['menciones_cuerpo']} | {c['titulo_seccion'][:70]}")
            if len(r['candidatas']) > 4:
                print(f"    ... (+{len(r['candidatas']) - 4} candidatas más)")
        else:
            print("    (sin coincidencias)")


def _main() -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    mapeo = construir_mapeo()
    _imprimir(mapeo)
    SALIDA.write_text(json.dumps(mapeo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nEscrito: {SALIDA}")
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
