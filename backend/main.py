import os
import json
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schemas import HouseFeatures, PredictionResponse, ModelInfoResponse

# Estado global para almacenar el artefacto cargado
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cargar artefactos durante el arranque
    base_dir = os.path.dirname(__file__)
    # Ruta local o ruta montada dentro del contenedor
    possible_paths = [
        os.path.join(base_dir, "artifacts"),
        os.path.join(base_dir, "..", "model", "artifacts"),
        "/app/artifacts"
    ]
    
    artifacts_dir = None
    for p in possible_paths:
        if os.path.exists(os.path.join(p, "house_price_model.joblib")):
            artifacts_dir = p
            break

    if not artifacts_dir:
        raise RuntimeError("No se encontraron los artefactos del modelo. Ejecute primero la Fase 1 (model/train.py).")

    print(f"🔵 [AGENTE 2: BACKEND] Cargando artefactos desde: {artifacts_dir}")
    ml_models["model"] = joblib.load(os.path.join(artifacts_dir, "house_price_model.joblib"))
    
    with open(os.path.join(artifacts_dir, "features_contract.json"), "r", encoding="utf-8") as f:
        ml_models["contract"] = json.load(f)
        
    with open(os.path.join(artifacts_dir, "metrics.json"), "r", encoding="utf-8") as f:
        ml_models["metrics"] = json.load(f)

    print(f"✅ Modelo {ml_models['contract']['model_name']} cargado exitosamente.")
    yield
    # Limpieza al apagar
    ml_models.clear()

app = FastAPI(
    title="King County House Price Prediction API",
    description="Microservicio REST de inferencia de precios de casas entrenado optimizando MAE.",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS segura para permitir la conexión desde el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check():
    """Endpoint de comprobación de salud del servicio y del modelo."""
    model_loaded = "model" in ml_models
    return {
        "status": "healthy" if model_loaded else "degraded",
        "service": "kc-house-price-api",
        "model_loaded": model_loaded
    }

@app.get("/model-info", response_model=ModelInfoResponse, tags=["Model Info"])
async def get_model_info():
    """Retorna información del modelo, features esperadas y métricas de error."""
    if "contract" not in ml_models:
        raise HTTPException(status_code=503, detail="Modelo no inicializado.")
    return {
        "model_name": ml_models["contract"]["model_name"],
        "algorithm": ml_models["contract"]["algorithm"],
        "target": ml_models["contract"]["target"],
        "total_features": ml_models["contract"]["total_features"],
        "features": ml_models["contract"]["features"],
        "metrics": ml_models["metrics"]
    }

@app.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK, tags=["Inference"])
async def predict_price(payload: HouseFeatures):
    """Realiza la predicción del precio de una vivienda dada su especificación."""
    if "model" not in ml_models:
        raise HTTPException(status_code=503, detail="El modelo aún no está disponible.")

    try:
        data_dict = payload.model_dump()
        features_order = ml_models["contract"]["features"]
        
        # Construir dataframe respetando el orden exacto de features del contrato
        df_input = pd.DataFrame([data_dict])[features_order]
        
        # Inferencia
        prediction = float(ml_models["model"].predict(df_input)[0])
        mae_margin = float(ml_models["metrics"].get("test_mae", 66734.0))

        return {
            "estimated_price": round(prediction, 2),
            "formatted_price": f"${prediction:,.2f} USD",
            "currency": "USD",
            "mae_margin": round(mae_margin, 2),
            "features_received": data_dict
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la inferencia: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
