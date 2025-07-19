#🚀 MODULE 2 — Modèle XGBoost pour prédiction de rendement
# train_yield_predictor.py
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

df = pd.read_csv("dataset_agricole_prepared.csv")
df.columns = [col.strip().lower() for col in df.columns]

features = [
    "production", "pesticides_use", "ws10m_range",
    "gwettop", "gwetroot", "gwetprof", "wd10m"
]
features = [f for f in features if f in df.columns]

df = df.dropna(subset=features + ["yield_target"])
X = df[features]
y = df["yield_target"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=8, subsample=0.8, colsample_bytree=0.8, tree_method="hist", verbosity=1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
rmse = mean_squared_error(y_test, y_pred, squared=False)
r2 = r2_score(y_test, y_pred)

print(f"✅ RMSE : {rmse:.2f}")
print(f"✅ R²   : {r2:.2f}")

plt.figure(figsize=(10, 6))
plt.barh(features, model.feature_importances_)
plt.title("🎯 Importance des variables dans la prédiction de rendement")
plt.xlabel("Importance")
plt.tight_layout()
plt.show()
