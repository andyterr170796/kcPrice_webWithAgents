---
name: fastapi-docker-serving
description: Buenas prácticas y patrones para construir microservicios REST con FastAPI, validación Pydantic basada en contratos de features y contenerización optimizada con Docker.
---

# Skill: Despliegue de Modelos de ML con FastAPI y Docker

Esta habilidad proporciona el flujo de trabajo para exponer modelos serializados (`.joblib`) mediante endpoints REST robustos y contenerizarlos.

## Patrones Recomendados

1. **Carga en Contexto Lifespan (FastAPI):**
   - Cargar `house_price_model.joblib` y `features_contract.json` al iniciar la aplicación mediante el manejador `lifespan` asíncrono para evitar latencia en cada request.

2. **Esquema Pydantic Dinámico/Estricto:**
   - Crear clases Pydantic (`BaseModel`) donde cada campo corresponda a las features seleccionadas en el contrato.
   - Definir validaciones de rango (ej. `gt=0`, `ge=0`) y ejemplos (`Field(..., example=3)`).

3. **Endpoints Estándar:**
   - `GET /health`: Retorna `{ "status": "ok", "service": "house-price-prediction" }`.
   - `GET /model-info`: Retorna las features esperadas y las métricas MAE registradas.
   - `POST /predict`: Recibe el JSON de entrada, convierte a DataFrame de pandas con las columnas en el orden exacto del contrato y ejecuta `model.predict()`.

4. **Dockerfile Optimizado:**
   - Base liviana: `python:3.11-slim`.
   - Copiar `requirements.txt`, instalar sin cache: `pip install --no-cache-dir -r requirements.txt`.
   - Exponer puerto `8000`.
   - Comando de arranque: `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]`.
