import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

# Page configuration
st.set_page_config(
    page_title="Smart Sènè Yield Predictor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise styling
st.markdown("""
<style>
    /* Main container styling */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Header styling */
    .enterprise-header {
        background: linear-gradient(135deg, #1f77b4 0%, #2e8b57 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .enterprise-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .enterprise-subtitle {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    
    /* Navigation styling */
    .nav-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    .nav-title {
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Status indicators */
    .status-online {
        color: #28a745;
    }
    
    .status-warning {
        color: #ffc107;
    }
    
    .status-error {
        color: #dc3545;
    }
    
    /* Dashboard cards */
    .dashboard-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
        transition: transform 0.2s;
    }
    
    .dashboard-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Footer */
    .enterprise-footer {
        margin-top: 3rem;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 10px;
        text-align: center;
        color: #6c757d;
        border-top: 3px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'navigation_state' not in st.session_state:
    st.session_state.navigation_state = {}

# Import modules
try:
    from core.database import init_db
    from core.auth import authenticate_user, get_user_role
    from ui.dashboard import render_dashboard
    from ui.yield_prediction import render_yield_prediction
    from ui.disease_detection import render_disease_detection
    from ui.climate_analysis import render_climate_analysis
    from ui.model_training import render_model_training
    from ui.analytics import render_analytics
    from config.settings import APP_CONFIG
    from utils.translations import get_translations, get_available_languages
    # Initialize database
    init_db()
    
except ImportError as e:
    st.error(f"❌ Module import error: {e}")
    st.stop()

# Header
st.markdown("""
<div class="enterprise-header">
    <h1 class="enterprise-title">🌾 Smart Sènè Enterprise</h1>
    <p class="enterprise-subtitle">Advanced Agricultural Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div class="nav-section">
        <div class="nav-title">🏢 Enterprise Platform</div>
        <p style="margin: 0; color: #6c757d; font-size: 0.85rem;">
            Professional Agricultural Intelligence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status
    st.markdown("""
    <div class="nav-section">
        <div class="nav-title">System Status</div>
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
            <span class="status-online">●</span> 
            <span style="font-size: 0.85rem;">ML Models Online</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.3rem;">
            <span class="status-online">●</span> 
            <span style="font-size: 0.85rem;">Weather API Active</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span class="status-online">●</span> 
            <span style="font-size: 0.85rem;">Database Connected</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Menu
    st.markdown('<div class="nav-title">📊 Executive Dashboard</div>', unsafe_allow_html=True)
    executive_menu = [
        "🏠 Executive Overview",
        "📈 Business Intelligence", 
        "🎯 Performance KPIs"
    ]
    
    st.markdown('<div class="nav-title">🔬 Technical Operations</div>', unsafe_allow_html=True)
    technical_menu = [
        "🌾 Yield Prediction",
        "🔍 Disease Detection",
        "☁️ Climate Analysis",
        "🚀 Model Training",
        "📊 Advanced Analytics"
    ]
    
    st.markdown('<div class="nav-title">⚙️ System Management</div>', unsafe_allow_html=True)
    system_menu = [
        "📋 Data Management",
        "🔧 System Settings",
        "📚 Documentation"
    ]
    
    # Combined menu
    all_menu_items = executive_menu + technical_menu + system_menu
    
    selected_option = st.selectbox(
        "Navigate to:",
        all_menu_items,
        index=0,
        key="main_navigation"
    )

# Main content area
if selected_option == "🏠 Executive Overview":
    render_dashboard()
elif selected_option == "🌾 Yield Prediction":
    render_yield_prediction()
elif selected_option == "🔍 Disease Detection":
    render_disease_detection()
elif selected_option == "☁️ Climate Analysis":
    render_climate_analysis()
elif selected_option == "🚀 Model Training":
    render_model_training()
elif selected_option == "📊 Advanced Analytics":
    render_analytics()
elif selected_option == "📈 Business Intelligence":
    render_analytics()
elif selected_option == "🎯 Performance KPIs":
    render_dashboard()
else:
    st.info(f"🚧 {selected_option} module is under development")

# Footer
st.markdown("""
<div class="enterprise-footer">
    <p><strong>Smart Sènè Enterprise Platform</strong> | Version 2.0</p>
    <p>Powered by Advanced ML & AI | © 2024 Smart Agriculture Solutions</p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">
        🌍 Serving agricultural communities worldwide | 
        🔒 Enterprise-grade security | 
        📞 24/7 Support available
    </p>
</div>
""", unsafe_allow_html=True)
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
