# 📊 Customer Churn Prediction

> A minimal, student-friendly MLOps project.  
> Model trained in the notebooks → served via **FastAPI** → shown in a **Streamlit** UI → packaged with **Docker**.

---

## 📁 Structure

```
project/
├── app/
│   └── main.py          ← FastAPI: routes + preprocessing + startup
├── frontend/
│   └── app.py           ← Streamlit UI
├── models/
│   ├── model.pkl        ← Trained RandomForest (from notebook)
│   ├── encoder.pkl      ← Fitted OneHotEncoder (from notebook)
│   └── model_metadata.json
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── DEPLOYMENT.md
```

**That's it.** Three Python files. One for the API, one for the UI.

---

## 🚀 Run Locally

```bash
# 1. Install dependencies (.venv/Scripts/activate)
pip install -r requirements.txt

# 2. Start the API
uvicorn app.main:app --reload
# → http://localhost:8000/docs  (try the API interactively)

# 3. Start the frontend (new terminal)
streamlit run frontend/app.py
# → http://localhost:8501
```

---

## 🐳 Run with Docker (API + UI together)

```bash
docker-compose up --build
# API  → http://localhost:8000/docs
# UI   → http://localhost:8501
```

---

## 📡 API Endpoints

| Method | Path | What it does |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/model-info` | Model metrics |
| `POST` | `/predict` | Predict one customer |
| `POST` | `/predict-batch` | Predict many at once |

### Try it

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35, "tenure": 24, "usage_frequency": 10,
    "support_calls": 8, "payment_delay": 20, "total_spend": 400.0,
    "last_interaction": 5, "gender": "Male",
    "subscription_type": "Basic", "contract_length": "Monthly"
  }'
```

Response:
```json
{"prediction": 1, "probability": 0.87, "label": "Will Churn"}
```

---

## 🌐 Deploy

See **[DEPLOYMENT.md](DEPLOYMENT.md)** — four approaches covered:
- Render (free, 10 min)
- Railway (free, 5 min)
- AWS EC2 + Docker (production)
- Hugging Face Spaces (ML demos)
