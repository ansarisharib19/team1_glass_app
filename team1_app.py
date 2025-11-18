import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --------------------------------------------------------
# CONFIG
# --------------------------------------------------------
st.set_page_config(page_title="Team 1 – Glass Request Tool", layout="wide")

MASTER_SHEET_CSV = "https://docs.google.com/spreadsheets/d/17SlnhEb2w4SI-gIix5qA5FQePcqQB51R6YgXl-vUVoE/export?format=csv"
API_URL = "https://script.google.com/macros/s/AKfycbxCZvecfhqqxHbOJ6klz7GIjsOr1qA_Dvot6l3Ep7DTb-UmeFUNVW4MsJZSiPFvGtB__Q/exec"

# --------------------------------------------------------
# LOAD MASTER GLASS LIST
# --------------------------------------------------------
@st.cache_data
def load_master():
    return pd.read_csv(MASTER_SHEET_CSV)

master_df = load_master()
glass_options = master_df["Glass Description"].dropna().unique().tolist()

# --------------------------------------------------------
# SQM CALCULATION
# --------------------------------------------------------
def calc_sqm_mm(h_mm, w_mm, qty):
    try:
        return (float(h_mm) / 1000) * (float(w_mm) / 1000) * float(qty)
    except:
        return 0

# --------------------------------------------------------
# UI
# --------------------------------------------------------
st.title("📦 Team 1 – Add New Glass Request")

col1, col2, col3 = st.columns(3)

with col1:
    date = st.date_input("Date", datetime.today())
    project_code = st.text_input("Project Code")
    project = st.text_input("Project Name")
    customer = st.text_input("Customer Name")

with col2:
    project_sqm = st.number_input("Project SQM", min_value=0.0)
    cutting = st.text_input("Cutting list received")
    glass_desc = st.selectbox("Glass Description", options=glass_options)

with col3:
    height_mm = st.number_input("Glass Height (mm)", min_value=0.0)
    width_mm = st.number_input("Glass Width (mm)", min_value=0.0)
    qty = st.number_input("Optimize Qty", min_value=0)
    wastage = st.number_input("Wastage %", min_value=0.0)

remarks_t1 = st.text_area("Team 1 Remarks")

sqm = calc_sqm_mm(height_mm, width_mm, qty)
st.info(f"Calculated SQM: **{sqm:.3f} m²**")

# --------------------------------------------------------
# REQUEST NUMBER (simple increasing count)
# --------------------------------------------------------
def generate_request_number():
    now = datetime.now()
    return f"{now.strftime('%Y%m%d%H%M%S')}"

request_number = generate_request_number()
st.success(f"Auto Request Number: {request_number}")

# --------------------------------------------------------
# ADD REQUEST
# --------------------------------------------------------
# --------------------------------------------------------
# SESSION STORAGE FOR REQUESTS
# --------------------------------------------------------
if "added_requests" not in st.session_state:
    st.session_state["added_requests"] = []


# --------------------------------------------------------
# ADD REQUEST BUTTON HANDLER
# --------------------------------------------------------
if st.button("➕ ADD REQUEST", use_container_width=True):

    new_row = {
        "Request #": request_number,
        "Date": str(date),
        "Customer Name": customer,
        "Project Code": project_code,
        "Project Name": project,
        "Project SQM": project_sqm,
        "Cutting list received": cutting,
        "Glass Description": glass_desc,
        "Glass Height (mm)": height_mm,
        "Glass Width (mm)": width_mm,
        "Optimize Qty": qty,
        "Wastage %": wastage,
        "SQM": sqm,
        "Team 1 Remarks": remarks_t1
    }

    # ---- SEND TO GOOGLE SHEETS API ----
    response = requests.post(API_URL, json=new_row)

    if response.status_code == 200:
        st.success("✅ Request saved!")

        # Store request locally for preview
        st.session_state["added_requests"].append(new_row)

        # RESET INPUTS
        st.session_state["project_code"] = ""
        st.session_state["project"] = ""
        st.session_state["customer"] = ""
        st.session_state["project_sqm"] = 0.0
        st.session_state["cutting"] = ""
        st.session_state["height_mm"] = 0.0
        st.session_state["width_mm"] = 0.0
        st.session_state["qty"] = 0
        st.session_state["wastage"] = 0.0
        st.session_state["remarks_t1"] = ""

    else:
        st.error("❌ Failed to save to Google Sheets")



