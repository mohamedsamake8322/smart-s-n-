import os
import faiss  # pyright: ignore[reportMissingImports]
import pickle
import numpy as np
import pyttsx3  # pyright: ignore[reportMissingImports]
import whisper  # pyright: ignore[reportMissingImports] # openai-whisper
import torch  # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer  # pyright: ignore[reportMissingImports]


class VoiceAssistant:
    def __init__(self, vector_store_dir="vector_store", embedding_model="all-MiniLM-L6-v2", whisper_model="base"):
        self.vector_store_dir = vector_store_dir
        self.embedding_model = embedding_model
        self.whisper_model = whisper_model

        # Détection du device (CPU forcé si pas de GPU dispo)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Charger FAISS + métadonnées
        self.index, self.texts, self.metadata = self._load_vector_store()

        # Charger SentenceTransformer sans .to() puis forcer _target_device (évite bug meta tensor)
        self.embedding_model_instance = SentenceTransformer(self.embedding_model)
        self.embedding_model_instance._target_device = torch.device(self.device)

        # Charger Whisper directement sur le bon device
        self.whisper_model_instance = whisper.load_model(self.whisper_model, device=self.device)

    def _load_vector_store(self):
        """Charge FAISS + textes sauvegardés. Retourne des valeurs vides si absent."""
        try:
            index_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
            texts_path = os.path.join(self.vector_store_dir, "texts.pkl")
            metadata_path = os.path.join(self.vector_store_dir, "metadata.pkl")

            if not (os.path.exists(index_path) and os.path.exists(texts_path) and os.path.exists(metadata_path)):
                print("[INFO] Aucun index FAISS trouvé, retour à un index vide.")
                return None, [], []

            index = faiss.read_index(index_path)
            with open(texts_path, "rb") as f:
                texts = pickle.load(f)
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)

            return index, texts, metadata

        except Exception as e:
            print(f"[ERREUR] Impossible de charger le vector store : {e}")
            return None, [], []

    def search(self, query, top_k=3):
        """Recherche les passages les plus proches du query."""
        if self.index is None:
            return ["[Aucun index disponible]"]

        query_embedding = self.embedding_model_instance.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_embedding, top_k)
        return [self.texts[i] for i in I[0]]

    def speak(self, text):
        """Prononce un texte en utilisant pyttsx3."""
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def transcribe(self, audio_path):
        """Transcrit un fichier audio en texte via Whisper."""
        result = self.whisper_model_instance.transcribe(audio_path)
        return result["text"]
