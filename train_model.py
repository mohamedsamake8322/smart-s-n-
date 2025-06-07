import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import logging
import optuna
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # type: ignore
import joblib
import xgboost as xgb
from sklearn.linear_model import LinearRegression  # 📌 Ajout pour régression climatique

# 📂 Vérification des chemins du dataset CNN
CNN_TRAIN_DIR = r"C:\Mah fah\plant_disease_dataset\train"
CNN_VAL_DIR = r"C:\Mah fah\plant_disease_dataset\val"
MODEL_PATH = "C:/Mah fah/model/plant_disease_model.h5"  # 📌 Uniformisation du format `.h5`

if not os.path.exists(CNN_TRAIN_DIR) or not os.path.exists(CNN_VAL_DIR):
    raise FileNotFoundError("🛑 Dataset folder not found. Check paths!")

# 📌 Prétraitement des images avec Data Augmentation
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_data = datagen.flow_from_directory(CNN_TRAIN_DIR, target_size=(224, 224), batch_size=32, class_mode="categorical")
val_data = datagen.flow_from_directory(CNN_VAL_DIR, target_size=(224, 224), batch_size=32, class_mode="categorical")

# 🔹 Définition du modèle CNN
base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights="imagenet")
base_model.trainable = False

cnn_model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(train_data.num_classes, activation="softmax")
])

cnn_model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
model = cnn_model  # ✅ Rend `model` accessible à l'importation
# ✅ Entraînement du modèle uniquement si `train_model.py` est exécuté directement
if __name__ == "__main__":
    print("🚀 `train_model.py` est exécuté seul. Entraînement en cours...")
    cnn_model.fit(train_data, validation_data=val_data, epochs=30)

    # ✅ Création du dossier `model`
    os.makedirs("model", exist_ok=True)

    # 📌 Sauvegarde du modèle CNN
    cnn_model.save(MODEL_PATH)
    print(f"✅ Modèle CNN entraîné et sauvegardé à {MODEL_PATH} !")

    # 📥 Chargement du modèle pour vérification
    try:
        model = tf.keras.models.load_model(MODEL_PATH)  # ✅ Chargement vérifié
        print("✅ Disease model loaded successfully!")
    except Exception as e:
        print(f"🚨 Erreur lors du chargement du modèle : {e}")

    # 📥 Simulation de données pour prédiction climatique
    data = {
        'humidity': np.random.uniform(30, 90, 100),
        'pH': np.random.uniform(4.5, 8.5, 100),
        'rainfall': np.random.uniform(20, 300, 100),
        'temperature': np.random.normal(loc=25, scale=5, size=100)
    }

    df = pd.DataFrame(data)

    # 🔹 Modèle de régression climatique
    X_climate = df[['humidity', 'pH', 'rainfall']]
    y_climate = df['temperature']

    climate_model = LinearRegression()
    climate_model.fit(X_climate, y_climate)

    # 📌 Sauvegarde du modèle climatique
    joblib.dump(climate_model, 'model/climate_prediction.pkl')
    print("✅ Modèle de prédiction climatique sauvegardé avec succès !")
# 📥 Encodage des variables catégoriques pour la fertilisation
fertilization_data = pd.read_csv(r"C:\Mah fah\fertilization_data.csv")  # ✅ Chargement correct
categorical_cols = ["soil_type", "crop_type"]  # ✅ Définition des colonnes catégoriques
label_encoders = {}  # ✅ Initialisation du dictionnaire pour stocker les encodeurs
for col in categorical_cols:
    le = LabelEncoder()
    fertilization_data[col] = le.fit_transform(fertilization_data[col])
    label_encoders[col] = le  # ✅ Sauvegarde de l'encodeur

# 📌 Séparation des données pour le modèle de fertilisation
X = fertilization_data.drop(columns=["fertilizer_amount"])
y = fertilization_data["fertilizer_amount"]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 Définition et entraînement du modèle XGBoost
fertilization_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.05, max_depth=6)
fertilization_model.fit(X_train, y_train)

y_pred = fertilization_model.predict(X_val)
mse = mean_squared_error(y_val, y_pred)
logging.info(f"📊 Erreur quadratique moyenne (MSE) : {mse}")

# ✅ Sauvegarde du modèle de fertilisation
model_path_fertilization = "model/fertilization_model.pkl"
os.makedirs(os.path.dirname(model_path_fertilization), exist_ok=True)
joblib.dump(fertilization_model, model_path_fertilization)
logging.info("✅ Modèle de fertilisation entraîné et sauvegardé !")

# ✅ Configuration CPU pour PyTorch
device = torch.device("cpu")

# 📥 Chargement et prétraitement des données
def load_data(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"🛑 Erreur : Fichier {csv_path} introuvable.")

    df = pd.read_csv(csv_path)
    logging.info(f"🔎 Colonnes disponibles : {df.columns.tolist()}")

    if "yield" not in df.columns:
        raise KeyError("🛑 Erreur : La colonne 'yield' est absente.")

    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
    scaler = StandardScaler()
    df[df.columns] = scaler.fit_transform(df[df.columns])

    return train_test_split(df.drop(columns=["yield"]), df["yield"], test_size=0.2, random_state=42)

# 🔥 Définition du modèle PyTorch
class PyTorchModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2):
        super(PyTorchModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

# 🚀 Optimisation du modèle LSTM avec Optuna
def optimize_lstm(trial, X_train, y_train):
    hidden_size = trial.suggest_int("hidden_size", 32, 128)
    num_layers = trial.suggest_int("num_layers", 1, 4)
    learning_rate = trial.suggest_loguniform("learning_rate", 0.001, 0.01)

    model = PyTorchModel(X_train.shape[1], hidden_size=hidden_size, num_layers=num_layers)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()

    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32).unsqueeze(1)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32)

    for _ in range(5):  # Réduction du nombre d'epochs pour optimisation
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs.squeeze(), y_train_tensor)
        loss.backward()
        optimizer.step()

    return mean_squared_error(y_train, outputs.detach().numpy().squeeze())

# 🚀 Entraînement du modèle de prédiction de rendement
def train_yield_model():
    logging.info("🚀 Entraînement du modèle LSTM pour prédiction de rendement...")
    
    X_train, X_test, y_train, y_test = load_data("data.csv")

    # 🔍 Optimisation avec Optuna
    study = optuna.create_study(direction="minimize")
    study.optimize(lambda trial: optimize_lstm(trial, X_train, y_train), n_trials=15)
    best_params = study.best_params
    logging.info(f"🏆 Meilleurs paramètres trouvés : {best_params}")

    # 🔧 Entraînement final du LSTM
    model = PyTorchModel(X_train.shape[1], hidden_size=best_params["hidden_size"], num_layers=best_params["num_layers"])
    optimizer = torch.optim.Adam(model.parameters(), lr=best_params["learning_rate"])
    criterion = nn.MSELoss()

    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32).unsqueeze(1)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32)

    for _ in range(10):
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs.squeeze(), y_train_tensor)
        loss.backward()
        optimizer.step()

    # 💾 Sauvegarde du modèle
    MODEL_PATH = "model/crop_model.pth"
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    torch.save(model.state_dict(), MODEL_PATH)
    logging.info(f"✅ Modèle LSTM sauvegardé à {MODEL_PATH}")

if __name__ == "__main__":
    logging.info("🚀 Exécution du script `train_model.py`...")
    train_yield_model()
if __name__ == "__main__":
    logging.info("🚀 Entraînement du modèle en cours...")
    cnn_model.fit(train_data, validation_data=val_data, epochs=30)
    cnn_model.save(r"C:\Mah fah\model\plant_disease_model.h5")  # ✅ Sauvegarde du modèle mis à jour
    logging.info("✅ Modèle entraîné et sauvegardé avec succès !")
