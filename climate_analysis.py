import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import joblib
import os
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib

# ✅ Adaptation du backend Matplotlib pour éviter les conflits
matplotlib.use("TkAgg")  # 🖼️ Active le mode interactif si en local
matplotlib.rcParams["font.family"] = "DejaVu Sans"  # ✅ Ajout d'une police supportant les emojis et glyphes

# 🌍 API pour récupérer les données climatiques en temps réel
WEATHER_API = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m"

# 📊 Chargement du modèle de prédiction climatique
MODEL_PATH = "model/climate_prediction.pkl"

# ✅ Récupération des données météo
def fetch_weather_data():
    """Récupère les données climatiques en temps réel."""
    try:
        response = requests.get(WEATHER_API, timeout=10)  # ✅ Ajout d'un timeout
        response.raise_for_status()
        data = response.json()
        temperature = np.array(data["hourly"]["temperature_2m"])
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"🚨 Erreur lors de la récupération des données climatiques: {e}")
        return None

# 📊 Analyse des tendances climatiques
def generate_climate_trends():
    """Analyse les tendances climatiques à partir des données historiques."""
    try:
        df = pd.read_csv("data/climate_history.csv")

        if "date" not in df.columns or "temperature" not in df.columns:
            raise ValueError("🚨 Les colonnes 'date' et 'temperature' sont absentes du dataset.")

        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=df.index, y=df["temperature"], label="Température")
        if "humidity" in df.columns:
            sns.lineplot(x=df.index, y=df["humidity"], label="Humidité", linestyle="dashed")

        plt.title("Tendances climatiques historiques")  # ✅ Suppression des emojis pour éviter les erreurs de rendu
        plt.xlabel("Date")
        plt.ylabel("Valeurs normalisées")
        plt.legend()
        plt.grid()
        plt.savefig("climate_trends.png")  # ✅ Enregistrement au lieu d'affichage
        plt.close()

        return df
    except Exception as e:
        print(f"🚨 Erreur dans `generate_climate_trends`: {e}")
        return None

# ✅ Corrélation entre le climat et la qualité du sol
def generate_climate_soil_correlation():
    """Analyse la corrélation entre le climat et la qualité du sol."""
    try:
        df_soil = pd.read_csv("data/soil_conditions.csv")

        numeric_df = df_soil.select_dtypes(include='number')
        if numeric_df.empty:
            raise ValueError("🚨 Aucune donnée numérique trouvée dans le fichier sol.")

        # 🔍 Normalisation avancée
        scaler = MinMaxScaler()
        numeric_df_scaled = pd.DataFrame(scaler.fit_transform(numeric_df), columns=numeric_df.columns)

        correlation = numeric_df_scaled.corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("Matrice de corrélation Climat-Sol")
        plt.savefig("climate_soil_correlation.png")  # ✅ Enregistrement au lieu d'affichage
        plt.close()

        return correlation
    except Exception as e:
        print(f"🚨 Erreur dans `generate_climate_soil_correlation`: {e}")
        return None

# ✅ Prédiction climatique avec modèle ML
def predict_future_climate(features):
    """Prédit le climat futur en fonction des tendances et de la qualité du sol."""
    try:
        if not isinstance(features, dict):
            raise ValueError("🚨 Les paramètres doivent être fournis sous forme de dictionnaire.")

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"🚨 Modèle introuvable: {MODEL_PATH}")

        model = joblib.load(MODEL_PATH)
        input_data = pd.DataFrame([features])

        # 🔍 Vérification des caractéristiques utilisées dans le modèle
        expected_features = model.feature_names_in_
        print(f"Modèle entraîné avec features: {expected_features}")
        print(f"Features fournis en prédiction: {input_data.columns}")

        # ✅ Ajustement des features pour correspondre à celles du modèle
        input_data = input_data[expected_features]

        prediction = model.predict(input_data)

        return prediction[0] if prediction is not None else None
    except Exception as e:
        print(f"🚨 Erreur dans `predict_future_climate`: {e}")
        return None

# ✅ Analyse des risques climatiques et agricoles
def analyze_climate_risk(temperature, humidity, soil_type):
    """Analyse les risques agricoles et climatiques."""
    risk_factors = {
        "Loamy": {"humidity": 60, "temperature": 25, "risk": "⚠️ Risque modéré d'acidification"},
        "Clay": {"humidity": 80, "temperature": 30, "risk": "⚠️ Risque élevé de rétention d'eau"},
        "Sandy": {"humidity": 50, "temperature": 35, "risk": "⚠️ Risque fort de dessèchement"}
    }

    risk_messages = []
    if soil_type in risk_factors:
        if humidity >= risk_factors[soil_type]["humidity"]:
            risk_messages.append(f"💧 Humidité élevée -> {risk_factors[soil_type]['risk']}")
        if temperature >= risk_factors[soil_type]["temperature"]:
            risk_messages.append(f"🌡️ Température critique -> {risk_factors[soil_type]['risk']}")

    return "✅ Aucun risque immédiat détecté." if not risk_messages else " | ".join(risk_messages)

# 🧪 **Tests du module**
if __name__ == "__main__":
    try:
        print("🔍 Récupération des données météo...")
        temps_data = fetch_weather_data()
        if temps_data is not None:
            print(f"✅ Température moyenne prédite: {np.mean(temps_data):.2f}°C")

        print("\n📊 Analyse de corrélation Climat-Sol...")
        correlation_matrix = generate_climate_soil_correlation()
        if correlation_matrix is not None:
            print("✅ Corrélation calculée avec succès !")

        print("\n🔮 Prédiction climatique...")
        future_climate = predict_future_climate({"temperature": 25, "humidity": 60, "pH": 6.5, "rainfall": 100})
        if future_climate is not None:
            print(f"🌡️ Climat futur prédit: {future_climate:.2f}")
        else:
            print("🚨 Aucune prédiction disponible.")

        print("\n⚠️ Analyse des risques climatiques...")
        climate_risk = analyze_climate_risk(temperature=30, humidity=85, soil_type="Clay")
        print(f"🌍 Risques détectés: {climate_risk}")

    except Exception as e:
        print(f"🚨 Erreur: {e}")
