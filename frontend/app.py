"""
Customer Churn Prediction — Streamlit Frontend
Run: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import os

# ── Config ─────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:5000")

# ── Page setup ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Churn Predictor",
    page_icon="📊",
    layout="centered",
)

# ── Inject CSS (reference: clean underline-input style) ────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #ffffff;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 4rem 2rem 4rem; max-width: 900px; }

/* ── Title block ── */
.page-title {
    font-size: 3rem;
    font-weight: 900;
    color: #111;
    line-height: 1.1;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    color: #444;
    margin-bottom: 0.8rem;
}
.page-subtitle::before { content: "— "; color: #e0245e; }
.page-desc {
    font-size: 0.95rem;
    color: #555;
    margin-bottom: 2.5rem;
    max-width: 560px;
    line-height: 1.6;
}

/* ── Section label ── */
.field-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #888;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ── Streamlit input overrides → underline style ── */
div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div:first-child {
    background-color: transparent !important;
    border: none !important;
    border-bottom: 2px solid #d0d0d0 !important;
    border-radius: 0 !important;
    padding-left: 0 !important;
    box-shadow: none !important;
}
div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:first-child:focus-within {
    border-bottom: 2px solid #e0245e !important;
}
div[data-baseweb="input"] input,
div[data-baseweb="select"] input {
    font-size: 1rem !important;
    color: #111 !important;
    padding-left: 0 !important;
}
div[data-baseweb="select"] svg { color: #888; }

/* Slider */
div[data-testid="stSlider"] > div { padding-top: 0.4rem; }
div[data-testid="stSlider"] [role="slider"] {
    background-color: #e0245e !important;
}
div[data-testid="stSlider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-testid="stTickBarMax"] {
    color: #888;
    font-size: 0.75rem;
}

/* Number input */
div[data-testid="stNumberInput"] input {
    border-bottom: 2px solid #d0d0d0 !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
    border-radius: 0 !important;
    padding-left: 0 !important;
    font-size: 1rem;
}

/* ── Submit button ── */
div[data-testid="stButton"] > button {
    background-color: #e0245e !important;
    color: #fff !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.7rem 2.5rem !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    cursor: pointer;
    transition: background 0.2s;
}
div[data-testid="stButton"] > button:hover {
    background-color: #b8003f !important;
}

/* ── Status badge ── */
.status-ok  { color: #27ae60; font-weight: 600; font-size: 0.85rem; }
.status-err { color: #e0245e; font-weight: 600; font-size: 0.85rem; }

/* ── Result card ── */
.result-card {
    border-left: 4px solid #e0245e;
    background: #fdf4f7;
    padding: 1.2rem 1.5rem;
    border-radius: 4px;
    margin-top: 1.5rem;
}
.result-card.safe {
    border-left-color: #27ae60;
    background: #f0fdf5;
}
.result-label {
    font-size: 1.4rem;
    font-weight: 800;
    color: #111;
    margin-bottom: 0.3rem;
}
.result-prob {
    font-size: 0.9rem;
    color: #555;
}

/* Divider */
.thin-rule {
    border: none;
    border-top: 1px solid #eee;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Check API status (non-blocking) ────────────────────────────────────────
def check_api():
    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        return r.status_code == 200, r.json()
    except Exception:
        return False, {}

api_ok, api_info = check_api()

# ── Page Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class='page-title'>Customer Churn<br>Predictor</div>
<div class='page-subtitle'>Prediction Request</div>
<p class='page-desc'>
    Enter customer details below to predict whether they are at risk of churning.
    The model will return a probability score and a risk label.
</p>
""", unsafe_allow_html=True)

# API status inline (not a sidebar blocker)
if api_ok:
    model_name = api_info.get("model", "Unknown")
    st.markdown(f"<span class='status-ok'>● API connected &nbsp;|&nbsp; Model: {model_name}</span>",
                unsafe_allow_html=True)
else:
    st.markdown(
        f"<span class='status-err'>● API unreachable — start it with: "
        f"<code>uvicorn app.main:app --reload --port 5000</code></span>",
        unsafe_allow_html=True
    )

st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

# ── Form ─────────────────────────────────────────────────────────────────────

st.markdown("#### Demographics")
col1, col2, col3 = st.columns(3)
with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=35, step=1, label_visibility="visible")
with col2:
    gender = st.selectbox("Gender", ["Male", "Female"])
with col3:
    tenure = st.number_input("Tenure (months)", min_value=0, max_value=120, value=24, step=1)

st.markdown("#### Behaviour & Support")
col4, col5, col6 = st.columns(3)
with col4:
    usage_frequency = st.number_input("Usage Frequency / month", 0, 30, 10, step=1)
with col5:
    support_calls = st.number_input("Support Calls / month", 0, 20, 2, step=1)
with col6:
    last_interaction = st.number_input("Days since last contact", 0, 60, 10, step=1)

st.markdown("#### Contract & Spend")
col7, col8, col9 = st.columns(3)
with col7:
    subscription_type = st.selectbox("Subscription", ["Basic", "Standard", "Premium"])
with col8:
    contract_length = st.selectbox("Contract", ["Monthly", "Quarterly", "Annual"])
with col9:
    payment_delay = st.number_input("Payment delay (days)", 0, 60, 5, step=1)

total_spend = st.number_input("Total Spend ($)", min_value=0.0, max_value=10000.0,
                               value=500.0, step=50.0)

st.markdown("<hr class='thin-rule'>", unsafe_allow_html=True)

# ── Submit ────────────────────────────────────────────────────────────────────
if st.button("PREDICT CHURN"):
    if not api_ok:
        st.error("❌ Cannot predict — API is not running. "
                 "Start it with: `uvicorn app.main:app --reload --port 5000`")
    else:
        payload = {
            "age": int(age),
            "tenure": int(tenure),
            "usage_frequency": int(usage_frequency),
            "support_calls": int(support_calls),
            "payment_delay": int(payment_delay),
            "total_spend": float(total_spend),
            "last_interaction": int(last_interaction),
            "gender": gender,
            "subscription_type": subscription_type,
            "contract_length": contract_length,
        }

        with st.spinner("Running prediction..."):
            try:
                response = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                result = response.json()

                pred = result["prediction"]
                prob = result["probability"]
                label = result["label"]
                model_name = result.get("model", "RandomForest")

                card_class = "result-card" if pred == 1 else "result-card safe"
                icon = "⚠️" if pred == 1 else "✅"
                detail = (
                    "This customer shows high churn risk. Consider a proactive retention action."
                    if pred == 1 else
                    "This customer is likely to stay. No immediate action needed."
                )

                st.markdown(f"""
                <div class='{card_class}'>
                    <div class='result-label'>{icon} {label}</div>
                    <div class='result-prob'>
                        Churn probability: <strong>{prob:.1%}</strong>
                        &nbsp;|&nbsp; Model: {model_name}
                    </div>
                    <p style='margin-top:0.6rem; color:#444; font-size:0.9rem;'>{detail}</p>
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Request failed: {e}")
