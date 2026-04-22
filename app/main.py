"""
Customer Churn Prediction — FastAPI Backend
============================================
One file. Easy to read. Every section is labeled.

⚠️  Always run from the PROJECT ROOT (the folder that contains app/, models/, frontend/)

    cd project/
    uvicorn app.main:app --reload --port 5000

Then open:  http://localhost:5000/docs
"""

# ── Imports ──────────────────────────────────────────────────────────────────

import pickle
import json
import numpy as np
import pandas as pd
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, List

# ── Paths ────────────────────────────────────────────────────────────────────

MODELS_DIR = Path(__file__).resolve().parents[1] / "models"

# ── Load Model Artifacts ─────────────────────────────────────────────────────
#
# We load ONCE at startup — not on every request.
# Loading from disk is slow; keeping them in memory is fast.
#
# We need three things:
#   model   → the trained RandomForest (makes predictions)
#   encoder → the OneHotEncoder (converts text categories → numbers)
#   meta    → saved column names & feature order (must match training exactly)

model = None
encoder = None
feature_names = None
metadata = None


def load_artifacts():
    """Load all model artifacts from the models/ folder.

    Wrapped in try/except so the app starts cleanly on Vercel/serverless
    even when .pkl files are not bundled. Prediction endpoints will return
    a 503 instead of crashing the whole process.
    """
    global model, encoder, feature_names, metadata

    print("Loading model artifacts...")

    try:
        with open(MODELS_DIR / "model.pkl", "rb") as f:
            model = pickle.load(f)

        with open(MODELS_DIR / "encoder.pkl", "rb") as f:
            encoder = pickle.load(f)

        with open(MODELS_DIR / "model_metadata.json") as f:
            metadata = json.load(f)

        feature_names = metadata["features"]

        print(f"✅ Model loaded: {metadata['model_type']}")
        print(f"   Accuracy: {metadata['metrics']['accuracy']:.4f} | F1: {metadata['metrics']['f1']:.4f}")

    except FileNotFoundError as e:
        print(f"⚠️  Model artifacts not found: {e}")
        print("   API will start but /predict endpoints will return 503.")
        print("   Upload model files to the models/ directory to enable predictions.")


# ── Startup / Shutdown ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs at startup. Load model here so it is ready before any request."""
    load_artifacts()
    yield  # app runs
    print("Shutting down.")


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Churn Prediction API",
    description="Predicts whether a customer will churn.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the Streamlit frontend to call us (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas (Request & Response) ─────────────────────────────────────────────
#
# Pydantic validates input automatically.
# If a client sends a wrong type or value → 422 error with a clear message.
# This protects the model from bad input.

class CustomerInput(BaseModel):
    age: int               = Field(..., ge=18, le=100, description="Age of the customer")
    tenure: int            = Field(..., ge=0,          description="Months as a customer")
    usage_frequency: int   = Field(..., ge=0,          description="Times used service last month")
    support_calls: int     = Field(..., ge=0,          description="Support calls last month")
    payment_delay: int     = Field(..., ge=0,          description="Payment delay in days")
    total_spend: float     = Field(..., ge=0,          description="Total lifetime spend ($)")
    last_interaction: int  = Field(..., ge=0,          description="Days since last interaction")
    gender: Literal["Male", "Female"]
    subscription_type: Literal["Basic", "Standard", "Premium"]
    contract_length: Literal["Monthly", "Quarterly", "Annual"]

    model_config = {
        "json_schema_extra": {
            "example": {
                "age": 35, "tenure": 24, "usage_frequency": 10,
                "support_calls": 8, "payment_delay": 20,
                "total_spend": 400.0, "last_interaction": 5,
                "gender": "Male", "subscription_type": "Basic",
                "contract_length": "Monthly",
            }
        }
    }


class PredictionOut(BaseModel):
    prediction: int    # 0 = stays, 1 = churns
    probability: float # 0.0 → 1.0 chance of churning
    label: str         # "Will Churn" / "Will Stay"
    model: str         # name of the model that made the prediction


# ── Preprocessing ─────────────────────────────────────────────────────────────
#
# This MUST exactly mirror what was done during training.
# The most common production bug is "training-serving skew":
# training preprocessed data one way, inference does it differently → wrong predictions.

CAT_FEATURES = ["gender", "subscription_type", "contract_length"]


def preprocess(raw: dict) -> np.ndarray:
    """Convert raw customer dict → model-ready numpy array."""

    df = pd.DataFrame([raw])

    # 1. Encode categorical columns using the SAVED encoder
    #    We use the same encoder from training — same categories, same column order.
    encoded = encoder.transform(df[CAT_FEATURES])
    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(CAT_FEATURES)
    )

    # 2. Combine numeric + encoded columns
    numeric_cols = [c for c in df.columns if c not in CAT_FEATURES]
    X = pd.concat([df[numeric_cols].reset_index(drop=True), encoded_df], axis=1)

    # 3. Reorder to match training column order (critical!)
    X = X.reindex(columns=feature_names, fill_value=0)

    return X.values


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health():
    """Is the API alive? What model is loaded?"""
    if metadata is None:
        return {
            "status": "degraded",
            "model": None,
            "version": "1.0.0",
            "detail": "Model artifacts not loaded — predictions unavailable.",
        }
    return {
        "status": "ok",
        "model": metadata["model_type"],
        "version": "1.0.0",
    }


@app.get("/model-info", tags=["Info"])
def model_info():
    """Training metrics and metadata for the loaded model."""
    return metadata


@app.post("/predict", response_model=PredictionOut, tags=["Prediction"])
def predict(customer: CustomerInput):
    """
    Predict churn for a single customer.

    Returns:
    - **prediction**: 0 (stays) or 1 (churns)
    - **probability**: chance of churning (0.0 – 1.0)
    - **label**: human-readable result
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Upload model artifacts to the models/ directory.",
        )
    try:
        X = preprocess(customer.model_dump())

        pred = int(model.predict(X)[0])
        prob = float(model.predict_proba(X)[0][1])

        return {
            "prediction": pred,
            "probability": round(prob, 4),
            "label": "Will Churn" if pred == 1 else "Will Stay",
            "model": metadata["model_type"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict-batch", tags=["Prediction"])
def predict_batch(customers: List[CustomerInput]):
    """Predict churn for a list of customers in one call."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Upload model artifacts to the models/ directory.",
        )
    results = []
    for c in customers:
        X = preprocess(c.model_dump())
        pred = int(model.predict(X)[0])
        prob = float(model.predict_proba(X)[0][1])
        results.append({
            "prediction": pred,
            "probability": round(prob, 4),
            "label": "Will Churn" if pred == 1 else "Will Stay",
        })
    return {"count": len(results), "results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)