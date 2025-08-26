# pages/12_Voice_Assistant.py
import streamlit as st
from utils.voice_assistant import VoiceAssistant
import os
import tempfile

st.set_page_config(page_title="Voice Assistant", page_icon="🗣️", layout="wide")

# language selection stub (assuming you have translator util)
if 'language' not in st.session_state:
    st.session_state.language = 'en'

col1, col2 = st.columns([3, 1])
with col2:
    st.caption("Language (session)")
    # you can replace with your real translator.get_available_languages()
    # selected_lang = st.selectbox("Language / Langue", options=["en", "fr"], index=0)
    # st.session_state.language = selected_lang

st.title("🗣️ Voice Assistant - Agricultural (MVP)")

# Initialize assistant once (cached)
@st.experimental_singleton
def get_assistant():
    # adjust LLM_MODE and LOCAL_LLM_MODEL inside the util file if needed
    assistant = VoiceAssistant()
    return assistant

assistant = get_assistant()

st.write("Upload an audio question (wav/mp3) or type a text question below. The system will transcribe (if audio) then search the PDF knowledge base and generate a response.")

# File uploader for audio
audio_file = st.file_uploader("Upload voice (wav/mp3/ogg)", type=["wav", "mp3", "ogg"])
if audio_file is not None:
    st.info("Audio received. Transcribing...")
    try:
        # read bytes and send to assistant.transcribe_audio_bytes
        audio_bytes = audio_file.read()
        question_text = assistant.transcribe_audio_bytes(audio_bytes, suffix=os.path.splitext(audio_file.name)[1])
        st.success("Transcription completed:")
        st.write(question_text)
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        question_text = ""

else:
    # plain text fallback
    question_text = st.text_input("Or type your question here:")

if st.button("Ask"):
    if not question_text or question_text.strip() == "":
        st.warning("Please provide a question (audio or text).")
    else:
        with st.spinner("Searching knowledge base and generating answer..."):
            try:
                result = assistant.generate_answer(question_text)
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                st.subheader("Answer")
                st.write(answer)
                st.subheader("Sources / snippets used")
                for i, s in enumerate(sources):
                    st.markdown(f"- Source {i+1}: {s.get('source', 'unknown')} (chunk {s.get('chunk_id', 'n/a')})")
                # Optionally speak the answer
                if st.checkbox("Play audio (TTS)", value=True):
                    try:
                        assistant.speak(answer)
                    except Exception as e:
                        st.error("TTS error: " + str(e))
            except Exception as e:
                st.error("Error generating answer: " + str(e))
                st.exception(e)

st.markdown("---")
st.markdown("**Notes & Tips**")
st.markdown("""
- If you use a local LLM (LLM_MODE='local'), choose a small model if you have limited RAM.
- For Whisper STT, install the whisper package and the model weights (tiny/small).
- To use OpenAI instead, install `openai` and set `LLM_MODE='openai'` and export OPENAI_API_KEY.
- Logged outputs appear in your terminal where Streamlit runs.
""")
