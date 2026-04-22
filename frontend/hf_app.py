"""
Customer Churn Prediction — Hugging Face Spaces Streamlit App
No API required! This loads the model directly.
"""

import streamlit as st
import requests
import json
import os

# ── Page setup ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Predictor",
    page_icon="📊",
    layout="centered",
)

# ── Backend API Setup ──────────────────────────────────────────────────────
# Set your deployed Render API URL here
API_URL = os.environ.get("BACKEND_API_URL", "https://your-render-backend-url.onrender.com")

def predict_churn(payload: dict):
    try:
        response = requests.post(f"{API_URL}/predict", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

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

st.markdown(f"<span class='status-ok'>● Configured to use Backend API: {API_URL}</span>", unsafe_allow_html=True)

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
    payload = {
        "age": age, "tenure": tenure, "usage_frequency": usage_frequency,
        "support_calls": support_calls, "payment_delay": payment_delay,
        "total_spend": total_spend, "last_interaction": last_interaction,
        "gender": gender, "subscription_type": subscription_type,
        "contract_length": contract_length,
    }

    with st.spinner("Calling Backend API..."):
        result = predict_churn(payload)
        
        if "error" in result:
            st.error(f"Prediction failed: Cannot connect to the API. {result['error']}")
        else:
            pred = result["prediction"]
            prob = result["probability"]

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
                <p style='margin-top:0.6rem; color:#888; font-size:0.75rem;'>Model: {result.get('model', 'API')}</p>
            </div>
            """, unsafe_allow_html=True)
