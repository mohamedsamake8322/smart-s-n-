import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from utils.weather_api import WeatherAPI
from utils.visualization import create_overview_charts
import os

# Configuration de la page
st.set_page_config(
    page_title="Agricultural Analytics Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.write("🚀 L'application démarre... Vérification en cours.")

# Contenu principal
st.title("🌾 Agricultural Analytics Platform")
st.markdown("### Welcome to your comprehensive agricultural data analysis and prediction system")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the pages in the sidebar to navigate through different features:")
st.sidebar.markdown("- **Dashboard**: Overview of your agricultural data")
st.sidebar.markdown("- **Yield Prediction**: ML-powered crop yield forecasting")
st.sidebar.markdown("- **Weather Data**: Real-time and historical weather information")
st.sidebar.markdown("- **Soil Monitoring**: Soil condition analysis")
st.sidebar.markdown("- **Data Upload**: Import your agricultural datasets")

# Indicateur de démarrage
if __name__ == "__main__":
    st.write("🚀 Smart Fertilization App is running!")
    import sys

# 🔎 Vérifier que Streamlit tourne dans le bon contexte
if not hasattr(st.runtime, "scriptrunner"):
    st.error("❌ Streamlit semble ne pas fonctionner correctement dans son contexte.")
    sys.exit(1)  # Arrêter l'exécution si Streamlit Cloud ne reconnaît pas l'application
 # 🔧 Forcer Streamlit Cloud à utiliser le bon port
# Main dashboard overview
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Active Farms",
        value="--",
        help="Number of farms being monitored"
    )

with col2:
    st.metric(
        label="Current Season",
        value=datetime.now().strftime("%B %Y"),
        help="Current agricultural season"
    )

with col3:
    st.metric(
        label="Weather Status",
        value="--",
        help="Current weather conditions"
    )

with col4:
    st.metric(
        label="Predictions Made",
        value="--",
        help="Total number of yield predictions generated"
    )

# Quick overview section
st.markdown("---")
st.subheader("Platform Overview")

tab1, tab2, tab3 = st.tabs(["Features", "Getting Started", "Recent Activity"])

with tab1:
    st.markdown("""
    **🔬 Advanced Analytics**
    - Machine learning-powered yield predictions
    - Statistical analysis of agricultural metrics
    - Trend analysis and forecasting
    
    **🌤️ Weather Intelligence**
    - Real-time weather data integration
    - Historical weather pattern analysis
    - Weather-based risk assessment
    
    **📊 Data Visualization**
    - Interactive charts and graphs
    - Customizable dashboards
    - Export capabilities for reports
    
    **🌱 Soil Monitoring**
    - Soil condition analysis
    - Nutrient level tracking
    - pH and moisture monitoring
    """)

with tab2:
    st.markdown("""
    **Step 1: Upload Your Data**
    - Go to the Data Upload page
    - Upload your CSV/Excel files with agricultural data
    - Ensure data includes fields like crop type, yield, weather conditions
    
    **Step 2: Configure Weather Monitoring**
    - Visit the Weather Data page
    - Set your location for weather tracking
    - Review current and historical weather data
    
    **Step 3: Generate Predictions**
    - Use the Yield Prediction page
    - Input your crop and field parameters
    - Get ML-powered yield forecasts
    
    **Step 4: Monitor and Analyze**
    - Use the Dashboard for comprehensive overview
    - Track soil conditions on the Soil Monitoring page
    - Generate reports and insights
    """)

with tab3:
    st.info("No recent activity to display. Start by uploading data or making predictions.")

# Quick actions
st.markdown("---")
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔮 Make Yield Prediction", use_container_width=True):
        st.switch_page("pages/2_Yield_Prediction.py")

with col2:
    if st.button("📊 View Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with col3:
    if st.button("📁 Upload Data", use_container_width=True):
        st.switch_page("pages/5_Data_Upload.py")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 20px;'>
    Agricultural Analytics Platform - Empowering farmers with data-driven insights
    </div>
    """,
    unsafe_allow_html=True
)
