import tensorflow as tf
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2S, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
import os
from datetime import datetime

# === 📁 Dossiers ===
base_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
train_dir = os.path.join(base_path, "train")
val_dir = os.path.join(base_path, "val")

# === ⚙️ Paramètres ===
img_size = (384, 384)  # resolution native pour EfficientNetV2S
batch_size = 32
epochs = 30
model_name = "efficientnetv2s_waouh.keras"

# === 🚀 Accélération GPU et précision mixte (si supportée) ===
try:
    from tensorflow.keras.mixed_precision import set_global_policy
    set_global_policy("mixed_float16")
    print("✅ Précision mixte activée pour GPU moderne.")
except:
    print("ℹ️ Précision mixte non disponible.")

# === 🧪 Pré-traitement & Augmentation ===
train_gen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=25,
    zoom_range=0.25,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

val_gen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_data = train_gen.flow_from_directory(
    train_dir, target_size=img_size, batch_size=batch_size,
    class_mode="categorical", shuffle=True
)
val_data = val_gen.flow_from_directory(
    val_dir, target_size=img_size, batch_size=batch_size,
    class_mode="categorical", shuffle=False
)

# === 🧠 Modèle EfficientNetV2S avec gel intelligent ===
base_model = EfficientNetV2S(
    include_top=False, weights="imagenet", input_shape=img_size + (3,)
)
base_model.trainable = False  # freeze initial pour entraînement stable

x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.4)(x)
x = Dense(512, activation="relu")(x)
x = Dropout(0.3)(x)
output = Dense(train_data.num_classes, activation="softmax", dtype="float32")(x)  # float32 pour compat mixed_precision

model = Model(inputs=base_model.input, outputs=output)

# === ⚙️ Compilation ===
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# === 💾 Callbacks ===
log_dir = os.path.join("logs", datetime.now().strftime("%Y%m%d-%H%M%S"))
os.makedirs("checkpoints", exist_ok=True)

callbacks = [
    EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True),
    ModelCheckpoint(
        filepath=os.path.join("checkpoints", model_name),
        save_best_only=True
    ),
    TensorBoard(log_dir=log_dir),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, verbose=1)
]

# === 🔥 Entraînement du haut du réseau uniquement ===
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=epochs,
    callbacks=callbacks
)

# === 🔓 Fine-tuning : on dégèle tout EfficientNetV2S après stabilisation ===
print("🔓 Dégel complet du modèle pour fine-tuning…")
base_model.trainable = True
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

history_finetune = model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks
)

# === ✅ Sauvegarde finale ===
model.save(model_name)
print("✅ Modèle EfficientNetV2S entraîné et sauvegardé :", model_name)
