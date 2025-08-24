import pandas as pd
import xgboost as xgb
import json

# 📦 Charger le modèle et les métadonnées
MODEL_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_model.bin"
COLS_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_columns.json"
LABELS_PATH = r"C:\plateforme-agricole-complete-v2\models\fertilizer_labels.json"

booster = xgb.Booster()
booster.load_model(MODEL_PATH)

with open(COLS_PATH, "r", encoding="utf-8") as f:
    model_cols = json.load(f)

with open(LABELS_PATH, "r", encoding="utf-8") as f:
    label_map = json.load(f)


# 🔮 Fonction de prédiction robuste
def predict_fertilizer(user_inputs: dict) -> str:
    try:
        # Construire le dictionnaire d'inputs initialisé à 0
        X_input_dict = {c: 0 for c in model_cols}

        for k, v in user_inputs.items():
            col_key = k.lower().strip().replace(" ", "_")

            # One-hot encoding si la colonne correspond à une catégorie
            for col in model_cols:
                if col.startswith(col_key + "_") and str(v).lower() in col.lower():
                    X_input_dict[col] = 1

            # Valeur numérique directe si correspondance exacte
            if col_key in model_cols:
                X_input_dict[col_key] = v

        # Conversion en DataFrame pour XGBoost
        X_input = pd.DataFrame([X_input_dict], columns=model_cols)
        dmat = xgb.DMatrix(X_input.values, feature_names=model_cols)

        # Prédiction
        pred = booster.predict(dmat)
        pred_value = float(pred[0])          # conversion en scalaire
        pred_label = int(round(pred_value))  # arrondi + cast en int

        # Retourner le label mappé
        return label_map.get(pred_label, "Fertilizer inconnu")

    except Exception as e:
        return f"❌ Erreur lors de la prédiction : {str(e)}"
