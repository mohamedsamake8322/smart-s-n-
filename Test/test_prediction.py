import os
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow import keras

def main():
    MODEL_PATH = "model/efficientnet_resnet.keras"
    IMG_PATH = r"C:\Users\moham\Music\test\1-768x521-1.webp"

    # Vérification du modèle
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Modèle introuvable : {MODEL_PATH}")
        return

    # Chargement du modèle
    print("📦 Chargement du modèle...")
    try:
        model = keras.models.load_model(MODEL_PATH, compile=False)
        print("✅ Modèle chargé avec succès !")
    except Exception as e:
        print("🚨 Erreur lors du chargement du modèle :", e)
        return

    # Récupération de la taille d'entrée attendue
    _, img_height, img_width, _ = model.input_shape
    print(f"📐 Taille d'entrée attendue par le modèle : {img_width}x{img_height}")

    # Vérification de l'image
    if not os.path.exists(IMG_PATH):
        print(f"❌ Image introuvable : {IMG_PATH}")
        return

    # Chargement et prétraitement de l'image
    print("🔄 Préparation de l'image...")
    try:
        img = image.load_img(IMG_PATH, target_size=(img_height, img_width))
        print("✅ Image chargée avec succès")
    except Exception as e:
        print("❌ Erreur lors du chargement de l’image :", e)
        return

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = x / 255.0  # normalisation

    # Prédiction
    print("🧠 Prédiction en cours...")
    try:
        pred = model.predict(x)
        print("✅ Prédiction brute :", pred)
        predicted_class = np.argmax(pred, axis=1)
        print("🔎 Classe prédite (index) :", predicted_class)
    except Exception as e:
        print("🚨 Erreur pendant la prédiction :", e)

if __name__ == "__main__":
    main()
