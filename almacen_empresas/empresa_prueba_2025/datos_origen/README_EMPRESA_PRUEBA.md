# Workspace de empresa de prueba: empresa_prueba_2025

Prueba de concepto multi-empresa (2026-09-20). Datos 100 % SINTETICOS
(semilla 2025) generados por `agente_financiero\construir_empresa_prueba.py`.

## Estructura

- `datos_origen\estados_financieros_sinteticos.csv` -- estados SINTETICOS
  2020-2025 con identidad contable verificada (activo = pasivo + patrimonio).
- `salidas\` -- insumos del Data Mart con el mismo esquema que la entidad
  ancla: `indicadores.csv`, `datos_estados_financieros.csv`,
  `fase7_wacc_roi\wacc_roi_2020_2025.csv`,
  `fase8_evidencia_formal\evidencia_formal_conceptos.csv`.

## Aislamiento

- Ningun archivo de la entidad ancla (raiz `salidas\`) se modifica.
- El Data Mart se genera en `salidas\power_bi\` de ESTE workspace:

  ```
  venv\Scripts\python.exe agente_financiero\fase10_powerbi_data_mart.py --empresa empresa_prueba_2025
  ```

## Trazabilidad

- Origen: generador deterministico (semilla 2025).
- Estado: SINTETICO / prueba. No corresponde a ninguna entidad real.
