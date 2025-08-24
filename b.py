import pandas as pd
import xgboost as xgb
import json
import os

# 📁 Charger les données
df = pd.read_csv(r"C:\Downloads\Crop-Fertilizer-Analysis\Crop_recommendation.csv")

# 🧪 Features à utiliser
features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
target = 'label'

# 🔢 Encodage du label
df[target] = df[target].astype('category').cat.codes

# 🧠 Entraînement XGBoost
X = df[features]
y = df[target]
dtrain = xgb.DMatrix(X, label=y, feature_names=features)

params = {
    'objective': 'reg:squarederror',
    'max_depth': 6,
    'eta': 0.1,
    'nthread': 4,
    'seed': 42
}
booster = xgb.train(params, dtrain, num_boost_round=100)

# 💾 Sauvegarde du modèle
os.makedirs("models", exist_ok=True)
booster.save_model("models/xgb_mali_model.bin")

# 💾 Sauvegarde des colonnes
with open("models/model_columns.json", "w", encoding="utf-8") as f:
    json.dump(features, f, indent=2)

print("✅ Modèle et colonnes sauvegardés.")
