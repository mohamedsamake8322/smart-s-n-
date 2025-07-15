import pandas as pd
import os
from glob import glob

weather_folder = r"C:\plateforme-agricole-complete-v2\weather_final"
output_folder = r"C:\plateforme-agricole-complete-v2\weather_reduit"
os.makedirs(output_folder, exist_ok=True)

# 🔎 Colonnes à conserver
variables_clés = ["Country", "Latitude", "Longitude", "DATE"]
patterns_utiles = ["PRECTOT", "WS2M", "PS", "IMERG"]

# 📦 Parcours et copie réduite
weather_files = glob(os.path.join(weather_folder, "*.csv"))

for file_path in weather_files:
    try:
        file_name = os.path.basename(file_path)
        df = pd.read_csv(file_path, low_memory=False)

        keep = [c for c in df.columns if any(p in c for p in patterns_utiles)] + variables_clés
        df_reduit = df[keep]

        output_path = os.path.join(output_folder, file_name)
        df_reduit.to_csv(output_path, index=False)
        print(f"✅ Fichier réduit : {file_name} ({df_reduit.shape[0]} lignes, {df_reduit.shape[1]} colonnes)")

    except Exception as e:
        print(f"⛔ Erreur réduction {file_name} : {e}")
