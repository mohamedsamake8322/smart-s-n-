import os
import numpy as np
from typing import List, Dict, Tuple
from PIL import Image, ImageEnhance
import streamlit as st
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess # type: ignore

from utils.config_model import load_model, load_labels

class DiseaseDetector:
    def __init__(self):
        self.model = load_model()
        self.class_labels = load_labels()

    def preprocess_image(self, image_pil: Image.Image, target_size: Tuple[int, int] = (380, 380)) -> np.ndarray:
        try:
            # Redimensionnement avec fond blanc et centrage
            image_pil = image_pil.convert("RGB")
            image_pil.thumbnail(target_size, Image.Resampling.LANCZOS)
            new_image = Image.new("RGB", target_size, (255, 255, 255))
            x = (target_size[0] - image_pil.width) // 2
            y = (target_size[1] - image_pil.height) // 2
            new_image.paste(image_pil, (x, y))

            img_array = np.expand_dims(np.array(new_image, dtype=np.float32), axis=0)
            return efficientnet_preprocess(img_array)
        except Exception as e:
            st.error(f"🚨 Erreur dans le preprocessing : {e}")
            return np.zeros((1, 380, 380, 3), dtype=np.float32)

    def predict(self, image_pil: Image.Image, confidence_threshold: float = 0.7) -> List[Dict[str, str]]:
        try:
            img_array = self.preprocess_image(image_pil)
            predictions = self.model.predict(img_array, verbose=0)[0]
            sorted_indices = np.argsort(predictions)[::-1]

            results = []

            for idx in sorted_indices:
                confidence = float(predictions[idx]) * 100
                if confidence < confidence_threshold * 100:
                    break

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
        # Mapping basique de sévérité en fonction du nom de la maladie
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
            st.warning(f"⚠️ Amélioration d'image échouée : {e}")
            return image_pil
