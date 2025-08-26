import streamlit as st
import os

st.set_page_config(page_title="🛠️ Corrections Admin", layout="wide")
st.title("🛠️ Corrections proposées par les utilisateurs")

corrections_file = "corrections_log.txt"

if os.path.exists(corrections_file):
    with open(corrections_file, "r", encoding="utf-8") as f:
        corrections = f.read()
    st.text_area("📋 Corrections enregistrées :", corrections, height=600)
else:
    st.warning("Aucune correction enregistrée pour le moment.")
