import pandas as pd
import os

# 📁 Dossier principal
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📄 Liste des fichiers à analyser
files = [
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
    "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv",
    "GEDI_Mangrove_CSV.csv",
    "X_land_water_cleanedRessources en terres et en eau.csv"
]

# 🔍 Boucle sur chaque fichier
for file in files:
    print(f"\n{'='*60}")
    print(f"📂 Fichier : {file}")
    print(f"{'='*60}")

    file_path = os.path.join(base_path, file)

    try:
        df = pd.read_csv(file_path)

        # Dimensions
        print(f"➡ Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes\n")

        # Colonnes
        print("📝 Colonnes :", list(df.columns), "\n")

        # Types
        print("📊 Types de données :")
        print(df.dtypes, "\n")

        # Aperçu
        print("🔎 Aperçu des 5 premières lignes :")
        print(df.head(), "\n")

    except Exception as e:
        print(f"❌ Erreur de lecture : {e}")
