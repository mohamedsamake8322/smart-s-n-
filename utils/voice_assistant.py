import os
import faiss # pyright: ignore[reportMissingImports]
import pickle
import numpy as np
import pyttsx3 # pyright: ignore[reportMissingImports]
import whisper # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer # pyright: ignore[reportMissingImports]

# -----------------------
# CONFIGURATION
# -----------------------
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
WHISPER_MODEL = "base"
VECTOR_STORE_DIR = "vector_store"

# -----------------------
# CHARGEMENT DE LA BASE VECTORIELLE
# -----------------------
def load_vector_store(vector_store_dir=VECTOR_STORE_DIR):
    index = faiss.read_index(os.path.join(vector_store_dir, "faiss_index.bin"))
    with open(os.path.join(vector_store_dir, "texts.pkl"), "rb") as f:
        texts = pickle.load(f)
    with open(os.path.join(vector_store_dir, "metadata.pkl"), "rb") as f:
        metadata = pickle.load(f)
    return index, texts, metadata

# -----------------------
# RECHERCHE SEMANTIQUE
# -----------------------
def search_query(query, index, texts, model_name=EMBEDDING_MODEL, top_k=3):
    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, top_k)
    results = [texts[i] for i in I[0]]
    return results

# -----------------------
# SYNTHÈSE VOCALE
# -----------------------
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -----------------------
# RECONNAISSANCE VOCALE
# -----------------------
def transcribe_audio(audio_path, model_name=WHISPER_MODEL):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    return result["text"]
