import tensorflow as tf
from tensorflow.keras import layers, models  # type: ignore
import os

# 🔁 Paramètres modifiables
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
NUM_CLASSES = None

train_dir = "plant_disease_dataset/train"
val_dir = "plant_disease_dataset/val"
model_dir = "model"
os.makedirs(model_dir, exist_ok=True)

# 📥 Chargement du dataset image
train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    train_dir,
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int"
)
val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    val_dir,
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    label_mode="int"
)

NUM_CLASSES = len(train_ds.class_names)
print(f"✅ {NUM_CLASSES} classes détectées : {train_ds.class_names}")

# 🚀 Prétraitement performant
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# 🌱 Pipeline de normalisation + data augmentation
data_augmentation = tf.keras.Sequential([
    layers.Rescaling(1. / 255),
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])

# 🧠 Base EfficientNetB0 gelée
base_model = tf.keras.applications.EfficientNetB0(
    include_top=False,
    input_shape=(*IMG_SIZE, 3),
    weights="imagenet"
)
base_model.trainable = False  # Warm-up training

# 🏗️ Construction du modèle
inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
x = data_augmentation(inputs)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)
model = models.Model(inputs, outputs)

# ⚙️ Compilation initiale
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# 🧠 Callbacks intelligents
callbacks = [
    tf.keras.callbacks.ModelCheckpoint(
        filepath=os.path.join(model_dir, "best_model.keras"),
        save_best_only=True,
        monitor="val_accuracy",
        verbose=1
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy",
        patience=3,
        restore_best_weights=True,
        verbose=1
    )
]

# 🔥 Phase 1 — Entraînement initial gelé
print("🚦 Phase 1 : warm-up training (EfficientNet gelé)")
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=3,
    callbacks=callbacks
)

# 🔓 Phase 2 — Fine-tuning complet
print("⚙️ Phase 2 : activation du fine-tuning")
base_model.trainable = True

# 🔁 Tu peux aussi ne défiger que les dernières couches :
# fine_tune_at = 100
# for layer in base_model.layers[:fine_tune_at]:
#     layer.trainable = False

# ❗ Recompiler impérativement après modification trainable
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# 🏋🏽 Reprise de l'entraînement
model.fit(
    train_ds,
    validation_data=val_ds,
    initial_epoch=3,
    epochs=EPOCHS,
    callbacks=callbacks
)

# 💾 Sauvegarde finale
model.save(os.path.join(model_dir, "efficientnet_agro_final.keras"))
print("✅ Entraînement complet terminé et modèle sauvegardé.")
