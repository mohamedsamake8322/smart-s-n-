import os
import numpy as np
from typing import List, Dict, Tuple
from PIL import Image, ImageEnhance
import streamlit as st
import tensorflow as tf
from utils.config_model import load_model, load_labels

# Dans disease_detector.py
class DiseaseDetector:
    def __init__(self, model_path="model/default_model.keras"):
        self.model = tf.keras.models.load_model(model_path)
        self.class_labels = load_labels()  # ✅ Mapping des classes ajouté ici

    def preprocess_image(self, image_pil: Image.Image, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        try:
            image_pil = image_pil.convert("RGB")
            image_pil = image_pil.resize(target_size, Image.Resampling.LANCZOS)
            img_array = np.array(image_pil, dtype=np.float32) / 255.0
            return np.expand_dims(img_array, axis=0)
        except Exception as e:
            st.error(f"🚨 Erreur dans le prétraitement : {e}")
            return np.zeros((1, target_size[0], target_size[1], 3), dtype=np.float32)

    def predict(self, image_pil: Image.Image, confidence_threshold: float = 0.7) -> List[Dict[str, str]]:
        try:
            img_array = self.preprocess_image(image_pil)
            predictions = self.model.predict(img_array, verbose=0)[0]
            predictions = self.model.predict(img_array, verbose=0)[0]
            print("🧠 Prédictions brutes :", predictions)
            sorted_indices = np.argsort(predictions)[::-1]

            results = []
            for idx in sorted_indices[:3]:
                confidence = float(predictions[idx]) * 100
                if confidence < confidence_threshold * 100:
                    continue
                label = self.class_labels.get(str(idx), f"Classe inconnue {idx}")
                severity, urgency = self._assess_disease_severity(label, confidence)

                results.append({
                    "disease": label,
                    "confidence": round(confidence, 2),
                    "severity": severity,
                    "urgency": urgency
                })

            return results

        except Exception as e:
            st.error(f"❌ Erreur lors de la prédiction : {e}")
            return []

    def _assess_disease_severity(self, label: str, confidence: float) -> Tuple[str, str]:
        high_severity_keywords = ["blight", "rot", "wilt", "rust"]
        moderate_keywords = ["spot", "mildew"]

        severity = "Faible"
        urgency = "Faible"

        if any(word in label.lower() for word in high_severity_keywords):
            severity = "Élevée"
            urgency = "Haute"
        elif any(word in label.lower() for word in moderate_keywords):
            severity = "Modérée"
            urgency = "Moyenne"

        if confidence > 90:
            urgency = "Haute" if severity == "Élevée" else "Moyenne"

        return severity, urgency

    def enhance_image(self, image_pil: Image.Image) -> Image.Image:
        try:
            image_pil = ImageEnhance.Contrast(image_pil).enhance(1.3)
            image_pil = ImageEnhance.Sharpness(image_pil).enhance(1.2)
            image_pil = ImageEnhance.Color(image_pil).enhance(1.15)
            return image_pil
        except Exception as e:
            st.warning(f"⚠️ Amélioration d’image échouée : {e}")
            return image_pil
