import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Team 1 – Glass Request Tool", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbyu7SrPievCnS0w9UW2v6WMc46med_HpzRGh92lqpiNawFzvURKqaq3o6ffUPtaeb_YWg/exec"

# Sample master list - replace with your Google Sheet or Excel
glass_options = [
    "5mm Pattern Glass Curves",
    "5mm Fluted Glass",
    "6mm Clear",
    "8mm Clear"
]

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "preview_data" not in st.session_state:
    st.session_state.preview_data = []

def init_field(name, default):
    if name not in st.session_state:
        st.session_state[name] = default

# Initialize all fields
init_field("date", datetime.today())
init_field("project_code", "")
init_field("project_name", "")
init_field("customer_name", "")
init_field("project_sqm", 0.0)
init_field("cutting", "")
init_field("glass_desc", glass_options[0])
init_field("height_mm", 0.0)
init_field("width_mm", 0.0)
init_field("qty", 0)
init_field("wastage", 0.0)
init_field("remarks_t1", "")

# ---------------------------------------------------------
# RESET FORM FUNCTION
# ---------------------------------------------------------
def reset_form():
    st.session_state.date = datetime.today()
    st.session_state.project_code = ""
    st.session_state.project_name = ""
    st.session_state.customer_name = ""
    st.session_state.project_sqm = 0.0
    st.session_state.cutting = ""
    st.session_state.glass_desc = glass_options[0]
    st.session_state.height_mm = 0.0
    st.session_state.width_mm = 0.0
    st.session_state.qty = 0
    st.session_state.wastage = 0.0
    st.session_state.remarks_t1 = ""

# ---------------------------------------------------------
# CALCULATE SQM
# ---------------------------------------------------------
def calc_sqm_mm(h, w, q):
    try:
        return (float(h) / 1000) * (float(w) / 1000) * float(q)
    except:
        return 0

# ---------------------------------------------------------
# GET REQUEST NUMBER
# ---------------------------------------------------------
def get_auto_request_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return timestamp

# ---------------------------------------------------------
# SEND DATA TO GOOGLE SHEETS
# ---------------------------------------------------------
def save_to_google_sheets(data):
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 200:
            return True
    except Exception as e:
        st.error(f"Google Sheets Error: {e}")
    return False

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("📦 Team 1 – Add New Glass Request")

col1, col2, col3 = st.columns(3)

with col1:
    date = st.date_input("Date", key="date")
    project_code = st.text_input("Project Code", key="project_code")
    project_name = st.text_input("Project Name", key="project_name")
    customer_name = st.text_input("Customer Name", key="customer_name")

with col2:
    project_sqm = st.number_input("Project SQM", key="project_sqm", min_value=0.0)
    cutting = st.text_input("Cutting list received", key="cutting")
    glass_desc = st.selectbox("Glass Description", glass_options, key="glass_desc")

with col3:
    height_mm = st.number_input("Glass Height (mm)", key="height_mm", min_value=0.0)
    width_mm = st.number_input("Glass Width (mm)", key="width_mm", min_value=0.0)
    qty = st.number_input("Optimize Qty", key="qty", min_value=0)
    wastage = st.number_input("Wastage %", key="wastage", min_value=0.0)

remarks_t1 = st.text_area("Team 1 Remarks", key="remarks_t1")

sqm = calc_sqm_mm(height_mm, width_mm, qty)

st.info(f"Calculated SQM: **{sqm:.4f} m²**")

request_number = get_auto_request_number()
st.success(f"Auto Request Number: {request_number}")

# ---------------------------------------------------------
# ADD REQUEST BUTTON
# ---------------------------------------------------------
if st.button("➕ ADD REQUEST", use_container_width=True):

    new_row = {
        "Request #": request_number,
        "Date": str(date),
        "Customer Name": customer_name,
        "Project Code": project_code,
        "Project Name": project_name,
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

    # Save to google sheets
    success = save_to_google_sheets(new_row)

    if success:
        st.session_state.preview_data.append(new_row)
        st.success("✅ Request saved to Google Sheets!")
        reset_form()
        st.rerun()
    else:
        st.error("❌ Failed to save request")

# ---------------------------------------------------------
# PREVIEW TABLE
# ---------------------------------------------------------
if len(st.session_state.preview_data) > 0:
    st.subheader("🔍 Preview – All Added Requests")
    df_preview = pd.DataFrame(st.session_state.preview_data)
    st.dataframe(df_preview, use_container_width=True)

    # DOWNLOAD ALL
    st.download_button(
        "⬇️ Download All Requests",
        data=df_preview.to_csv(index=False).encode("utf-8"),
        file_name="all_requests.csv",
        mime="text/csv"
    )
