import os
import faiss # pyright: ignore[reportMissingImports]
import pickle
import numpy as np
import pyttsx3 # pyright: ignore[reportMissingImports]
import whisper # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer # pyright: ignore[reportMissingImports]

class VoiceAssistant:
    def __init__(self, vector_store_dir="vector_store", embedding_model="all-MiniLM-L6-v2", whisper_model="base"):
        self.vector_store_dir = vector_store_dir
        self.embedding_model = embedding_model
        self.whisper_model = whisper_model
        self.index, self.texts, self.metadata = self._load_vector_store()
        self.embedding_model_instance = SentenceTransformer(self.embedding_model)
        self.whisper_model_instance = whisper.load_model(self.whisper_model)

    def _load_vector_store(self):
        index = faiss.read_index(os.path.join(self.vector_store_dir, "faiss_index.bin"))
        with open(os.path.join(self.vector_store_dir, "texts.pkl"), "rb") as f:
            texts = pickle.load(f)
        with open(os.path.join(self.vector_store_dir, "metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)
        return index, texts, metadata

    def search(self, query, top_k=3):
        query_embedding = self.embedding_model_instance.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_embedding, top_k)
        return [self.texts[i] for i in I[0]]

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def transcribe(self, audio_path):
        result = self.whisper_model_instance.transcribe(audio_path)
        return result["text"]
