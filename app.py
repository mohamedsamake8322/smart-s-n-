import os
import json
import torch
import logging
import requests
import numpy as np
import streamlit as st
import shap
import folium
import xgboost as xgb
import plotly.express as px
import pandas as pd
import tensorflow as tf  # ✅ Ajout de TensorFlow pour charger le modèle
import plotly.express as px
import visualizations
import train_model
from PIL import Image
from fastapi import FastAPI
from streamlit_lottie import st_lottie
from streamlit_folium import st_folium
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib  # ✅ Ajout de joblib pour éviter les erreurs de chargement
import train_model  # ✅ Importation correcte
# 📌 Importation des modules internes
from diseases_infos import disease_manager
from image_processing import upload_image, preprocess_image
from evaluate import evaluate_model
from map_utils import generate_map  # Exemple si `generate_map()` est défini dans `map_utils.py`
from climate_analysis import generate_climate_trends, analyze_climate_risk
from diseases_infos import disease_manager  # ✅ Import du gestionnaire de maladies
from database import save_prediction, get_user_predictions, save_observation, save_location
from extract_images import extract_images_from_pdf
from field_stress_map import display_stress_trend, display_stress_heatmap, display_weather_prediction
from generate_data import generate_data
from predictor_fertilizer import predict_rendement, get_fertilization_advice
from climate_analysis import fetch_weather_data, generate_climate_soil_correlation
from field_stress_map import generate_stress_trend
from train_model import MODEL_PATH  # Vérifie que `MODEL_PATH` est bien défini dans `train_model.py`
from disease_risk_predictor import DiseaseRiskPredictor
from map_utils import generate_map, generate_field_map, get_climate_yield_correlation
from predictor_fertilizer import generate_yield_trends, compare_model_performance
from predictor_fertilizer import validate_input
import disease_detector  # ✅ Importation complète du module
from validation import validate_input  # ✅ Importation de la fonction
from climate_analysis import generate_climate_trends, analyze_climate_risk  # ✅ Fonction maintenant existante
import disease_detector  # ✅ Importation correcte
import database
print("🔍 Vérification : `generate_yield_trends()` est bien importé")  # ✅ Ajout temporaire
yield_trend_df = generate_yield_trends()
print(f"✅ Debugging `app.py`: yield_trend_df = {yield_trend_df}")  # ✅ Vérifie si un DataFrame est retourné

model = train_model.model  # ✅ Accès correct au modèle
disease_manager.load_model(r"C:\Boua\model\plant_disease_model.h5")  # ✅ Chemin corrigé
  # Charge le modèle au démarrage
load_model = tf.keras.models.load_model  # ✅ Solution sans dépendance externe
df = generate_data()
df.to_csv("new_data.csv", index=False)  # Sauvegarde sous un autre fichier
# === Initialisation de la base de données ===
database.init_db()
  # ❌ Erreur
# ✅ Configuration du logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🚀 Chargement du modèle CNN (plant_disease_model.h5)
model_path = r"C:\Boua\model\plant_disease_model.h5"  # 🔥 Chemin absolu ajouté
if os.path.exists(model_path):
    model_cnn = tf.keras.models.load_model(model_path)
    print("✅ Modèle CNN chargé avec succès !")
else:
    print("🚨 Erreur : Modèle CNN introuvable ! Vérifiez le chemin du fichier.")

# 🔍 Test rapide du modèle avec une image factice
dummy_input = np.random.rand(1, 224, 224, 3)  # Image factice
try:
    prediction = model_cnn.predict(dummy_input)
    print("✅ Prédiction test réussie :", prediction)
except Exception as e:
    print("🚨 Erreur lors de la prédiction :", e)

# 🌍 Initialisation de Streamlit
st.set_page_config(page_title="Smart Sènè Yield Predictor", layout="wide")
st.title("🌱 Welcome to Smart Sènè!")
st.write("🌾 Smart Sènè helps you predict plant diseases and optimize crops using artificial intelligence. 🌍✨")

# 🔥 Animation Lottie
def load_lottie_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    else:
        return None

lottie_plant = load_lottie_file("plant_loader.json")
if lottie_plant:
    st_lottie(lottie_plant, height=150)
else:
    st.warning("🚨 Animation file not found.")


# 📌 Sidebar avec le menu restructuré
menu = [
    "🏠 Accueil",
    "🚀 Retrain Model",
    "🌾 Prédiction & Fertilisation Optimisée",
    "🔍 Détection des maladies",
    "☁ Suivi des conditions climatiques",
    "📖 Base de connaissances des maladies",
    "📊 Dashboard interactif",
    "🛡️ Analyse des risques",
    "📊 Performance",
    "🌍 Field Map",
    "History"
]
choice = st.sidebar.selectbox("Menu", menu)

# 🏠 Accueil
if choice == "🏠 Accueil":
    st.subheader("👋 Welcome to Smart Sènè Yield Predictor")
    st.subheader("📈 Agricultural Yield Prediction")

# 🔄 Retrain Model (Optimisé pour inclure fertilisation & rendement)
if choice == "🚀 Retrain Model":
    st.subheader("🚀 Retraining the Model")
    uploaded_file = st.file_uploader("📤 Upload your dataset (CSV format)", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("🔍 Data Preview:", df.head())

        if st.button("📊 Check Data Quality"):
            st.write(f"🔹 Number of samples: {len(df)}")
            st.write(f"🔹 Missing values: {df.isnull().sum().sum()}")
            st.write(f"🔹 Column details: {df.dtypes}")

        # Paramètres initiaux
        model_type = st.selectbox("🤖 Choose Model Type", ["XGBoost", "Random Forest", "Neural Network"])
        max_depth = st.slider("🌲 Max Depth (Only for Tree-Based Models)", min_value=3, max_value=15, value=6)
        learning_rate = st.slider("📈 Learning Rate (Only for XGBoost)", min_value=0.001, max_value=0.3, value=0.1, step=0.01)

        # ✅ Suggestion de nettoyage
        if df.isnull().sum().sum() > 0:
            st.warning("🚨 Missing values detected! Consider preprocessing your dataset.")

        if st.button("🚀 Retrain Model"):
            with st.spinner("🔄 Training in progress..."):
                try:
                    if "yield" not in df.columns:
                        st.error("🚨 The dataset does not contain a 'yield' column.")
                    else:
                        retrained_model = train_model(df, model_type=model_type, max_depth=max_depth, learning_rate=learning_rate)
                        st.success("✅ Model retrained successfully!")

                        # 💾 Enregistrement dans un fichier
                        model_filename = f"model/{model_type}_retrained.pkl"
                        joblib.dump(retrained_model, model_filename)
                        st.write(f"📥 Model saved as **{model_filename}**")

                        # 📊 Comparaison des performances
                        previous_model = load_model()
                        performance_before = evaluate_model(previous_model, df.drop(columns=["yield"]), df["yield"])
                        performance_after = evaluate_model(retrained_model, df.drop(columns=["yield"]), df["yield"])

                        st.subheader("📉 Model Performance Comparison")
                        comparison_df = pd.DataFrame({
                            "Previous Model": performance_before,
                            "New Model": performance_after
                        })
                        st.line_chart(comparison_df)

                        # 📌 Feature Importance (optionnelle)
                        if model_type == "XGBoost":
                            st.subheader("📌 Feature Importance (XGBoost)")
                            importance_df = pd.DataFrame({
                                "Feature": df.drop(columns=["yield"]).columns,
                                "Importance": retrained_model.feature_importances_
                            }).sort_values(by="Importance", ascending=False)
                            st.bar_chart(importance_df.set_index("Feature"))

                        # ✅ Résumé
                        st.subheader("📊 Performance Summary")
                        st.table(comparison_df)

                        # ✅ Enregistrement dans la base de données
                        try:
                            # moyenne des features pour l'enregistrement (adaptable)
                            avg_features = df.drop(columns=["yield"]).mean().tolist()
                            avg_predicted_yield = df["yield"].mean()
                            database.save_prediction(avg_features, avg_predicted_yield)
                            st.success("✅ Enregistrement de la prédiction moyen dans la base de données.")
                        except Exception as db_err:
                            st.warning(f"⚠️ Base de données : {db_err}")

                except Exception as e:
                    st.error(f"🛑 Error during model retraining: {e}")

                
# 🔄 Prédiction & Fertilisation Optimisée (Fusionnée)
if choice == "🌾 Prédiction & Fertilisation Optimisée":
    st.subheader("🌾 Smart Agriculture Optimizer")

    crop = st.selectbox("🌾 Select Crop", ["Maize", "Millet", "Rice", "Sorghum", "Tomato", "Okra"])
    pH = st.slider("Soil pH", 3.5, 9.0, 6.5)
    soil_type = st.selectbox("🧱 Soil Type", ["Sandy", "Clay", "Loamy"])
    growth_stage = st.selectbox("🌱 Growth Stage", ["Germination", "Vegetative", "Flowering", "Maturity"])
    temperature = st.number_input("🌡️ Temperature (°C)")
    humidity = st.number_input("💧 Humidity (%)")
    uploaded_file = st.file_uploader("📤 Upload your yield dataset (CSV format)", type=["csv"])

    if st.button("🔍 Predict Yield"):
        if uploaded_file:
            predictions = predict_rendement(uploaded_file)
            st.success(f"✅ Predicted Yield: {predictions[:5]}")

    if st.button("🧮 Get Fertilization Advice"):
        valid, error_message = validate_input(crop, pH, soil_type, growth_stage, temperature, humidity)
        if not valid:
            st.error(error_message)
        else:
            advice = get_fertilization_advice(crop, pH, soil_type, growth_stage, temperature, humidity)
            st.success(f"✅ Recommended Fertilizer: {advice}")
    # 🌾 Ajout des visualisations dynamiques avec les prédictions
    if uploaded_file:
        df = pd.read_csv(uploaded_file)  # 📌 Chargement des données
        if "PredictedYield" in df.columns:
           st.subheader("📊 Yield Distribution") 
           fig1 = visualizations.plot_yield_distribution(df)
           st.pyplot(fig1)
           st.subheader("🎂 Yield Frequency (Pie Chart)")
           fig2 = visualizations.plot_yield_pie(df)
           st.pyplot(fig2)
           st.subheader("📈 Yield Trend Over Time")
           if "timestamp" in df.columns:
              fig3 = visualizations.plot_yield_over_time(df)
              st.pyplot(fig3) 
           else:
               st.warning("⚠️ Column 'timestamp' not found in data!")
    else:
        st.warning("⚠️ Column 'PredictedYield' not found in uploaded file!")              
# 🌾 Tendances du rendement agricole
if choice == "📊 Yield Trends":
    st.subheader("📊 Yield Trends Over Time")

# ✅ Appel direct de la fonction sans risque d'écrasement
yield_trend_df = generate_yield_trends()
print(f"🔍 Debugging: yield_trend_df = {yield_trend_df}")  # ✅ Vérifie le contenu

if yield_trend_df is not None and not yield_trend_df.empty:
    fig_yield = px.line(yield_trend_df, x="Date", y="Yield", title="📊 Agricultural Yield Trends")
    st.plotly_chart(fig_yield)
else:
    st.warning("🚨 No yield trend data available!")
    print("⚠️ Erreur : `generate_yield_trends()` a retourné un DataFrame vide ou `None`")

# 📈 Comparaison des performances des modèles
st.subheader("📉 Model Performance Comparison")
comparison_df = compare_model_performance()
if comparison_df is not None:
    st.line_chart(comparison_df)
else:
    st.warning("🚨 No model comparison data available!")

# Interface pour l'importation et la prédiction des maladies
st.subheader("🔍 Détection des maladies")
image_file = st.file_uploader("Télécharge une image", type=["jpg", "jpeg", "png", "bmp", "gif", "tiff"])

if image_file is not None:
    image_path = upload_image(image_file)
    image = preprocess_image(image_path)
    detected_disease = disease_detector.detect_disease(image, model, disease_manager)  # ✅ Appel correct
    st.write(f"🔍 Maladie détectée : {detected_disease}")

    # 📌 Afficher les infos détaillées si la maladie est connue
    if detected_disease in disease_manager.diseases:
        disease_info = disease_manager.diseases[detected_disease]
        st.write("🌱 **Informations sur la maladie :**")
        st.write(f"**Hôtes :** {', '.join(disease_info['hosts'])}")
        st.write(f"**Description :** {disease_info['overview']}")
        st.write(f"**Symptômes :** {disease_info['symptoms']}")
        st.write(f"**Gestion :** {disease_info['management']}")
        st.write(f"**Traitements disponibles :** {', '.join(disease_info['insecticides'])}")

        # 📌 Génération de PDF pour la maladie détectée
        pdf_path = disease_manager.export_to_pdf(detected_disease)
        st.write(f"📜 [Télécharger le rapport PDF]({pdf_path})")
        
# ☁ Suivi des conditions climatiques📌 API météo OpenWeatherMap (Remplace "YOUR_API_KEY" par ta clé)
WEATHER_API_KEY = "YOUR_API_KEY"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(location):
    """Récupère les données météo via OpenWeatherMap"""
    params = {"q": location, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(WEATHER_URL, params=params)
        data = response.json()
        if response.status_code == 200:
            weather_info = {
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "description": data["weather"][0]["description"]
            }
            return weather_info
        else:
            return {"error": f"🚨 API Error: {data.get('message', 'Unknown error')}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"🚨 Erreur API météo: {e}"}

# 📌 Ajout dans l'application Streamlit
if choice == "☁ Suivi des conditions climatiques":
    st.subheader("🌦 Weather Monitoring & Agricultural Risk Analysis")

    location = st.text_input("📍 Enter your location (City, Country)")

    if st.button("🔍 Get Weather Data"):
        if location:
            weather_data = get_weather_data(location)
            if "error" in weather_data:
                st.error(weather_data["error"])
            else:
                st.write(f"🌡️ **Temperature:** {weather_data['temperature']} °C")
                st.write(f"💧 **Humidity:** {weather_data['humidity']} %")
                st.write(f"💨 **Wind Speed:** {weather_data['wind_speed']} m/s")
                st.write(f"🌤 **Condition:** {weather_data['description']}")
        else:
            st.warning("🚨 Please enter a valid location!")

    # 📊 Ajout d’un graphique des tendances climatiques
    if st.button("📊 Show Climate Trends"):
        climate_data = generate_climate_trends(location)
        st.line_chart(climate_data)

    st.subheader("⚠️ Agricultural Risk Analysis")
    risk_level = analyze_climate_risk(location)
    st.warning(f"🚨 Climate Risk Level: {risk_level}")
elif choice == "📖 Base de connaissances des maladies":
    st.subheader("📖 Plant Disease Knowledge Base")

    # 🔍 Barre de recherche
    disease_query = st.text_input("🔍 Search for a disease")

    # 📚 Affichage structuré des maladies
# 📚 Affichage structuré des maladies
disease_query = st.text_input("🔎 Enter disease name:")  # ✅ Définit `disease_query`
if disease_query:
    disease_info = disease_manager.get_disease_info(disease_query)
    if disease_info and isinstance(disease_info, dict):  # ✅ Vérification du type
        st.write(f"📝 **Disease:** {disease_query}")
        st.write(f"🌱 **Affected Crops:** {', '.join(disease_info.get('hosts', []))}")
        st.write(f"⚠️ **Symptoms:** {disease_info.get('symptoms', 'No symptoms available.')}")
        st.write(f"🛡 **Management Tips:** {disease_info.get('management', 'No management tips available.')}")
        if "image" in disease_info:
            st.image(disease_info["image"], caption=f"Example of {disease_query}")
    else:
        st.error("🚨 Disease not found in database!")
else:
    st.warning("⚠️ Please enter a disease name!")
# 🔍 Liste complète des maladies
if st.button("📜 View All Diseases"):
    st.table(disease_manager.diseases)  # ✅ Accès correct à la liste des maladies

# 📷 Détection automatique avec image
if choice == "🔍 Disease Detection":
    st.subheader("🔍 Disease Detection")
uploaded_image = st.file_uploader("📤 Upload a plant image", type=["png", "jpg", "jpeg"])

if uploaded_image:
    # ✅ Conversion automatique pour tout format d'image
    image = Image.open(uploaded_image).convert("RGB").resize((224, 224))
    img_array = np.array(image) / 255.0  # ✅ Normalisation
    img_array = np.expand_dims(img_array, axis=0)  # ✅ Format prêt pour TensorFlow

    # 📌 Correction : on passe maintenant une image prétraitée
    disease_prediction = disease_detector.detect_disease(image=img_array)  # ✅ Appel correct

    st.success(f"✅ Predicted Disease: {disease_prediction}")

    # ✅ Gestion des informations sur la maladie
    disease_info = disease_manager.get_disease_info(disease_prediction)
    if disease_info and isinstance(disease_info, dict):
        st.write(f"📝 **Disease:** {disease_prediction}")
        st.write(f"🛡 **Management Tips:** {disease_info.get('management', 'No management tips available.')}")
        if "image" in disease_info:
            st.image(disease_info["image"], caption=f"Example of {disease_prediction}")

elif choice == "📊 Dashboard interactif":
    st.subheader("📊 Agricultural Performance Dashboard")



    # 📊 Affichage des tendances du rendement
    st.subheader("🌾 Yield Trends")
    yield_data = generate_yield_trends()  # 🔄 Fonction pour récupérer les tendances
    fig_yield = px.line(yield_data, x="date", y="yield", title="Yield Over Time")
    st.plotly_chart(fig_yield)

    # 🌦 Corrélation climat/rendement
    st.subheader("☁ Climate Impact on Yield")
    climate_yield_df = get_climate_yield_correlation()
    fig_climate = px.scatter(climate_yield_df, x="temperature", y="yield", color="humidity", title="Yield vs Climate Factors")
    st.plotly_chart(fig_climate)

    # 🗺 Cartographie des champs
    st.subheader("🗺 Field Map & Performance")
    map_html = generate_field_map()
    st.components.v1.html(map_html, height=600)

    # 📈 Comparaison des modèles avant/après réentraînement
    st.subheader("📉 Model Performance Comparison")
    comparison_df = compare_model_performance()
    st.line_chart(comparison_df)

if choice == "📊 Dashboard interactif":
    st.subheader("📊 Agricultural Performance Dashboard")

    # 📊 Affichage des tendances du rendement
    st.subheader("🌾 Yield Trends")
    yield_data = generate_yield_trends()  # 🔄 Fonction pour récupérer les tendances
    if yield_data is not None:
        fig_yield = px.line(yield_data, x="date", y="yield", title="Yield Over Time")
        st.plotly_chart(fig_yield)
    else:
        st.warning("🚨 No yield data available!")

    # 🌦 Corrélation climat/rendement
    st.subheader("☁ Climate Impact on Yield")
    climate_yield_df = get_climate_yield_correlation()
    if climate_yield_df is not None:
        fig_climate = px.scatter(climate_yield_df, x="temperature", y="yield", color="humidity", title="Yield vs Climate Factors")
        st.plotly_chart(fig_climate)
    else:
        st.warning("🚨 Climate yield correlation data missing!")

    # 🗺 Cartographie des champs
    st.subheader("🗺 Field Map & Performance")
    map_html = generate_field_map()
    if map_html:
        st.components.v1.html(map_html, height=600)
    else:
        st.warning("🚨 Field map data unavailable!")

    # 📈 Comparaison des modèles avant/après réentraînement
    st.subheader("📉 Model Performance Comparison")
    comparison_df = compare_model_performance()
    if comparison_df is not None:
        st.line_chart(comparison_df)
    else:
        st.warning("🚨 No model comparison data available!")


if choice == "🛡️ Analyse des risques":
    st.title("🛡️ Analyse des risques agricoles")

    # 📝 Saisie des paramètres de risque
    disease_name = st.text_input("🦠 Entrez le nom de la maladie")
    temperature = st.number_input("🌡️ Température (°C)", min_value=-10.0, max_value=50.0, value=25.0)
    humidity = st.number_input("💧 Humidité (%)", min_value=0, max_value=100, value=60)
    wind_speed = st.number_input("🍃 Vitesse du vent (km/h)", min_value=0.0, max_value=100.0, value=10.0)
    soil_type = st.selectbox("🌱 Type de sol", ["Sandy", "Clay", "Loamy"])
    aphid_population = st.slider("🐜 Population de pucerons", 0, 1000, 50)
    crop_stage = st.selectbox("🌾 Stade de la culture", ["Germination", "Vegetative", "Flowering", "Maturity"])
    season = st.selectbox("🍂 Saison", ["Spring", "Summer", "Autumn", "Winter"])

    if st.button("🔍 Évaluer le risque"):
        predictor = DiseaseRiskPredictor(disease_name, temperature, humidity, wind_speed, soil_type, aphid_population, crop_stage, season)
        risk_score = predictor.calculate_risk()

        # ✅ Affichage du score de risque
        st.success(f"✅ Score de risque calculé : {risk_score:.2f}")

        # 📊 Graphique interactif des facteurs de risque
        risk_data = pd.DataFrame({
            "Factor": ["Temperature", "Humidity", "Wind Speed", "Aphid Population"],
            "Value": [temperature, humidity, wind_speed, aphid_population]
        })
        fig_risk = px.bar(risk_data, x="Factor", y="Value", title="Risk Factors Impact")
        st.plotly_chart(fig_risk)

        # 🛡 Suggestions basées sur le risque
        if risk_score > 75:
            st.error("🚨 High Risk! Consider immediate intervention.")
            st.write("🔹 Apply disease-resistant crops")
            st.write("🔹 Use targeted pest control measures")
            st.write("🔹 Optimize irrigation and soil health")
        elif risk_score > 40:
            st.warning("⚠️ Moderate Risk! Monitoring required.")
            st.write("🔹 Monitor plant conditions frequently")
            st.write("🔹 Adjust environmental control strategies")
        else:
            st.success("✅ Low Risk! No urgent action needed.")


# 📜 History
def fetch_user_predictions():
    url = "http://127.0.0.1:5000/get_user_predictions"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

user_predictions = fetch_user_predictions()
if user_predictions and "predictions" in user_predictions:
    user_predictions = pd.DataFrame(user_predictions["predictions"])
else:
    user_predictions = None

if choice == "History" and user_predictions is not None:
    st.subheader("📜 Prediction History")
    selected_disease = st.selectbox("🔎 Filter by Disease", ["All"] + list(user_predictions["disease"].unique()))
    start_date = st.date_input("📅 Start Date", user_predictions["date"].min())
    end_date = st.date_input("📅 End Date", user_predictions["date"].max())

    filtered_df = user_predictions[
        (user_predictions["date"] >= start_date) &
        (user_predictions["date"] <= end_date) &
        ((selected_disease == "All") | (user_predictions["disease"] == selected_disease))
    ]
    st.dataframe(filtered_df)

    st.subheader("📊 Prediction Statistics")
    disease_counts = filtered_df["disease"].value_counts()
    st.bar_chart(disease_counts)

    if not filtered_df.empty and st.button("📤 Download History"):
        filtered_df.to_csv("history.csv", index=False)
        st.success("✅ History exported successfully!")
    elif filtered_df.empty:
        st.warning("⚠️ No predictions found.")

# 📊 Performance
if choice == "📊 Performance":
    st.subheader("📊 Model Performance Analysis")

    if st.button("📊 Show Performance Metrics"):
        # ✅ Vérification de l'existence du fichier de modèle
        if not os.path.exists(MODEL_PATH):
            st.error("🚨 Model file not found! Please train the model first.")
        else:
            try:
                model_data = torch.load(MODEL_PATH)
                scores = model_data.get("metrics", {})

                if scores:
                    st.metric("🔹 Accuracy", f"{scores.get('accuracy', 0):.2%}")
                    st.metric("🔹 F1 Score", f"{scores.get('f1_score', 0):.2%}")
                    st.metric("🔹 Precision", f"{scores.get('precision', 0):.2%}")
                    st.metric("🔹 Recall", f"{scores.get('recall', 0):.2%}")
                    st.metric("🔹 RMSE", f"{scores.get('rmse', 0):.2f}")
                    st.metric("🔹 R² Score", f"{scores.get('r2', 0):.2%}")

                    # 📊 Graphique interactif des performances
                    performance_df = pd.DataFrame([
                        {"Metric": "Accuracy", "Score": scores.get("accuracy", 0)},
                        {"Metric": "F1 Score", "Score": scores.get("f1_score", 0)},
                        {"Metric": "Precision", "Score": scores.get("precision", 0)},
                        {"Metric": "Recall", "Score": scores.get("recall", 0)},
                        {"Metric": "RMSE", "Score": scores.get("rmse", 0)},
                        {"Metric": "R² Score", "Score": scores.get("r2", 0)}
                    ])
                    fig_performance = px.bar(performance_df, x="Metric", y="Score", title="📊 Model Performance Metrics")
                    st.plotly_chart(fig_performance)

                    # 🧐 Explication des métriques
                    st.subheader("ℹ️ Interpretation of Metrics")
                    st.write("- **Accuracy**: Measures overall correctness of the model.")
                    st.write("- **F1 Score**: Balances precision and recall for a robust metric.")
                    st.write("- **Precision**: Measures correct positive predictions.")
                    st.write("- **Recall**: Captures missed positives.")
                    st.write("- **RMSE**: Evaluates error magnitude in continuous predictions.")
                    st.write("- **R² Score**: Determines how well predictions match actual results.")

                else:
                    st.error("🚨 No performance metrics found! Please retrain the model.")
            except Exception as e:
                st.error(f"🚨 Error loading model data: {e}")

# 🌍 Field Map & Agricultural Stress Analysis
if choice == "🌍 Field Map":
    st.subheader("🌍 Field Map & Agricultural Stress Analysis")

    # ✅ Récupération des données climatiques en temps réel
    st.info("🌦 Fetching live weather data...")
    try:
        weather_data = fetch_weather_data()
        avg_temp = round(np.mean(weather_data), 2)
        st.success(f"🌡️ Average forecasted temperature: {avg_temp}°C")
    except Exception as e:
        st.error(f"🚨 Weather data unavailable: {e}")

    # 🗺️ Génération de la carte interactive avec Folium
    st.subheader("🗺 Interactive Field Map")
    map_object = generate_map()
    st_folium(map_object, width=800, height=500)

    # 📊 Ajout d’une légende dynamique pour les zones du champ
    st.markdown("""
    **Legend:**  
    🔵 **Blue** - Optimal Growth Zone 📈  
    🟠 **Yellow** - Moderate Stress Zone 🌱  
    🔴 **Red** - High-Risk Stress Zone 🚨  
    """)

    # 📉 Analyse des tendances de stress agricole
    st.subheader("📊 Stress Trend Over Time")
    stress_trend_df = generate_stress_trend()

    if stress_trend_df is None or stress_trend_df.empty:
        st.warning("🚨 No stress data available!")
    else:
        fig_stress = px.line(stress_trend_df, x="Date", y="Stress Level", title="📊 Agricultural Stress Trends Over Time")
        st.plotly_chart(fig_stress)

    # 🔍 Filtrage avancé par période
    st.subheader("📅 Filter Stress Data by Time Range")

    # ✅ Sélection des dates dynamiquement en fonction des données existantes
    min_date, max_date = stress_trend_df["Date"].min(), stress_trend_df["Date"].max()
    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    # 🚨 Vérification avant d'appliquer le filtrage
    if start_date > end_date:
        st.error("🚨 Invalid date range! Start date must be before end date.")
    else:
        filtered_df = stress_trend_df[(stress_trend_df["Date"] >= start_date) & (stress_trend_df["Date"] <= end_date)]
        if not filtered_df.empty:
            fig_filtered = px.line(filtered_df, x="Date", y="Stress Level", title="📊 Filtered Agricultural Stress Trends")
            st.plotly_chart(fig_filtered)
        else:
            st.warning("🚨 No data for selected time range!")

    # 🌦 Corrélation avancée entre climat et rendement
    st.subheader("☁ Climate & Soil Condition Impact on Yield")
    climate_soil_df = generate_climate_soil_correlation()

    if climate_soil_df is None or climate_soil_df.empty:
        st.warning("🚨 Climate-Soil correlation data unavailable!")
    else:
        fig_correlation = px.scatter(
            climate_soil_df, x="Temperature", y="Soil Moisture", color="Stress Level",
            title="🌍 Climate Impact on Soil & Growth",
            labels={"Temperature": "🌡️ Temperature (°C)", "Soil Moisture": "💧 Soil Moisture Level"}
        )
        st.plotly_chart(fig_correlation)

        
# 📌 Compute SHAP values
def compute_shap_values(df, model_path, sample_size=100):
    """Calcule les valeurs SHAP pour expliquer les prédictions du modèle"""
    if not os.path.exists(model_path):
        raise FileNotFoundError("❌ Model file not found. SHAP cannot be computed.")

    try:
        model_data = torch.load(model_path)
        model = model_data.get("model")

        if model is None:
            raise ValueError("🚨 Model loading error. SHAP cannot be computed.")

        # 📝 Vérification des données avant SHAP
        if df.empty:
            raise ValueError("🚨 The dataset is empty. SHAP cannot be computed.")

        for col in ["soil_type", "crop_type"]:
            if col in df.columns:
                df[col] = df[col].astype("category")
        
        # 🔍 Gestion des valeurs manquantes avant SHAP
        df.fillna(df.median(), inplace=True)

        # 🔄 Sélection des échantillons dynamiquement
        sample_size = min(sample_size, len(df))
        X_sample = df.sample(sample_size).drop(columns=["yield"], errors="ignore")

        explainer = shap.Explainer(model)
        shap_values = explainer(X_sample)

        return shap_values

    except Exception as e:
        raise RuntimeError(f"🛑 SHAP computation error: {e}")
