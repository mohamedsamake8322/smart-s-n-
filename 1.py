import pandas as pd
import os
#Pour lire les dossiers
# Dossier contenant les fichiers
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Liste des fichiers à explorer
files_to_map = [
    "Soil_AllLayers_AllAfrica-002.csv",
    "WorldClim BIO Variables V1.csv",
    "WorldClim_Monthly_Fusion.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "merged_weather_africa.csv",
    "FAOSTAT_data_en_8-7-2025.csv",
    "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv",
    "X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv"
]

# Afficher les colonnes de chaque fichier
for file in files_to_map:
    path = os.path.join(data_dir, file)
    try:
        df = pd.read_csv(path, nrows=5)  # Lecture partielle pour éviter les gros fichiers
        print(f"\n📄 Fichier : {file}")
        print("Colonnes :", list(df.columns))
    except Exception as e:
        print(f"Erreur avec {file} : {e}")
