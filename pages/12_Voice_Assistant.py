import streamlit as st
from utils.voice_assistant import VoiceAssistant
from utils.micro_input import get_voice_input
import tempfile
import os

st.set_page_config(page_title="🧠 Smart Voice Assistant", layout="centered")
st.title("🧠 Assistant Vocal Agricole Intelligent")

voice_assistant = VoiceAssistant()

# -----------------------
# 💬 Saisie manuelle
# -----------------------
st.subheader("💬 Posez votre question en texte")

user_message = st.text_input("Votre question ici (ex : Quels sont les besoins en azote du maïs ?)")

if user_message:
    results = voice_assistant.search(user_message, top_k=3)
    st.markdown("### 🤖 Réponse principale :")
    st.write(results[0]["text"])
    voice_assistant.speak(results[0]["text"])

    with st.expander("🔍 Voir les autres suggestions"):
        for r in results[1:]:
            st.markdown(f"**Source** : `{r['source']}` | **Score** : `{r['score']}`")
            st.write(r["text"])
            st.markdown("---")

    # 🔧 Bloc de correction
    st.markdown("---")
    st.subheader("✏️ Proposer une correction")
    correction = st.text_area("Si la réponse est incomplète ou incorrecte, proposez une meilleure formulation :")

    if st.button("📥 Soumettre la correction"):
        with open("corrections_log.txt", "a", encoding="utf-8") as f:
            f.write(f"Question : {user_message}\n")
            f.write(f"Réponse initiale : {results[0]['text']}\n")
            f.write(f"Correction proposée : {correction}\n")
            f.write(f"---\n")
        st.success("✅ Correction enregistrée. Merci pour votre contribution !")

# -----------------------
# 🎙️ Saisie vocale
# -----------------------
st.markdown("---")
st.subheader("🎙️ Parlez au micro")

audio_file = st.file_uploader("🎧 Téléversez un fichier audio (.wav, .mp3)", type=["wav", "mp3"])

if audio_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio:
        tmp_audio.write(audio_file.read())
        tmp_audio_path = tmp_audio.name

    transcription = voice_assistant.transcribe(tmp_audio_path)
    st.markdown(f"📝 Transcription détectée : `{transcription}`")
    os.remove(tmp_audio_path)

    if st.button("🧠 Répondre à cette question transcrite"):
        results = voice_assistant.search(transcription, top_k=3)
        st.markdown("### 🤖 Réponse principale :")
        st.write(results[0]["text"])
        voice_assistant.speak(results[0]["text"])

        with st.expander("🔍 Voir les autres suggestions"):
            for r in results[1:]:
                st.markdown(f"**Source** : `{r['source']}` | **Score** : `{r['score']}`")
                st.write(r["text"])
                st.markdown("---")

        # 🔧 Correction vocale
        st.markdown("---")
        st.subheader("✏️ Proposer une correction sur la transcription")
        correction = st.text_area("Si la réponse vocale est incomplète ou incorrecte, proposez une meilleure formulation :")

        if st.button("📥 Soumettre la correction vocale"):
            with open("corrections_log.txt", "a", encoding="utf-8") as f:
                f.write(f"Question (audio) : {transcription}\n")
                f.write(f"Réponse initiale : {results[0]['text']}\n")
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
    🌾 SmartSènè Voice Assistant - Empowering African farmers with AI-driven insights
    🚀 Developed by <strong>SAMAKE</strong> | Precision farming for a better future
    </div>
    """,
    unsafe_allow_html=True
)
