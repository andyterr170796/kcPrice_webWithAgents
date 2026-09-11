# ORQUESTADOR GENERAL DEL PROYECTO (Multi-Agente)

Este proyecto está dividido en 3 sub-agentes especializados organizados por carpeta. Cada uno tiene su propio `AGENTS.md` y conjunto de responsabilidades.

## Diagrama de Flujo y Orquestación (Graph TD)

```mermaid
graph TD
    %% Agente 1: Entrenamiento Secuencial (Bloqueante)
    subgraph F1["🟢 Fase 1: Agente 1 (model/ - Data & ML Scientist)"]
        SK1["🛠️ Skill: mae-feature-selection"] -.-> TRAIN["train.py<br/>(Selección de Features por MAE)"]
        EXCEL["kc_house_data_train.xlsx"] --> TRAIN
        TRAIN --> ART1["model/artifacts/house_price_model.joblib"]
        TRAIN --> ART2["model/artifacts/features_contract.json"]
        TRAIN --> ART3["model/artifacts/metrics.json"]
    end

    %% Fork: Ejecución en Paralelo gracias al Contrato de Artefactos
    ART2 ==>|Contrato Publicado| PARALLEL{"⚡ FORK: Ejecución en Paralelo"}

    %% Agente 2: Backend API & Docker (En paralelo con Agente 3)
    subgraph F2["🔵 Fase 2A: Agente 2 (backend/) [PARALELO]"]
        SK2["🛠️ Skill: fastapi-docker-serving"] -.-> MAIN["main.py (FastAPI)"]
        ART1 -.-> MAIN
        MAIN --> API["API Endpoints:<br/>/health<br/>/model-info<br/>/predict"]
        API --> DOCK_B["backend/Dockerfile"]
    end

    %% Agente 3: Frontend Web UI (En paralelo con Agente 2)
    subgraph F3["🟣 Fase 2B: Agente 3 (frontend/) [PARALELO]"]
        SK3["🛠️ Skill: streamlit-dashboard"] -.-> APP["app.py (Streamlit UI)"]
        APP --> DOCK_F["frontend/Dockerfile"]
    end

    PARALLEL --> F2
    PARALLEL --> F3

    %% Join: Orquestación Final con Docker Compose
    subgraph F4["📦 Fase 3: Despliegue Unificado (JOIN)"]
        DOCK_B --> COMPOSE["docker-compose.yml"]
        DOCK_F --> COMPOSE
        COMPOSE --> RUN["Red Docker:<br/>Backend :8000<br/>Frontend :8501"]
    end

    %% Comunicación en tiempo de ejecución
    APP -.->|HTTP POST /predict| API
```

## Asignación de Modelos LLM y Skills por Agente

| Sub-Agente   | Carpeta     | Color      | Modelo LLM    | Skill Asignada (`.agents/skills/`) | Modo de Ejecución |
| :----------- | :---------- | :--------- | :------------ | :--------------------------------- | :---------------- |
| **Agente 1** | `model/`    | 🟢 Verde   | **Gemini 3.6** | `mae-feature-selection`            | **Secuencial** (Paso 1, genera contrato) |
| **Agente 2** | `backend/`  | 🔵 Cian    | **Gemini 3.8** | `fastapi-docker-serving`           | **⚡ Paralelo** (Paso 2A, consume contrato) |
| **Agente 3** | `frontend/` | 🟣 Magenta | **Gemini 3.8** | `streamlit-dashboard`              | **⚡ Paralelo** (Paso 2B, consume contrato) |

> **Criterio de Selección de Modelos:**
> - **Gemini 3.6 (Model):** Optimizado para cálculo analítico, procesamiento de datos tabulares, bucles de entrenamiento y selección de features con mínima latencia y costo.
> - **Gemini 3.8 (Backend & Frontend):** Mayor capacidad de razonamiento, estándares de seguridad web (OWASP, validación estricta de esquemas, sanitización de inputs y CORS) y robustez en entornos productivos Docker.


## Reglas de Orquestación: Patrón Fork-Join (Paralelo)

1. **Fase 1 (🟢 Agente 1 - Bloqueante):**
   - Se ejecuta primero de forma obligatoria.
   - Entrena el modelo y publica el **contrato de datos** (`model/artifacts/features_contract.json`) junto al modelo `.joblib`.

2. **Fase 2 (⚡ Agente 2 y Agente 3 - En Paralelo):**
   - **Agente 2 (🔵 Backend):** Lee el contrato y construye la API FastAPI (`main.py`, `schemas.py`) y `Dockerfile`.
   - **Agente 3 (🟣 Frontend):** Lee el mismo contrato en paralelo y construye la interfaz Streamlit (`app.py`) con sus controles dinámicos y `Dockerfile`.
   - *¿Por qué pueden trabajar al mismo tiempo?* Porque ambos se basan en la especificación formal del contrato (`features_contract.json` y el endpoint acordado `POST /predict`), sin bloquearse mutuamente.

3. **Fase 3 (📦 Join & Despliegue):**
   - Una vez finalizados ambos agentes, se integra `docker-compose.yml` para levantar y conectar ambos servicios en una sola red.
