# === 🔄 Nettoyage mémoire Colab (bonus)
import gc, psutil
import tensorflow as tf
import os, time
from datetime import datetime
from tensorflow.keras import layers
from tensorflow.keras.applications import EfficientNetV2L
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau, Callback

gc.collect()
tf.keras.backend.clear_session()
print(f"💡 RAM utilisée : {psutil.virtual_memory().percent}%")

# === 📁 Dossiers
base_path = '/content/drive/My Drive/My Drive/plantdataset'
train_dir = os.path.join(base_path, 'train')
val_dir   = os.path.join(base_path, 'val')

# === ⏱️ Callback pour mesurer le temps par epoch
class EpochTimer(Callback):
    def on_train_begin(self, logs=None):
        self.epoch_times = []

    def on_epoch_begin(self, epoch, logs=None):
        self.start_time = time.time()

    def on_epoch_end(self, epoch, logs=None):
        duration = time.time() - self.start_time
        self.epoch_times.append(duration)
        print(f"⏱️ Durée epoch {epoch + 1}: {duration:.2f} secondes")

# === ⚙️ Paramètres
batch_size = 32
img_size = (480, 480)
epochs = 30
model_name = 'efficientnetv2l_agri.keras'
model_save_path = os.path.join(base_path, model_name)

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

# === ⚙️ Pré-traitement sans cache (évite crash RAM)
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE).ignore_errors()
val_ds   = val_ds.prefetch(buffer_size=AUTOTUNE).ignore_errors()

# === 🧠 Modèle EfficientNetV2-L
base_model = EfficientNetV2L(
    include_top=False,
    weights='imagenet',
    input_shape=img_size + (3,)
)
base_model.trainable = False

inputs  = tf.keras.Input(shape=img_size + (3,))
x       = tf.keras.applications.efficientnet_v2.preprocess_input(inputs)
x       = base_model(x, training=False)
x       = layers.GlobalAveragePooling2D()(x)
x       = layers.Dropout(0.4)(x)
x       = layers.Dense(512, activation='relu')(x)
x       = layers.Dropout(0.3)(x)
outputs = layers.Dense(num_classes, activation='softmax')(x)

model = tf.keras.Model(inputs, outputs)

# === 🚀 Compilation
model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# === 📟 Callbacks
checkpoint_dir = os.path.join(base_path, 'checkpoints')
os.makedirs(checkpoint_dir, exist_ok=True)

callbacks = [
    EpochTimer(),
    EarlyStopping(patience=5, monitor='val_accuracy', restore_best_weights=True),
    ModelCheckpoint(filepath=os.path.join(checkpoint_dir, 'checkpoint.keras'), save_best_only=True),
    ReduceLROnPlateau(factor=0.5, patience=2, monitor='val_loss'),
    TensorBoard(log_dir=os.path.join(checkpoint_dir, 'logs', datetime.now().strftime("%Y%m%d-%H%M%S")))
]

# === 🏋️ Entraînement initial
try:
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )
except Exception as e:
    print(f"⚠️ Entraînement interrompu : {e}")

# === 🔓 Fine-tuning partiel
base_model.trainable = True
for layer in base_model.layers[:-100]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

try:
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=10,
        callbacks=callbacks
    )
except Exception as e:
    print(f"⚠️ Fine-tuning interrompu. Erreur : {e}")

# === 💾 Sauvegarde finale
model.save(model_save_path)
print("✅ Modèle entraîné et sauvegardé dans :", model_save_path)
