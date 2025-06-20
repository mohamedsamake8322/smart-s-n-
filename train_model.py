import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Concatenate, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ReduceLROnPlateau
import os

# 🔹 1. Optimisation CPU désactivée
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# 🔹 2. Définition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# 🔍 3. Vérification que les dossiers train/ et val/ existent
for subdir in ["train", "val"]:
    path = os.path.join(DATASET_PATH, subdir)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Dossier manquant : {path}")

# ✅ 4. Création du modèle EfficientNet + ResNet
def create_model():
    input_layer = Input(shape=(224, 224, 3), name="input_layer")

    base_model_efficient = EfficientNetB4(weights="imagenet", include_top=False, input_tensor=input_layer)
    base_model_resnet = ResNet50(weights="imagenet", include_top=False, input_tensor=input_layer)

    x1 = base_model_efficient.output
    x2 = base_model_resnet.output

    x1 = GlobalAveragePooling2D()(x1)
    x2 = GlobalAveragePooling2D()(x2)

    x1 = Flatten()(x1)
    x2 = Flatten()(x2)

    merged = Concatenate()([x1, x2])
    x = Dense(256, activation="relu")(merged)
    x = Dense(128, activation="relu")(x)
    output = Dense(45, activation="softmax", name="output_layer")(x)

    return Model(inputs=input_layer, outputs=output)

# 🚀 5. Compilation du modèle
model = create_model()
model.compile(optimizer=Adam(learning_rate=0.0001),
              loss="categorical_crossentropy",
              metrics=["accuracy"])

# 📦 6. Prétraitement des images
train_datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input,
    rotation_range=20,
    zoom_range=0.15,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224, 224),
    batch_size=4,
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224, 224),
    batch_size=4,
    class_mode="categorical"
)

# ⏱️ 7. Callback pour réduction du LR
lr_callback = ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3, verbose=1)

# 🧪 8. Entraînement léger juste pour générer le `.keras` propre
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=2,
    batch_size=4,
    callbacks=[lr_callback]
)

# 💾 9. Sauvegarde du modèle
try:
    model.save(MODEL_PATH, save_format="keras")
    print(f"✅ Modèle entraîné et enregistré avec succès : {MODEL_PATH}")
except Exception as e:
    print(f"❌ Échec de la sauvegarde : {e}")
