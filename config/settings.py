"""
Enterprise Configuration Settings
"""
import os
from typing import Dict, Any

# Application Configuration
APP_CONFIG = {
    "app_name": "Smart Sènè Yield Predictor",
    "version": "2.0.0",
    "environment": os.getenv("ENVIRONMENT", "production"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    
    # Database Configuration
    "database": {
        "url": os.getenv("DATABASE_URL", "sqlite:///smart_sene.db"),
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "echo": os.getenv("DB_ECHO", "false").lower() == "true"
    },
    
    # API Keys and External Services
    "api_keys": {
        "weather_api": os.getenv("WEATHER_API_KEY", ""),
        "openai_api": os.getenv("OPENAI_API_KEY", ""),
        "google_earth_api": os.getenv("GOOGLE_EARTH_API_KEY", "")
    },
    
    # ML Model Configuration
    "models": {
        "disease_model_path": os.getenv("DISEASE_MODEL_PATH", "models/plant_disease_model.h5"),
        "yield_model_path": os.getenv("YIELD_MODEL_PATH", "models/yield_prediction_model.pkl"),
        "model_cache_timeout": int(os.getenv("MODEL_CACHE_TIMEOUT", "3600"))
    },
    
    # Feature Flags
    "features": {
        "enable_advanced_analytics": True,
        "enable_weather_integration": True,
        "enable_satellite_imagery": True,
        "enable_real_time_monitoring": True,
        "enable_export_functionality": True
    },
    
    # UI Configuration
    "ui": {
        "max_file_upload_size": int(os.getenv("MAX_FILE_SIZE", "200")),  # MB
        "default_chart_height": 400,
        "items_per_page": 50,
        "session_timeout": int(os.getenv("SESSION_TIMEOUT", "3600"))  # seconds
    },
    
    # Logging Configuration
    "logging": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_path": os.getenv("LOG_FILE", "logs/smart_sene.log")
    },
    
    # Security Configuration
    "security": {
        "jwt_secret": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
        "jwt_expiration": int(os.getenv("JWT_EXPIRATION", "86400")),  # 24 hours
        "allowed_file_types": ["csv", "xlsx", "json", "png", "jpg", "jpeg", "pdf"],
        "max_login_attempts": int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    },
    
    # Cache Configuration
    "cache": {
        "ttl": int(os.getenv("CACHE_TTL", "300")),  # 5 minutes
        "max_size": int(os.getenv("CACHE_MAX_SIZE", "1000"))
    }
}

# Crop Configuration
CROP_TYPES = [
    "Maize", "Millet", "Rice", "Sorghum", "Tomato", "Okra", 
    "Peanuts", "Cotton", "Sugarcane", "Cassava"
]

SOIL_TYPES = [
    "Sandy", "Clay", "Loamy", "Silty", "Peaty", "Saline"
]

GROWTH_STAGES = [
    "Germination", "Vegetative", "Flowering", "Fruiting", "Maturity"
]

# Disease Categories
DISEASE_CATEGORIES = {
    "Fungal": ["Leaf Spot", "Rust", "Blight", "Mildew"],
    "Bacterial": ["Bacterial Wilt", "Leaf Streak", "Crown Rot"],
    "Viral": ["Mosaic Virus", "Leaf Curl", "Stunting"],
    "Pest": ["Aphids", "Caterpillars", "Mites", "Beetles"]
}

# Weather Parameters
WEATHER_PARAMETERS = [
    "temperature", "humidity", "rainfall", "wind_speed", 
    "solar_radiation", "pressure", "uv_index"
]

# Model Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    "yield_prediction": {
        "excellent": 0.9,
        "good": 0.8,
        "acceptable": 0.7,
        "poor": 0.6
    },
    "disease_detection": {
        "excellent": 0.95,
        "good": 0.9,
        "acceptable": 0.85,
        "poor": 0.8
    }
}

def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation
    Example: get_config_value('database.url')
    """
    keys = key_path.split('.')
    value = APP_CONFIG
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def validate_config() -> Dict[str, bool]:
    """
    Validate essential configuration settings
    """
    validation_results = {}
    
    # Check API keys
    validation_results['weather_api'] = bool(APP_CONFIG['api_keys']['weather_api'])
    
    # Check model paths
    disease_model_exists = os.path.isfile(APP_CONFIG['models']['disease_model_path'])
    yield_model_exists = os.path.isfile(APP_CONFIG['models']['yield_model_path'])
    
    validation_results['disease_model'] = disease_model_exists
    validation_results['yield_model'] = yield_model_exists
    
    # Check database configuration
    validation_results['database_config'] = bool(APP_CONFIG['database']['url'])
    
    return validation_results
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
