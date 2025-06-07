import time
import tensorflow as tf
from PIL import Image
import pandas as pd
import tensorflow as tf
import diseases_infos  # ✅ Correct Import
import numpy as np
import cv2
load_model = tf.keras.models.load_model  # ✅ Alternative solution to avoid import conflicts


# ✅ Loading AI Model (Keras/TensorFlow)
def load_disease_model(model_path):
    """Loads a Keras/TensorFlow model for disease detection."""
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"✅ Model loaded successfully from {model_path}!")
        return model
    except Exception as e:
        print(f"🛑 Error loading model: {e}")
        return None

# 📌 Load the correct model (adaptable for `.h5` or `.keras`)
MODEL_PATH = "C:/Mah fah/model/plant_disease_model.h5"  # 🔹 Modify as needed
disease_model = load_disease_model(MODEL_PATH)

def predict_disease(image):
    """Analyzes the image to predict the disease."""
    import tensorflow as tf  # 📌 Ensure TensorFlow is available
    from diseases_infos import decode_prediction  # ✅ Utilizing decoding function

    if disease_model is None:
        return "🚨 Model not loaded, unable to predict."

    img_array = tf.keras.preprocessing.image.img_to_array(image)
    img_array = tf.expand_dims(img_array, axis=0)
    prediction = disease_model.predict(img_array)

    return decode_prediction(prediction)  # ✅ Returns the interpreted label


def preprocess_image(image_file):
    """Prepares and converts an image for disease detection."""
    try:
        # 📌 Open the image with PIL, regardless of format
        image = Image.open(image_file).convert("RGB").resize((224, 224))

        # 📌 Convert to NumPy array
        img_array = np.array(image) / 255.0  # ✅ Normalization

        # 📌 Check if OpenCV can read the image (extra safety)
        img_cv = cv2.imread(image_file) if isinstance(image_file, str) else None
        if img_cv is None:
            print("⚠️ OpenCV couldn't load the image, but PIL successfully converted it.")

        return np.expand_dims(img_array, axis=0)  # ✅ Ready for TensorFlow

    except Exception as e:
        print(f"🚨 Error processing the image: {e}")
        return None


# 🔍 Advanced Detection (Image, Symptom, Database)
def detect_disease(image=None, symptom=None):
    """
    Detects disease based on:
    - 🖼️ Image analyzed by AI model
    - 🔬 Symptom searched in the database
    - 🌍 Environmental conditions
    """
    if image and disease_model:
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = tf.expand_dims(img_array, axis=0)
        prediction = disease_model.predict(img_array)
        
        label = decode_prediction(prediction)  # AI label translation function
        disease_details = diseases_infos.get_disease_info(label) if label and label in diseases_infos.DISEASE_DATABASE else None
        detected_plant = label.split()[0] if label else "Unknown"
    
    elif symptom:
        disease_details = next((d for d in diseases_infos.DISEASE_DATABASE.values() if symptom.lower() in d["symptoms"].lower()), None)
        label = disease_details.name if disease_details else "Unknown"
        detected_plant = "Unknown"
    
    else:
        return {"error": "🚨 Provide either an image or a symptom for detection."}

    return {
        "label": label,
        "plant": detected_plant,
        "info": disease_details or "⚠️ No matching disease found."
    }

# 📌 AI Label Decoding
def decode_prediction(prediction):
    """Transforms AI prediction into a comprehensible label."""
    labels = ["Healthy", "Blight", "Rust", "Mildew"]
    return labels[prediction.argmax()] if prediction is not None else "Unknown"

# 🔍 Environmental Risk Assessment
def assess_disease_risk(crop, temperature, humidity, soil_type):
    """
    Analyzes risk factors and detects **conditions favorable for diseases**.
    - 🏜️ Abnormal temperature
    - 💦 Excessive humidity
    - 🌱 Incompatible soil type
    """
    risk_factors = {
        "Rice": {"humidity": 85, "temperature": 30, "soil": "Sandy", "risk": "High risk of **Rice Blast Disease**"},
        "Tomato": {"humidity": 80, "temperature": 28, "soil": "Clay", "risk": "High risk of **Powdery Mildew**"},
        "Maize": {"humidity": 60, "temperature": 25, "soil": "Loamy", "risk": "Moderate risk of **Fusarium Wilt**"}
    }

    crop_data = risk_factors.get(crop)
    risk_messages = []

    if crop_data:
        if humidity >= crop_data["humidity"]:
            risk_messages.append(f"💧 High Humidity favors {crop_data['risk']}")
        if temperature >= crop_data["temperature"]:
            risk_messages.append(f"🌡️ High Temperature accelerates {crop_data['risk']}")
        if soil_type == crop_data["soil"]:
            risk_messages.append(f"🌱 Unsuitable soil type may worsen {crop_data['risk']}")

    return "⚠️ " + " | ".join(risk_messages) if risk_messages else "✅ No immediate disease risk detected."

print("🚀 Unified disease detection system is fully operational!")
