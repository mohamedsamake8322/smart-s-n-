import os
import faiss
import pickle
import numpy as np
import pyttsx3
import whisper
import torch
from sentence_transformers import SentenceTransformer


class VoiceAssistant:
    def __init__(self, vector_store_dir="vector_store", embedding_model="all-MiniLM-L6-v2", whisper_model="base"):
        self.vector_store_dir = vector_store_dir
        self.embedding_model = embedding_model
        self.whisper_model = whisper_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.index, self.texts, self.metadata = self._load_vector_store()
        self.embedding_model_instance = SentenceTransformer(self.embedding_model)
        self.embedding_model_instance._target_device = torch.device(self.device)
        self.whisper_model_instance = whisper.load_model(self.whisper_model, device=self.device)

    def _load_vector_store(self):
        try:
            index_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
            texts_path = os.path.join(self.vector_store_dir, "texts.pkl")
            metadata_path = os.path.join(self.vector_store_dir, "metadata.pkl")

            if not (os.path.exists(index_path) and os.path.exists(texts_path) and os.path.exists(metadata_path)):
                print("[INFO] Aucun index FAISS trouvé.")
                return None, [], []

            index = faiss.read_index(index_path)
            with open(texts_path, "rb") as f:
                texts = pickle.load(f)
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)

            return index, texts, metadata

        except Exception as e:
            print(f"[ERREUR] Chargement vector store : {e}")
            return None, [], []

    def search(self, query, top_k=3, min_score=0.3):
        if self.index is None:
            return [{"text": "[Aucun index disponible]", "score": 0.0, "source": "N/A"}]

        query_embedding = self.embedding_model_instance.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            score = 1 / (1 + dist)
            if score >= min_score:
                results.append({
                    "text": self.texts[idx],
                    "score": round(score, 3),
                    "source": self.metadata[idx].get("source", "unknown")
                })
        return results or [{"text": "[Aucune réponse pertinente trouvée]", "score": 0.0, "source": "N/A"}]

    def speak(self, text, lang="fr"):
        engine = pyttsx3.init()
        engine.setProperty("voice", "com.apple.speech.synthesis.voice.thomas" if lang == "fr" else "")
        engine.say(text)
        engine.runAndWait()

    def transcribe(self, audio_path):
        result = self.whisper_model_instance.transcribe(audio_path, language="fr")
        return result["text"]
