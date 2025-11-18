import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Team 1 – Glass Request Tool", layout="wide")

API_URL = "https://script.google.com/macros/s/AKfycbyu7SrPievCnS0w9UW2v6WMc46med_HpzRGh92lqpiNawFzvURKqaq3o6ffUPtaeb_YWg/exec"

glass_options = [
    "5mm Pattern Glass Curves",
    "5mm Fluted Glass",
    "6mm Clear",
    "8mm Clear"
]

# -------------------------------
# SESSION STATE
# -------------------------------
if "preview_data" not in st.session_state:
    st.session_state.preview_data = []

# Used to force widget reset
if "form_nonce" not in st.session_state:
    st.session_state.form_nonce = 0

# -------------------------------
# CALCULATE SQM
# -------------------------------
def calc_sqm_mm(h, w, q):
    try:
        return (float(h) / 1000) * (float(w) / 1000) * float(q)
    except:
        return 0


# -------------------------------
# AUTO REQUEST NUMBER
# -------------------------------
def get_auto_request_number():
    return datetime.now().strftime("%Y%m%d%H%M%S")


# -------------------------------
# GOOGLE SHEETS SAVE
# -------------------------------
def save_to_google_sheets(data):
    try:
        r = requests.post(API_URL, json=data)
        return r.status_code == 200
    except:
        return False


# -----------------------------------
# FORM UI (USES NONCE TO RESET)
# -----------------------------------
def render_form():
    nonce = st.session_state.form_nonce  # Changing nonce redraws form

    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date", value=datetime.today(), key=f"date_{nonce}")
        project_code = st.text_input("Project Code", key=f"project_code_{nonce}")
        project_name = st.text_input("Project Name", key=f"project_name_{nonce}")
        customer_name = st.text_input("Customer Name", key=f"customer_name_{nonce}")

    with col2:
        project_sqm = st.number_input("Project SQM", min_value=0.0, key=f"project_sqm_{nonce}")
        cutting = st.text_input("Cutting list received", key=f"cutting_{nonce}")
        glass_desc = st.selectbox("Glass Description", glass_options, key=f"glass_desc_{nonce}")

    with col3:
        height_mm = st.number_input("Glass Height (mm)", min_value=0.0, key=f"height_mm_{nonce}")
        width_mm = st.number_input("Glass Width (mm)", min_value=0.0, key=f"width_mm_{nonce}")
        qty = st.number_input("Optimize Qty", min_value=0, key=f"qty_{nonce}")
        wastage = st.number_input("Wastage %", min_value=0.0, key=f"wastage_{nonce}")

    remarks_t1 = st.text_area("Team 1 Remarks", key=f"remarks_{nonce}")

    sqm = calc_sqm_mm(height_mm, width_mm, qty)
    st.info(f"Calculated SQM: **{sqm:.4f} m²**")

    request_number = get_auto_request_number()
    st.success(f"Auto Request Number: {request_number}")

    # SAVE BUTTON
    if st.button("➕ ADD REQUEST", use_container_width=True):

        new_entry = {
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

        success = save_to_google_sheets(new_entry)

        if success:
        st.session_state.preview_data.append(new_entry)
        st.success("✅ Request saved to Google Sheets!")
    
        # Force reset form
        st.session_state.form_nonce += 1
        st.rerun()
    else:
        st.error("❌ Failed to save request")


# ---------------------------------
# PAGE UI
# ---------------------------------
st.title("📦 Team 1 – Add New Glass Request")

render_form()

# -------------------------
# PREVIEW TABLE
# -------------------------
if len(st.session_state.preview_data) > 0:
    st.subheader("🔍 Preview – All Added Requests")
    df_preview = pd.DataFrame(st.session_state.preview_data)
    st.dataframe(df_preview, use_container_width=True)

    st.download_button(
        "⬇️ Download All Requests",
        data=df_preview.to_csv(index=False).encode(),
        file_name="all_requests.csv",
        mime="text/csv"
    )

