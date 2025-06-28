import tensorflow as tf
import os
from datetime import datetime
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetV2L
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau

# === 📁 Dossiers ===
base_path = '/content/drive/My Drive/My Drive/plantdataset'
train_dir = os.path.join(base_path, 'train')
val_dir = os.path.join(base_path, 'val')

# === ⚙️ Paramètres
batch_size = 32
img_size = (480, 480)
epochs = 30
model_name = '/content/drive/My Drive/My Drive/plantdataset/efficientnetv2l_agri.keras'


# === 📦 Chargement des datasets
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    seed=42,
    image_size=img_size,
    batch_size=batch_size,
    label_mode='categorical'
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    val_dir,
    seed=42,
    image_size=img_size,
    batch_size=batch_size,
    label_mode='categorical'
)

class_names = train_ds.class_names
num_classes = len(class_names)

# === ⚙️ Pré-traitement + optimisation mémoire
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE).cache()
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE).cache()

# === 🧠 Modèle EfficientNetV2-L
base_model = EfficientNetV2L(
    include_top=False,
    weights='imagenet',
    input_shape=img_size + (3,)
)
base_model.trainable = False

inputs = tf.keras.Input(shape=img_size + (3,))
x = tf.keras.applications.efficientnet_v2.preprocess_input(inputs)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(num_classes, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

# === 🚀 Compilation
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === 📟 Callbacks
log_dir = os.path.join("logs", datetime.now().strftime("%Y%m%d-%H%M%S"))
os.makedirs("checkpoints", exist_ok=True)

callbacks = [
    EarlyStopping(patience=5, monitor='val_accuracy', restore_best_weights=True),
    ModelCheckpoint(filepath=os.path.join("checkpoints", model_name), save_best_only=True),
    ReduceLROnPlateau(factor=0.5, patience=2, monitor='val_loss'),
    TensorBoard(log_dir=log_dir)
]

# === 🏋️ Entraînement
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    callbacks=callbacks
)

# === 🔓 Fine-tuning (dégel partiel)
base_model.trainable = True
for layer in base_model.layers[:-100]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10,
    callbacks=callbacks
)

# === 💾 Sauvegarde finale
model.save(model_name)
print("✅ Modèle entraîné et sauvegardé :", model_name)
