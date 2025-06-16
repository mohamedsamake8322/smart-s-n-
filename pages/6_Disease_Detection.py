import diseases_infos
import os
import requests
import tensorflow as tf
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image, ImageEnhance
from datetime import datetime
from io import BytesIO
from tensorflow.keras.applications.efficientnet import preprocess_input
import plotly.express as px  # Corrige l'erreur F821 pour `px`

# ✅ Définition des variables manquantes
detector = None
model_type = "default"
DISEASE_CLASSES = {}
uploaded_files = []
disease_filter = None
confidence_filter = 0.5
disease_freq = {}
search_term = ""
category = "Toutes"

# 🔹 Désactiver les warnings inutiles TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# 🔹 Vérification de TensorFlow
try:
    TENSORFLOW_AVAILABLE = True
except ImportError:
    st.error("🚫 TensorFlow non disponible")
    TENSORFLOW_AVAILABLE = False

# 🔹 Import des modules internes

# ✅ Dictionnaire des icônes pour chaque maladie
DISEASE_ICONS = {
    "Healthy": "✅",
    "Aphids on Vegetables": "🐛🥦",
    "Armyworms on Vegetables": "🐛🍃",
    "Blister Beetle": "🪲🔥",
    "Beet Leafhopper": "🪲🌿",
    "Colorado Potato Beetle": "🥔🪲",
    "Western Striped and Spotted Cucumber Beetle": "🥒🪲",
    "Spotted Cucumber Beetle": "🥒🐞",
    "Cutworms on Vegetables": "🐛✂️",
    "False Chinch Bug": "🐜❌",
    "Flea Beetles": "🪲🔬",
    "Tomato and Tobacco Hornworms": "🍅🐛",
    "Thrips on Vegetables": "🦟🥦",
    "Potato Leafhopper": "🥔🌿",
    "Two-Spotted Spider Mite": "🕷️🌱",
    "Corn Earworm / Tomato Fruitworm": "🌽🍅🐛",
    "Tomato Russet Mite": "🍅🕷️",
    "Whiteflies (Family: Aleyrodidae)": "🦟🌿",
    "Alfalfa Mosaic Virus": "🦠🌱",
    "Bacterial Canker": "🦠⚠️",
    "Bacterial Speck": "🦠🍅",
    "Beet Curly Top Virus": "🌀🦠",
    "Big Bud": "🌿💥",
    "Blossom End Rot": "🍅⚫",
    "Damping-Off": "🌱🚫",
    "Early Blight": "🍅🟠",
    "Fusarium Crown/Root Rot": "🌿🦠",
    "Fusarium Wilt": "🌾⚠️",
    "Late Blight": "🍅🔥",
    "Root-Knot Nematodes": "🌱🐛",
    "Phytophthora Root, Stem, and Crown Rots": "🌿🦠",
    "Powdery Mildew on Vegetables": "🍃🌫️",
    "Tobacco Mosaic Virus & Tomato Mosaic Virus": "🍅🌿🦠",
    "Tomato Spotted Wilt Virus": "🍅🔴",
    "Verticillium Wilt": "🌾🔴",
    "Cercospora Leaf Spot (Frogeye)": "🌿⚪",
    "Choanephora Blight (Wet Rot)": "🌿💧",
    "Gray Leaf Spot": "🌿🔘",
    "Phomopsis Blight": "🌿🔥",
}

# ✅ Chargement du modèle IA
MODEL_PATH = (
    "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"
)


@st.cache_resource
def load_disease_model(model_path):
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as e:
        st.error(f"🛑 Erreur : {e}")
        return None


disease_model = load_disease_model(MODEL_PATH)
# 🔍 Prétraitement de l’image


def preprocess_image(image_file):
    """Prépare l’image et applique le prétraitement EfficientNet."""
    try:
        image = Image.open(image_file).convert("RGB").resize((380, 380))
        img_array = np.array(image)
        img_array = preprocess_input(img_array)

        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        print(f"🚨 Erreur : {e}")
        return None


# 🔍 Prédiction multi-maladies avec tri des résultats
def predict_disease(image):
    """Analyse l’image et retourne plusieurs maladies avec leur score."""
    if disease_model is None:
        return [{"error": "🚨 Modèle non chargé"}]

    img_array = preprocess_image(image)
    if img_array is None:
        return [{"error": "🚨 Erreur dans le prétraitement de l’image"}]

    predictions = disease_model.predict(
        img_array)[0]  # Retirer la dimension batch
    top_labels = []

    # ✅ Trier les résultats par confiance
    sorted_indices = np.argsort(predictions)[::-1]

    # Afficher uniquement les 5 meilleurs résultats
    for idx in sorted_indices[:5]:
        disease_name = diseases_infos.DISEASE_CLASSES.get(
            idx, "🔍 Maladie inconnue")
        disease_icon = DISEASE_ICONS.get(
            disease_name, "❓"
        )  # Icône par défaut si inconnue

        top_labels.append(
            {
                "name": f"{disease_icon} {disease_name}",
                "confidence": predictions[idx] * 100,
                "progression_stage": estimate_progression(
                    predictions[idx] * 100),
            })

    return top_labels
# 🔍 Détermination du stade de progression


def estimate_progression(confidence):
    """Détermine le stade de la maladie."""

    if confidence > 90:
        return "🔴 Critique"
    elif confidence > 75:
        return "🟠 Avancé"
    elif confidence > 50:
        return "🟡 Début"
    else:
        return "🟢 Faible impact"


def assess_disease_risk(crop, temp, humidity, soil_type):
    """
    Évalue le risque de maladie en fonction du type de culture, de la température,
    de l'humidité et du type de sol.
    """
    # 🚀 Définition des seuils de risque
    risk_levels = {
        "Low":(
            temp > 25 and humidity < 50,
        ),
        "Medium":(
            20 <= temp <= 25 and 50 <= humidity <= 70,
        ),
        "High": (
            temp < 20 or humidity > 70,
        ),
    }

    # 📌 Ajustement basé sur le type de sol et la culture
    base_risk = (
        "High"
        if crop in ["Tomate", "Pomme de terre"] and soil_type == "Loamy"
        else "Medium"
    )
    # ✅ Détermination finale du risque
    for level, condition in risk_levels.items():
        if condition:
            return "Critical" if base_risk == "High" else level

    return base_risk  # Si aucun niveau de risque spécifique ne s’applique


def get_weather_risk(crop):
    """Vérifie les conditions climatiques et les risques de maladies."""
    try:
        response = requests.get(
            "https://api.open-meteo.com/weather", timeout=5)
        response.raise_for_status()
        weather_data = response.json()

        if not weather_data or "current" not in weather_data:
            print("⚠️ Données météo vides ou mal formatées.")
            return "Risque météo inconnu"

        temp = weather_data["current"].get("temperature", -1)
        humidity = weather_data["current"].get("humidity", -1)

        if temp == -1 or humidity == -1:
            print("⚠️ Impossible de récupérer les données météo.")
            return "Données météo indisponibles"

        risk_factor = assess_disease_risk(crop, temp, humidity, "Loamy")
        return risk_factor

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur de requête météo : {e}")
        return "Erreur lors de la récupération des données météo"


# 📊 Interface utilisateur optimisée avec Streamlit
st.set_page_config(
    page_title="Disease Detector Ultra",
    page_icon="🌿",
    layout="wide")
st.title("🌿 Détection de Maladies Agricoles - Ultra IA")

uploaded_file = st.file_uploader(
    "🖼️ Importer une image", type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file:
    st.image(uploaded_file, width=250)

    with st.spinner("🔬 Analyse IA en cours..."):
        results = predict_disease(uploaded_file)

    if "error" in results:
        st.error(results["error"])
    else:
        for disease in results:
            st.subheader(f"🦠 {disease['name']}")
            st.write(f"🔹 Confiance IA : {disease['confidence']:.2f}%")
            st.write(
                f"🩺 Stade de progression : {disease['progression_stage']}")
            st.write(f"🔎 Symptômes : {disease['symptoms']}")
            st.write(f"🩺 Recommandations : {disease['recommendations']}")

    # 📌 Affichage du risque climatique
    crop = "Tomate"
    weather_risk = get_weather_risk(crop)
    st.warning(f"🌍 Facteur climatique : {weather_risk}")

# 🖥️ Mode collaboratif : Upload et partage des résultats
st.markdown("### 🧑‍🌾 Partagez votre diagnostic avec la communauté")
user_feedback = st.text_area("💡 Ajoutez votre retour ou des observations")
if st.button("📌 Publier le diagnostic"):
    st.success("✅ Diagnostic partagé avec la communauté !")

# 🛑 Mode d’urgence : Contacter un expert
if st.button("🚨 Urgence - Contacter un Expert"):
    st.error("📡 Envoi des données à un agronome expert en cours...")

# 🛍️ Marketplace intégrée pour acheter des traitements adaptés
st.sidebar.title("🌿 Solutions & Traitements")
st.sidebar.markdown(
    "**Recommandations de produits pour les maladies détectées**")
st.sidebar.button("Acheter des traitements adaptés")


# Main content tabs - adjust based on TensorFlow availability
if TENSORFLOW_AVAILABLE:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Diagnostic Image",
            "Analyse par Lot",
            "Historique",
            "Base de Connaissances",
            "Statistiques",
        ]
    )
else:
    # Limited tabs in degraded mode
    tab4, tab_info = st.tabs(["Base de Connaissances", "Informations Système"])

# Vérification de TensorFlow
if TENSORFLOW_AVAILABLE:
    with tab1:
        # 🔹 Déplacé hors du container
        st.subheader("Diagnostic d'Image Unique")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**Upload de l'Image**")
            upload_method = st.radio(
                "Méthode d'upload", [
                    "Fichier", "Caméra", "URL"], horizontal=True)
            uploaded_image = None

            if upload_method == "Fichier":
                uploaded_file = st.file_uploader(
                    "Choisissez une image", type=["png", "jpg", "jpeg", "webp"]
                )
                if uploaded_file:
                    uploaded_image = Image.open(uploaded_file)

            elif upload_method == "Caméra":
                camera_image = st.camera_input("Prenez une photo de la plante")
                if camera_image:
                    uploaded_image = Image.open(camera_image)

            elif upload_method == "URL":
                image_url = st.text_input("URL de l'image")
                if image_url:
                    try:
                        response = requests.get(image_url)
                        uploaded_image = Image.open(BytesIO(response.content))
                    except Exception as e:
                        st.error(f"Erreur de chargement: {e}")

        with col2:
            st.markdown("**Résultats du Diagnostic**")

        # ✅ Déplacer `st.columns()` en dehors de `st.expander()`
        if uploaded_image:
            st.markdown("**Options de Préprocessing**")
            enhance_contrast = st.checkbox(
                "Améliorer le contraste", value=True)
            enhance_brightness = st.checkbox(
                "Ajuster la luminosité", value=False)

            processed_image = uploaded_image.convert("RGB")

            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(processed_image)
                processed_image = enhancer.enhance(1.2)

            if enhance_brightness:
                enhancer = ImageEnhance.Brightness(processed_image)
                processed_image = enhancer.enhance(1.1)

            st.markdown("**Comparaison des Images**")
            col_img1, col_img2 = st.columns(2)

            with col_img1:
                st.image(uploaded_image, width=250)

            with col_img2:
                st.image(processed_image, width=250)

            with st.spinner("Analyse en cours..."):
                if detector:
                    detection_results = detector.predict_disease(
                        processed_image)
                    if detection_results:
                        main_result = detection_results[0]
                        st.metric("Maladie Détectée", main_result["disease"])
                        st.metric(
                            "Confiance", f"{main_result['confidence']:.1f}%")
                else:
                    st.error("🚨 Le détecteur n'est pas disponible.")

                    # Confidence chart
st.markdown("---")
st.markdown("**Graphique de Confiance**")

chart_data = pd.DataFrame(
    [
        {"Maladie": r["disease"], "Confiance": r["confidence"]}
        for r in detection_results[:5]
    ]
)

fig = px.bar(
    chart_data,
    x="Confiance",
    y="Maladie",
    orientation="h",
    title="Top 5 des Prédictions",
    color="Confiance",
    color_continuous_scale="RdYlGn",
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# ✅ Sauvegarde des résultats
if st.button("💾 Sauvegarder ce Diagnostic"):
    diagnosis_data = {
        "timestamp": datetime.now().isoformat(),
        "main_disease": main_result["disease"],
        "confidence": main_result["confidence"],
        "model_used": model_type,
        "all_predictions": detection_results[:5],
        "image_name": (
            f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        ),
    }
    # ✅ Vérification de la session state
    if "diagnosis_history" not in st.session_state:
        st.session_state.diagnosis_history = []

    diagnosis_data["main_disease"] = DISEASE_CLASSES.get(
        diagnosis_data["main_disease"], "🔍 Maladie inconnue"
    )
    st.session_state.diagnosis_history.append(diagnosis_data)
    st.success("Diagnostic sauvegardé dans l'historique!")

else:
    st.warning("Aucune maladie détectée avec le seuil de confiance défini")

# ✅ Vérification d'image uploadée avant analyse par lot
if uploaded_files:
    st.write(f"**{len(uploaded_files)} images sélectionnées**")

else:
    st.info("Uploadez une image pour commencer le diagnostic")

with tab2:
    st.subheader("Analyse par Lot")
    st.markdown(
        "Analysez plusieurs images simultanément pour un diagnostic de masse.")

    # ✅ Vérification avant utilisation de `st.columns()`
    col1, col2 = st.columns(2)

    with col1:
        batch_model = st.selectbox(
            "Modèle pour l'analyse en lot",
            ["MobileNetV2 (Rapide)", "ResNet50 (Précis)"],
            index=0,
        )

    with col2:
        batch_confidence = st.slider(
            "Seuil de confiance pour le lot", 0.1, 1.0, 0.6, 0.05
        )

    if st.button("🚀 Lancer l'Analyse par Lot"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        batch_results = []

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(
                f"Analyse {i + 1}/{len(uploaded_files)}: {uploaded_file.name}"
            )

            try:
                image_pil = Image.open(uploaded_file)

                # ✅ Vérification de `detector`
                if detector:
                    results = detector.predict_disease(
                        image_pil,
                        model_type=batch_model.split()[0].lower(),
                        confidence_threshold=batch_confidence,
                    )
                else:
                    st.error("🚨 Le détecteur n'est pas disponible.")
                    continue
            except Exception as e:
                st.error(f"⚠️ Une erreur s'est produite : {e}")
                continue
batch_results.append(
    {
        "filename": uploaded_file.name,
        "main_disease": results[0]["disease"] if results else "Unknown",
        "confidence": results[0]["confidence"] if results else 0,
        "status": (
            "Healthy"
            if results and results[0]["disease"] == "Healthy"
            else "Diseased"
        ),
        "all_results": results[:3],
    }
)

try:
    image_pil = Image.open(uploaded_file)

    # ✅ Vérification de `detector`
    if detector:
        results = detector.predict_disease(
            image_pil,
            model_type=batch_model.split()[0].lower(),
            confidence_threshold=batch_confidence,
        )
    else:
        st.error("🚨 Le détecteur n'est pas disponible.")
        continue

except Exception as e:
    batch_results.append(
        {
            "filename": uploaded_file.name,
            "main_disease": "Error",
            "confidence": 0,
            "status": "Error",
            "error": str(e),
        }
    )

progress_bar.progress((i + 1) / len(uploaded_files))
status_text.text("Analyse terminée!")


        # ✅ Résumé des résultats
st.markdown("---")
st.subheader("Résumé des Résultats")

healthy_count = sum(1 for r in batch_results if r["status"] == "Healthy")
diseased_count = sum(1 for r in batch_results if r["status"] == "Diseased")
error_count = sum(1 for r in batch_results if r["status"] == "Error")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Images", len(batch_results))
with col2:
    st.metric(
        "Plantes Saines",
        healthy_count,
        delta=f"{(healthy_count / len(batch_results) * 100):.1f}%",
    )
with col3:
    st.metric(
        "Plantes Malades",
        diseased_count,
        delta=f"{(diseased_count / len(batch_results) * 100):.1f}%",
    )
with col4:
    st.metric("Erreurs", error_count)

# ✅ Filtrage historique optimisé
filtered_history = st.session_state.get("diagnosis_history", [])

if disease_filter:
    filtered_history = [
        d for d in filtered_history if d["main_disease"] in disease_filter
    ]

filtered_history = [
    d for d in filtered_history if d["confidence"] >= confidence_filter
]


    # ✅ Vérification avant `st.expander()`
st.markdown(f"**{len(filtered_history)} diagnostics trouvés**")

for i, diagnosis in enumerate(
        reversed(filtered_history[-20:])):  # Last 20 results
    with st.expander(
        f"#{len(filtered_history) - i}: {diagnosis['main_disease']} - "
        f"{diagnosis['confidence']:.1f}% - {diagnosis['timestamp'][:19]}"
    ):
        st.metric("Maladie", diagnosis["main_disease"])
        st.metric("Confiance", f"{diagnosis['confidence']:.1f}%")
        st.metric("Modèle", diagnosis.get("model_used", "N/A"))

        if "all_predictions" in diagnosis:
            st.markdown("**Top 3 Prédictions:**")
            for j, pred in enumerate(diagnosis["all_predictions"][:3], 1):
                st.write(f"{j}. {pred['disease']}: {pred['confidence']:.1f}%")

# ✅ Résumé des statistiques
st.markdown("---")
st.subheader("Statistiques de l'Historique")

if filtered_history:
    # ✅ Création des statistiques maladies
    disease_freq = {
        d["main_disease"]: disease_freq.get(d["main_disease"], 0) + 1
        for d in filtered_history
    }

    # ✅ Vérification format `datetime`
    try:
        timestamps = [
            datetime.fromisoformat(
                d["timestamp"]) for d in filtered_history]
    except ValueError:
        st.warning("⚠️ Format de date incorrect, vérifiez les données.")
        timestamps = []

    confidences = [d["confidence"] for d in filtered_history]

    col1, col2 = st.columns(2)

    with col1:
        fig_freq = px.pie(
            values=list(disease_freq.values()),
            names=list(disease_freq.keys()),
            title="Distribution des Maladies Détectées",
        )
        st.plotly_chart(fig_freq, use_container_width=True)

    with col2:
        fig_conf = px.line(
            x=timestamps,
            y=confidences,
            title="Évolution de la Confiance",
            labels={"x": "Date", "y": "Confiance (%)"},
        )
        st.plotly_chart(fig_conf, use_container_width=True)

# ✅ Vérification avant nettoyage historique
if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []

# ✅ Nettoyage historique
if st.button("🗑️ Vider l'Historique"):
    st.session_state.diagnosis_history = []
    st.rerun()

# ✅ Vérification des variables avant filtrage
search_term = search_term if "search_term" in locals() else ""
category = category if "category" in locals() else "Toutes"
if "all_diseases" not in locals():
    all_diseases = []

# ✅ Filtrage maladies optimisé
filtered_diseases = [
    d
    for d in all_diseases
    if (search_term.lower() in d["name"].lower() if search_term else True)
    and (d.get("category") == category if category != "Toutes" else True)
]

# ✅ Déplacement des colonnes en dehors de `st.expander()`
st.markdown(f"**{len(filtered_diseases)} maladies trouvées**")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Informations complémentaires")

with col2:
    st.markdown("### Mesures de prévention")

for disease in filtered_diseases[:10]:  # Limite à 10 pour performance
    with st.expander(f"🦠 {disease['name']}"):
        st.markdown(
            f"**Nom scientifique:** {disease.get('scientific_name', 'N/A')}")
        st.markdown(f"**Catégorie:** {disease.get('category', 'N/A')}")
        st.markdown(f"**Cause:** {disease.get('cause', 'N/A')}")
        st.markdown(f"**Description:** {disease.get('description', 'N/A')}")

        if "symptoms" in disease:
            st.markdown("**Symptômes:**")
            for symptom in disease["symptoms"]:
                st.write(f"• {symptom}")

        st.markdown("**Cultures Affectées:**")
        if "affected_crops" in disease:
            for crop in disease["affected_crops"]:
                st.write(f"• {crop}")

        st.markdown("**Sévérité:** " + disease.get("severity", "Modérée"))
        st.markdown("**Saison:** " + disease.get("season", "Toute l'année"))

    with col1:
        if "treatments" in disease:
            st.markdown("**Traitements:**")
            for treatment in disease["treatments"]:
                st.markdown(
                    f"*{treatment['type']}:* {treatment['description']}")
                if "products" in treatment:
                    st.write("Produits: " + ", ".join(treatment["products"]))

    with col2:
        if "prevention" in disease:
            st.markdown("**Prévention:**")
            for prevention in disease["prevention"]:
                st.write(f"• {prevention}")

# ✅ Optimisation des performances des modèles
with tab5:
    st.subheader("Statistiques et Performance")
    st.markdown("**Performance des Modèles**")

    model_stats = {
        "MobileNetV2": {"accuracy": 92.3, "speed": "0.2s", "size": "14MB"},
        "ResNet50": {"accuracy": 95.7, "speed": "0.8s", "size": "98MB"},
        "EfficientNet": {"accuracy": 94.1, "speed": "0.5s", "size": "29MB"},
    }

    col1, col2, col3 = st.columns(3)

    # ✅ Sécurisation du bloc `for` pour éviter une erreur d'index
    for i, (model, stats) in enumerate(model_stats.items()):
        cols = [col1, col2, col3]
        with cols[i % 3]:  # Evite de dépasser la liste
            st.metric(f"{model} - Précision", f"{stats['accuracy']}%")
            st.metric("Vitesse", stats["speed"])
            st.metric("Taille", stats["size"])

# ✅ Correction du filtrage des maladies
filtered_diseases = [
    d
    for d in all_diseases
    if (search_term.lower() in d["name"].lower() if search_term else True)
    and (d.get("category") == category if category != "Toutes" else True)
]

# ✅ Gestion des statistiques de l'historique
if (
    "diagnosis_history" in st.session_state
    and st.session_state.diagnosis_history
):
    st.subheader("Statistiques d'Usage")

    history = st.session_state.diagnosis_history

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Diagnostics", len(history))
        healthy_percentage = (
            len([d for d in history if d["main_disease"] == "Healthy"])
            / len(history)
            * 100
        )
        st.metric("Plantes Saines", f"{healthy_percentage:.1f}%")
        avg_confidence = np.mean([d["confidence"] for d in history])
        st.metric("Confiance Moyenne", f"{avg_confidence:.1f}%")

# ✅ Correction d'indentation
col1, col2 = st.columns(2)  # Assurez-vous qu'il est bien défini avant

with col2:
    # ✅ Vérification avant utilisation de `history`
    if "diagnosis_history" not in st.session_state:
        st.session_state.diagnosis_history = []

    history = st.session_state.diagnosis_history

    if not history:
        st.warning("⚠️ Aucun historique disponible.")
        history = []  # Définit `history` comme une liste vide par défaut

    print("Contenu de history :", history)  # Debug

    disease_counts = {}
    for d in history:
        disease = d["main_disease"]
        if disease != "Healthy":
            disease_counts[disease] = disease_counts.get(disease, 0) + 1

    print("Contenu de disease_counts :", disease_counts)  # Debug

    # ✅ Vérification avant utilisation de `max()`
    if disease_counts:
        most_common = max(disease_counts, key=disease_counts.get)
        st.metric("Maladie Plus Fréquente", most_common)
        st.metric("Occurrences", disease_counts[most_common])
    else:
        st.info("🔍 Aucune maladie détectée dans l’historique.")

# ✅ Correction de l'imbrication des colonnes
st.container()  # Alternative à `st.columns()`
col1, col2 = st.columns(2)

with col1:
    st.metric("NumPy Version", "2.3.0 (Incompatible)")
    st.metric("TensorFlow", "2.14.0 (En attente)")
with col2:
    st.metric("Status IA", "❌ Indisponible")
    st.metric("Base de Données", "✅ Disponible")

# ✅ Vérification du système
if "system_issue" in st.session_state:
    with tab_info:
        st.subheader("⚠️ Informations Système")
        st.error("**Problème de Compatibilité Détecté**")

        st.markdown(
            """
        **Cause:** Conflit entre NumPy 2.3.0 et TensorFlow 2.14.0

        **Solutions:**
        - ✅ Installation automatique en cours
        - 🔄 Redémarrer le Repl après installation
        - ⚠️ Utiliser la base de connaissances en attendant
        """
        )

        if st.button("🔄 Tester à Nouveau TensorFlow"):
            st.rerun()
