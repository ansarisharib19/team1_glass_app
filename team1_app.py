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
