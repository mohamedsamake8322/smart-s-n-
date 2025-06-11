import os
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense # type: ignore
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Assurer l'existence du dossier 'models'
os.makedirs("models", exist_ok=True)

### 🚜 **1. Entraînement du modèle de prédiction de rendement (`yield_model.pkl`)**
def train_yield_model():
    df = pd.read_csv("data/yield_data.csv")
    X, y = df.drop(columns=["yield"]), df["yield"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = xgb.XGBRegressor(n_estimators=300, max_depth=8, learning_rate=0.05,
                             colsample_bytree=0.8, subsample=0.8, gamma=3,
                             min_child_weight=5, random_state=42)
    model.fit(X_train_scaled, y_train)

    joblib.dump(model, "models/yield_model.pkl")
    joblib.dump(scaler, "models/yield_model_scaler.pkl")
    print("✅ yield_model.pkl entraîné et sauvegardé !")

### 🌦 **2. Entraînement du modèle de prévision météo (`weather_model.pkl`)**
def train_weather_model():
    df = pd.read_csv("data/weather_data.csv")
    X, y = df.drop(columns=["temperature"]), df["temperature"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=500, max_depth=15, min_samples_split=4,
                                  min_samples_leaf=2, bootstrap=True, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "models/weather_model.pkl")
    print("✅ weather_model.pkl entraîné et sauvegardé !")

### 🦠 **3. Entraînement du modèle de détection de maladies (`disease_model.h5`)**
def train_disease_model():
    train_dir = "C:/Mah fah/plant_disease_dataset/train"
    val_dir = "C:/Mah fah/plant_disease_dataset/val"

    datagen = ImageDataGenerator(rescale=1./255, rotation_range=20, zoom_range=0.2, horizontal_flip=True)
    train_data = datagen.flow_from_directory(train_dir, target_size=(224, 224), batch_size=32, class_mode="categorical")
    val_data = datagen.flow_from_directory(val_dir, target_size=(224, 224), batch_size=32, class_mode="categorical")

    model = Sequential([
        Conv2D(32, (3,3), activation="relu", input_shape=(224,224,3)),
        MaxPooling2D(2,2),
        Conv2D(64, (3,3), activation="relu"),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(128, activation="relu"),
        Dense(len(train_data.class_indices), activation="softmax")  # Nombre de classes dynamique
    ])

    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    
    model.fit(train_data, epochs=15, validation_data=val_data)
    model.save("models/disease_model.h5")
    print("✅ disease_model.h5 entraîné et sauvegardé !")

### 🌱 **4. Entraînement du modèle de recommandation d'engrais (`fertilizer_model.pkl`)**
def train_fertilizer_model():
    df = pd.read_csv("data/fertilizer_data.csv")
    X, y = df.drop(columns=["fertilizer_type"]), df["fertilizer_type"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(n_estimators=300, max_depth=8, learning_rate=0.05,
                              colsample_bytree=0.8, subsample=0.8, gamma=3,
                              min_child_weight=5, random_state=42)
    model.fit(X_train, y_train)

    joblib.dump(model, "models/fertilizer_model.pkl")
    print("✅ fertilizer_model.pkl entraîné et sauvegardé !")

### 🚀 **Exécuter tous les entraînements**
if __name__ == "__main__":
    train_yield_model()
    train_weather_model()
    train_disease_model()
    train_fertilizer_model()
    print("🎯 Tous les modèles ont été entraînés et sauvegardés !")
