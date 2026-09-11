FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Healthcheck interno del contenedor
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de ejecución
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
