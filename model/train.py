"""
Entrenamiento de Modelo de Predicción de Precios de Viviendas (King County)
Agente 1: Data Scientist & ML Engineer (🟢 Gemini 3.6)
Objetivo: Seleccionar las mejores características minimizando MAE y generar artefactos.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def run_training():
    print("=" * 60)
    print("🟢 [AGENTE 1: MODEL] Iniciando Fase 1: Entrenamiento & Feature Selection")
    print("=" * 60)

    # 1. Cargar Datos
    data_path = os.path.join(os.path.dirname(__file__), "..", "kc_house_data_train.xlsx")
    if not os.path.exists(data_path):
        data_path = "kc_house_data_train.xlsx"
    
    print(f"📂 Cargando dataset desde: {data_path}")
    df = pd.read_excel(data_path)
    print(f"📊 Registros cargados: {df.shape[0]} filas, {df.shape[1]} columnas")

    # 2. Limpieza y separación Target / Features
    if 'id' in df.columns:
        df = df.drop(columns=['id'])
    
    # Manejo de nulos si existieran
    df = df.dropna()

    X = df.drop(columns=['price'])
    y = df['price']

    # 3. Selección de Features evaluando impacto en MAE
    # Evaluamos correlaciones e importancia con modelo base
    rf_selector = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    rf_selector.fit(X, y)
    importances = pd.Series(rf_selector.feature_importances_, index=X.columns).sort_values(ascending=False)
    
    print("\n🔍 Importancia relativa de características:")
    for feat, imp in importances.items():
        print(f"   - {feat:15s}: {imp:.4f}")

    # Probamos subconjuntos de mejores features (top 8, top 10, top 12, all) evaluando MAE con validación cruzada
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    candidate_k = [8, 10, 12, len(X.columns)]
    best_mae = float('inf')
    best_features = None

    print("\n🧪 Evaluando subconjuntos de características con K-Fold (Scoring: MAE)...")
    for k in candidate_k:
        selected = importances.head(k).index.tolist()
        model_eval = HistGradientBoostingRegressor(random_state=42, max_iter=200, min_samples_leaf=20)
        scores = -cross_val_score(model_eval, X[selected], y, cv=cv, scoring='neg_mean_absolute_error', n_jobs=-1)
        mean_mae = scores.mean()
        print(f"   Top {k:2d} features -> CV MAE: ${mean_mae:,.2f} USD")
        if mean_mae < best_mae:
            best_mae = mean_mae
            best_features = selected

    print(f"\n🏆 Mejor conjunto seleccionado ({len(best_features)} features) con CV MAE = ${best_mae:,.2f} USD")
    print(f"   Features: {best_features}")

    # 4. Train-Test Split y Entrenamiento Final
    X_train, X_test, y_train, y_test = train_test_split(
        X[best_features], y, test_size=0.2, random_state=42
    )

    final_model = HistGradientBoostingRegressor(
        random_state=42,
        max_iter=300,
        learning_rate=0.08,
        max_leaf_nodes=45,
        min_samples_leaf=15
    )
    final_model.fit(X_train, y_train)

    # 5. Evaluación de Métricas
    y_pred_train = final_model.predict(X_train)
    y_pred_test = final_model.predict(X_test)

    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    test_r2 = r2_score(y_test, y_pred_test)

    print("\n📈 Métricas del Modelo Final:")
    print(f"   - MAE en Entrenamiento : ${train_mae:,.2f} USD")
    print(f"   - MAE en Test (Holdout): ${test_mae:,.2f} USD")
    print(f"   - R² en Test           : {test_r2:.4f}")

    # 6. Exportar Artefactos y Contrato de Datos
    artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    # A. Modelo serializado
    model_path = os.path.join(artifacts_dir, "house_price_model.joblib")
    joblib.dump(final_model, model_path)
    print(f"\n💾 Modelo guardado en: {model_path}")

    # B. Contrato de Features
    feature_specs = {}
    for col in best_features:
        feature_specs[col] = {
            "type": "float" if X[col].dtype in ['float64', 'float32'] else "int",
            "min": float(X[col].min()),
            "max": float(X[col].max()),
            "median": float(X[col].median()),
            "mean": float(X[col].mean())
        }

    contract = {
        "model_name": "King County House Price Predictor",
        "algorithm": "HistGradientBoostingRegressor",
        "target": "price",
        "features": best_features,
        "feature_details": feature_specs,
        "total_features": len(best_features)
    }

    contract_path = os.path.join(artifacts_dir, "features_contract.json")
    with open(contract_path, "w", encoding="utf-8") as f:
        json.dump(contract, f, indent=2)
    print(f"📜 Contrato de Features guardado en: {contract_path}")

    # C. Métricas
    metrics = {
        "cv_mae": float(best_mae),
        "train_mae": float(train_mae),
        "test_mae": float(test_mae),
        "test_r2": float(test_r2)
    }
    metrics_path = os.path.join(artifacts_dir, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"📊 Métricas guardadas en: {metrics_path}")
    print("\n✅ Fase 1 Completada con Éxito.\n")

if __name__ == "__main__":
    run_training()
