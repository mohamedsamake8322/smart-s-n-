# utils/voice_assistant.py
"""
Voice assistant util for Streamlit app.

Features:
- Load FAISS vector store (faiss_index.bin, texts.pkl, metadata.pkl)
- STT: Whisper (if installed) for audio -> text
- Embeddings: sentence-transformers (already used to index)
- Retrieval: FAISS
- Generation: local transformers LLM (optional) OR OpenAI
- TTS: pyttsx3 (offline) if installed

Configure constants below.
"""

import os
import tempfile
import pickle
import faiss
import traceback
from typing import List, Tuple

# Optional heavy imports wrapped in try/except
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    import whisper
except Exception:
    whisper = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

# transformers optional for local LLM
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
except Exception:
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    torch = None

# OpenAI fallback (optional)
try:
    import openai
except Exception:
    openai = None

# -----------------------
# CONFIGURATION
# -----------------------
VECTOR_STORE_DIR = "vector_store"               # where faiss_index.bin, texts.pkl, metadata.pkl are
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"      # must match the model used to build the index
TOP_K = 3                                      # number of chunks to retrieve
LLM_MODE = "local"   # "local" or "openai" or "none"  (set "none" to disable generation: returns context)
LOCAL_LLM_MODEL = "NousResearch/Llama-2-7b-hf"  # change to a small model if low RAM (or to MPT/Dolly)
USE_TTS = True                                 # use pyttsx3 to speak replies (if installed)
WHISPER_MODEL = "small"                         # "tiny","base","small","medium","large" - choose according to resources

# Generation parameters (local)
GEN_MAX_NEW_TOKENS = 150
GEN_TEMPERATURE = 0.2

# -----------------------
# VoiceAssistant class
# -----------------------
class VoiceAssistant:
    def __init__(self,
                 vector_store_dir: str = VECTOR_STORE_DIR,
                 embedding_model_name: str = EMBEDDING_MODEL_NAME,
                 top_k: int = TOP_K,
                 llm_mode: str = LLM_MODE,
                 local_llm_model: str = LOCAL_LLM_MODEL):
        self.vector_store_dir = vector_store_dir
        self.embedding_model_name = embedding_model_name
        self.top_k = top_k
        self.llm_mode = llm_mode
        self.local_llm_model = local_llm_model

        # Load FAISS & chunks
        self.index = None
        self.chunks = []
        self.metadata = []
        self._load_vector_store()

        # Load embedding model (for queries)
        self.embedding_model = None
        if SentenceTransformer is not None:
            try:
                print(f"[VA] Loading embedding model: {self.embedding_model_name}")
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
            except Exception as e:
                print("[VA] Error loading embedding model:", e)
                self.embedding_model = None

        # Load Whisper if available (STT)
        self.stt_model = None
        if whisper is not None:
            try:
                print(f"[VA] Loading Whisper STT model: {WHISPER_MODEL}")
                self.stt_model = whisper.load_model(WHISPER_MODEL)
            except Exception as e:
                print("[VA] Whisper load error:", e)
                self.stt_model = None

        # Prepare generator depending on mode
        self.generator = None
        self.tokenizer = None
        self.model = None
        if self.llm_mode == "local" and AutoTokenizer is not None:
            try:
                print(f"[VA] Loading local LLM: {self.local_llm_model} (this can be heavy)")
                self.tokenizer = AutoTokenizer.from_pretrained(self.local_llm_model)
                # CPU-friendly default; user can adjust device_map manually if they have GPU/accelerate
                self.model = AutoModelForCausalLM.from_pretrained(self.local_llm_model, device_map={"": "cpu"})
                self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer,
                                          max_new_tokens=GEN_MAX_NEW_TOKENS)
            except Exception as e:
                print("[VA] Error loading local LLM:", e)
                traceback.print_exc()
                self.generator = None
        elif self.llm_mode == "openai" and openai is not None:
            # user must set OPENAI_API_KEY in env externally
            print("[VA] OpenAI mode selected (ensure OPENAI_API_KEY is set in environment).")
        else:
            if self.llm_mode == "local":
                print("[VA] Local LLM requested but transformers or model not available. Falling back to 'none' mode.")
            elif self.llm_mode == "openai":
                print("[VA] OpenAI package not found; set llm_mode='none' or install openai.")
            self.llm_mode = "none"

        # TTS engine
        self.tts_engine = None
        if USE_TTS and pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
            except Exception as e:
                print("[VA] TTS init error:", e)
                self.tts_engine = None

        print("[VA] VoiceAssistant initialised. LLM mode:", self.llm_mode)

    # -------- vector store utilities --------
    def _load_vector_store(self):
        faiss_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
        texts_path = os.path.join(self.vector_store_dir, "texts.pkl")
        meta_path = os.path.join(self.vector_store_dir, "metadata.pkl")

        if not os.path.exists(faiss_path) or not os.path.exists(texts_path):
            raise FileNotFoundError(f"Vector store files missing in {self.vector_store_dir}. Expected faiss_index.bin and texts.pkl")

        print(f"[VA] Loading FAISS index from {faiss_path} ...")
        self.index = faiss.read_index(faiss_path)
        with open(texts_path, "rb") as f:
            self.chunks = pickle.load(f)
        try:
            with open(meta_path, "rb") as f:
                self.metadata = pickle.load(f)
        except Exception:
            self.metadata = []
        print(f"[VA] Loaded {len(self.chunks)} chunks from vector store.")

    # -------- STT --------
    def transcribe_audio_file(self, audio_path: str) -> str:
        """
        If whisper is available, transcribe audio file to text.
        Otherwise raise an informative error.
        """
        if self.stt_model is None:
            raise RuntimeError("Whisper STT model not available. Install 'whisper' and weights or set up external STT.")
        # whisper expects path
        print(f"[VA] Transcribing audio: {audio_path}")
        result = self.stt_model.transcribe(audio_path)
        text = result.get("text", "").strip()
        print("[VA] Transcription result:", text[:200], "...")
        return text

    # Alternately accept bytes (Streamlit uploader)
    def transcribe_audio_bytes(self, audio_bytes: bytes, suffix=".wav") -> str:
        fd, tmp = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        with open(tmp, "wb") as f:
            f.write(audio_bytes)
        try:
            txt = self.transcribe_audio_file(tmp)
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
        return txt

    # -------- Retrieval --------
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[str, dict]]:
        if top_k is None:
            top_k = self.top_k
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not loaded.")
        print(f"[VA] Encoding query for retrieval: {query[:80]}...")
        q_emb = self.embedding_model.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(q_emb, top_k)
        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.chunks):
                continue
            meta = self.metadata[idx] if idx < len(self.metadata) else {}
            results.append((self.chunks[idx], meta))
        return results

    # -------- Generation (RAG) --------
    def _build_prompt(self, question: str, contexts: List[str]) -> str:
        header = (
            "Tu es un assistant agricole expert. Utilise uniquement les informations fournies "
            "dans le contexte ci-dessous pour répondre.\n\nContexte (extraits) :\n"
        )
        ctx_text = "\n\n---\n\n".join(contexts)
        prompt = f"{header}{ctx_text}\n\nQuestion : {question}\nRéponse concise (français ou langue détectée) :"
        return prompt

    def generate_answer(self, question: str, top_k: int = None) -> dict:
        """
        Returns a dict: { 'answer': str, 'sources': [metadatas] }
        """
        if top_k is None:
            top_k = self.top_k

        # 1) retrieve context
        retrieved = self.retrieve(question, top_k=top_k)
        contexts = [r[0] for r in retrieved]
        sources = [r[1] for r in retrieved]

        # 2) build prompt
        prompt = self._build_prompt(question, contexts)

        # 3) generate according to selected LLM mode
        if self.llm_mode == "local" and self.generator is not None:
            try:
                print("[VA] Generating with local LLM...")
                out = self.generator(prompt, max_new_tokens=GEN_MAX_NEW_TOKENS, do_sample=False, temperature=GEN_TEMPERATURE)
                text = out[0]["generated_text"]
                # split out prompt in case generator echoes it
                if "Réponse concise" in text:
                    answer = text.split("Réponse concise")[-1].strip(": \n")
                else:
                    # try to remove repeated prompt
                    answer = text.replace(prompt, "").strip()
            except Exception as e:
                print("[VA] Local generation error:", e)
                traceback.print_exc()
                answer = "Désolé, erreur lors de la génération locale."
        elif self.llm_mode == "openai" and openai is not None:
            try:
                print("[VA] Generating with OpenAI API...")
                # Expect OPENAI_API_KEY env var set
                resp = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "Tu es un assistant agricole."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=GEN_TEMPERATURE,
                    max_tokens=300
                )
                answer = resp["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print("[VA] OpenAI generation error:", e)
                answer = "Désolé, erreur lors de la génération via OpenAI."
        else:
            # llm_mode == "none" => fallback: return concatenated contexts
            print("[VA] LLM disabled - returning concatenated context as answer.")
            answer = "Voici les informations trouvées :\n\n" + "\n\n---\n\n".join(contexts)

        return {"answer": answer, "sources": sources}

    # -------- TTS --------
    def speak(self, text: str):
        if self.tts_engine is None:
            print("[VA] TTS engine not available; skipping speak.")
            return
        try:
            print("[VA] Speaking reply...")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print("[VA] TTS error:", e)

# Simple helper/utility
def quick_demo_question(assistant: VoiceAssistant, question: str):
    print(f"\n[DEMO] Question: {question}")
    res = assistant.generate_answer(question)
    print("\n[DEMO] Answer:\n", res["answer"][:1000])
    print("\n[DEMO] Sources:", res["sources"])
