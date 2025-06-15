import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
from tensorflow.keras import layers, Model
# 🔹 Réduction des options CPU pour éviter l'OOM
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# 🔹 Définition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"

# 🔍 Vérification et création du dossier modèle
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# ✅ Création du modèle EfficientNet + ResNet avec une seule entré

def create_model():
    # Définition de la couche d'entrée
    input_layer = layers.Input(shape=(224, 224, 3), name="input_layer")

    # Ajout de la normalisation
    x = layers.Rescaling(1./255)(input_layer)

    # Exemple de quelques couches de traitement
    x = layers.Conv2D(32, (3,3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2,2))(x)
    x = layers.Conv2D(64, (3,3), activation="relu", padding="same")(x)
    x = layers.MaxPooling2D((2,2))(x)

    # Aplatissement et classification
    x = layers.Flatten()(x)
    x = layers.Dense(128, activation="relu")(x)
    output = layers.Dense(45, activation="softmax", name="output_layer")(x)  # 45 classes

    # Création du modèle
    model = Model(inputs=input_layer, outputs=output)

    return model

# Vérification de la structure du modèle
model = create_model()
model.summary()

# 🔹 Chargement et Prétraitement des images
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,  # 📌 Moins de rotation pour éviter la perte de caractéristiques
    zoom_range=0.15,  # 📌 Réduction de l'effet zoom
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224, 224),  # ✅ Réduction de la taille d'image
    batch_size=16,  # ✅ Réduction du batch pour éviter l'OOM
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224, 224),
    batch_size=16,
    class_mode="categorical"
)

# 🚀 **Entraînement du modèle**
model = create_model()
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=15,  # 📌 Réduction des epochs pour éviter le surapprentissage
    batch_size=16
)

# 💾 **Sauvegarde du modèle avec gestion d'erreur**
try:
    model.save(MODEL_PATH)
    print(f"✅ Modèle entraîné et enregistré sous {MODEL_PATH}")
except Exception as e:
    print(f"🚨 Erreur de sauvegarde : {e}")
