import streamlit as st
from utils.voice_assistant import VoiceAssistant
import os

st.set_page_config(page_title="Voice Assistant", page_icon="🗣️", layout="wide")

# Language selection stub
if 'language' not in st.session_state:
    st.session_state.language = 'en'

col1, col2 = st.columns([3, 1])
with col2:
    st.caption("Language (session)")
    # You can replace this with a real language selector
    # selected_lang = st.selectbox("Language / Langue", options=["en", "fr"], index=0)
    # st.session_state.language = selected_lang

st.title("🗣️ Voice Assistant - Agricultural (MVP)")

# Initialize assistant once (cached)
@st.singleton
def get_assistant():
    return VoiceAssistant()

assistant = get_assistant()

st.write("Upload an audio question (wav/mp3/ogg) or type a text question below. The system will transcribe (if audio), search the knowledge base, and generate a response.")

# File uploader for audio
audio_file = st.file_uploader("Upload voice (wav/mp3/ogg)", type=["wav", "mp3", "ogg"])
question_text = ""

if audio_file is not None:
    st.info("Audio received. Transcribing...")
    try:
        audio_bytes = audio_file.read()
        suffix = os.path.splitext(audio_file.name)[1]
        question_text = assistant.transcribe_audio_bytes(audio_bytes, suffix=suffix)
        st.success("Transcription completed:")
        st.write(question_text)
    except Exception as e:
        st.error(f"Transcription failed: {e}")
else:
    question_text = st.text_input("Or type your question here:")

if st.button("Ask"):
    if not question_text.strip():
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
                    source = s.get("source", "unknown")
                    chunk_id = s.get("chunk_id", "n/a")
                    st.markdown(f"- Source {i+1}: {source} (chunk {chunk_id})")

                # Optionally speak the answer
                if st.checkbox("Play audio (TTS)", value=True):
                    if hasattr(assistant, "speak"):
                        try:
                            assistant.speak(answer)
                        except Exception as e:
                            st.error("TTS error: " + str(e))
                    else:
                        st.warning("TTS function not available in this assistant.")
            except Exception as e:
                st.error("Error generating answer.")
                st.exception(e)

st.markdown("---")
st.markdown("**Notes & Tips**")
st.markdown("""
- If you use a local LLM (`LLM_MODE='local'`), choose a small model if you have limited RAM.
- For Whisper STT, install the `whisper` package and model weights (e.g. tiny/small).
- To use OpenAI, install `openai`, set `LLM_MODE='openai'`, and export your `OPENAI_API_KEY`.
- Logged outputs appear in your terminal where Streamlit runs.
""")
