"""
Smart Fertilizer Streamlit Application (Multipage Compatible)

Used as a standalone page within Streamlit's `pages/` directory.
Provides intelligent fertilizer recommendations for African agriculture.
"""

import sys
from pathlib import Path
import streamlit as st
import json

# 🔧 Set project root path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 📂 Load data
data_dir = project_root / "SmartFertilizerPro" / "data"

crop_profiles_path = data_dir / "crop_profiles.json"
regional_prices_path = data_dir / "regional_prices.json"

if not crop_profiles_path.exists() or not regional_prices_path.exists():
    st.error("❌ Fichiers de données manquants dans SmartFertilizerPro/data/")
    st.stop()

with open(crop_profiles_path, encoding="utf-8") as f:
    crop_profiles = json.load(f)

with open(regional_prices_path, encoding="utf-8") as f:
    regional_prices = json.load(f)


# 🚀 Import core app modules
from SmartFertilizerPro.api import main as fertilizer_api
from SmartFertilizerPro.api.models import SoilAnalysis
from SmartFertilizerPro.core.smart_fertilizer_engine import SmartFertilizerEngine
from SmartFertilizerPro.core.smart_fertilization import SmartFertilizationEngine
from SmartFertilizerPro.core.fertilizer_optimizer import FertilizerOptimizer
from SmartFertilizerPro.core.agronomic_knowledge_base import get_nutrient_thresholds
from SmartFertilizerPro.core.regional_context import RegionalContext
from SmartFertilizerPro.exports.pdf_generator import generate_pdf_report
from SmartFertilizerPro.exports.export_utils import prepare_export_payload
from SmartFertilizerPro.regions.region_selector import get_region_by_gps
from SmartFertilizerPro.ui.smart_ui import SmartFertilizerUI
from SmartFertilizerPro.ui.crop_selector import get_crop_options
from SmartFertilizerPro.ui.translations import translate_label
from SmartFertilizerPro.weather.weather_client import fetch_weather_forecast
from SmartFertilizerPro.weather.iot_simulator import simulate_sensor_data
from SmartFertilizerPro.interfaces import run_smart_fertilizer_app

# ▶️ Launch the Smart Fertilizer interface
run_smart_fertilizer_app()

# Utiliser l'objet app ou les fonctions

# Aller à la racine du projet
app = fertilizer_api.app

# 🌿 Page configuration
st.set_page_config(
    page_title="Smart Fertilizer - African Agriculture",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/smartfertilizer/help",
        "Report a bug": "https://github.com/smartfertilizer/issues",
        "About": """
        # Smart Fertilizer Application

        **Version:** 1.0.0
        **Features:** Soil analysis, crop recommendations, weather & IoT support, multilingual UI, PDF exports
        **Regions:** West, East, Central, and Southern Africa
        **Sources:** FAO, ESDAC, ICRISAT, NOAA
        **Contact:** support@smartfertilizer.org
        """
    }
)

def main():
    try:
        from ui.smart_ui import SmartFertilizerUI
        app_ui = SmartFertilizerUI()
        app_ui.render_main_interface()

    except ImportError as e:
        st.error(f"❌ Module import failed: {e}")
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            **To resolve this issue:**

            - Ensure the following directories exist in your project root:
              - `ui/`, `core/`, `api/`, `data/`, `exports/`
            - Install required dependencies with:
              ```bash
              pip install -r requirements.txt
              ```

            **Common fixes:**
            - Check for missing or misnamed folders
            - Verify `ui.smart_ui.py` exists and contains `SmartFertilizerUI`
            """)
        st.stop()

    except Exception as e:
        st.error(f"❌ Unexpected Error: {e}")
        if st.button("🔄 Reload"):
            st.rerun()
        st.stop()

# Optional: system checks & welcome
def check_system_status():
    import os
    import warnings
    warnings.filterwarnings('ignore')

    required_dirs = ['data', 'ui', 'core', 'api', 'exports']
    missing_dirs = [d for d in required_dirs if not os.path.exists(project_root / d)]

    if missing_dirs:
        st.sidebar.warning(f"⚠️ Missing directories: {', '.join(missing_dirs)}")

    required_files = [
        'data/crop_profiles.json',
        'data/regional_prices.json',
        'data/soil_samples.csv',
        'data/yield_training_data.csv'
    ]
    missing_files = [f for f in required_files if not os.path.exists(project_root / f)]

    if missing_files:
        st.sidebar.info(f"ℹ️ Missing files: {', '.join(missing_files)}")

def display_startup_info():
    if 'startup_info_shown' not in st.session_state:
        st.session_state.startup_info_shown = True
        st.balloons()
        check_system_status()

def handle_errors():
    def error_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            return
        st.error(f"❌ Fatal error: {exc_type.__name__}: {exc_value}")
    sys.excepthook = error_handler

# 🌟 Init
handle_errors()
display_startup_info()
main()
