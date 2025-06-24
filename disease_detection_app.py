import streamlit as st
from PIL import Image
import numpy as np
import json
import keras
from datetime import datetime
from deep_translator import GoogleTranslator
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import altair as alt
from fastapi import FastAPI
# 📱 CSS pour affichage mobile responsive
st.markdown("""
<style>
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
    .stTextInput, .stTextArea, .stButton, .stSelectbox {
        font-size: 1.1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# 📦 Chemins vers ressources
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_agro_final.keras"
FICHES_PATH_EN = "mapping_fiches_maladies_en.json"
FICHES_PATH_FR = "mapping_fiches_maladies.json"

# 📁 Sauvegarde de l’historique de diagnostic
def sauvegarder_diagnostic(image_name, prediction, lang, symptoms):
    historique_path = Path("diagnostic_history.json")
    try:
        with open(historique_path, "r", encoding="utf-8") as f:
            historique = json.load(f)
    except FileNotFoundError:
        historique = []

    historique.append({
        "datetime": datetime.now().isoformat(),
        "image": image_name,
        "prediction": prediction,
        "language": lang,
        "symptoms": symptoms
    })

    with open(historique_path, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=2, ensure_ascii=False)

# 🔠 Traduction dynamique
def tr(txt, lang):
    try:
        return GoogleTranslator(source='en', target=lang).translate(txt) if lang != "en" else txt
    except:
        return txt

# 🧠 Modèle et données
@st.cache_resource
def load_model():
    return keras.models.load_model(MODEL_PATH)

@st.cache_data
def load_fiches(lang="en"):
    path = FICHES_PATH_FR if lang == "fr" else FICHES_PATH_EN
    with open(path, encoding="utf-8") as f:
        return json.load(f)
def recherche_maladies_par_symptome(query, fiches_path="mapping_fiches_maladies_en.json", top_k=5):
    with open(fiches_path, "r", encoding="utf-8") as f:
        fiches = json.load(f)

    corpus = [fiches[maladie]["symptoms"] + " " + fiches[maladie].get("description", "") for maladie in fiches]
    noms = list(fiches.keys())

    tfidf = TfidfVectorizer().fit_transform(corpus + [query])
    sim = cosine_similarity(tfidf[-1], tfidf[:-1])
    indices = sim.argsort()[0][-top_k:][::-1]

    return [(noms[i], fiches[noms[i]]) for i in indices]

app = FastAPI()

with open("repartition_maladies_afrique.json", "r", encoding="utf-8") as f:
    db = json.load(f)

@app.get("/maladies")
def get_maladies(pays: str):
    maladies = [m for m, pays_list in db.items() if pays in pays_list]
    return {"pays": pays, "maladies": maladies}

@app.get("/pays")
def get_pays(maladie: str):
    return {"maladie": maladie, "pays": db.get(maladie, [])}

# 🚀 Initialisation UI
st.set_page_config(page_title="🌿 Disease Detection", layout="wide")
lang = st.sidebar.selectbox("🌍 Language", ["English", "Français"])
lang_code = "fr" if lang == "Français" else "en"
session_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 🔄 Chargement données
fiches = load_fiches(lang_code)
labels = list(fiches.keys())
model = load_model()

# 🕓 Affichage de l’historique
with st.sidebar.expander("🕓 Historique des prédictions"):
    try:
        with open("diagnostic_history.json", encoding="utf-8") as f:
            data = json.load(f)
        for d in reversed(data[-5:]):
            st.markdown(f"🔎 **{d['prediction']}** | {d['datetime'].split('T')[0]} — Langue : {d['language']}")
            st.markdown(f"• Symptômes : {d['symptoms'][:100]}")
    except:
        st.info("Aucun historique disponible.")

# --- 📸 Image section ---
st.title(tr("Advanced Disease Detection", lang_code))
st.write(tr("Upload an image or use your camera to diagnose a disease.", lang_code))
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("🖼️ " + tr("Upload image", lang_code), type=["jpg", "png", "jpeg"])
with col2:
    camera_img = st.camera_input("📸 " + tr("Take a photo", lang_code))

final_image = camera_img or uploaded_file

# --- 📝 Symptômes ---
st.subheader(tr("Symptom Description", lang_code))
symptoms_input = st.text_area(tr("Describe the symptoms observed", lang_code))
symptom_tags = st.multiselect(tr("Quick Tags", lang_code), [
    tr("Yellowing", lang_code), tr("Wilting", lang_code), tr("Spots", lang_code),
    tr("Rot", lang_code), tr("Curl", lang_code), tr("Rust", lang_code), tr("Blight", lang_code)
])

# --- 🔍 Prédiction ---
if final_image:
    st.image(Image.open(final_image), caption=tr("Selected Image", lang_code), use_column_width=True)
    with st.spinner(tr("Analyzing image...", lang_code)):
        img = Image.open(final_image).convert("RGB").resize((224, 224))
        arr = np.expand_dims(np.array(img) / 255.0, axis=0)
        preds = model.predict(arr)
        top_indices = preds[0].argsort()[-3:][::-1]
        top_labels = [(labels[i], preds[0][i]) for i in top_indices]

    st.subheader(tr("Prediction Results", lang_code))
    for disease, score in top_labels:
        st.markdown(f"**🦠 {tr(disease, lang_code)}** – {round(score * 100, 2)} %")
        fiche = fiches.get(disease, {})
        with st.expander(tr("Disease Profile", lang_code)):
            for key, label in {
                "crop": tr("Crop", lang_code),
                "causal agent": tr("Causal Agent", lang_code),
                "description": tr("Description", lang_code),
                "symptoms": tr("Symptoms", lang_code),
                "development": tr("Development", lang_code),
                "active ingredient": tr("Active Ingredient", lang_code),
                "treatment": tr("Treatment", lang_code)
            }.items():
                st.markdown(f"**{label}:** {fiche.get(key, '')}")

    st.download_button(tr("⬇ Download diagnosis", lang_code),
        data=json.dumps(fiche, indent=2),
        file_name=f"{top_labels[0][0].replace(' ', '_')}_diagnosis.json"
    )

    # 💾 Historique sauvegarde
    sauvegarder_diagnostic(
        image_name=final_image.name if uploaded_file else "camera_capture",
        prediction=top_labels[0][0],
        lang=lang_code,
        symptoms=symptoms_input
    )

# --- 🗣 Feedback ---
with st.expander(tr("💬 Give your feedback", lang_code)):
    correction = st.text_input(tr("If prediction is wrong, type correct disease:", lang_code))
    comment = st.text_area(tr("Any comment or suggestion", lang_code))
    if st.button(tr("📤 Submit feedback", lang_code)):
        st.success(tr("Thank you! Your feedback has been saved.", lang_code))
from tensorflow.keras.layers import Input, Dense, Concatenate
from tensorflow.keras.models import Model

# Image branch
img_input = Input(shape=(224, 224, 3), name="image")
x_img = ...  # CNN (MobileNet, EfficientNet, etc.)

# Texte branch
txt_input = Input(shape=(embedding_dim,), name="symptoms_vector")
x_txt = Dense(64, activation="relu")(txt_input)

# Fusion
x = Concatenate()([x_img, x_txt])
x = Dense(128, activation="relu")(x)
out = Dense(num_classes, activation="softmax")(x)

model = Model(inputs=[img_input, txt_input], outputs=out)
import pandas as pd

df = pd.read_json("diagnostic_history.json")
df["date"] = pd.to_datetime(df["datetime"]).dt.date

# 🔢 Par maladie
df["prediction"].value_counts().plot(kind="bar")

# 📆 Évolution dans le temps
df.groupby("date").size().plot()

# 📌 Par langue
df["language"].value_counts().plot.pie()
# Chargement des données
with open("repartition_maladies_afrique.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Inversion pour compter les maladies par pays
country_disease = {}
for disease, countries in data.items():
    for country in countries:
        country_disease[country] = country_disease.get(country, 0) + 1

# Création DataFrame
df = pd.DataFrame(list(country_disease.items()), columns=["Pays", "Nombre de maladies"])

# Affichage
st.title("📊 Répartition des maladies par pays")
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Pays:N", sort="-y"),
    y="Nombre de maladies:Q"
).properties(width=800)
st.altair_chart(chart, use_container_width=True)
# Footer
st.caption(f"📅 {session_time} – Mohamed'SAMAKE Diagnostic Interface")
