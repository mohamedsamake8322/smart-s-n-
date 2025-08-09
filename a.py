import dask.dataframe as dd
import pandas as pd
import os

# Liste de tes fichiers CSV
files = [
    "Soil_AllLayers_AllAfrica-002.csv",
    "GEDI_Mangrove_CSV.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
    "WorldClim BIO Variables V1.csv",
    "WAPOR_All_Variables_Merged.csv",
    "NDMI_Afrique_fusionné.csv",
    "WorldClim_Monthly_Fusion.csv"
]

# Colonnes sur lesquelles on fusionne
merge_keys = ["ADM0_NAME", "ADM1_NAME", "Year"]

# Fichier final en Parquet
final_file = "merged_final.parquet"

def load_and_prepare(file_path):
    """Charge un CSV avec Dask, harmonise les types."""
    print(f"📥 Traitement : {file_path}")
    df = dd.read_csv(file_path, dtype=str, assume_missing=True, blocksize="64MB")
    # On garde toutes les colonnes en string pour éviter les conflits de merge
    for col in merge_keys:
        if col not in df.columns:
            df[col] = None
    return df

# Initialisation avec le premier fichier
df_final = load_and_prepare(files[0])
df_final.to_parquet(final_file, overwrite=True)

# Fusion incrémentale
for file in files[1:]:
    df_temp = load_and_prepare(file)

    # Charger uniquement les deux fichiers nécessaires
    df_final = dd.read_parquet(final_file)
    df_merged = dd.merge(df_final, df_temp, on=merge_keys, how="outer")

    # Écriture sur disque
    df_merged.to_parquet(final_file, overwrite=True)
    print(f"✅ Fusion terminée pour {file}")

print("🎯 Fusion complète terminée. Résultat :", final_file)

# Export en CSV si vraiment nécessaire
# dd.read_parquet(final_file).to_csv("merged_final.csv", single_file=True)
