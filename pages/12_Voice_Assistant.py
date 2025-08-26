import streamlit as st
from utils.voice_assistant import VoiceAssistant
from utils.micro_input import get_voice_input
import os

# Configuration
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"
st.set_page_config(page_title="🧠 Smart Voice Assistant", layout="centered")
st.title("🧠 Smart Voice Assistant for Farmers")

# Initialisation de l'assistant
voice_assistant = VoiceAssistant()

# 💬 Saisie manuelle
user_message = st.text_input("Posez votre question ici (en texte)")

if user_message:
    response_text = voice_assistant.search(user_message)[0]
    st.markdown("### 🤖 Réponse de l'assistant :")
    st.write(response_text)
    voice_assistant.speak(response_text)

# 🎙️ Saisie vocale
st.markdown("---")
st.subheader("🎙️ Ou parlez directement au micro")

if st.button("🎙️ Parler maintenant"):
    try:
        user_message = get_voice_input()
        st.write(f"🗣️ Vous avez dit : {user_message}")

        if user_message:
            response_text = voice_assistant.search(user_message)[0]
            st.markdown("### 🤖 Réponse de l'assistant :")
            st.write(response_text)
            voice_assistant.speak(response_text)
        else:
            st.warning("🎤 Aucun message vocal détecté.")

    except Exception as e:
        st.error("🎙️ Erreur lors de la capture vocale :")
        st.exception(e)

# Footer
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
