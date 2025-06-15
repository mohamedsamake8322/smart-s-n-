import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
from tensorflow.keras.callbacks import ReduceLROnPlateau
import numpy as np
from PIL import Image

# 🔹 Réduction des options CPU pour éviter l'OOM
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# 🔹 Définition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"

# 🔍 Vérification et création du dossier modèle
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# ✅ **Création du modèle EfficientNetB4 + ResNet50**
def create_model():
    input_layer = Input(shape=(224, 224, 3), name="input_layer")

    # 🔹 Ajout de la normalisation
    x = tf.keras.layers.Rescaling(1./255)(input_layer)

    # 🔹 Bases pré-entraînées EfficientNetB4 et ResNet50
    base_model_efficientnet = EfficientNetB4(weights="imagenet", include_top=False, input_tensor=x)
    base_model_resnet = ResNet50(weights="imagenet", include_top=False, input_tensor=x)

    # 🔹 Fusion des deux modèles
    x1 = GlobalAveragePooling2D()(base_model_efficientnet.output)
    x2 = GlobalAveragePooling2D()(base_model_resnet.output)
    merged = Concatenate()([x1, x2])

    # 🔹 Ajout de couches fully connected
    x = Dense(256, activation="relu")(merged)
    x = Dense(128, activation="relu")(x)
    output = Dense(45, activation="softmax", name="output_layer")(x)  # 45 classes

    model = Model(inputs=input_layer, outputs=output)

    return model

# 🚀 Création et compilation du modèle
model = create_model()
model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])

# 📌 **Prétraitement des images avec gestion de transparence**
def preprocess_image(img):
    if isinstance(img, np.ndarray):  # Vérification si c'est bien un tableau NumPy
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8)  # Normalisation en uint8 si nécessaire
        img = Image.fromarray(img)  # Conversion en image PIL

    return img.convert("RGBA").convert("RGB")  # Conversion transparente → RGB
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_image,
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.15,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224, 224),
    batch_size=16,
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224, 224),
    batch_size=16,
    class_mode="categorical"
)

# 🔹 Ajout d'un callback pour ajuster le taux d’apprentissage
lr_callback = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1)

# 🚀 **Entraînement du modèle**
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=25,  # Augmentation des epochs pour une meilleure convergence
    batch_size=16,
    callbacks=[lr_callback]
)

# 💾 **Sauvegarde du modèle avec gestion d'erreur**
try:
    model.save(MODEL_PATH)
    print(f"✅ Modèle entraîné et enregistré sous {MODEL_PATH}")
except Exception as e:
    print(f"🚨 Erreur de sauvegarde : {e}")
