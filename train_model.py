﻿import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB4, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Input, Concatenate, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
from tensorflow.keras.callbacks import ReduceLROnPlateau

# ðŸ”¹ DÃ©sactivation des optimisations CPU pour Ã©viter lâ€™OOM
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# ðŸ”¹ DÃ©finition des chemins
DATASET_PATH = "C:/plateforme-agricole-complete-v2/plant_disease_dataset"
MODEL_PATH = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"

# ðŸ” VÃ©rification et crÃ©ation du dossier modÃ¨le
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# âœ… **CrÃ©ation du modÃ¨le EfficientNetB4 + ResNet50**
def create_model():
    input_layer = Input(shape=(224, 224, 3), name="input_layer")

    # ðŸ”¹ Connexion des modÃ¨les sans Rescaling
    base_model_efficient = EfficientNetB4(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model_resnet = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))

    x1 = base_model_efficient(input_layer)
    x2 = base_model_resnet(input_layer)

    # ðŸ”¹ Ajout de Flatten pour amÃ©liorer la fusion des features
    x1 = GlobalAveragePooling2D()(x1)
    x2 = GlobalAveragePooling2D()(x2)
    x1 = Flatten()(x1)
    x2 = Flatten()(x2)

    merged = Concatenate()([x1, x2])

    # ðŸ”¹ Couches fully connected
    x = Dense(256, activation="relu")(merged)
    x = Dense(128, activation="relu")(x)
    output = Dense(45, activation="softmax", name="output_layer")(x)

    model = Model(inputs=input_layer, outputs=output)
    return model

# ðŸš€ CrÃ©ation et compilation du modÃ¨le
model = create_model()
model.compile(optimizer=Adam(learning_rate=0.0001), loss="categorical_crossentropy", metrics=["accuracy"])

# ðŸ”¹ Chargement et prÃ©traitement des images
train_datagen = ImageDataGenerator(
    preprocessing_function=tf.keras.applications.efficientnet.preprocess_input,  # âœ… Correction
    rotation_range=20,
    zoom_range=0.15,
    horizontal_flip=True,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "train"),
    target_size=(224, 224),
    batch_size=4,  # âœ… RÃ©duction du batch pour Ã©viter l'OOM
    class_mode="categorical"
)

val_generator = train_datagen.flow_from_directory(
    os.path.join(DATASET_PATH, "val"),
    target_size=(224, 224),
    batch_size=4,
    class_mode="categorical"
)

# ðŸ”¹ Ajout d'un callback pour ajuster le taux dâ€™apprentissage
lr_callback = ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=3, verbose=1)

# ðŸš€ **EntraÃ®nement du modÃ¨le**
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,  # âœ… RÃ©duction des epochs pour tester la stabilitÃ©
    batch_size=4,
    callbacks=[lr_callback]
)

# ðŸ’¾ **Sauvegarde du modÃ¨le avec gestion d'erreur**
try:
    model.save(MODEL_PATH, save_format="keras")
    print(f"âœ… ModÃ¨le entraÃ®nÃ© et enregistrÃ© sous {MODEL_PATH}")
except Exception as e:
    print(f"ðŸš¨ Erreur de sauvegarde : {e}")

