import streamlit as st
from utils.voice_assistant import load_vector_store, search_query, speak, transcribe_audio
import tempfile
import os

st.set_page_config(page_title="Assistant Vocal Agricole", layout="centered")
st.title("🎙️ Assistant Vocal Agricole")

# -----------------------
# CHARGEMENT DE LA BASE
# -----------------------
index, texts, metadata = load_vector_store()

# -----------------------
# INTERFACE UTILISATEUR
# -----------------------
st.markdown("Posez une question en texte ou en audio sur l'agronomie 👇")

# Option 1 : Texte
query_text = st.text_input("Votre question (texte)")

# Option 2 : Audio
audio_file = st.file_uploader("Ou téléversez un fichier audio (.wav, .mp3)", type=["wav", "mp3"])

if st.button("🔍 Interroger"):
    if query_text:
        results = search_query(query_text, index, texts)
        st.subheader("📚 Réponse probable :")
        st.write(results[0])
        speak(results[0])
    elif audio_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
            tmp_audio.write(audio_file.read())
            tmp_audio_path = tmp_audio.name
        transcribed = transcribe_audio(tmp_audio_path)
        st.markdown(f"📝 Transcription : `{transcribed}`")
        results = search_query(transcribed, index, texts)
        st.subheader("📚 Réponse probable :")
        st.write(results[0])
        speak(results[0])
        os.remove(tmp_audio_path)
    else:
        st.warning("Veuillez entrer une question ou téléverser un fichier audio.")
