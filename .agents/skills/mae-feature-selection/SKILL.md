---
name: mae-feature-selection
description: Guía y metodología para realizar Feature Selection y entrenamiento de modelos de regresión tabular minimizando Mean Absolute Error (MAE) y exportando artefactos de inferencia.
---

# Skill: Selección de Características Optimizando MAE

Esta habilidad enseña al agente de Machine Learning a evaluar y seleccionar las mejores variables predictoras para minimizar el MAE.

## Procedimiento Paso a Paso

1. **Carga y Limpieza de Datos:**
   - Leer el Excel con `pandas.read_excel('kc_house_data_train.xlsx')`.
   - Excluir identificadores arbitrarios (ej. `id`).
   - Separar la variable objetivo: `y = df['price']` y matriz de features `X = df.drop(columns=['price', 'id'])`.

2. **Ingeniería de Características y Selección:**
   - Calcular correlaciones lineales y no lineales (Spearman / Pearson) contra el target.
   - Usar técnicas de selección automática:
     - `SelectKBest(score_func=f_regression, k=...)` o
     - Importancia con modelos basados en árboles (`RandomForestRegressor` o `HistGradientBoostingRegressor`).
   - Evaluar con K-Fold Cross Validation usando `neg_mean_absolute_error`.

3. **Métrica Principal:**
   - El objetivo es **minimizar MAE**:
     $$\text{MAE} = \frac{1}{n}\sum_{i=1}^n |y_i - \hat{y}_i|$$
   - Registrar MAE de entrenamiento, validación y test.

4. **Exportación de Contrato:**
   - Guardar el pipeline entrenado en `model/artifacts/house_price_model.joblib`.
   - Guardar `features_contract.json` con la lista exacta de features seleccionadas, su orden y su tipo de dato (float, int, etc.).
   - Guardar `metrics.json` con los puntajes MAE y R2 obtenidos.
