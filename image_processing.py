import os
import cv2
import numpy as np
import logging
from PIL import Image

# 🚀 Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def upload_image(image_file, save_path="uploads/"):
    """Allows image uploading and saving with error handling."""
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 🔹 Extension verification
    allowed_extensions = {"jpg", "jpeg", "png", "bmp", "gif", "tiff"}
    file_extension = image_file.name.split(".")[-1].lower()

    if file_extension not in allowed_extensions:
        return "🚨 Unsupported image format."

    file_path = os.path.join(save_path, image_file.name)
    
    try:
        with open(file_path, "wb") as f:
            f.write(image_file.getbuffer())
        logger.info(f"✅ Image successfully saved: {file_path}")
    except Exception as e:
        logger.error(f"🚨 Error saving the image: {e}")
        return f"🚨 Error: {e}"

    return file_path

def preprocess_image(image_path):
    """Prepares the image for prediction by normalizing and resizing it."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"🚨 File not found: {image_path}")

    try:
        image = Image.open(image_path)
        image = image.convert("RGB")  # Ensures color compatibility
        image = image.resize((224, 224))  # Suitable size for the model
        image = np.array(image) / 255.0  # Normalization
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        logger.info(f"📊 Image successfully preprocessed: {image.shape}")
        return image
    
    except Exception as e:
        logger.error(f"🚨 Error preprocessing the image: {e}")
        raise RuntimeError(f"🚨 Unable to process the image: {e}")
print("✅ Script exécuté avec succès !")
