"""
Smart Fertilizer Streamlit Application

Main entry point for the Smart Fertilizer web application using Streamlit.
This application provides intelligent fertilizer recommendations for African agriculture.
"""
import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import json

# ✅ Résout le chemin racine du projet, même sur Streamlit Cloud
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent  # monte depuis /pages/
sys.path.insert(0, str(project_root))      # ajoute le projet à PYTHONPATH

# ✳️ Debug info (facultatif)
st.sidebar.info(f"📁 project_root: {project_root}")
st.sidebar.info(f"📦 sys.path[0]: {sys.path[0]}")

# ✅ Test d'import de l'interface principale
try:
    from smart_fertilizer.ui.smart_ui import SmartFertilizerUI
except Exception as e:
    import traceback
    st.error("❌ Problème d'import")
    st.code(traceback.format_exc())
    st.stop()
from modules.smart_fertilizer.ui.smart_ui import SmartFertilizerUI
from modules.smart_fertilizer.ui.crop_selector import CropSelector
from modules.smart_fertilizer.ui.translations import Translator
from modules.smart_fertilizer.core.smart_fertilizer_engine import SmartFertilizerEngine
from modules.smart_fertilizer.core.fertilizer_optimizer import FertilizerOptimizer
from modules.smart_fertilizer.core.smart_fertilization import SmartFertilization
from modules.smart_fertilizer.core.agronomic_knowledge_base import AgronomicKnowledgeBase
from modules.smart_fertilizer.core.regional_context import RegionalContext
from modules.smart_fertilizer.regions.region_selector import RegionSelector
from modules.smart_fertilizer.regions.regional_context import get_regional_config
from modules.smart_fertilizer.api.main import fertilizer_router
from modules.smart_fertilizer.api.models import FertilizerRequest
from modules.smart_fertilizer.exports.pdf_generator import PDFGenerator
from modules.smart_fertilizer.exports.export_utils import format_recommendation_data
from modules.smart_fertilizer.weather.weather_client import WeatherClient
from modules.smart_fertilizer.weather.iot_simulator import SoilSensorSimulator
# Configure Streamlit page
st.set_page_config(
    page_title="Smart Fertilizer - African Agriculture",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/smartfertilizer/help',
        'Report a bug': 'https://github.com/smartfertilizer/issues',
        'About': """
        # Smart Fertilizer Application

        **Version:** 1.0.0

        **Description:** Intelligent fertilizer recommendation system for African agriculture

        **Features:**
        - Soil analysis and interpretation
        - Crop-specific recommendations
        - Regional adaptation
        - Weather integration
        - IoT sensor support
        - Multi-language interface
        - PDF report generation

        **Data Sources:** FAO, ESDAC, ICAR/ICRISAT, NOAA/CHIRPS

        **Methodology:** STCR (Soil Test Crop Response)

        **Regions Supported:** West Africa, East Africa, Southern Africa, Central Africa

        **Contact:** support@smartfertilizer.org
        """
    }
)

def main():
    """Main application entry point"""

    try:
        # Import UI class from modular path
        from modules.smart_fertilizer.ui.smart_ui import SmartFertilizerUI

        # Initialize and render
        app_ui = SmartFertilizerUI()
        app_ui.render_main_interface()

    except ImportError as e:
        st.error(f"❌ Error importing application modules: {e}")
        st.info("Please ensure all required dependencies are installed.")

        with st.expander("📋 Installation Instructions"):
            st.markdown("""
            ### Required Dependencies

            ```bash
            pip install streamlit fastapi uvicorn pandas numpy plotly
            pip install requests reportlab openpyxl scikit-learn scipy
            ```

            ### Module structure must include:
            - `modules/smart_fertilizer/ui/`
            - `modules/smart_fertilizer/core/`
            - `modules/smart_fertilizer/api/`
            - `modules/smart_fertilizer/data/`
            - `modules/smart_fertilizer/exports/`
            """)
        st.stop()

    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.info("Please check your configuration and try again.")

        if st.button("🔄 Reload Application"):
            st.rerun()
        st.stop()

def check_system_status():
    """Check system status and display warnings if needed"""
    import os
    import warnings

    warnings.filterwarnings('ignore')

    base_dir = Path(__file__).parent.parent / "modules" / "smart_fertilizer"

    required_dirs = ['data', 'ui', 'core', 'api', 'exports']
    missing_dirs = [d for d in required_dirs if not (base_dir / d).exists()]
    if missing_dirs:
        st.sidebar.warning(f"⚠️ Missing directories: {', '.join(missing_dirs)}")

    required_files = [
        'data/crop_profiles.json',
        'data/regional_prices.json',
        'data/soil_samples.csv',
        'data/yield_training_data.csv'
    ]
    missing_files = [
        f for f in required_files if not (base_dir / f).exists()
    ]
    if missing_files:
        st.sidebar.info(f"ℹ️ Some data files are missing. Using defaults.")

def display_startup_info():
    if 'startup_info_shown' not in st.session_state:
        st.session_state.startup_info_shown = True
        st.balloons()
        check_system_status()

def handle_errors():
    def error_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            return
        error_msg = f"Error: {exc_type.__name__}: {exc_value}"
        st.error(f"❌ Application Error: {error_msg}")
        if st.button("📝 Report this Error"):
            st.info("Error reporting functionality would be implemented here.")
    sys.excepthook = error_handler

handle_errors()
display_startup_info()

if __name__ == "__main__":
    main()
