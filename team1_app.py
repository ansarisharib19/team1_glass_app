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
        df = pd.read
