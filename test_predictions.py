import pandas as pd
import joblib
import json
import os
import datetime

# ✅ Chemin du modèle optimisé
MODEL_PATH = "model/model_xgb.pkl"

# Vérifier si le modèle existe
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("❌ Model file not found. Please check its location.")

print("🔄 Loading the trained model...")
model = joblib.load(MODEL_PATH)

# ✅ Charger les données de test
TEST_DATA_PATH = "test_data.csv"

if not os.path.exists(TEST_DATA_PATH):
    raise FileNotFoundError("❌ Test data file not found. Please check its location.")

test_data = pd.read_csv(TEST_DATA_PATH)

# ✅ Vérification des colonnes attendues
expected_features = model.feature_names_in_
missing_cols = [col for col in expected_features if col not in test_data.columns]

if missing_cols:
    raise ValueError(f"❗ Test data is missing columns: {missing_cols}")

# ✅ Prédire le rendement
print("🚀 Predicting yield...")
test_data["PredictedYield"] = model.predict(test_data)

# ✅ Sauvegarder les résultats avec logs
RESULTS_PATH = "predictions_results.csv"
test_data.to_csv(RESULTS_PATH, index=False)
print(f"✅ Predictions completed and saved in {RESULTS_PATH}")

# ✅ Enregistrement des logs
log_entry = {
    "timestamp": str(datetime.datetime.now()),
    "model_used": MODEL_PATH,
    "num_predictions": len(test_data),
}

with open("predictions_log.json", "a") as f:
    json.dump(log_entry, f)
    f.write("\n")

print("📜 Prediction log updated.")

