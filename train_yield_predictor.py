# 📦 Import des bibliothèques
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# ================================
# 🧪 ÉTAPE 1 : Chargement du Dataset
# ================================

# 📥 Charger le dataset préparé
df = pd.read_csv("dataset_agricole_prepared.csv")

# 🧼 Nettoyage des colonnes principales
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["yield_target"] = pd.to_numeric(df["yield_target"], errors="coerce")

# 🎯 Sélection des variables explicatives
features = [
    "Production", "pesticides_use",
    "PRECTOTCORR", "WS10M_RANGE", "T2M_MAX", "T2M_MIN", "QV2M", "RH2M",
    "ph", "carbon_organic", "nitrogen_total"
]

# 🔍 Extraction des variables X et y
X = df[features].dropna()
y = df.loc[X.index, "yield_target"]

# 🎓 Séparation train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ================================
# 🤖 ÉTAPE 2 : Entraînement du Modèle
# ================================

model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",
    verbosity=1
)

model.fit(X_train, y_train)

# 📈 Évaluation du modèle
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)

print("\n📊 Évaluation du modèle :")
print(f"✅ RMSE : {rmse:.2f}")
print(f"✅ R²    : {r2:.2f}")

# ================================
# 🔍 ÉTAPE 3 : Visualisation des Importances
# ================================

importances = model.feature_importances_
plt.figure(figsize=(10, 6))
plt.barh(features, importances)
plt.title("🎯 Importance des variables dans la prédiction de rendement")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()
