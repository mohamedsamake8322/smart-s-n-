"""
Smart Fertilizer Streamlit Application

Main entry point for the Smart Fertilizer web application using Streamlit.
This application provides intelligent fertilizer recommendations for African agriculture.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

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
        # Import the main UI class
        from ui.smart_ui import SmartFertilizerUI
        
        # Initialize and render the application
        app_ui = SmartFertilizerUI()
        app_ui.render_main_interface()
        
    except ImportError as e:
        st.error(f"❌ Error importing application modules: {e}")
        st.info("Please ensure all required dependencies are installed.")
        
        with st.expander("📋 Installation Instructions"):
            st.markdown("""
            ### Required Dependencies
            
            Install the following packages:
            
            ```bash
            pip install streamlit fastapi uvicorn pandas numpy plotly
            pip install requests reportlab openpyxl scikit-learn scipy
            ```
            
            ### Directory Structure
            
            Ensure the following directories exist:
            - `ui/` - User interface components
            - `core/` - Core fertilizer engine
            - `api/` - API models and endpoints
            - `data/` - Data files
            - `exports/` - Export utilities
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
    
    # Suppress warnings in production
    warnings.filterwarnings('ignore')
    
    # Check for required directories
    required_dirs = ['data', 'ui', 'core', 'api', 'exports']
    missing_dirs = []
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
    
    if missing_dirs:
        st.sidebar.warning(f"⚠️ Missing directories: {', '.join(missing_dirs)}")
    
    # Check for data files
    required_files = [
        'data/crop_profiles.json',
        'data/regional_prices.json',
        'data/soil_samples.csv',
        'data/yield_training_data.csv'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        st.sidebar.info(f"ℹ️ Some data files are missing. Using defaults.")

def display_startup_info():
    """Display startup information and system status"""
    
    # Only show on first run or when explicitly requested
    if 'startup_info_shown' not in st.session_state:
        st.session_state.startup_info_shown = True
        
        # Welcome message
        st.balloons()
        
        # System check
        check_system_status()

def handle_errors():
    """Global error handler for the application"""
    
    def error_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle Ctrl+C gracefully
            return
        
        # Log error (in production, this would go to a logging service)
        error_msg = f"Error: {exc_type.__name__}: {exc_value}"
        st.error(f"❌ Application Error: {error_msg}")
        
        # Option to report error
        if st.button("📝 Report this Error"):
            st.info("Error reporting functionality would be implemented here.")
    
    sys.excepthook = error_handler

# Initialize error handling
handle_errors()

# Display startup information
display_startup_info()

# Run the main application
if __name__ == "__main__":
    main()
