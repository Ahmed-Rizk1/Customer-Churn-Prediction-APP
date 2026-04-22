"""
Customer Churn Prediction — Hugging Face Spaces Streamlit App
No API required! This loads the model directly.
"""

import streamlit as st
import pickle
import json
import pandas as pd
import numpy as np
import os

# ── Page setup ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Predictor",
    page_icon="📊",
    layout="centered",
)

# ── Load Model Artifacts ───────────────────────────────────────────────────
# In Hugging Face Spaces, all files are usually in the same root folder.
@st.cache_resource
def load_models():
    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("encoder.pkl", "rb") as f:
            encoder = pickle.load(f)
        with open("model_metadata.json") as f:
            metadata = json.load(f)
        return model, encoder, metadata
    except FileNotFoundError:
        return None, None, None

model, encoder, metadata = load_models()

# ── Preprocessing ──────────────────────────────────────────────────────────
CAT_FEATURES = ["gender", "subscription_type", "contract_length"]

def preprocess(raw: dict) -> np.ndarray:
    df = pd.DataFrame([raw])
    encoded = encoder.transform(df[CAT_FEATURES])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(CAT_FEATURES))
    
    numeric_cols = [c for c in df.columns if c not in CAT_FEATURES]
    X = pd.concat([df[numeric_cols].reset_index(drop=True), encoded_df], axis=1)
    
    # Reorder columns to match training exactly
    X = X.reindex(columns=metadata["features"], fill_value=0)
    return X.values

# ── Inject CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.page-title { font-size: 3rem; font-weight: 900; color: #111; line-height: 1.1; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.12em; color: #444; margin-bottom: 0.8rem; }
.page-subtitle::before { content: "— "; color: #e0245e; }
.page-desc { font-size: 0.95rem; color: #555; margin-bottom: 2.5rem; line-height: 1.6; }
div[data-testid="stButton"] > button { background-color: #e0245e !important; color: #fff !important; font-weight: 700 !important; }
.status-ok  { color: #27ae60; font-weight: 600; font-size: 0.85rem; }
.status-err { color: #e0245e; font-weight: 600; font-size: 0.85rem; }
.result-card { border-left: 4px solid #e0245e; background: #fdf4f7; padding: 1.2rem 1.5rem; border-radius: 4px; margin-top: 1.5rem; }
.result-card.safe { border-left-color: #27ae60; background: #f0fdf5; }
.result-label { font-size: 1.4rem; font-weight: 800; margin-bottom: 0.3rem; }
.result-prob { font-size: 0.9rem; color: #555; }
</style>
""", unsafe_allow_html=True)

# ── Page Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='page-title'>Customer Churn<br>Predictor</div>
<div class='page-subtitle'>Prediction Request</div>
<p class='page-desc'>
    Enter customer details below to predict whether they are at risk of churning.
</p>
""", unsafe_allow_html=True)

if model is not None:
    model_name = metadata.get("model_type", "RandomForest")
    st.markdown(f"<span class='status-ok'>● Model Loaded Successfully: {model_name}</span>", unsafe_allow_html=True)
else:
    st.markdown("<span class='status-err'>● Model files not found! Please upload model.pkl, encoder.pkl, and model_metadata.json</span>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Form ─────────────────────────────────────────────────────────────────────
st.markdown("#### Demographics")
col1, col2, col3 = st.columns(3)
with col1: age = st.number_input("Age", min_value=18, max_value=100, value=35)
with col2: gender = st.selectbox("Gender", ["Male", "Female"])
with col3: tenure = st.number_input("Tenure (months)", min_value=0, max_value=120, value=24)

st.markdown("#### Behaviour & Support")
col4, col5, col6 = st.columns(3)
with col4: usage_frequency = st.number_input("Usage Frequency / month", 0, 30, 10)
with col5: support_calls = st.number_input("Support Calls / month", 0, 20, 2)
with col6: last_interaction = st.number_input("Days since last contact", 0, 60, 10)

st.markdown("#### Contract & Spend")
col7, col8, col9 = st.columns(3)
with col7: subscription_type = st.selectbox("Subscription", ["Basic", "Standard", "Premium"])
with col8: contract_length = st.selectbox("Contract", ["Monthly", "Quarterly", "Annual"])
with col9: payment_delay = st.number_input("Payment delay (days)", 0, 60, 5)

total_spend = st.number_input("Total Spend ($)", 0.0, 10000.0, 500.0)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("PREDICT CHURN"):
    if model is None:
        st.error("❌ Cannot predict — Model artifacts are missing.")
    else:
        payload = {
            "age": age, "tenure": tenure, "usage_frequency": usage_frequency,
            "support_calls": support_calls, "payment_delay": payment_delay,
            "total_spend": total_spend, "last_interaction": last_interaction,
            "gender": gender, "subscription_type": subscription_type,
            "contract_length": contract_length,
        }

        with st.spinner("Running prediction..."):
            try:
                # Run prediction directly instead of API call
                X = preprocess(payload)
                pred = int(model.predict(X)[0])
                prob = float(model.predict_proba(X)[0][1])

                label = "Will Churn" if pred == 1 else "Will Stay"
                card_class = "result-card" if pred == 1 else "result-card safe"
                icon = "⚠️" if pred == 1 else "✅"
                detail = "This customer shows high churn risk." if pred == 1 else "This customer is likely to stay."

                st.markdown(f"""
                <div class='{card_class}'>
                    <div class='result-label'>{icon} {label}</div>
                    <div class='result-prob'>
                        Churn probability: <strong>{prob:.1%}</strong>
                    </div>
                    <p style='margin-top:0.6rem; color:#444; font-size:0.9rem;'>{detail}</p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Prediction failed: {e}")
