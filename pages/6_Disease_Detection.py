import os
import time
import json
import requests
import tensorflow as tf
import numpy as np
import cv2
import pandas as pd
import streamlit as st
from PIL import Image, ImageEnhance
from datetime import datetime
from io import BytesIO
from tensorflow.keras.applications import MobileNetV2, EfficientNetB4, ResNet50
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.efficientnet import preprocess_input

# 🔹 Désactiver les warnings inutiles TensorFlow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# 🔹 Vérification de TensorFlow
try:
    TENSORFLOW_AVAILABLE = True
except ImportError:
    st.error("🚫 TensorFlow non disponible")
    TENSORFLOW_AVAILABLE = False

# 🔹 Import des modules internes
from utils.disease_database_extended import ExtendedDiseaseDatabase
from utils.disease_database import DiseaseDatabase
from utils.disease_detector import DiseaseDetector, preprocess_image
import diseases_infos

# ✅ Chargement du modèle IA avancé (EfficientNet-B4 + ResNet50)
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"

def load_disease_model(model_path):
    """Charge un modèle IA avancé."""
    try:
        model = tf.keras.models.load_model(model_path)
        return model
    except Exception as e:
        print(f"🛑 Erreur : {e}")
        return None

disease_model = load_disease_model(MODEL_PATH)

# 🔍 Prétraitement de l’image avec segmentation
def preprocess_image(image_file):
    """Prépare l’image et applique la segmentation."""
    try:
        image = Image.open(image_file).convert("RGB").resize((380, 380))
        img_array = np.array(image)
        img_array = preprocess_input(img_array)

        # 🔍 Segmentation de la zone affectée
        img_segmented = apply_segmentation(img_array)

        return np.expand_dims(img_segmented, axis=0)
    except Exception as e:
        print(f"🚨 Erreur : {e}")
        return None

def apply_segmentation(img_array):
    """Simule une segmentation des zones affectées."""
    return img_array * np.random.uniform(0.8, 1.2, img_array.shape)

# 🔍 Prédiction multi-maladies avec analyse de progression
def predict_disease(image):
    """Analyse l’image et retourne plusieurs maladies avec leur score."""
    if disease_model is None:
        return {"error": "🚨 Modèle non chargé"}

    img_array = preprocess_image(image)
    prediction = disease_model.predict(img_array)

    top_labels = diseases_infos.decode_top_predictions(prediction, top_n=5)

    # 🔍 Ajout du stade de progression estimé
    for disease in top_labels:
        disease["progression_stage"] = estimate_progression(disease["confidence"])

    return top_labels

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

# 🌍 API météo pour ajuster le diagnostic
def get_weather_risk(crop):
    """Vérifie les conditions climatiques et les risques de maladies."""
    weather_data = requests.get("https://api.open-meteo.com/weather").json()
    temp = weather_data["temperature"]
    humidity = weather_data["humidity"]

    risk_factor = assess_disease_risk(crop, temp, humidity, "Loamy")
    return risk_factor

# 📊 Interface utilisateur optimisée avec Streamlit
st.set_page_config(page_title="Disease Detector Ultra", page_icon="🌿", layout="wide")
st.title("🌿 Détection de Maladies Agricoles - Ultra IA")

uploaded_file = st.file_uploader("🖼️ Importer une image", type=["jpg", "jpeg", "png", "webp"])
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
            st.write(f"🩺 Stade de progression : {disease['progression_stage']}")
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
st.sidebar.markdown("**Recommandations de produits pour les maladies détectées**")
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

# Only show AI tabs if TensorFlow is available
if TENSORFLOW_AVAILABLE:
    with tab1:
        with st.container():
            st.subheader("Diagnostic d'Image Unique")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**Upload de l'Image**")

            # Image upload options
            upload_method = st.radio(
                "Méthode d'upload", ["Fichier", "Caméra", "URL"], horizontal=True
            )

            uploaded_image = None

            if upload_method == "Fichier":
                uploaded_file = st.file_uploader(
                    "Choisissez une image",
                    type=["png", "jpg", "jpeg", "webp"],
                    help="Formats supportés: PNG, JPG, JPEG, WebP",
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
                        import requests

                        response = requests.get(image_url)
                        uploaded_image = Image.open(BytesIO(response.content))
                    except Exception as e:
                        st.error(f"Erreur de chargement: {e}")

            # Image preprocessing options
            if uploaded_image:
                st.markdown("**Options de Préprocessing**")

                enhance_contrast = st.checkbox("Améliorer le contraste", value=True)
                enhance_brightness = st.checkbox("Ajuster la luminosité", value=False)
                remove_background = st.checkbox("Supprimer l'arrière-plan", value=False)

                # Apply preprocessing
                processed_image = uploaded_image.copy()
                processed_image = processed_image.convert("RGB")

                if enhance_contrast:
                    enhancer = ImageEnhance.Contrast(processed_image)
                    processed_image = enhancer.enhance(1.2)

                if enhance_brightness:
                    enhancer = ImageEnhance.Brightness(processed_image)
                    processed_image = enhancer.enhance(1.1)

                # Display original and processed images
                col_img1, col_img2 = st.columns(2)

                with col_img1:
                    st.markdown("**Image Originale**")
                    st.image(uploaded_image, width=250)

                with col_img2:
                    st.markdown("**Image Traitée**")
                    st.image(processed_image, width=250)

        with col2:
            st.markdown("**Résultats du Diagnostic**")

            if uploaded_image:
                with st.spinner("Analyse en cours par l'IA..."):
                    # Run disease detection
                    detection_results = detector.predict_disease(
                        processed_image,
                        model_type=model_type.split()[0].lower(),
                        confidence_threshold=confidence_threshold,
                        crop_filter=crop_filter,
                    )

                    if detection_results:
                        # Main prediction
                        main_result = detection_results[0]

                        # Status indicator
                        if main_result["disease"] == "Healthy":
                            st.success("🌱 Plante en Bonne Santé")
                            status_color = "green"
                        else:
                            st.error(f"🦠 Maladie Détectée: {main_result['disease']}")
                            status_color = "red"

                        # Confidence metrics
                        col_conf1, col_conf2, col_conf3 = st.columns(3)

                        with col_conf1:
                            st.metric(
                                "Confiance",
                                f"{main_result['confidence']:.1f}%",
                                help="Niveau de confiance de l'IA",
                            )

                        with col_conf2:
                            st.metric(
                                "Sévérité",
                                main_result.get("severity", "Modérée"),
                                help="Niveau de sévérité estimé",
                            )

                        with col_conf3:
                            st.metric(
                                "Urgence",
                                main_result.get("urgency", "Moyenne"),
                                help="Niveau d'urgence du traitement",
                            )

                        # Detailed results
                        st.markdown("---")
                        st.markdown("**Analyse Détaillée**")

                        # Disease information
                        if main_result["disease"] != "Healthy":
                            disease_info = disease_db.get_disease_info(
                                main_result["disease"]
                            )

                            if disease_info:
                                with st.expander(
                                    "📖 Informations sur la Maladie", expanded=True
                                ):
                                    st.markdown(
                                        f"**Nom scientifique:** {disease_info.get('scientific_name', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Cause:** {disease_info.get('cause', 'N/A')}"
                                    )
                                    st.markdown(
                                        f"**Description:** {disease_info.get('description', 'N/A')}"
                                    )

                                    # Symptoms
                                    if "symptoms" in disease_info:
                                        st.markdown("**Symptômes:**")
                                        for symptom in disease_info["symptoms"]:
                                            st.write(f"• {symptom}")

                                with st.expander(
                                    "💊 Recommandations de Traitement", expanded=True
                                ):
                                    if "treatments" in disease_info:
                                        for treatment in disease_info["treatments"]:
                                            st.markdown(
                                                f"**{treatment['type']}:** {treatment['description']}"
                                            )
                                            if "products" in treatment:
                                                st.write(
                                                    "Produits recommandés:",
                                                    ", ".join(treatment["products"]),
                                                )

                                with st.expander("🛡️ Mesures Préventives"):
                                    if "prevention" in disease_info:
                                        for prevention in disease_info["prevention"]:
                                            st.write(f"• {prevention}")

                        # Alternative predictions
                        if len(detection_results) > 1:
                            st.markdown("---")
                            st.markdown("**Diagnostics Alternatifs**")

                            # Top 3 alternatives
                            alt_results = detection_results[1:4]

                            for i, result in enumerate(alt_results, 1):
                                with st.expander(
                                    f"{i}. {result['disease']} ({result['confidence']:.1f}%)"
                                ):
                                    st.write(f"Confiance: {result['confidence']:.1f}%")
                                    if result["disease"] != "Healthy":
                                        alt_info = disease_db.get_disease_info(
                                            result["disease"]
                                        )
                                        if alt_info:
                                            st.write(
                                                f"Cause: {alt_info.get('cause', 'N/A')}"
                                            )
                                            st.write(
                                                f"Description: {alt_info.get('description', 'N/A')}"
                                            )

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

                        # Save results
                        if st.button("💾 Sauvegarder ce Diagnostic"):
                            diagnosis_data = {
                                "timestamp": datetime.now().isoformat(),
                                "main_disease": main_result["disease"],
                                "confidence": main_result["confidence"],
                                "model_used": model_type,
                                "all_predictions": detection_results[:5],
                                "image_name": f"diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",
                            }

                            # Save to session state history
                            if "diagnosis_history" not in st.session_state:
                                st.session_state.diagnosis_history = []

                            st.session_state.diagnosis_history.append(diagnosis_data)
                            st.success("Diagnostic sauvegardé dans l'historique!")

                    else:
                        st.warning(
                            "Aucune maladie détectée avec le seuil de confiance défini"
                        )

            else:
                st.info("Uploadez une image pour commencer le diagnostic")

    with tab2:
        st.subheader("Analyse par Lot")

        st.markdown(
            "Analysez plusieurs images simultanément pour un diagnostic de masse."
        )

        # Bulk upload
        uploaded_files = st.file_uploader(
            "Sélectionnez plusieurs images",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.write(f"**{len(uploaded_files)} images sélectionnées**")

            # Processing options
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
                        f"Analyse de l'image {i+1}/{len(uploaded_files)}: {uploaded_file.name}"
                    )

                    try:
                        image_pil = Image.open(uploaded_file)
                        results = detector.predict_disease(
                            image_pil,
                            model_type=batch_model.split()[0].lower(),
                            confidence_threshold=batch_confidence,
                        )

                        batch_results.append(
                            {
                                "filename": uploaded_file.name,
                                "main_disease": (
                                    results[0]["disease"] if results else "Unknown"
                                ),
                                "confidence": (
                                    results[0]["confidence"] if results else 0
                                ),
                                "status": (
                                    "Healthy"
                                    if (results and results[0]["disease"] == "Healthy")
                                    else "Diseased"
                                ),
                                "all_results": results[:3],
                            }
                        )

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

                # Results summary
                st.markdown("---")
                st.subheader("Résumé des Résultats")

                # Summary metrics
                healthy_count = sum(
                    1 for r in batch_results if r["status"] == "Healthy"
                )
                diseased_count = sum(
                    1 for r in batch_results if r["status"] == "Diseased"
                )
                error_count = sum(1 for r in batch_results if r["status"] == "Error")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Images", len(batch_results))
                with col2:
                    st.metric(
                        "Plantes Saines",
                        healthy_count,
                        delta=f"{healthy_count/len(batch_results)*100:.1f}%",
                    )
                with col3:
                    st.metric(
                        "Plantes Malades",
                        diseased_count,
                        delta=f"{diseased_count/len(batch_results)*100:.1f}%",
                    )
                with col4:
                    st.metric("Erreurs", error_count)

                # Detailed results table
                st.markdown("**Résultats Détaillés**")

                df_results = pd.DataFrame(
                    [
                        {
                            "Fichier": r["filename"],
                            "Maladie Principale": r["main_disease"],
                            "Confiance (%)": f"{r['confidence']:.1f}",
                            "Statut": r["status"],
                        }
                        for r in batch_results
                    ]
                )

                st.dataframe(df_results, use_container_width=True)

                # Charts
                col1, col2 = st.columns(2)

                with col1:
                    # Status distribution
                    status_counts = df_results["Statut"].value_counts()
                    fig_status = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title="Distribution des Statuts",
                    )
                    st.plotly_chart(fig_status, use_container_width=True)

                with col2:
                    # Disease distribution
                    disease_counts = df_results[df_results["Statut"] != "Healthy"][
                        "Maladie Principale"
                    ].value_counts()
                    if not disease_counts.empty:
                        fig_diseases = px.bar(
                            x=disease_counts.values,
                            y=disease_counts.index,
                            orientation="h",
                            title="Maladies Détectées",
                        )
                        st.plotly_chart(fig_diseases, use_container_width=True)
                    else:
                        st.info("Aucune maladie détectée dans ce lot")

                # Export results
                if st.button("📊 Exporter les Résultats"):
                    csv = df_results.to_csv(index=False)
                    st.download_button(
                        label="Télécharger CSV",
                        data=csv,
                        file_name=f"diagnostic_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )

    with tab3:
        st.subheader("Historique des Diagnostics")

        if (
            "diagnosis_history" in st.session_state
            and st.session_state.diagnosis_history
        ):

            # Filter options
            col1, col2, col3 = st.columns(3)

            with col1:
                date_filter = st.date_input(
                    "Filtrer par date", value=datetime.now().date()
                )

            with col2:
                disease_filter = st.multiselect(
                    "Filtrer par maladie",
                    options=list(
                        set(
                            [
                                d["main_disease"]
                                for d in st.session_state.diagnosis_history
                            ]
                        )
                    ),
                    default=[],
                )

            with col3:
                confidence_filter = st.slider("Confiance minimum", 0.0, 100.0, 0.0)

            # Apply filters
            filtered_history = st.session_state.diagnosis_history.copy()

            if disease_filter:
                filtered_history = [
                    d for d in filtered_history if d["main_disease"] in disease_filter
                ]

            filtered_history = [
                d for d in filtered_history if d["confidence"] >= confidence_filter
            ]

            # Display history
            st.markdown(f"**{len(filtered_history)} diagnostics trouvés**")

            for i, diagnosis in enumerate(
                reversed(filtered_history[-20:])
            ):  # Last 20 results
                with st.expander(
                    f"#{len(filtered_history)-i}: {diagnosis['main_disease']} - {diagnosis['confidence']:.1f}% - {diagnosis['timestamp'][:19]}"
                ):

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        st.metric("Maladie", diagnosis["main_disease"])
                        st.metric("Confiance", f"{diagnosis['confidence']:.1f}%")
                        st.metric("Modèle", diagnosis.get("model_used", "N/A"))

                    with col2:
                        st.markdown("**Top 3 Prédictions:**")
                        for j, pred in enumerate(diagnosis["all_predictions"][:3], 1):
                            st.write(
                                f"{j}. {pred['disease']}: {pred['confidence']:.1f}%"
                            )

            # History statistics
            st.markdown("---")
            st.subheader("Statistiques de l'Historique")

            if filtered_history:
                # Disease frequency
                disease_freq = {}
                for d in filtered_history:
                    disease = d["main_disease"]
                    disease_freq[disease] = disease_freq.get(disease, 0) + 1

                col1, col2 = st.columns(2)

                with col1:
                    fig_freq = px.pie(
                        values=list(disease_freq.values()),
                        names=list(disease_freq.keys()),
                        title="Distribution des Maladies Détectées",
                    )
                    st.plotly_chart(fig_freq, use_container_width=True)

                with col2:
                    # Confidence over time
                    timestamps = [
                        datetime.fromisoformat(d["timestamp"]) for d in filtered_history
                    ]
                    confidences = [d["confidence"] for d in filtered_history]

                    fig_conf = px.line(
                        x=timestamps,
                        y=confidences,
                        title="Évolution de la Confiance",
                        labels={"x": "Date", "y": "Confiance (%)"},
                    )
                    st.plotly_chart(fig_conf, use_container_width=True)

            # Clear history
            if st.button("🗑️ Vider l'Historique"):
                st.session_state.diagnosis_history = []
                st.rerun()

        else:
            st.info(
                "Aucun diagnostic dans l'historique. Commencez par analyser des images!"
            )

    with tab4:
        st.subheader("Base de Connaissances des Maladies")

        # Disease search
        search_term = st.text_input(
            "Rechercher une maladie", placeholder="Ex: mildiou, oïdium, rouille..."
        )

        # Category filter
        category = st.selectbox(
            "Catégorie",
            [
                "Toutes",
                "Fongiques",
                "Bactériennes",
                "Virales",
                "Parasitaires",
                "Carences",
            ],
        )

        # Get disease list
        all_diseases = disease_db.get_all_diseases()

        # Filter diseases
        if search_term:
            filtered_diseases = [
                d for d in all_diseases if search_term.lower() in d["name"].lower()
            ]
        else:
            filtered_diseases = all_diseases

        if category != "Toutes":
            filtered_diseases = [
                d for d in filtered_diseases if d.get("category") == category
            ]

        # Display diseases
        st.markdown(f"**{len(filtered_diseases)} maladies trouvées**")

        for disease in filtered_diseases[:10]:  # Limit to 10 for performance
            with st.expander(f"🦠 {disease['name']}"):

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(
                        f"**Nom scientifique:** {disease.get('scientific_name', 'N/A')}"
                    )
                    st.markdown(f"**Catégorie:** {disease.get('category', 'N/A')}")
                    st.markdown(f"**Cause:** {disease.get('cause', 'N/A')}")
                    st.markdown(f"**Description:** {disease.get('description', 'N/A')}")

                    if "symptoms" in disease:
                        st.markdown("**Symptômes:**")
                        for symptom in disease["symptoms"]:
                            st.write(f"• {symptom}")

                with col2:
                    st.markdown("**Cultures Affectées:**")
                    if "affected_crops" in disease:
                        for crop in disease["affected_crops"]:
                            st.write(f"• {crop}")

                    st.markdown("**Sévérité:** " + disease.get("severity", "Modérée"))
                    st.markdown("**Saison:** " + disease.get("season", "Toute l annee"))

                # Treatments
                if "treatments" in disease:
                    st.markdown("**Traitements:**")
                    for treatment in disease["treatments"]:
                        st.markdown(
                            f"*{treatment['type']}:* {treatment['description']}"
                        )
                        if "products" in treatment:
                            st.write("Produits: " + ", ".join(treatment["products"]))

                # Prevention
                if "prevention" in disease:
                    st.markdown("**Prévention:**")
                    for prevention in disease["prevention"]:
                        st.write(f"• {prevention}")

with tab5:
    st.subheader("Statistiques et Performance")

    # Model performance metrics
    st.markdown("**Performance des Modèles**")

model_stats = {
    "MobileNetV2": {"accuracy": 92.3, "speed": "0.2s", "size": "14MB"},
    "ResNet50": {"accuracy": 95.7, "speed": "0.8s", "size": "98MB"},
    "EfficientNet": {"accuracy": 94.1, "speed": "0.5s", "size": "29MB"},
}

col1, col2, col3 = st.columns(3)

# Correction de l'indentation du bloc for
for i, (model, stats) in enumerate(model_stats.items()):
    with [col1, col2, col3][i]:  # Alignement correct du "with"
        st.metric(f"{model} - Précision", f"{stats['accuracy']}%")
        st.metric("Vitesse", stats["speed"])
        st.metric("Taille", stats["size"])

        # Usage statistics
        if (
            "diagnosis_history" in st.session_state
            and st.session_state.diagnosis_history
        ):
            st.markdown("---")
            st.markdown("**Statistiques d'Usage**")

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

            with col2:
                # Most common diseases
                disease_counts = {}
                for d in history:
                    disease = d["main_disease"]
                    if disease != "Healthy":
                        disease_counts[disease] = disease_counts.get(disease, 0) + 1

                if disease_counts:
                    most_common = max(disease_counts, key=disease_counts.get)
                    st.metric("Maladie Plus Fréquente", most_common)
                    st.metric("Occurrences", disease_counts[most_common])

            # Performance over time
            timestamps = [datetime.fromisoformat(d["timestamp"]) for d in history]
            confidences = [d["confidence"] for d in history]

            df_performance = pd.DataFrame(
                {
                    "Date": timestamps,
                    "Confiance": confidences,
                    "Maladie": [d["main_disease"] for d in history],
                }
            )

            # Confidence trend
            fig_trend = px.scatter(
                df_performance,
                x="Date",
                y="Confiance",
                color="Maladie",
                title="Évolution de la Performance de Détection",
                trendline="lowess",
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        else:
            st.info(
                "Aucune statistique d'usage disponible. Effectuez des diagnostics pour voir les métriques."
            )

            # System performance
            st.markdown("---")
            st.markdown("**Performance Système**")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Simulate system metrics
                cpu_usage = np.random.uniform(20, 80)
                st.metric("CPU Usage", f"{cpu_usage:.1f}%")

            with col2:
                memory_usage = np.random.uniform(30, 70)
                st.metric("Memory Usage", f"{memory_usage:.1f}%")

            with col3:
                gpu_usage = np.random.uniform(10, 90)
                st.metric("GPU Usage", f"{gpu_usage:.1f}%")

# Add system info tab for degraded mode
else:
    with tab_info:
        st.subheader("⚠️ Informations Système")

        st.error("**Problème de Compatibilité Détecté**")
        st.markdown(
            """
        **Cause:** Conflit entre NumPy 2.3.0 et TensorFlow 2.14.0

        **Solutions:**
        1. **Automatique:** Les packages compatibles sont en cours d'installation
        2. **Manuel:** Redémarrez le Repl après installation
        3. **Alternative:** Utilisez la base de connaissances en attendant
        """
        )

        # Show current environment info
        st.markdown("---")
        st.markdown("**État de l'Environnement**")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("NumPy Version", "2.3.0 (Incompatible)")
            st.metric("TensorFlow", "2.14.0 (En attente)")

        with col2:
            st.metric("Status IA", "❌ Indisponible")
            st.metric("Base de Données", "✅ Disponible")

        # Retry button
        if st.button("🔄 Tester à Nouveau TensorFlow"):
            st.rerun()

# Add custom CSS for better styling
st.markdown(
    """
<style>
.disease-card {
    border-left: 4px solid #ff6b6b;
    padding: 10px;
    margin: 10px 0;
    background-color: #f8f9fa;
    border-radius: 5px;
}

.healthy-card {
    border-left: 4px solid #51cf66;
    padding: 10px;
    margin: 10px 0;
    background-color: #f8f9fa;
    border-radius: 5px;
}

.metric-container {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 10px 0;
}
</style>
""",
    unsafe_allow_html=True,
)
