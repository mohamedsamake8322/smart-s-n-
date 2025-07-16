import pandas as pd
import os

# Dossier contenant les fichiers météo
folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned"

# Inspection de chaque fichier
for file in os.listdir(folder_meteo):
    if not file.endswith(".csv"):
        continue

    path = os.path.join(folder_meteo, file)
    try:
        df = pd.read_csv(path)
        print(f"\n📁 Fichier : {file}")
        print(f"🔢 Lignes : {len(df)}")
        print(f"🧱 Colonnes : {df.columns.tolist()}")
        print("👁️ Aperçu :")
        print(df.head(2))  # affiche 2 premières lignes pour plus de lisibilité

    except Exception as e:
        print(f"\n❌ Erreur lors de la lecture de {file} : {e}")
