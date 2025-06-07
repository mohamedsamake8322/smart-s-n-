import torch
import torch.nn as nn
import pandas as pd
import xgboost as xgb
import numpy as np
import logging
import optuna
import joblib
import shap
import requests
import json
import folium
import os
from fastapi import FastAPI
from streamlit_folium import st_folium
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore
import streamlit as st
import train_model  # ✅ Importation correcte

PyTorchModel = train_model.PyTorchModel  # 📌 Accès à la classe
MODEL_PATH = getattr(train_model, "MODEL_PATH", "C:/Boua/model/default_model.pth")  # ✅ Sécurise l'accès

# ✅ Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 📌 API météo
WEATHER_API = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m"

# 📌 Chargement des modèles
def load_torch_model():
    """Charge le modèle PyTorch"""
    try:
        model = PyTorchModel(input_size=5)  # Assurez-vous que `input_size` correspond au modèle entraîné
        model.load_state_dict(torch.load(MODEL_PATH))
        model.eval()
        logging.info("✅ Modèle PyTorch chargé avec succès !")
        return model
    except Exception as e:
        logging.error(f"🛑 Erreur lors du chargement du modèle PyTorch : {e}")
        return None

def load_xgb_model():
    """Charge le modèle XGBoost"""
    model_path = "model/fertilization_model.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"🛑 Modèle XGBoost introuvable : {model_path}")

    model = joblib.load(model_path)
    logging.info("✅ Modèle XGBoost chargé avec succès !")
    return model

# 📊 Prétraitement des données
def preprocess_data(df):
    """Encodage des catégories et normalisation des données"""
    categorical_cols = ["soil_type", "crop_type"]
    label_encoders = {}

    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])  # Convertir en numérique
        label_encoders[col] = le

    scaler = StandardScaler()
    X = df.drop(columns=["yield"], errors="ignore")
    y = df.get("yield", pd.Series([0] * len(df)))  # Gérer l'absence éventuelle de 'yield'
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler

# 🔎 **Insère `validate_input()` ici, juste après `preprocess_data()` !**
def validate_input(crop, pH, soil_type, growth_stage, temperature, humidity):
    """Validation des entrées pour la prédiction de fertilisation"""
    if crop not in ["Maize", "Millet", "Rice", "Sorghum", "Tomato", "Okra"]:
        return False, "🚨 Invalid crop type!"
    if not (3.5 <= pH <= 9.0):
        return False, "🚨 Soil pH is out of range!"
    if soil_type not in ["Sandy", "Clay", "Loamy"]:
        return False, "🚨 Unknown soil type!"
    return True, "✅ Input is valid."

# 🌱 Prédiction de fertilisation
def get_fertilization_advice(crop, pH, soil_type, growth_stage, temperature, humidity):
    """Prédiction du besoin en fertilisant"""
    features = pd.DataFrame([[pH, temperature, humidity]], columns=["pH", "temperature", "humidity"])
    fertilizer_model = load_xgb_model()
    prediction = fertilizer_model.predict(features)[0]
    return prediction


def get_fertilization_advice(crop, pH, soil_type, growth_stage, temperature, humidity):
    """Prédiction du besoin en fertilisant"""
    # Tu peux choisir une valeur par défaut pour 'fertilizer_type' et 'yield_prediction' si non disponibles
    fertilizer_type = "Unknown"         # ou une valeur utilisée dans ton modèle d'entraînement
    yield_prediction = 0                # une valeur par défaut

    features = pd.DataFrame([{
        'temperature': temperature,
        'humidity': humidity,
        'soil_type': soil_type,
        'crop_type': crop,
        'fertilizer_type': fertilizer_type,
        'yield_prediction': yield_prediction
    }])

    fertilizer_model = load_xgb_model()
    prediction = fertilizer_model.predict(features)[0]
    return prediction

# 🔮 Prédiction avancée du rendement
def predict_rendement(csv_file):
    """Prédiction du rendement agricole"""
    try:
        df = pd.read_csv(csv_file)
        df = df.apply(pd.to_numeric, errors="coerce")
        df.fillna(0, inplace=True)

        # 🔹 Prétraitement des données
        X_scaled, y, scaler = preprocess_data(df)

        # 🔹 Prédiction avec PyTorch
        model_torch = load_torch_model()
        if model_torch:
            X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
            predictions_torch = model_torch(X_tensor).detach().numpy().squeeze()
        else:
            predictions_torch = None

        # 🔹 Prédiction avec XGBoost
        model_xgb = load_xgb_model()
        predictions_xgb = model_xgb.predict(X_scaled)

        # ✅ Validation des performances
        mse = mean_squared_error(y, predictions_xgb)
        r2 = r2_score(y, predictions_xgb)
        logging.info(f"✅ Prédictions validées - MSE: {mse:.4f}, R² Score: {r2:.4f}")

        return predictions_xgb

    except Exception as e:
        logging.error(f"🛑 Erreur de prédiction : {e}")
        return f"🚨 Erreur : {e}"
# 🌾 Génération des tendances du rendement agricole
def generate_yield_trends():
    """Simule l'évolution du rendement agricole sur une période donnée."""
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    yield_values = np.random.uniform(3, 10, size=30)  # Simulation des valeurs de rendement
    stress_levels = np.random.uniform(0, 1, size=30)  # Niveau de stress simulé
    temperature = np.random.uniform(15, 35, size=30)  # Température simulée

    df = pd.DataFrame({"Date": dates, "Yield": yield_values, "Stress Level": stress_levels, "Temperature": temperature})

    logger.info("✅ Yield trends generated successfully!")
    return df
df = generate_yield_trends()
print(f"✅ Fonction `generate_yield_trends()` exécutée, DataFrame généré :\n{df.head()}")

# 📈 Comparaison des performances des modèles
def compare_model_performance():
    """Simule une comparaison des performances entre différents modèles ML."""
    epochs = list(range(1, 11))
    accuracy_before = np.random.uniform(70, 85, len(epochs))
    accuracy_after = np.random.uniform(80, 95, len(epochs))

    df = pd.DataFrame({
        "Epoch": epochs,
        "Accuracy Before": accuracy_before,
        "Accuracy After": accuracy_after,
    })

    logger.info("✅ Model performance comparison generated successfully!")
    return df
def validate_input(crop, pH, soil_type, growth_stage, temperature, humidity):
    """Vérifie que les paramètres d’entrée sont valides pour l’analyse de fertilisation."""
    if not crop or not isinstance(crop, str):
        return False, "🚨 Crop type must be a valid string."
    if not isinstance(pH, (int, float)) or not (3.5 <= pH <= 9.0):
        return False, "🚨 pH level must be a number between 3.5 and 9.0."
    if not soil_type or not isinstance(soil_type, str):
        return False, "🚨 Soil type must be a valid string."
    if not growth_stage or not isinstance(growth_stage, str):
        return False, "🚨 Growth stage must be specified correctly."
    if not isinstance(temperature, (int, float)) or not (0 <= temperature <= 50):
        return False, "🚨 Temperature must be between 0°C and 50°C."
    if not isinstance(humidity, (int, float)) or not (0 <= humidity <= 100):
        return False, "🚨 Humidity must be a percentage between 0 and 100%."

    return True, ""  # ✅ Si tout est valide, retourne `True`

# 🎯 Interface Streamlit fusionnée
def fertilization_rendement_ui():
    st.subheader("🌾 Smart Agriculture Optimizer")

    crop = st.selectbox("🌾 Select Crop", ["Maize", "Millet", "Rice", "Sorghum", "Tomato", "Okra"])
    pH = st.slider("Soil pH", 3.5, 9.0, 6.5)
    soil_type = st.selectbox("🧱 Soil Type", ["Sandy", "Clay", "Loamy"])
    growth_stage = st.selectbox("🌱 Growth Stage", ["Germination", "Vegetative", "Flowering", "Maturity"])
    temperature = st.number_input("🌡️ Temperature (°C)", value=25.0)
    humidity = st.number_input("💧 Humidity (%)", value=60.0)

    if st.button("🔍 Get Prediction"):
        advice = get_fertilization_advice(crop, pH, soil_type, growth_stage, temperature, humidity)
        st.success(f"✅ Recommended Fertilizer: {advice}")

if __name__ == "__main__":
    fertilization_rendement_ui()
