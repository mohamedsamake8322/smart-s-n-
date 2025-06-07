import shap
import pandas as pd
import matplotlib.pyplot as plt
import joblib

# Charger les données d'entraînement
data = pd.read_csv("data.csv")
X = data.drop(columns=["Yield"])
y = data["Yield"]

# Charger ton modèle
model = joblib.load("trained_model.pkl")  # Assure-toi que ce fichier existe

# Initialiser SHAP explainer
explainer = shap.Explainer(model, X)
shap_values = explainer(X)

# Résumé global
shap.summary_plot(shap_values, X)

# Sauvegarde du plot
plt.savefig("shap_summary.png")

# Explication pour une prédiction spécifique (ex : premier élément)
shap.plots.waterfall(shap_values[0], max_display=10)
