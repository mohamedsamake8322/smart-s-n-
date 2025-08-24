import pandas as pd
import xgboost as xgb
import json

# 📦 Charger le modèle
MODEL_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_model.bin"
COLS_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_columns.json"
LABELS_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_labels.json"

booster = xgb.Booster()
booster.load_model(MODEL_PATH)

with open(COLS_PATH, "r", encoding="utf-8") as f:
    model_cols = json.load(f)

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    label_map = json.load(f)

# 🔮 Fonction de prédiction
def predict_fertilizer(user_inputs: dict) -> str:
    X_input_dict = {c: 0 for c in model_cols}
    for k, v in user_inputs.items():
        col_key = k.lower().strip().replace(" ", "_")
        for col in model_cols:
            if col.startswith(col_key + "_") and str(v).lower() in col.lower():
                X_input_dict[col] = 1
        if col_key in model_cols:
            X_input_dict[col_key] = v
    X_input = pd.DataFrame([X_input_dict], columns=model_cols)
    dmat = xgb.DMatrix(X_input.values, feature_names=model_cols)
    pred = booster.predict(dmat)
    pred_label = int(pred[0].round())
    return label_map[pred_label]
