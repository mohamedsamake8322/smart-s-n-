import streamlit as st
from utils.voice_assistant import VoiceAssistant
import tempfile
import os

st.set_page_config(page_title="🧠 Assistant Vocal Agricole", layout="centered")
st.title("🧠 Assistant Vocal Agricole Intelligent")

# -----------------------
# 🔹 Initialisation de l'assistant
# -----------------------
voice_assistant = VoiceAssistant(
    vector_db_path="vector_db.pkl",      # ✅ ton modèle déjà créé
    vector_store_dir="vector_store"      # fallback si FAISS existe
)

# -----------------------
# 💬 Saisie manuelle
# -----------------------
st.subheader("💬 Posez votre question en texte")

user_message = st.text_input("Votre question ici (ex : Quels sont les besoins en azote du maïs ?)")

if user_message:
    response_text = voice_assistant.answer(user_message)

    st.markdown("### 🤖 Réponse principale :")
    st.write(response_text)
    voice_assistant.speak(response_text, lang="fr")

    # 🔧 Bloc de correction
    st.markdown("---")
    st.subheader("✏️ Proposer une correction")
    correction = st.text_area("Si la réponse est incomplète ou incorrecte, proposez une meilleure formulation :")

    if st.button("📥 Soumettre la correction"):
        with open("corrections_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Question : {user_message}\n")
            f.write(f"Réponse initiale : {response_text}\n")
            f.write(f"Correction proposée : {correction}\n")
            f.write(f"---\n")
        st.success("✅ Correction enregistrée. Merci pour votre contribution !")

# -----------------------
# 🎙️ Saisie vocale
# -----------------------
st.markdown("---")
st.subheader("🎙️ Posez votre question à l'oral")

audio_file = st.file_uploader("🎧 Téléversez un fichier audio (.wav, .mp3)", type=["wav", "mp3"])

if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_file.read())
        tmp_audio_path = tmp_audio.name

    transcription = voice_assistant.transcribe(tmp_audio_path)
    os.remove(tmp_audio_path)

    st.markdown(f"📝 Transcription détectée : `{transcription}`")

    if st.button("🧠 Répondre à cette question transcrite"):
        response_text = voice_assistant.answer(transcription)
        st.markdown("### 🤖 Réponse principale :")
        st.write(response_text)
        voice_assistant.speak(response_text, lang="fr")

        # 🔧 Correction vocale
        st.markdown("---")
        st.subheader("✏️ Proposer une correction sur la transcription")
        correction = st.text_area("Si la réponse vocale est incomplète ou incorrecte, proposez une meilleure formulation :")

        if st.button("📥 Soumettre la correction vocale"):
            with open("corrections_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Question (audio) : {transcription}\n")
                f.write(f"Réponse initiale : {response_text}\n")
                f.write(f"Correction proposée : {correction}\n")
                f.write(f"---\n")
            st.success("✅ Correction enregistrée. Merci pour votre contribution !")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; padding: 20px;'>
    🌾 SmartSènè Voice Assistant - Empowering African farmers with AI-driven insights<br>
    🚀 Developed by <strong>SAMAKE</strong> | Precision farming for a better future
    </div>
    """,
    unsafe_allow_html=True
)
