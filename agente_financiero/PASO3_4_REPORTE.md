# Paso 3.4 — Auditoría del JSON de extracción por lote (reporte)

Fecha: 2026-09-17. Alcance: verificar la compatibilidad de los scripts de auditoría previos con el esquema v3 y crear/probar un auditor de lote. **No** se generó extracción nueva ni se amplió la cobertura (eso es el Paso 3.5). No se modificaron los scripts previos.

## 1. Compatibilidad de los scripts previos con el esquema v3 (verificación empírica)

Se corrieron los scripts originales (copias en temp) contra los 5 registros atómicos del Paso 3.3: sección 16 corregida (`proveedores/2021`, `proveedores/2020`, ambos `ACEPTADO`/`ALTA`), `NO_ENCONTRADO` (`proveedores/None`) y `DUDOSO` (`partes_relacionadas/2021`, `partes_relacionadas/2020`, ambos `DUDOSO`/`MEDIA`).

| Script | Qué espera | Qué produce v3 | Resultado empírico | Veredicto |
|---|---|---|---|---|
| `detector_requerimiento.py` | `valor_original`/`dato`/`monto`/`contenido`; `es_consolidado`; marcadores de texto (`AMBIGUO`, `CONFLICTO`, `NO_ENCONTRADO`, …) | `valor`, `estado` (enum), `confianza`, `pagina`, `documento_origen`, `evidencia` | `NO_ENCONTRADO` → detectado por marcador de texto en `estado`. `DUDOSO/MEDIA` → `PENDIENTE_VERIFICACION`, `requiere_revision=False` (¡no lo marca!). `ACEPTADO/ALTA` → `PENDIENTE_VERIFICACION` | **DESALINEADO**: no reconoce `estado=DUDOSO` ni usa `confianza`; no entiende `valor` |
| `auditor_rapido.py` | `valor_2021`/`valor_2020`, `estado_financiero`, `periodo`; importa `validador_json` | `valor`, `estado`, `confianza`, `periodo`, … | Corre (exit 0) pero reporta **5/5 errores de estructura**, **5/5 "ambos valores NULL"**, **0 con valor**, **0 estados financieros** (falso) | **DESALINEADO**: no crashea, pero el reporte es incorrecto |
| `audit_step3.py` | `nombre_cuenta_original`, `valor_2021`/`valor_2020`, `unidad_original`, `estado_financiero`, `confianza_*`; importa `validador_json` | `variable_madre_id`, `valor`, `unidad`, `estado`, `confianza`, … | **CRASHEA**: `AttributeError: 'NoneType' object has no attribute 'lower'` (línea 134) porque `estado_financiero` es `None` | **DESALINEADO**: falla en ejecución |
| `validador_json.py` | esquema antiguo de `CONTRATO_DATOS.md` | — | ya marcado OBSOLETO en el Paso 3.3 | **OBSOLETO** |

Conclusión: los tres scripts de auditoría previos están desalineados con v3 (uno crashea, uno produce un reporte incorrecto, uno aplica semántica equivocada). **No se adaptaron** — queda pendiente la decisión del usuario (probable desenlace: marcarlos obsoletos, igual que `validador_json.py`).

## 2. Auditor nuevo: `auditor_lote_extraccion.py`

Construido sobre el esquema v3 y reutilizando la validación oficial (`validador_extraccion.py`). Audita un **lote** (varios archivos) y reporta:

1. **Cobertura**: `variables IA-searchable × periodos esperados` (26 × 2 = 52 objetivos): cubiertos vs faltantes; variables con/sin resultado. Las variables esperadas se derivan de `taxonomia_variable_madre.csv` (`tipo_variable=primaria`, `fuente_esperada` ∈ {`notas`, `informe_gestion`, `informe_auditoria`}).
2. **Distribución** de `estado` y de `confianza` (con detección de valores fuera de enum).
3. **Revisión humana**: todo `DUDOSO`, todo `NO_ENCONTRADO`, todo `INCONSISTENTE` y todo `ACEPTADO` con `confianza != ALTA`.
4. **Duplicados/inconsistencias** en `(variable_madre_id, periodo)` (marca `conflictivo` si los valores difieren).
5. **Validación oficial** del lote (errores de esquema y determinísticos, advertencias).

CLI: `python auditor_lote_extraccion.py archivo1.json [archivo2.json ...] [--periodos 2021 2020] [--csv ruta] [--json salida.json]`.

## 3. Prueba con los registros existentes (5 atómicos)

```
Registros totales: 5 (con periodo: 4, sin periodo: 1)
Objetivos esperados: 52 (26 variables IA-searchable × 2 periodos ['2021','2020'])
  Cubiertos: 4 | Faltantes: 48
Variables con algún resultado: 2/26

DISTRIBUCIÓN DE ESTADO:   ACEPTADO: 2 | DUDOSO: 2 | NO_ENCONTRADO: 1 | INCONSISTENTE: 0
DISTRIBUCIÓN DE CONFIANZA: ALTA: 2 | MEDIA: 2 | BAJA: 0 | NO_DETERMINADA: 1

REQUIEREN REVISIÓN HUMANA: 3
  - [2] proveedores/None        estado=NO_ENCONTRADO conf=NO_DETERMINADA pag=1   -> NO_ENCONTRADO
  - [3] partes_relacionadas/2021 estado=DUDOSO        conf=MEDIA          pag=100 -> DUDOSO
  - [4] partes_relacionadas/2020 estado=DUDOSO        conf=MEDIA          pag=100 -> DUDOSO

DUPLICADOS (variable_madre_id, periodo): 0
REGISTROS SIN PERIODO (no cubren un objetivo variable×periodo):
  - proveedores estado=NO_ENCONTRADO pag=1
VALIDACIÓN OFICIAL: valido=True | errores esquema=0 | determinísticos=0 | advertencias=2
```

Interpretación: cobertura real 4/52 (2 variables × 2 periodos); el `NO_ENCONTRADO` con `periodo=null` no cubre ningún objetivo `variable×periodo` y queda listado aparte; los 3 registros de revisión humana son exactamente los esperados.

## 4. Artefactos

| Acción | Archivo |
|---|---|
| **Creado (auditor oficial de lote)** | `auditor_lote_extraccion.py` |
| Sin cambios (pendiente decisión) | `detector_requerimiento.py`, `auditor_rapido.py`, `audit_step3.py` |
| Creado | `PASO3_4_REPORTE.md` (este documento) |

Scripts temporales: `paso34_compat.py` (harness de compatibilidad) y `paso34_reporte.json` (reporte JSON del lote).

## 5. Pendiente

Decisión del usuario sobre los tres scripts previos desalineados (probable: marcarlos obsoletos). Luego, autorización para el Paso 3.5 (cobertura completa del año 2021).
