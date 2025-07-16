import pandas as pd
import os

# 📥 Charger les données sol
df_sol = pd.read_csv(r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv")
pays_sol = sorted(df_sol['Country'].dropna().unique())

# 📁 Extraire les noms de pays à partir des fichiers météo
folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned"
pays_meteo = [f.replace("weather_", "").replace(".csv", "") for f in os.listdir(folder_meteo) if f.endswith(".csv")]

# 🔄 Générer la table de correspondance (basée sur similarité textuelle)
alias_table = {}

for meteo in pays_meteo:
    matches = [sol for sol in pays_sol if meteo.lower() in sol.lower()]
    if matches:
        alias_table[meteo] = matches
    else:
        # Aucun match direct → tenter suggestions manuelles plus tard
        alias_table[meteo] = []

# 📋 Afficher les correspondances
print("📌 Table de correspondance météo → sol :\n")
for k, v in alias_table.items():
    if v:
        print(f"✅ {k} → {v}")
    else:
        print(f"⚠️ {k} → Aucun nom sol détecté")
