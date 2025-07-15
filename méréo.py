import pandas as pd
from glob import glob
import os

# Dossier météo
weather_folder = r"C:\plateforme-agricole-complete-v2\weather_by_country"
weather_files = glob(os.path.join(weather_folder, "*.csv"))

# ⚡ Limiter à 3 fichiers pour test rapide
for file in weather_files[:3]:
    try:
        print(f"\n📁 Fichier : {os.path.basename(file)}")

        df = pd.read_csv(file, low_memory=False)
        print(f"➤ Dimensions : {df.shape}")
        print(f"➤ Colonnes : {list(df.columns[:15])} ...")
        print(f"➤ Aperçu des premières lignes :\n{df.head(2)}")

        # Vérifier si la colonne 'DATE' est convertible
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], errors="coerce")
            print("✅ Conversion des dates réussie")
            print(f"🔢 Dates min/max : {df['DATE'].min()} → {df['DATE'].max()}")
        else:
            print("⚠️ Colonne DATE absente")

    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
