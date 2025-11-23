import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Team 1 – Glass Request Tool", layout="wide")

# =========================================================
# GOOGLE SHEET LINKS
# =========================================================

REQUEST_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1zCHYqqRwaekDMPj5uNxwOXnm92CnBffx_hbDzbJwSx8/export?format=csv"
)

GLASS_MASTER_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "17SlnhEb2w4SI-gIix5qA5FQePcqQB51R6YgXl-vUVoE/export?format=csv&gid=1918780294"
)

API_URL = (
    "https://script.google.com/macros/s/AKfycbyu7SrPievCnS0w9UW2v6WMc46med_HpzRGh92lqpiNawFzvURKqaq3o6ffUPtaeb_YWg/exec"
)

# =========================================================
# LOAD GLASS MASTER
# =========================================================
@st.cache_data(ttl=300)
def load_glass_master():
    try:
        df = pd.read_csv(GLASS_MASTER_CSV)
        return df
    except Exception as e:
        st.error(f"❌ Failed to load Glass Master: {e}")
        return pd.DataFrame()

master_df = load_glass_master()
glass_options = (
    master_df["Glass Description"].dropna().unique().tolist()
    if "Glass Description" in master_df.columns
    else []
)

# =========================================================
# FIXED REQUEST-NUMBER GENERATOR (NOW USES USER DATE)
# =========================================================
def generate_request_number(project_code, selected_date):
    """Generate request number MMYYNN-X based on user-selected date."""

    try:
        df = pd.read_csv(REQUEST_SHEET_CSV)
    except:
        df = pd.DataFrame()

    # Use USER DATE instead of today's device date
    today = pd.to_datetime(selected_date)

    MM = today.strftime("%m")
    YY = today.strftime("%y")

    project_code_str = str(project_code).strip()

    # CLEAN existing project list
    if "Project Code" in df.columns:
        raw_codes = df["Project Code"].astype(str).str.strip().tolist()
        valid_codes = [c for c in raw_codes if c.isdigit()]
    else:
        valid_codes = []

    project_list = []
    for c in valid_codes:
        if c not in project_list:
            project_list.append(c)

    # PROJECT SEQUENCE NUMBER (NN)
    if project_code_str in project_list:
        NN = project_list.index(project_code_str) + 1
    else:
        NN = len(project_list) + 1

    NN_str = f"{NN:02d}"
    base_number = f"{MM}{YY}{NN_str}"

    # INSTANCE NUMBER (X)
    if ("Project Code" in df.columns
        and "Date" in df.columns
        and "Request #" in df.columns):
        
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        df_project = df[df["Project Code"].astype(str).str.strip() == project_code_str]

        same_day = df_project[df_project["Date"].dt.date == today.date()]
        prev_days = df_project[df_project["Date"].dt.date != today.date()]

        if len(same_day) > 0:
            X = 1
        else:
            if prev_days.empty:
                X = 1
            else:
                last_req = str(prev_days.iloc[0]["Request #"])
                try:
                    last_x = int(last_req.split("-")[1])
                    X = last_x + 1
                except:
                    X = 1
    else:
        X = 1

    return f"{base_number}-{X}"

# =========================================================
# SESSION STATE
# =========================================================
if "preview_data" not in st.session_state:
    st.session_state.preview_data = []

if "nonce" not in st.session_state:
    st.session_state.nonce = 0

# =========================================================
# SAVE TO GOOGLE SHEETS
# =========================================================
def save_to_google_sheets(data):
    try:
        r = requests.post(API_URL, json=data)
        return r.status_code == 200
    except:
        return False

# =========================================================
# FORM UI
# =========================================================
def render_form():
    nonce = st.session_state.nonce

    st.title("📦 Team 1 – Add New Glass Request")

    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date", datetime.today(), key=f"date_{nonce}")
        project_code = st.text_input("Project Code", key=f"project_code_{nonce}")
        project_name = st.text_input("Project Name", key=f"project_name_{nonce}")
        customer_name = st.text_input("Customer Name", key=f"customer_{nonce}")

    with col2:
        project_sqm = st.number_input("Project SQM", min_value=0.0, key=f"sqm_{nonce}")
        cutting = st.text_input("Cutting list received", key=f"cutting_{nonce}")
        glass_desc = st.selectbox("Glass Description", glass_options, key=f"glass_{nonce}")

    with col3:
        height = st.number_input("Glass Height (mm)", 0.0, key=f"h_{nonce}")
        width = st.number_input("Glass Width (mm)", 0.0, key=f"w_{nonce}")
        qty = st.number_input("Optimize Qty", 0, key=f"qty_{nonce}")
        wastage = st.number_input("Wastage %", 0.0, key=f"wast_{nonce}")

    remarks = st.text_area("Team 1 Remarks", key=f"remarks_{nonce}")

    sqm = (height / 1000) * (width / 1000) * qty
    st.info(f"Calculated SQM: **{sqm:.4f} m²**")

    # GENERATE REQUEST NUMBER (FIX: USE SELECTED DATE)
    if project_code:
        request_number = generate_request_number(project_code, date)
        st.success(f"Auto Request Number: {request_number}")
    else:
        request_number = None

    if st.button("➕ ADD REQUEST", use_container_width=True):
        if not project_code:
            st.error("❌ Project Code is required.")
            return

        new_entry = {
            "Request #": request_number,
            "Date": date.strftime("%Y-%m-%d"),
            "Customer Name": customer_name,
            "Project Code": project_code,
            "Project Name": project_name,
            "Project SQM": project_sqm,
            "Cutting list received": cutting,
            "Glass Description": glass_desc,
            "Glass Height (mm)": height,
            "Glass Width (mm)": width,
            "Optimize Qty": qty,
            "Wastage %": wastage,
            "SQM": sqm,
            "Team 1 Remarks": remarks,
        }

        ok = save_to_google_sheets(new_entry)

        if ok:
            st.session_state.preview_data.append(new_entry)
            st.success("✅ Request saved successfully!")
            st.session_state.nonce += 1
            st.rerun()
        else:
            st.error("❌ Failed to save request.")

# =========================================================
# RENDER PAGE
# =========================================================
render_form()

# =========================================================
# PREVIEW TABLE
# =========================================================
if len(st.session_state.preview_data) > 0:
    st.subheader("🔍 Preview – Added Requests")
    df_prev = pd.DataFrame(st.session_state.preview_data)
    st.dataframe(df_prev, use_container_width=True)

    st.download_button(
        "⬇️ Download All Requests",
        data=df_prev.to_csv(index=False).encode(),
        file_name="all_requests.csv",
        mime="text/csv",
    )
