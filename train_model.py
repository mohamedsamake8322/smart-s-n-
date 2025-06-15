import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os

# 🔹 Réduction des options CPU pour éviter l'OOM
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# 🔹 Définition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"

# 🔍 Vérification et création du dossier modèle
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# ✅ Création du modèle EfficientNet + ResNet avec une seule entrée
def create_model():
    """Construit un modèle fusionné (EfficientNetB4 + ResNet50) avec entrée unique."""
    input_layer = Input(shape=(224, 224, 3))  # 📌 Réduction de la taille d’entrée

    base_model_efficient = EfficientNetB4(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model_resnet = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))

    x_eff = GlobalAveragePooling2D()(base_model_efficient.output)
    x_res = GlobalAveragePooling2D()(base_model_resnet.output)
    merged = tf.keras.layers.concatenate([x_eff, x_res])

    x = Dense(256, activation="relu")(merged)
    output = Dense(45, activation="softmax")(x)  # ✅ Ajusté pour **45 classes**

    model = Model(inputs=input_layer, outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])
    return model

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
