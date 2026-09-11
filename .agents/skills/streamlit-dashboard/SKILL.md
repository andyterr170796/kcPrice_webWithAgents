---
name: streamlit-dashboard
description: Procedimiento para crear interfaces de usuario interactivas con Streamlit que consumen APIs REST de Machine Learning con validación y visualizaciones de impacto.
---

# Skill: Dashboard Interactivo de Machine Learning con Streamlit

Esta habilidad guía al agente en la construcción de interfaces interactivas intuitivas y reactivas para predicción de modelos.

## Principios de Diseño

1. **Configuración de Página y Estética:**
   - Título, ícono y layout expandido (`st.set_page_config(page_title="King County House Price", layout="wide")`).
   - Uso de tarjetas métricas (`st.metric`) para mostrar el precio estimado formateado en dólares ($USD).

2. **Formulario Reactivo:**
   - Agrupar entradas en columnas (`col1, col2 = st.columns(2)`).
   - Generar controles acordes al tipo de dato (sliders para rangos continuos/enteros como habitaciones, selectboxes para categorías/grades).

3. **Consumo de la API Backend:**
   - Definir URL base parametrizable mediante variable de entorno: `os.getenv("BACKEND_URL", "http://backend:8000")`.
   - Llamada HTTP con `requests.post(f"{BACKEND_URL}/predict", json=payload, timeout=10)`.
   - Manejo de excepciones de conexión amigables con `st.error` y tips de reintento.

4. **Dockerfile para Streamlit:**
   - Exponer puerto `8501`.
   - Configurar `HEALTHCHECK`.
   - Arrancar con `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`.
