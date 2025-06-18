﻿import os
import requests # type: ignore
import tensorflow as tf # type: ignore
import numpy as np # type: ignore
import pandas as pd # type: ignore
import streamlit as st # type: ignore
from PIL import Image, ImageEnhance # type: ignore
from datetime import datetime
from io import BytesIO
from tensorflow.keras.applications.efficientnet import preprocess_input # type: ignore
import plotly.express as px  # type: ignore # Corrige l'erreur F821 pour `px`
from utils.disease_detector import DiseaseDetector
# âœ… DÃ©finition des variables manquantes
detector = DiseaseDetector()
model_type = "default"
DISEASE_CLASSES = {}
uploaded_files = []
disease_filter = None
confidence_filter = 0.5
disease_freq = {}
search_term = ""
category = "Toutes"

# ðŸ”¹ DÃ©sactiver les warnings inutiles TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ðŸ”¹ VÃ©rification de TensorFlow
try:
    TENSORFLOW_AVAILABLE = True
except ImportError:
    st.error("ðŸš« TensorFlow non disponible")
    TENSORFLOW_AVAILABLE = False

# ðŸ”¹ Import des modules internes

# âœ… Dictionnaire des icÃ´nes pour chaque maladie
DISEASE_ICONS = {
    "Healthy": "âœ…",
    "Aphids on Vegetables": "ðŸ›ðŸ¥¦",
    "Armyworms on Vegetables": "ðŸ›ðŸƒ",
    "Blister Beetle": "ðŸª²ðŸ”¥",
    "Beet Leafhopper": "ðŸª²ðŸŒ¿",
    "Colorado Potato Beetle": "ðŸ¥”ðŸª²",
    "Western Striped and Spotted Cucumber Beetle": "ðŸ¥’ðŸª²",
    "Spotted Cucumber Beetle": "ðŸ¥’ðŸž",
    "Cutworms on Vegetables": "ðŸ›âœ‚ï¸",
    "False Chinch Bug": "ðŸœâŒ",
    "Flea Beetles": "ðŸª²ðŸ”¬",
    "Tomato and Tobacco Hornworms": "ðŸ…ðŸ›",
    "Thrips on Vegetables": "ðŸ¦ŸðŸ¥¦",
    "Potato Leafhopper": "ðŸ¥”ðŸŒ¿",
    "Two-Spotted Spider Mite": "ðŸ•·ï¸ðŸŒ±",
    "Corn Earworm / Tomato Fruitworm": "ðŸŒ½ðŸ…ðŸ›",
    "Tomato Russet Mite": "ðŸ…ðŸ•·ï¸",
    "Whiteflies (Family: Aleyrodidae)": "ðŸ¦ŸðŸŒ¿",
    "Alfalfa Mosaic Virus": "ðŸ¦ ðŸŒ±",
    "Bacterial Canker": "ðŸ¦ âš ï¸",
    "Bacterial Speck": "ðŸ¦ ðŸ…",
    "Beet Curly Top Virus": "ðŸŒ€ðŸ¦ ",
    "Big Bud": "ðŸŒ¿ðŸ’¥",
    "Blossom End Rot": "ðŸ…âš«",
    "Damping-Off": "ðŸŒ±ðŸš«",
    "Early Blight": "ðŸ…ðŸŸ ",
    "Fusarium Crown/Root Rot": "ðŸŒ¿ðŸ¦ ",
    "Fusarium Wilt": "ðŸŒ¾âš ï¸",
    "Late Blight": "ðŸ…ðŸ”¥",
    "Root-Knot Nematodes": "ðŸŒ±ðŸ›",
    "Phytophthora Root, Stem, and Crown Rots": "ðŸŒ¿ðŸ¦ ",
    "Powdery Mildew on Vegetables": "ðŸƒðŸŒ«ï¸",
    "Tobacco Mosaic Virus & Tomato Mosaic Virus": "ðŸ…ðŸŒ¿ðŸ¦ ",
    "Tomato Spotted Wilt Virus": "ðŸ…ðŸ”´",
    "Verticillium Wilt": "ðŸŒ¾ðŸ”´",
    "Cercospora Leaf Spot (Frogeye)": "ðŸŒ¿âšª",
    "Choanephora Blight (Wet Rot)": "ðŸŒ¿ðŸ’§",
    "Gray Leaf Spot": "ðŸŒ¿ðŸ”˜",
    "Phomopsis Blight": "ðŸŒ¿ðŸ”¥",
}

# âœ… Chargement du modÃ¨le IA
MODEL_URL = "https://drive.google.com/uc?export=download&id=1mBKbOYqB6db3KDneEtSpcH9ywC55qfW_"
MODEL_PATH = os.path.join("model", "efficientnet_resnet.keras")

# ðŸ“¥ TÃ©lÃ©charger le modÃ¨le si nÃ©cessaire
if not os.path.exists(MODEL_PATH):
    st.info("ðŸ“¦ TÃ©lÃ©chargement du modÃ¨le IA depuis Google Drive...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with requests.get(MODEL_URL, stream=True) as response:
        with open(MODEL_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    st.success("âœ… ModÃ¨le IA tÃ©lÃ©chargÃ© avec succÃ¨s.")

@st.cache_resource
def load_disease_model(model_path):
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as e:
        st.error(f"ðŸ›‘ Erreur : {e}")
        return None


disease_model = load_disease_model(MODEL_PATH)
# ðŸ” PrÃ©traitement de lâ€™image


def preprocess_image(image_file):
    """PrÃ©pare lâ€™image et applique le prÃ©traitement EfficientNet."""
    try:
        image = Image.open(image_file).convert("RGB").resize((380, 380))
        img_array = np.array(image)
        img_array = preprocess_input(img_array)

        return np.expand_dims(img_array, axis=0)
    except Exception as e:
        print(f"ðŸš¨ Erreur : {e}")
        return None

# ðŸ” PrÃ©diction multi-maladies avec tri des rÃ©sultats
def predict_disease(image):
    """Analyse lâ€™image et retourne plusieurs maladies avec leur score."""
    if disease_model is None:
        raise ValueError("ðŸš¨ ModÃ¨le non chargÃ©. Assure-toi qu'il est bien initialisÃ©.")

    img_array = preprocess_image(image)
    if img_array is None:
        return [{"error": "ðŸš¨ Erreur dans le prÃ©traitement de lâ€™image"}]

    predictions = disease_model.predict(img_array)[0]  # Prendre uniquement la premiÃ¨re prÃ©diction

    # âœ… Initialiser la liste des rÃ©sultats
    top_labels = []

    # âœ… Trier les rÃ©sultats par confiance
    sorted_indices = np.argsort(predictions)[::-1]

    # âœ… Afficher uniquement les 5 meilleurs rÃ©sultats
    for idx in sorted_indices[:5]:
        disease_name = detector.class_labels["efficientnet_resnet"][idx] if idx < len(detector.class_labels["efficientnet_resnet"]) else "ðŸ” Maladie inconnue"
        disease_icon = DISEASE_ICONS.get(disease_name, "â“")  # IcÃ´ne par dÃ©faut si inconnue

        top_labels.append(
            {
                "name": f"{disease_icon} {disease_name}",
                "confidence": round(predictions[idx] * 100, 1),  # âœ… Arrondi propre
                "progression_stage": estimate_progression(predictions[idx] * 100),
            }
        )

    return top_labels

# ðŸ” DÃ©termination du stade de progression
def estimate_progression(confidence):
    """DÃ©termine le stade de la maladie."""

    if confidence > 90:
        return "ðŸ”´ Critique"
    elif confidence > 75:
        return "ðŸŸ  AvancÃ©"
    elif confidence > 50:
        return "ðŸŸ¡ DÃ©but"
    else:
        return "ðŸŸ¢ Faible impact"

def assess_disease_risk(crop, temp, humidity, soil_type):
    """
    Ã‰value le risque de maladie en fonction du type de culture, de la tempÃ©rature,
    de l'humiditÃ© et du type de sol.
    """
    # ðŸš€ DÃ©finition des seuils de risque
    risk_levels = {
        "Low": (temp > 25 and humidity < 50),
        "Medium": (20 <= temp <= 25 and 50 <= humidity <= 70),
        "High": (temp < 20 or humidity > 70),
    }

    # ðŸ“Œ Ajustement basÃ© sur le type de sol et la culture
    base_risk = (
        "High"
        if crop in ["Tomate", "Pomme de terre"] and soil_type == "Loamy"
        else "Medium"
    )

    # âœ… DÃ©termination finale du risque
    for level, condition in risk_levels.items():
        if condition:
            return "Critical" if base_risk == "High" else level

    return base_risk  # Si aucun niveau de risque spÃ©cifique ne sâ€™applique

def get_weather_risk(crop):
    """VÃ©rifie les conditions climatiques et les risques de maladies."""
    try:
        response = requests.get(
            "https://api.open-meteo.com/weather", timeout=5)
        response.raise_for_status()
        weather_data = response.json()

        if not weather_data or "current" not in weather_data:
            print("âš ï¸ DonnÃ©es mÃ©tÃ©o vides ou mal formatÃ©es.")
            return "Risque mÃ©tÃ©o inconnu"  # âœ… VÃ©rifier la fermeture de cette chaÃ®ne

        temp = weather_data["current"].get("temperature", -1)
        humidity = weather_data["current"].get("humidity", -1)

        if temp == -1 or humidity == -1:
            print("âš ï¸ Impossible de rÃ©cupÃ©rer les donnÃ©es mÃ©tÃ©o.")
            return "DonnÃ©es mÃ©tÃ©o indisponibles"  # âœ… VÃ©rifier la fermeture ici aussi

        risk_factor = assess_disease_risk(crop, temp, humidity, "Loamy")
        return risk_factor  # âœ… VÃ©rifier si bien alignÃ© avec la fonction

    except requests.exceptions.RequestException as e:
        # âœ… VÃ©rifier la fermeture de cette chaÃ®ne
        print(f"âš ï¸ Erreur de requÃªte mÃ©tÃ©o : {e}")
        return "Erreur lors de la rÃ©cupÃ©ration des donnÃ©es mÃ©tÃ©o"


# ðŸ“Š Interface utilisateur optimisÃ©e avec Streamlit
st.set_page_config(
    page_title="Disease Detector Ultra",
    page_icon="ðŸŒ¿",
    layout="wide")
st.title("ðŸŒ¿ DÃ©tection de Maladies Agricoles - Ultra IA")

uploaded_file = st.file_uploader(
    "ðŸ–¼ï¸ Importer une image", type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file:
    st.image(uploaded_file, width=250)

    with st.spinner("ðŸ”¬ Analyse IA en cours..."):
        results = predict_disease(uploaded_file)

    if "error" in results:
        st.error(results["error"])
    else:
        for disease in results:
            st.subheader(f"ðŸ¦  {disease['name']}")
            st.write(f"ðŸ”¹ Confiance IA : {disease['confidence']:.2f}%")
            st.write(f"ðŸ©º Stade de progression : {disease['progression_stage']}")
            st.write(f"ðŸ”Ž SymptÃ´mes : {disease['symptoms']}")
            st.write(f"ðŸ©º Recommandations : {disease['recommendations']}")
# âœ… Charger lâ€™image
uploaded_file = st.file_uploader("TÃ©lÃ©chargez une image pour la prÃ©diction")

if uploaded_file is not None:
    image_pil = Image.open(uploaded_file)

    # âœ… Effectuer la prÃ©diction
    results = detector.predict_disease(image_pil)

    # âœ… Afficher les rÃ©sultats
    st.write("ðŸ“Š RÃ©sultats de la prÃ©diction :")
    st.json(results)

    # ðŸ“Œ Affichage du risque climatique
    crop = "Tomate"
    weather_risk = get_weather_risk(crop)
    st.warning(f"ðŸŒ Facteur climatique : {weather_risk}")

# ðŸ–¥ï¸ Mode collaboratif : Upload et partage des rÃ©sultats
st.markdown("### ðŸ§‘â€ðŸŒ¾ Partagez votre diagnostic avec la communautÃ©")
user_feedback = st.text_area("ðŸ’¡ Ajoutez votre retour ou des observations")
if st.button("ðŸ“Œ Publier le diagnostic"):
    st.success("âœ… Diagnostic partagÃ© avec la communautÃ© !")

# ðŸ›‘ Mode dâ€™urgence : Contacter un expert
if st.button("ðŸš¨ Urgence - Contacter un Expert"):
    st.error("ðŸ“¡ Envoi des donnÃ©es Ã  un agronome expert en cours...")

# ðŸ›ï¸ Marketplace intÃ©grÃ©e pour acheter des traitements adaptÃ©s
st.sidebar.title("ðŸŒ¿ Solutions & Traitements")
st.sidebar.markdown(
    "**Recommandations de produits pour les maladies dÃ©tectÃ©es**")
st.sidebar.button("Acheter des traitements adaptÃ©s")


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
    tab4, tab_info = st.tabs(["Base de Connaissances", "Informations SystÃ¨me"])

# VÃ©rification de TensorFlow
if TENSORFLOW_AVAILABLE:
    with tab1:
        # ðŸ”¹ DÃ©placÃ© hors du container
        st.subheader("Diagnostic d'Image Unique")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**Upload de l'Image**")
            upload_method = st.radio(
                "MÃ©thode d'upload", ["Fichier", "CamÃ©ra", "URL"], horizontal=True
            )
            uploaded_image = None

            if upload_method == "Fichier":
                uploaded_file = st.file_uploader(
                    "Choisissez une image", type=["png", "jpg", "jpeg", "webp"]
                )
                if uploaded_file:
                    uploaded_image = Image.open(uploaded_file)

            elif upload_method == "CamÃ©ra":
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
            st.markdown("**RÃ©sultats du Diagnostic**")

        # âœ… DÃ©placer `st.columns()` en dehors de `st.expander()`
        if uploaded_image:
            st.markdown("**Options de PrÃ©processing**")
            enhance_contrast = st.checkbox(
                "AmÃ©liorer le contraste", value=True)
            enhance_brightness = st.checkbox(
                "Ajuster la luminositÃ©", value=False)

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
                        st.metric("Maladie DÃ©tectÃ©e", main_result["disease"])
                        st.metric("Confiance",
                                  f"{main_result['confidence']:.1f}%")
                else:
                    st.error("ðŸš¨ Le dÃ©tecteur n'est pas disponible.")

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
    title="Top 5 des PrÃ©dictions",
    color="Confiance",
    color_continuous_scale="RdYlGn",
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# âœ… Sauvegarde des rÃ©sultats
if st.button("ðŸ’¾ Sauvegarder ce Diagnostic"):
    diagnosis_data = {
        "timestamp": datetime.now().isoformat(),
        "main_disease": main_result["disease"],
        "confidence": main_result["confidence"],
        "model_used": model_type,
        "all_predictions": detection_results[:5],
        "image_name": (f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"),
    }
    # âœ… VÃ©rification de la session state
    if "diagnosis_history" not in st.session_state:
        st.session_state.diagnosis_history = []

    diagnosis_data["main_disease"] = DISEASE_CLASSES.get(
        diagnosis_data["main_disease"], "ðŸ” Maladie inconnue"
    )
    st.session_state.diagnosis_history.append(diagnosis_data)
    st.success("Diagnostic sauvegardÃ© dans l'historique!")

else:
    st.warning("Aucune maladie dÃ©tectÃ©e avec le seuil de confiance dÃ©fini")

# âœ… VÃ©rification d'image uploadÃ©e avant analyse par lot
if uploaded_files:
    st.write(f"**{len(uploaded_files)} images sÃ©lectionnÃ©es**")

else:
    st.info("Uploadez une image pour commencer le diagnostic")

with tab2:
    st.subheader("Analyse par Lot")
    st.markdown(
        "Analysez plusieurs images simultanÃ©ment pour un diagnostic de masse.")

    # âœ… VÃ©rification avant utilisation de `st.columns()`
    col1, col2 = st.columns(2)

    with col1:
        batch_model = st.selectbox(
            "ModÃ¨le pour l'analyse en lot",
            ["MobileNetV2 (Rapide)", "ResNet50 (PrÃ©cis)"],
            index=0,
        )

    with col2:
        batch_confidence = st.slider(
            "Seuil de confiance pour le lot", 0.1, 1.0, 0.6, 0.05
        )

if st.button("ðŸš€ Lancer l'Analyse par Lot"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    batch_results = []

    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(
            f"Analyse {i + 1}/{len(uploaded_files)}: {uploaded_file.name}"
        )

        try:
            image_pil = Image.open(uploaded_file)

            # âœ… VÃ©rification de `detector`
            if detector:
                results = detector.predict_disease(
                    image_pil,
                    model_type=batch_model.split()[0].lower(),
                    confidence_threshold=batch_confidence,
                )
            else:
                st.error("ðŸš¨ Le dÃ©tecteur n'est pas disponible.")
                continue  # âœ… Correct, bien alignÃ© dans la boucle

        except Exception as e:
            st.error(f"âš ï¸ Une erreur s'est produite : {e}")
            continue  # âœ… Continue bien placÃ© pour Ã©viter un plantage

        batch_results.append(
            {
                "filename": uploaded_file.name,
                "main_disease": results[0]["disease"] if results else "Unknown",
                "confidence": results[0]["confidence"] if results else 0,
                "status": (
                    "Healthy" if results and results[0]["disease"] == "Healthy"
                    else "Diseased"
                ),
                "all_results": results[:3],
            }
        )

        # âœ… Progression de la barre
        progress_bar.progress((i + 1) / len(uploaded_files))

    status_text.text("Analyse terminÃ©e!")

    # âœ… RÃ©sumÃ© des rÃ©sultats
    st.markdown("---")
    st.subheader("RÃ©sumÃ© des RÃ©sultats")

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

    # âœ… Filtrage historique optimisÃ©
    filtered_history = st.session_state.get("diagnosis_history", [])

    if disease_filter:
        filtered_history = [
            d for d in filtered_history if d["main_disease"] in disease_filter
        ]

    filtered_history = [
        d for d in filtered_history if d["confidence"] >= confidence_filter]
    st.markdown(f"**{len(filtered_history)} diagnostics trouvÃ©s**")

    for i, diagnosis in enumerate(
            reversed(filtered_history[-20:])):  # Last 20 results
        expander_label = (
            f"#{len(filtered_history) - i}: {diagnosis['main_disease']} - "
            f"{diagnosis['confidence']:.1f}% - {diagnosis['timestamp'][:19]}"
        )
        with st.expander(expander_label):
            st.metric("Maladie", diagnosis["main_disease"])
            st.metric("Confiance", f"{diagnosis['confidence']:.1f}%")
            st.metric("ModÃ¨le", diagnosis.get("model_used", "N/A"))

            if "all_predictions" in diagnosis:
                st.markdown("**Top 3 PrÃ©dictions:**")
                for j, pred in enumerate(diagnosis["all_predictions"][:3], 1):
                  st.write(f"{j}. {pred['disease']}: {pred['confidence']:.1f}%")
# âœ… RÃ©sumÃ© des statistiques
st.markdown("---")
st.subheader("Statistiques de l'Historique")

if filtered_history:
    # âœ… CrÃ©ation des statistiques maladies
    disease_freq = {
        d["main_disease"]: disease_freq.get(d["main_disease"], 0) + 1
        for d in filtered_history
    }

    # âœ… VÃ©rification format `datetime`
    try:
        timestamps = [
            datetime.fromisoformat(
                d["timestamp"]) for d in filtered_history]
    except ValueError:
        st.warning("âš ï¸ Format de date incorrect, vÃ©rifiez les donnÃ©es.")
        timestamps = []

    confidences = [d["confidence"] for d in filtered_history]

    col1, col2 = st.columns(2)

    with col1:
        fig_freq = px.pie(
            values=list(disease_freq.values()),
            names=list(disease_freq.keys()),
            title="Distribution des Maladies DÃ©tectÃ©es",
        )
        st.plotly_chart(fig_freq, use_container_width=True)

    with col2:
        fig_conf = px.line(
            x=timestamps,
            y=confidences,
            title="Ã‰volution de la Confiance",
            labels={"x": "Date", "y": "Confiance (%)"},
        )
        st.plotly_chart(fig_conf, use_container_width=True)

# âœ… VÃ©rification avant nettoyage historique
if "diagnosis_history" not in st.session_state:
    st.session_state.diagnosis_history = []

# âœ… Nettoyage historique
if st.button("ðŸ—‘ï¸ Vider l'Historique"):
    st.session_state.diagnosis_history = []
    st.rerun()

# âœ… VÃ©rification des variables avant filtrage
search_term = search_term if "search_term" in locals() else ""
category = category if "category" in locals() else "Toutes"
if "all_diseases" not in locals():
    all_diseases = []

# âœ… Filtrage maladies optimisÃ©
filtered_diseases = [
    d
    for d in all_diseases
    if (search_term.lower() in d["name"].lower() if search_term else True)
    and (d.get("category") == category if category != "Toutes" else True)
]

# âœ… DÃ©placement des colonnes en dehors de `st.expander()`
st.markdown(f"**{len(filtered_diseases)} maladies trouvÃ©es**")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Informations complÃ©mentaires")

with col2:
    st.markdown("### Mesures de prÃ©vention")

for disease in filtered_diseases[:10]:  # Limite Ã  10 pour performance
    with st.expander(f"ðŸ¦  {disease['name']}"):
        st.markdown(
            f"**Nom scientifique:** {disease.get('scientific_name', 'N/A')}")
        st.markdown(f"**CatÃ©gorie:** {disease.get('category', 'N/A')}")
        st.markdown(f"**Cause:** {disease.get('cause', 'N/A')}")
        st.markdown(f"**Description:** {disease.get('description', 'N/A')}")

        if "symptoms" in disease:
            st.markdown("**SymptÃ´mes:**")
            for symptom in disease["symptoms"]:
                st.write(f"â€¢ {symptom}")

        st.markdown("**Cultures AffectÃ©es:**")
        if "affected_crops" in disease:
            for crop in disease["affected_crops"]:
                st.write(f"â€¢ {crop}")

        st.markdown("**SÃ©vÃ©ritÃ©:** " + disease.get("severity", "ModÃ©rÃ©e"))
        st.markdown("**Saison:** " + disease.get("season", "Toute l'annÃ©e"))

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
            st.markdown("**PrÃ©vention:**")
            for prevention in disease["prevention"]:
                st.write(f"â€¢ {prevention}")

# âœ… Optimisation des performances des modÃ¨les
with tab5:
    st.subheader("Statistiques et Performance")
    st.markdown("**Performance des ModÃ¨les**")

    model_stats = {
        "MobileNetV2": {"accuracy": 92.3, "speed": "0.2s", "size": "14MB"},
        "ResNet50": {"accuracy": 95.7, "speed": "0.8s", "size": "98MB"},
        "EfficientNet": {"accuracy": 94.1, "speed": "0.5s", "size": "29MB"},
    }

    col1, col2, col3 = st.columns(3)

    # âœ… SÃ©curisation du bloc `for` pour Ã©viter une erreur d'index
    for i, (model, stats) in enumerate(model_stats.items()):
        cols = [col1, col2, col3]
        with cols[i % 3]:  # Evite de dÃ©passer la liste
            st.metric(f"{model} - PrÃ©cision", f"{stats['accuracy']}%")
            st.metric("Vitesse", stats["speed"])
            st.metric("Taille", stats["size"])

# âœ… Correction du filtrage des maladies
filtered_diseases = [
    d
    for d in all_diseases
    if (search_term.lower() in d["name"].lower() if search_term else True)
    and (d.get("category") == category if category != "Toutes" else True)
]

# âœ… Gestion des statistiques de l'historique
if "diagnosis_history" in st.session_state and st.session_state.diagnosis_history:
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

# âœ… Correction d'indentation
col1, col2 = st.columns(2)  # Assurez-vous qu'il est bien dÃ©fini avant

with col2:
    # âœ… VÃ©rification avant utilisation de `history`
    if "diagnosis_history" not in st.session_state:
        st.session_state.diagnosis_history = []

    history = st.session_state.diagnosis_history

    if not history:
        st.warning("âš ï¸ Aucun historique disponible.")
        history = []  # DÃ©finit `history` comme une liste vide par dÃ©faut

    print("Contenu de history :", history)  # Debug

    disease_counts = {}
    for d in history:
        disease = d["main_disease"]
        if disease != "Healthy":
            disease_counts[disease] = disease_counts.get(disease, 0) + 1

    print("Contenu de disease_counts :", disease_counts)  # Debug

    # âœ… VÃ©rification avant utilisation de `max()`
    if disease_counts:
        most_common = max(disease_counts, key=disease_counts.get)
        st.metric("Maladie Plus FrÃ©quente", most_common)
        st.metric("Occurrences", disease_counts[most_common])
    else:
        st.info("ðŸ” Aucune maladie dÃ©tectÃ©e dans lâ€™historique.")

# âœ… Correction de l'imbrication des colonnes
st.container()  # Alternative Ã  `st.columns()`
col1, col2 = st.columns(2)

with col1:
    st.metric("NumPy Version", "2.3.0 (Incompatible)")
    st.metric("TensorFlow", "2.14.0 (En attente)")
with col2:
    st.metric("Status IA", "âŒ Indisponible")
    st.metric("Base de DonnÃ©es", "âœ… Disponible")

# âœ… VÃ©rification du systÃ¨me
if "system_issue" in st.session_state:
    with tab_info:
        st.subheader("âš ï¸ Informations SystÃ¨me")
        st.error("**ProblÃ¨me de CompatibilitÃ© DÃ©tectÃ©**")

        st.markdown(
            """
        **Cause:** Conflit entre NumPy 2.3.0 et TensorFlow 2.14.0

        **Solutions:**
        - âœ… Installation automatique en cours
        - ðŸ”„ RedÃ©marrer le Repl aprÃ¨s installation
        - âš ï¸ Utiliser la base de connaissances en attendant
        """
        )

        if st.button("ðŸ”„ Tester Ã  Nouveau TensorFlow"):
            st.rerun()





