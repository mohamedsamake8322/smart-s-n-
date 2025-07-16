import os
import pandas as pd

folder = r"C:\plateforme-agricole-complete-v2\weather_by_country"

for file in os.listdir(folder):
    if file.endswith(".csv"):
        path = os.path.join(folder, file)
        try:
            df = pd.read_csv(path)

            # ✅ Vérification des colonnes
            if not {'Longitude', 'Latitude'}.issubset(df.columns):
                print(f"❌ {file} : Colonnes 'Longitude' ou 'Latitude' manquantes")
                continue

            # ✅ Vérification des types
            long_ok = pd.to_numeric(df['Longitude'], errors='coerce')
            lat_ok = pd.to_numeric(df['Latitude'], errors='coerce')

            if long_ok.isna().any() or lat_ok.isna().any():
                print(f"⚠️ {file} : Coordonnées non numériques détectées")
                print(df[['Longitude', 'Latitude']].head())

            else:
                print(f"✅ {file} : Coordonnées OK")

        except Exception as e:
            print(f"🔥 Erreur dans {file} : {e}")
