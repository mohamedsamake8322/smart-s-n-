import os
import pickle
import faiss
import numpy as np
import pyttsx3
import whisper
import torch
from sentence_transformers import SentenceTransformer


class VoiceAssistant:
    """
    VoiceAssistant v3
    - Peut charger soit FAISS (faiss_index.bin + pkl)
    - Soit directement le modèle sauvegardé (vector_db.pkl)
    - Répond précisément aux questions
    - Supporte texte + audio
    """
    def __init__(self, vector_store_dir="vector_store", vector_db_path="vector_db.pkl",
                 embedding_model="all-MiniLM-L6-v2", whisper_model="base"):
        self.vector_store_dir = vector_store_dir
        self.vector_db_path = vector_db_path
        self.embedding_model = embedding_model
        self.whisper_model = whisper_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 🔹 Charger embeddings
        self.index, self.texts, self.metadata, self.embeddings = self._load_vector_store()
        self.embedding_model_instance = SentenceTransformer(self.embedding_model)
        self.embedding_model_instance._target_device = torch.device(self.device)

        # 🔹 Charger Whisper
        self.whisper_model_instance = whisper.load_model(self.whisper_model, device=self.device)

    # -----------------------
    # 🔹 Chargement vector store
    # -----------------------
    def _load_vector_store(self):
        # Cas 1 : vector_db.pkl déjà prêt
        if os.path.exists(self.vector_db_path):
            try:
                with open(self.vector_db_path, "rb") as f:
                    data = pickle.load(f)
                print(f"[INFO] Base vectorielle chargée depuis {self.vector_db_path}")
                return None, data["texts"], data.get("metadata", [{}] * len(data["texts"])), data["embeddings"]
            except Exception as e:
                print(f"[ERREUR] Chargement {self.vector_db_path} : {e}")

        # Cas 2 : index FAISS
        try:
            index_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
            texts_path = os.path.join(self.vector_store_dir, "texts.pkl")
            metadata_path = os.path.join(self.vector_store_dir, "metadata.pkl")

            if not all(os.path.exists(p) for p in [index_path, texts_path, metadata_path]):
                print("[INFO] Aucun index vectoriel trouvé.")
                return None, [], [], None

            index = faiss.read_index(index_path)
            with open(texts_path, "rb") as f:
                texts = pickle.load(f)
            with open(metadata_path, "rb") as f:
                metadata = pickle.load(f)

            print(f"[INFO] {len(texts)} chunks chargés depuis {self.vector_store_dir}")
            return index, texts, metadata, None
        except Exception as e:
            print(f"[ERREUR] Chargement vector store : {e}")
            return None, [], [], None

    # -----------------------
    # 🔹 Recherche dans les chunks
    # -----------------------
    def search(self, query, top_k=5, min_score=0.3):
        if (self.index is None and self.embeddings is None) or not self.texts:
            return [{"text": "[Aucun index disponible]", "score": 0.0, "source": "N/A"}]

        query_embedding = self.embedding_model_instance.encode([query], convert_to_numpy=True)

        results = []
        if self.index is not None:  # Mode FAISS
            D, I = self.index.search(query_embedding, top_k)
            for dist, idx in zip(D[0], I[0]):
                score = 1 / (1 + dist)
                if score >= min_score and idx < len(self.texts):
                    results.append({
                        "text": self.texts[idx],
                        "score": round(score, 3),
                        "source": self.metadata[idx].get("source", "unknown")
                    })
        else:  # Mode vector_db.pkl (cosine similarity)
            norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            sims = np.dot(self.embeddings, query_embedding.T).flatten() / norms
            best_idx = np.argsort(-sims)[:top_k]
            for i in best_idx:
                score = float(sims[i])
                if score >= min_score:
                    results.append({
                        "text": self.texts[i],
                        "score": round(score, 3),
                        "source": self.metadata[i].get("source", "unknown")
                    })

        return results or [{"text": "[Aucune réponse pertinente trouvée]", "score": 0.0, "source": "N/A"}]

    # -----------------------
    # 🔹 Synthèse vocale
    # -----------------------
    def speak(self, text, lang="fr"):
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            if lang == "fr":
                fr_voices = [v for v in voices if "fr" in v.id or "French" in v.name]
                if fr_voices:
                    engine.setProperty("voice", fr_voices[0].id)
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"[ERREUR] Synthèse vocale : {e}")

    # -----------------------
    # 🔹 Transcription audio
    # -----------------------
    def transcribe(self, audio_path):
        try:
            result = self.whisper_model_instance.transcribe(audio_path, language="fr")
            return result.get("text", "").strip()
        except Exception as e:
            print(f"[ERREUR] Transcription audio : {e}")
            return ""

    # -----------------------
    # 🔍 Réponse intelligente
    # -----------------------
    def answer(self, query, top_k=5):
        chunks = self.search(query, top_k=top_k)
        return self._compose_answer(query, chunks)

    # -----------------------
    # 🔹 Composer la réponse
    # -----------------------
    def _compose_answer(self, query, chunks):
        if not chunks:
            return "Désolé, je n'ai pas trouvé de réponse précise à votre question."

        intro = f"🧠 Voici ce que j’ai trouvé concernant : **{query}**\n\n"
        body = ""
        for c in chunks[:5]:
            body += f"- {c['text'].strip()} (score: {c['score']})\n\n"
        return intro + body
