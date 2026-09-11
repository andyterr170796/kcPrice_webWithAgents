FROM python:3.11-slim

WORKDIR /app

# Dependencias mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación
COPY . .

# Exponer el puerto por defecto de Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Arrancar Streamlit en modo headless sin telemetría
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true", "--browser.gatherUsageStats=false"]
