import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
from tensorflow.keras.callbacks import ReduceLROnPlateau

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

    # 🔹 Normalisation des images avant d'entrer dans le modèle
    x = tf.keras.layers.Rescaling(1./255)(input_layer)

    # 🔹 Connexion de EfficientNetB4 et ResNet50
    base_model_efficient = EfficientNetB4(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model_resnet = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))

    x1 = base_model_efficient(x)
    x2 = base_model_resnet(x)

    # 🔹 Fusion des modèles
    x1 = GlobalAveragePooling2D()(x1)
    x2 = GlobalAveragePooling2D()(x2)
    merged = Concatenate()([x1, x2])

    # 🔹 Couches fully connected
    x = Dense(256, activation="relu")(merged)
    x = Dense(128, activation="relu")(x)
    output = Dense(45, activation="softmax", name="output_layer")(x)

    model = Model(inputs=input_layer, outputs=output)
    return model

# 🚀 Création et compilation du modèle
model = create_model()
model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])

# 🔹 Chargement et prétraitement des images
train_datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input,  # ✅ Correction
    rotation_range=20,
    zoom_range=0.15,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224, 224),
    batch_size=8,  # ✅ Réduction du batch pour éviter l'OOM
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224, 224),
    batch_size=8,
    class_mode="categorical"
)

# 🔹 Ajout d'un callback pour ajuster le taux d’apprentissage
lr_callback = ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, verbose=1)

# 🚀 **Entraînement du modèle**
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=15,  # ✅ Réduction des epochs pour éviter le surapprentissage
    batch_size=8,
    callbacks=[lr_callback]
)

# 💾 **Sauvegarde du modèle avec gestion d'erreur**
try:
    model.save(MODEL_PATH)
    print(f"✅ Modèle entraîné et enregistré sous {MODEL_PATH}")
except Exception as e:
    print(f"🚨 Erreur de sauvegarde : {e}")
