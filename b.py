import pandas as pd
import xgboost as xgb # type: ignore
import json
import os

# 📥 Charger les données
DATA_PATH = r"C:\Downloads\Crop-Fertilizer-Analysis\Fertilizer Prediction.csv"
df = pd.read_csv(DATA_PATH)

# 🧼 Nettoyage
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
df.rename(columns={"temparature": "temperature", "humidity_": "humidity"}, inplace=True)

# 🎯 Cible
target = "fertilizer_name"

# 🔢 Encodage des variables catégorielles
df_encoded = pd.get_dummies(df.drop(columns=[target]), drop_first=True)
X = df_encoded
y = df[target]

# 🔁 Encodage de la cible
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 🧠 Entraînement du modèle
model = xgb.XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
model.fit(X, y_encoded)

# 💾 Sauvegarde du modèle et des colonnes
MODEL_DIR = r"C:\Downloads\models"
os.makedirs(MODEL_DIR, exist_ok=True)
model.save_model(os.path.join(MODEL_DIR, "fertilizer_model.bin"))

with open(os.path.join(MODEL_DIR, "fertilizer_columns.json"), "w", encoding="utf-8") as f:
    json.dump(list(X.columns), f)

with open(os.path.join(MODEL_DIR, "fertilizer_labels.json"), "w", encoding="utf-8") as f:
    json.dump(list(le.classes_), f)
