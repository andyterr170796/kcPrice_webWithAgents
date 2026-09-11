from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class HouseFeatures(BaseModel):
    grade: int = Field(7, ge=1, le=13, description="Calidad de construcción y diseño (1-13)")
    sqft_living: int = Field(1900, ge=100, le=20000, description="Pies cuadrados de área habitable")
    lat: float = Field(47.5729, ge=47.0, le=48.0, description="Latitud geográfica")
    long: float = Field(-122.231, ge=-123.0, le=-121.0, description="Longitud geográfica")
    sqft_living15: int = Field(1830, ge=100, le=10000, description="Pies cuadrados habitables de los 15 vecinos más cercanos")
    yr_built: int = Field(1969, ge=1850, le=2026, description="Año de construcción")
    waterfront: int = Field(0, ge=0, le=1, description="Vista directa al agua (0 = No, 1 = Sí)")
    sqft_above: int = Field(1530, ge=100, le=15000, description="Pies cuadrados sobre el suelo")
    sqft_lot: int = Field(7904, ge=100, le=2000000, description="Pies cuadrados del terreno")
    zipcode: int = Field(98065, ge=98000, le=99000, description="Código postal en King County")
    sqft_lot15: int = Field(7820, ge=100, le=1000000, description="Pies cuadrados del lote de los 15 vecinos más cercanos")
    view: int = Field(0, ge=0, le=4, description="Calidad de la vista (0 a 4)")
    bathrooms: float = Field(2.0, ge=0.5, le=10.0, description="Número de baños")
    sqft_basement: int = Field(0, ge=0, le=10000, description="Pies cuadrados del sótano")
    condition: int = Field(3, ge=1, le=5, description="Condición general de la vivienda (1-5)")
    bedrooms: int = Field(3, ge=1, le=15, description="Número de habitaciones")
    yr_renovated: int = Field(0, ge=0, le=2026, description="Año de renovación (0 si nunca se renovó)")
    floors: float = Field(1.0, ge=1.0, le=4.0, description="Número de pisos")

    class Config:
        json_schema_extra = {
            "example": {
                "grade": 7,
                "sqft_living": 1900,
                "lat": 47.5729,
                "long": -122.231,
                "sqft_living15": 1830,
                "yr_built": 1969,
                "waterfront": 0,
                "sqft_above": 1530,
                "sqft_lot": 7904,
                "zipcode": 98065,
                "sqft_lot15": 7820,
                "view": 0,
                "bathrooms": 2.0,
                "sqft_basement": 0,
                "condition": 3,
                "bedrooms": 3,
                "yr_renovated": 0,
                "floors": 1.0
            }
        }

class PredictionResponse(BaseModel):
    estimated_price: float
    formatted_price: str
    currency: str = "USD"
    mae_margin: float
    features_received: Dict[str, Any]

class ModelInfoResponse(BaseModel):
    model_name: str
    algorithm: str
    target: str
    total_features: int
    features: List[str]
    metrics: Dict[str, float]
