import tensorflow as tf
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2S, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau
from tensorflow.keras.utils import Sequence
from PIL import Image, UnidentifiedImageError
import os
from datetime import datetime

# === 📁 Dossiers ===
base_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
train_dir = os.path.join(base_path, "train")
val_dir = os.path.join(base_path, "val")

# === ⚙️ Paramètres ===
img_size = (384, 384)
batch_size = 32
epochs = 30
model_name = "efficientnetv2s_cleaned.keras"

# === 🚀 Précision mixte pour accélérer (si supportée) ===
try:
    from tensorflow.keras.mixed_precision import set_global_policy
    set_global_policy("mixed_float16")
    print("✅ Précision mixte activée.")
except:
    print("ℹ️ Précision mixte non activée.")

# === 🧪 Générateur robuste avec filtre anti-corruption ===
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class SafeDirectoryIterator(Sequence):
    def __init__(self, datagen, directory, **kwargs):
        self.datagen = datagen
        self.directory = directory
        self.kwargs = kwargs
        print("🔍 Filtrage des images corrompues...")
        temp_gen = datagen.flow_from_directory(directory, shuffle=False, **kwargs)
        valid_files = []
        for fname in temp_gen.filenames:
            path = os.path.join(directory, fname)
            try:
                with Image.open(path) as img:
                    img.verify()
                valid_files.append(fname)
            except (UnidentifiedImageError, IOError):
                print(f"❌ Ignorée : {path}")
        self.generator = datagen.flow_from_directory(
            directory,
            **kwargs
        )
        self.generator.filenames = valid_files
        self.generator.samples = len(valid_files)
        self.generator._filepaths = [os.path.join(directory, fname) for fname in valid_files]
        self.generator._set_index_array()

    def __len__(self):
        return len(self.generator)

    def __getitem__(self, idx):
        return self.generator[idx]

# === 📦 Data Augmentation ===
train_datagen = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=25,
    zoom_range=0.25,
    horizontal_flip=True,
    width_shift_range=0.1,
    height_shift_range=0.1
)

val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

train_data = SafeDirectoryIterator(train_datagen, train_dir,
    target_size=img_size, batch_size=batch_size,
    class_mode="categorical", shuffle=True
)

val_data = SafeDirectoryIterator(val_datagen, val_dir,
    target_size=img_size, batch_size=batch_size,
    class_mode="categorical", shuffle=False
)

# === 🧠 EfficientNetV2S ===
base_model = EfficientNetV2S(
    include_top=False,
    weights="imagenet",
    input_shape=img_size + (3,)
)
base_model.trainable = False

x = GlobalAveragePooling2D()(base_model.output)
x = Dropout(0.4)(x)
x = Dense(512, activation="relu")(x)
x = Dropout(0.3)(x)
output = Dense(train_data.generator.num_classes, activation="softmax", dtype="float32")(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

# === 📟 Callbacks ===
log_dir = os.path.join("logs", datetime.now().strftime("%Y%m%d-%H%M%S"))
os.makedirs("checkpoints", exist_ok=True)

callbacks = [
    EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True),
    ModelCheckpoint(os.path.join("checkpoints", model_name), save_best_only=True),
    TensorBoard(log_dir=log_dir),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2)
]

# === 🏋️‍♂️ Entraînement ===
model.fit(
    train_data,
    validation_data=val_data,
    epochs=epochs,
    callbacks=callbacks
)

# === 🔓 Fine-tuning (optionnel)
print("🔓 Dégel du modèle pour fine-tuning...")
base_model.trainable = True
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)

model.fit(
    train_data,
    validation_data=val_data,
    epochs=10,
    callbacks=callbacks
)

# === ✅ Sauvegarde finale ===
model.save(model_name)
print("✅ Modèle entraîné et sauvegardé :", model_name)
