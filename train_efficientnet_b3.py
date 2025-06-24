import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB3, preprocess_input # type: ignore
from tensorflow.keras.models import Model # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard # type: ignore
import os
from datetime import datetime

# === 📁 Dossiers ===
base_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
train_dir = os.path.join(base_path, "train")
val_dir = os.path.join(base_path, "val")

# === 🔧 Paramètres ===
img_size = (300, 300)
batch_size = 32
epochs = 30
model_name = "efficientnet_b3_agri.keras"

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

# === 🧠 Modèle EfficientNetB3 ===
base_model = EfficientNetB3(
    include_top=False, weights="imagenet", input_shape=img_size + (3,)
)
x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.4)(x)
x = Dense(512, activation="relu")(x)
x = Dropout(0.3)(x)
output = Dense(train_data.num_classes, activation="softmax")(x)

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
    TensorBoard(log_dir=log_dir)
]

# === 🚀 Entraînement ===
model.fit(
    train_data,
    validation_data=val_data,
    epochs=epochs,
    callbacks=callbacks
)

# === ✅ Sauvegarde finale ===
model.save(model_name)
print("✅ Modèle entraîné et sauvegardé :", model_name)
