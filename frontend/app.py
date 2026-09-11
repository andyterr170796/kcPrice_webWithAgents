import os
import requests
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Predicción de Precios de Casas | King County",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado CSS para aspecto moderno y limpio
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-top: 1rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
    }
    .metric-label {
        font-size: 0.95rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# URL del backend (obtenida de variable de entorno o localhost por defecto)
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
# Alternativa fallback para desarrollo local fuera de docker
LOCAL_FALLBACK_URL = "http://localhost:8000"

def check_backend():
    for url in [BACKEND_URL, LOCAL_FALLBACK_URL]:
        try:
            r = requests.get(f"{url}/health", timeout=2)
            if r.status_code == 200:
                return url
        except Exception:
            continue
    return None

active_backend = check_backend()

# Header
st.markdown('<div class="main-header">🏡 Valuador Inteligente de Viviendas</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Modelo de Machine Learning entrenado con el dataset de King County minimizando MAE.</div>', unsafe_allow_html=True)

# Sidebar: Estado y Métricas del Modelo
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=600&q=80", use_container_width=True)
    st.header("⚙️ Estado del Servicio")
    if active_backend:
        st.success(f"Conectado al Backend: `{active_backend}`")
        try:
            info_res = requests.get(f"{active_backend}/model-info", timeout=3)
            if info_res.status_code == 200:
                info = info_res.json()
                st.markdown(f"**Algoritmo:** `{info.get('algorithm')}`")
                metrics = info.get("metrics", {})
                st.markdown(f"**MAE en Test:** `${metrics.get('test_mae', 0):,.2f} USD`")
                st.markdown(f"**R² Score:** `{metrics.get('test_r2', 0):.4f}`")
                st.markdown(f"**Total Features:** `{info.get('total_features')}`")
        except Exception:
            st.info("Obteniendo detalles del modelo...")
    else:
        st.warning("⚠️ Backend no detectado aún. Asegúrese de que el servicio esté corriendo en el puerto 8000.")

st.markdown("---")

# Formulario de entrada de características
st.subheader("📋 Ingrese las Características de la Propiedad")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("##### 📐 Dimensiones y Calidad")
    grade = st.slider("Grado de Calidad de Construcción (grade)", min_value=3, max_value=13, value=7, help="1-3 bajo, 7 promedio, 11-13 lujo")
    sqft_living = st.number_input("Área Habitable (sqft_living)", min_value=300, max_value=15000, value=1900, step=50)
    sqft_above = st.number_input("Área Sobre Superficie (sqft_above)", min_value=300, max_value=10000, value=1530, step=50)
    sqft_basement = st.number_input("Área de Sótano (sqft_basement)", min_value=0, max_value=5000, value=0, step=50)
    sqft_living15 = st.number_input("Área Habitable Vecinos (sqft_living15)", min_value=300, max_value=7000, value=1830, step=50)
    floors = st.selectbox("Número de Pisos (floors)", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5], index=0)

with col2:
    st.markdown("##### 🛏️ Habitaciones y Terreno")
    bedrooms = st.slider("Habitaciones (bedrooms)", min_value=1, max_value=10, value=3)
    bathrooms = st.slider("Baños (bathrooms)", min_value=1.0, max_value=7.0, value=2.0, step=0.25)
    condition = st.slider("Condición General (condition)", min_value=1, max_value=5, value=3, help="1 muy malo, 3 promedio, 5 excelente")
    sqft_lot = st.number_input("Tamaño del Lote (sqft_lot)", min_value=500, max_value=500000, value=7900, step=100)
    sqft_lot15 = st.number_input("Lote de los 15 Vecinos (sqft_lot15)", min_value=500, max_value=500000, value=7800, step=100)
    yr_built = st.number_input("Año de Construcción (yr_built)", min_value=1900, max_value=2026, value=1970)

with col3:
    st.markdown("##### 📍 Ubicación y Atributos Especiales")
    waterfront = st.selectbox("Vista al Agua (waterfront)", options=[("No", 0), ("Sí", 1)], format_func=lambda x: x[0])[1]
    view = st.slider("Calidad de Vista Panorámica (view)", min_value=0, max_value=4, value=0)
    yr_renovated = st.number_input("Año de Renovación (0 = No renovado)", min_value=0, max_value=2026, value=0)
    zipcode = st.number_input("Código Postal (zipcode)", min_value=98001, max_value=98199, value=98065)
    lat = st.number_input("Latitud (lat)", min_value=47.15, max_value=47.80, value=47.5729, format="%.4f")
    long = st.number_input("Longitud (long)", min_value=-122.55, max_value=-121.30, value=-122.2310, format="%.4f")

st.markdown("---")

predict_btn = st.button("🚀 Calcular Estimación de Precio", type="primary", use_container_width=True)

if predict_btn:
    backend_to_use = active_backend if active_backend else LOCAL_FALLBACK_URL
    payload = {
        "grade": int(grade),
        "sqft_living": int(sqft_living),
        "lat": float(lat),
        "long": float(long),
        "sqft_living15": int(sqft_living15),
        "yr_built": int(yr_built),
        "waterfront": int(waterfront),
        "sqft_above": int(sqft_above),
        "sqft_lot": int(sqft_lot),
        "zipcode": int(zipcode),
        "sqft_lot15": int(sqft_lot15),
        "view": int(view),
        "bathrooms": float(bathrooms),
        "sqft_basement": int(sqft_basement),
        "condition": int(condition),
        "bedrooms": int(bedrooms),
        "yr_renovated": int(yr_renovated),
        "floors": float(floors)
    }

    with st.spinner("Consultando modelo de inferencia en el backend..."):
        try:
            response = requests.post(f"{backend_to_use}/predict", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                price = result["estimated_price"]
                formatted_price = result["formatted_price"]
                mae = result["mae_margin"]
                
                st.balloons()
                
                res_col1, res_col2 = st.columns([2, 1])
                with res_col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">PRECIO ESTIMADO DE MERCADO</div>
                        <div class="metric-value">{formatted_price}</div>
                        <div class="metric-label">Margen de Error Absoluto Medio (MAE): ± ${mae:,.2f} USD</div>
                    </div>
                    """, unsafe_allow_html=True)
                with res_col2:
                    st.info(f"""
                    **Resumen de la Propiedad:**
                    - **Área:** {sqft_living:,} sqft
                    - **Dormitorios:** {bedrooms} | **Baños:** {bathrooms}
                    - **Grado Calidad:** {grade}/13
                    - **Rango sugerido:** ${(price - mae):,.0f} - ${(price + mae):,.0f} USD
                    """)
            else:
                st.error(f"Error en la respuesta del backend ({response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError:
            st.error(f"No fue posible conectar con el backend en `{backend_to_use}`. Verifique que el servicio esté activo.")
        except Exception as e:
            st.error(f"Error inesperado: {str(e)}")
