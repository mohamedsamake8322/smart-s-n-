"""
Smart Fertilizer Streamlit Application

Main entry point for the Smart Fertilizer web application using Streamlit.
This application provides intelligent fertilizer recommendations for African agriculture.
"""

# --------------------------
# 🌱 Initialisation Streamlit
# --------------------------
import streamlit as st  # type: ignore
import sys
import os
from pathlib import Path
import pandas as pd
import json

# --------------------------
# 🔍 Détection du chemin racine du projet
# --------------------------
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
sys.path.insert(0, str(project_root))  # Ajoute la racine du projet à PYTHONPATH

# 🛠️ Infos de debug (facultatif pour voir l'environnement)
st.sidebar.subheader("🛠️ Chemins et environnement")
st.sidebar.info(f"📁 Racine projet : {project_root}")
st.sidebar.info(f"📦 sys.path[0] : {sys.path[0]}")
if os.path.exists(project_root / "modules"):
    st.sidebar.success("✅ Le dossier modules/ est bien détecté")
else:
    st.sidebar.error("🚫 Le dossier modules/ n'est pas trouvé")

# --------------------------
# 🌍 Chargement des données régionales
# --------------------------
try:
    from modules.smart_fertilizer.regions.regional_context import get_regional_config

    region_name = "west_africa"
    region_info = get_regional_config(region_name)

    st.markdown(f"### 🌍 Contexte : {region_name.replace('_', ' ').title()}")
    st.json(region_info)

except Exception as e:
    import traceback
    st.error("❌ Erreur lors de l'import ou du chargement du contexte régional")
    st.code(traceback.format_exc())
    st.stop()

# --------------------------
# ⚙️ Imports principaux de l'application
# --------------------------
try:
    # 🌿 Interface Utilisateur
    from modules.smart_fertilizer.ui.smart_ui import SmartFertilizerUI
    from modules.smart_fertilizer.ui.crop_selector import CropSelector
    from modules.smart_fertilizer.ui.translations import Translator

    # 🔬 Moteur de recommandation
    from modules.smart_fertilizer.core.smart_fertilizer_engine import SmartFertilizerEngine
    from modules.smart_fertilizer.core.fertilizer_optimizer import FertilizerOptimizer
    from modules.smart_fertilizer.core.smart_fertilization import SmartFertilization
    from modules.smart_fertilizer.core.agronomic_knowledge_base import AgronomicKnowledgeBase
    from modules.smart_fertilizer.core.regional_context import RegionalContext

    # 🌍 Contexte Régional
    from modules.smart_fertilizer.regions.region_selector import RegionSelector

    # 🚀 API interne
    from modules.smart_fertilizer.api.main import fertilizer_router
    from modules.smart_fertilizer.api.models import FertilizerRequest

    # 🧾 Génération de rapports
    from modules.smart_fertilizer.exports.pdf_generator import PDFGenerator
    from modules.smart_fertilizer.exports.export_utils import format_recommendation_data

    # ☁️ Données météo et capteurs
    from modules.smart_fertilizer.weather.weather_client import WeatherClient
    from modules.smart_fertilizer.weather.iot_simulator import SoilSensorSimulator

except Exception as e:
    import traceback
    st.error("❌ Problème lors de l'import des modules Smart Fertilizer")
    st.code(traceback.format_exc())
    st.stop()


# ✅ Configuration de la page
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
        Intelligent fertilizer recommendation system for African agriculture

        **Fonctionnalités :**
        - Analyse du sol et interprétation
        - Recommandations spécifiques aux cultures
        - Adaptation régionale (Afrique de l’Ouest, Est, Centre, Sud)
        - Intégration météo et IoT
        - Interface multilingue
        - Génération de rapports PDF

        **Données :** FAO, ESDAC, ICRISAT, NOAA/CHIRPS
        **Contact :** support@smartfertilizer.org
        """
    }
)

# 🖥️ Lancement de l’interface si tout est bon
SmartFertilizerUI().render_main_interface()

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
