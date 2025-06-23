import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Input, GlobalAveragePooling2D, Dense, Flatten, Concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os, json

DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"
LABELS_PATH = "C:/plateforme-agricole-complete-v2/model/labels.json"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

for sub in ["train", "val"]:
    assert os.path.exists(os.path.join(DATASET_PATH, sub)), f"❌ Dossier manquant : {sub}"

input_layer = Input(shape=(224, 224, 3))
base1 = EfficientNetB4(weights="imagenet", include_top=False, input_tensor=input_layer)
base2 = ResNet50(weights="imagenet", include_top=False, input_tensor=input_layer)

x1 = Flatten()(GlobalAveragePooling2D()(base1.output))
x2 = Flatten()(GlobalAveragePooling2D()(base2.output))
merged = Concatenate()([x1, x2])
x = Dense(256, activation="relu")(merged)
x = Dense(128, activation="relu")(x)
output = Dense(45, activation="softmax")(x)
model = Model(inputs=input_layer, outputs=output)

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Image preprocessing
gen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input)
train = gen.flow_from_directory(os.path.join(DATASET_PATH, "train"), target_size=(224, 224), batch_size=4, class_mode="categorical")
val = gen.flow_from_directory(os.path.join(DATASET_PATH, "val"), target_size=(224, 224), batch_size=4, class_mode="categorical")

model.fit(train, validation_data=val, epochs=2)
model.save(MODEL_PATH, save_format="keras")
print(f"✅ Modèle sauvegardé dans : {MODEL_PATH}")

# Sauvegarde du mapping des classes
with open(LABELS_PATH, "w") as f:
    json.dump({v: k for k, v in train.class_indices.items()}, f)
    print(f"✅ Classes sauvegardées dans : {LABELS_PATH}")
