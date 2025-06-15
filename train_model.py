import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os

# 🔹 Définition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"

# 🔍 Vérification de la présence des dossiers
if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(f"🚨 Dataset introuvable : {DATASET_PATH}")

# ✅ Création du modèle EfficientNet + ResNet
def create_model():
    """Construit et retourne un modèle combiné EfficientNetB4 + ResNet50."""
    base_model_efficient = EfficientNetB4(weights="imagenet", include_top=False)
    base_model_resnet = ResNet50(weights="imagenet", include_top=False)

    x_eff = GlobalAveragePooling2D()(base_model_efficient.output)
    x_res = GlobalAveragePooling2D()(base_model_resnet.output)
    merged = tf.keras.layers.concatenate([x_eff, x_res])

    x = Dense(256, activation="relu")(merged)
    output = Dense(4, activation="softmax")(x)  # 🔹 Ajuster selon le nombre de classes

    model = Model(inputs=[base_model_efficient.input, base_model_resnet.input], outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])
    return model

# 🔹 Chargement et Prétraitement des images
train_datagen = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(380, 380),
    batch_size=32,
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(380, 380),
    batch_size=32,
    class_mode="categorical"
)

# 🚀 **Entraînement du modèle**
model = create_model()
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=20,
    batch_size=32
)

# 💾 **Sauvegarde du modèle**
model.save(MODEL_PATH)
print(f"✅ Modèle enregistré sous {MODEL_PATH}")

