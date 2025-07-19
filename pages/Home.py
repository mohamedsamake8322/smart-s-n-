import streamlit as st
from streamlit_dashboard.components.ndvi_viewer import show_ndvi
from streamlit_dashboard.components.npk_recommender import show_npk_tool
from streamlit_dashboard.components.postgres_browser import show_db_browser

st.set_page_config(page_title="SènèSmart", layout="wide")

st.title("🌱 Bienvenue sur la plateforme SènèSmart")
st.markdown("**Agriculture intelligente, recommandations basées sur données NDVI, sols, climat et productions.**")

st.image("assets/banner_agriculture.jpg", use_column_width=True)

section = st.radio("🌾 Que souhaitez-vous explorer ?", ["NDVI Explorer", "Recommandation NPK", "Base de données"])

if section == "NDVI Explorer":
    show_ndvi()
elif section == "Recommandation NPK":
    show_npk_tool()
elif section == "Base de données":
    show_db_browser()
