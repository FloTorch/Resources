import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from config import settings


st.set_page_config(
    page_title="Loan Underwriter",
    page_icon="🏦",
)

st.title("🏦 Loan Underwriter")
st.write("Please fill out the application.")

# Create a form
with st.form("loan_form"):
    name = st.text_input("Name", "Jane Doe")
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    income = st.number_input("Income", min_value=0, value=450000)
    loan_amount = st.number_input("Loan Amount", min_value=0, value=100000)
    credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=720)
    existing_liabilities = st.number_input("Existing Liabilities", min_value=0, value=15000)
    purpose = st.text_input("Purpose", "Home Renovation")

    # Submit button
    submitted = st.form_submit_button("Submit")

# Create data folder
from pathlib import Path
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)  # make sure data/ exists
CSV_PATH = DATA_DIR / "loan_application_history.csv"

# Locate backend
BACKEND_URL = settings.backend_url

# Persist application history
try:
    df = pd.read_csv(CSV_PATH)
    st.session_state.history = df.to_dict("records")
except FileNotFoundError:
    st.session_state.history = []

if submitted:
    # Build payload
    data = {
        "loan_details": {
            "name": name,
            "age": age,
            "income": income,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            "existing_liabilities": existing_liabilities,
            "purpose": purpose
        }
    }
    
    loan_decision = "Undetermined"

    # Send request to FastAPI backend
    try:
        res = requests.post(BACKEND_URL, json=data)
        if res.status_code == 200:
            st.success("Response received!")
            data = res.json()["output"]
            loan_decision = data["loan_decision"]
            risk_assessment = data["risk_assessment"]
            if loan_decision == "Approved":
                st.markdown("## ✅ Loan Approved")
            else:
                st.markdown("## ❌ Loan Denied")
            st.write(risk_assessment)
            # st.json(res.json())  # Pretty print JSON response
        else:
            st.error(f"Error {res.status_code}: {res.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
        
    # Save loan application
    st.session_state.history.append({
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name,
        "Age": age,
        "Income": income,
        "Loan Amount": loan_amount,
        "Credit Score": credit_score,
        "Liabilities": existing_liabilities,
        "Purpose": purpose,
        "Result": loan_decision
    })
    pd.DataFrame(st.session_state.history).to_csv(CSV_PATH, index=False)


# Function to color rows
def highlight_result(row):
    if row["Result"] == "Approved":
        return ["background-color: #1c4c31"] * len(row)  # green
    elif row["Result"] == "Denied":
        return ["background-color: #572d31"] * len(row)  # red
    elif row["Result"] == "Undetermined":
        return ["background-color: #575115"] * len(row)  # yellow
    else:
        return [""] * len(row)  # no color

# Display history as table
df = pd.DataFrame(st.session_state.history)
if not df.empty:
    df = df.sort_values("Timestamp", ascending=False)
    df = df.style.apply(highlight_result, axis=1)
st.subheader("📊 History")
st.dataframe(df, width="stretch")