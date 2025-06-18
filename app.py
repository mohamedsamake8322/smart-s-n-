﻿import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from utils.weather_api import WeatherAPI
from utils.visualization import create_overview_charts
from datetime import datetime
from utils.voice_assistant import voice_assistant
from utils.micro_input import get_voice_input
from utils.animations import typewriting_effect, pulsing_title
# âœ… Configuration de la page (doit Ãªtre la premiÃ¨re commande Streamlit)
st.set_page_config(
    page_title="SÃ¨nÃ¨Smart Yield Predictor",
    page_icon="ðŸŒ¾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# âœ… Effet dâ€™apparition progressif sur le titre
title_placeholder = st.empty()
typewriting_effect(title_placeholder, "ðŸŒ¾ SÃ¨nÃ¨Smart Yield Predictor")


# âœ… Effet de "typewriting" sur le sous-titre
subtitle_placeholder = st.empty()
typewriting_effect(subtitle_placeholder, "### ðŸš€ SÃ¨nÃ¨Smart Yield Predictor: Cultivating the Future with AI!ðŸŒ¾ðŸŒ ðŸŒ±Optimize your crops, predict your harvests, and boost productivity with the power of artificial intelligence. With SÃ¨nÃ¨Smart Yield Predictor, transform agricultural data into smart decisions and maximize your yields ðŸ“ˆ.")
pulsing_title(components)
# ðŸ”¹ Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("Use the pages in the sidebar to navigate through different features:")
st.sidebar.markdown("- **Dashboard**: Overview of your agricultural data")
st.sidebar.markdown("- **Yield Prediction**: ML-powered crop yield forecasting")
st.sidebar.markdown("- **Weather Data**: Real-time and historical weather information")
st.sidebar.markdown("- **Soil Monitoring**: Soil condition analysis")
st.sidebar.markdown("- **Data Upload**: Import your agricultural datasets")

# âœ… Indicateur de dÃ©marrage
st.write("ðŸš€ Smart Fertilization App is running!")


 # ðŸ”§ Forcer Streamlit Cloud Ã  utiliser le bon port
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
    **ðŸ”¬ Advanced Analytics**
    - Machine learning-powered yield predictions
    - Statistical analysis of agricultural metrics
    - Trend analysis and forecasting

    **ðŸŒ¤ï¸ Weather Intelligence**
    - Real-time weather data integration
    - Historical weather pattern analysis
    - Weather-based risk assessment

    **ðŸ“Š Data Visualization**
    - Interactive charts and graphs
    - Customizable dashboards
    - Export capabilities for reports

    **ðŸŒ± Soil Monitoring**
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
    if st.button("ðŸ”® Make Yield Prediction", use_container_width=True):
        st.switch_page("pages/2_Yield_Prediction.py")

with col2:
    if st.button("ðŸ“Š View Dashboard", use_container_width=True):
        st.switch_page("pages/1_Dashboard.py")

with col3:
    if st.button("ðŸ“ Upload Data", use_container_width=True):
        st.switch_page("pages/5_Data_Upload.py")
st.title("ðŸ§  Smart Voice Assistant for Farmers")

user_message = st.text_input("Ask your question here (in text)")

if user_message:
    response = voice_assistant.get_response(user_message)
    st.markdown("### ðŸ¤– Assistant's Response:")
    st.write(response['text'])

    # Handle actions
    if response['action'] == "open_weather_dashboard":
        st.info("ðŸ“¡ Opening the weather moduleâ€¦ (to be implemented)")
    elif response['action'] == "analyze_image":
        st.warning("ðŸ–¼ï¸ Image analysis awaiting your photoâ€¦")

if st.button("ðŸŽ™ï¸ Speak now"):
    user_message = get_voice_input()
    st.write(f"ðŸ—£ï¸ You said: {user_message}")
    response = voice_assistant.get_response(user_message)
    st.write(response['text'])

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 20px;'>
    ðŸŒ¾ SÃ¨nÃ¨Smart Yield Predictor - Empowering African farmers with AI-driven insights
    ðŸš€ Developed by <strong>plateforme-agricole-complete-v2 SAMAKE</strong> | Precision farming for a better future
    </div>
    """,
    unsafe_allow_html=True
)

