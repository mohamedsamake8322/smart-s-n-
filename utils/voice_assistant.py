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

            if not all(os.path.exists(p) for p in [index_path, texts_path, metadata_path]):
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

    def search(self, query, top_k=5, min_score=0.3):
        if self.index is None or not self.texts:
            return [{"text": "[Aucun index disponible]", "score": 0.0, "source": "N/A"}]

        query_embedding = self.embedding_model_instance.encode([query], convert_to_numpy=True)
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            score = 1 / (1 + dist)
            if score >= min_score and idx < len(self.texts):
                results.append({
                    "text": self.texts[idx],
                    "score": round(score, 3),
                    "source": self.metadata[idx].get("source", "unknown")
                })
        return results or [{"text": "[Aucune réponse pertinente trouvée]", "score": 0.0, "source": "N/A"}]

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

    def transcribe(self, audio_path):
        try:
            result = self.whisper_model_instance.transcribe(audio_path, language="fr")
            return result.get("text", "").strip()
        except Exception as e:
            print(f"[ERREUR] Transcription audio : {e}")
            return ""

    # -----------------------
    # 🔍 Moteur de réponse intelligent
    # -----------------------
    def answer(self, query, top_k=5):
        intent = self.detect_intent(query)
        keywords = self.extract_keywords(query)
        chunks = self.search(" ".join(keywords), top_k=top_k)
        filtered = self.filter_by_intent(chunks, intent)
        return self.synthesize(filtered, query)

    def detect_intent(self, query):
        q = query.lower()
        if q.startswith("qu'est-ce que") or "définis" in q or "c'est quoi" in q:
            return "definition"
        elif "comment" in q or "pourquoi" in q:
            return "explanation"
        elif "quel engrais" in q or "que dois-je utiliser" in q or "fertiliser" in q:
            return "recommendation"
        else:
            return "generic"

    def extract_keywords(self, query):
        stopwords = {"le", "la", "de", "du", "des", "et", "en", "un", "une", "pour", "avec", "sur", "dans"}
        return [word for word in query.lower().split() if word not in stopwords and len(word) > 2]

    def filter_by_intent(self, chunks, intent):
        if intent == "definition":
            return [c for c in chunks if "est" in c["text"] or "se définit" in c["text"]] or chunks
        elif intent == "recommendation":
            return [c for c in chunks if "engrais" in c["text"] or "fertilisation" in c["text"]] or chunks
        elif intent == "explanation":
            return [c for c in chunks if "parce que" in c["text"] or "cela permet" in c["text"]] or chunks
        return chunks

    def synthesize(self, chunks, query):
        intro = f"🧠 Voici ce que j’ai trouvé concernant : **{query}**\n\n"
        body = "\n\n".join([f"- {c['text'][:300].strip()}..." for c in chunks[:3]])
        return intro + body
