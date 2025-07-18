# 📦 Import des bibliothèques
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# ================================
# 🧪 ÉTAPE 1 : Préparation du Dataset
# ================================

# 📥 Charger le fichier fusionné
df = pd.read_csv("dataset_agronomique_final.csv")

# 🔄 Transformer les variables météo verticales en colonnes
df_pivot = df.pivot_table(
    index=["country", "year", "latitude_x", "longitude_x"],
    columns="variable",
    values="value"
).reset_index()

# 📌 Récupérer les colonnes de sol et intrants agricoles
df_sol = df.drop_duplicates(subset=["latitude_y", "longitude_y"])[[
    "latitude_y", "longitude_y", "ph", "carbon_organic", "nitrogen_total",
    "Value_engrais", "Value_pesticides"
]]

# 🔗 Fusion météo + sol
df_merged = pd.merge(
    df_pivot,
    df_sol,
    left_on=["latitude_x", "longitude_x"],
    right_on=["latitude_y", "longitude_y"],
    how="left"
)

# 📦 Charger et préparer la cible FAOSTAT (production)
column_names = [
    "domain_code", "domain", "country", "item_code", "item",
    "element_code", "element", "year_code", "year",
    "unit", "value", "flag"
]
df_fao = pd.read_csv("Production_Crops_Livestock_Afrique.csv")
df_fao = df_fao[df_fao["Element"] == "Production"]
df_fao = df_fao.rename(columns={
    "Area": "country",
    "Year": "year",
    "Item": "culture",
    "Value": "yield_target"
})
print(df_fao.columns.tolist())

# 🔗 Fusion finale
df_final = pd.merge(
    df_merged,
    df_fao[["country", "year", "culture", "yield_target"]],
    on=["country", "year"],
    how="left"
)

# 🧼 Nettoyage
df_final = df_final.dropna(subset=["yield_target"])

# ================================
# 🧠 ÉTAPE 2 : Entraînement du modèle
# ================================

# 🎯 Sélection des variables explicatives
features = [
    "ph", "carbon_organic", "nitrogen_total",
    "Value_engrais", "Value_pesticides",
    "PRECTOTCORR", "WS10M_RANGE", "T2M_MAX",
    "T2M_MIN", "QV2M", "RH2M"
]

# 🔍 Extraction des données
X = df_final[features]
y = df_final["yield_target"]

# 🎓 Séparation en train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ⚡️ Modèle XGBoost
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    tree_method="hist",  # Compatible avec TPU/GPU
    verbosity=1
)
model.fit(X_train, y_train)

# 📈 Évaluation
y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)

print("\n📊 Évaluation du modèle :")
print(f"✅ RMSE : {rmse:.2f}")
print(f"✅ R²    : {r2:.2f}")

# ================================
# 🔍 ÉTAPE 3 : Visualisation des importances
# ================================

importances = model.feature_importances_
plt.figure(figsize=(10, 6))
plt.barh(features, importances)
plt.title("🎯 Importance des variables dans la prédiction de rendement")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()
