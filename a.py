import dask.dataframe as dd
import pandas as pd
import os
import shutil

# Dossier contenant les fichiers
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Liste des fichiers CSV avec chemin complet
files = [
    os.path.join(base_path, "Soil_AllLayers_AllAfrica-002.csv"),
    os.path.join(base_path, "GEDI_Mangrove_CSV.csv"),
    os.path.join(base_path, "CHIRPS_DAILY_PENTAD.csv"),
    os.path.join(base_path, "SMAP_SoilMoisture.csv"),
    os.path.join(base_path, "WorldClim BIO Variables V1.csv"),
    os.path.join(base_path, "WAPOR_All_Variables_Merged.csv"),
    os.path.join(base_path, "NDMI_Afrique_fusionné.csv"),
    os.path.join(base_path, "WorldClim_Monthly_Fusion.csv"),
]

merge_keys = ["ADM0_NAME", "ADM1_NAME", "Year"]

final_file = os.path.join(base_path, "merged_final.parquet")
temp_file = os.path.join(base_path, "temp_merge.parquet")

def load_and_prepare(file_path):
    print(f"📥 Traitement : {os.path.basename(file_path)}")
    df = dd.read_csv(file_path, dtype=str, assume_missing=True, blocksize="64MB")
    for col in merge_keys:
        if col not in df.columns:
            df[col] = None
    # Forcer Year en string
    df["Year"] = df["Year"].astype(str)
    return df

# Initialisation avec le premier fichier
df_final = load_and_prepare(files[0])
df_final.to_parquet(final_file, overwrite=True)

# Fusion incrémentale
for file in files[1:]:
    df_temp = load_and_prepare(file)
    df_final = dd.read_parquet(final_file)

    # Forcer Year en string dans les deux DataFrames
    df_final["Year"] = df_final["Year"].astype(str)
    df_temp["Year"] = df_temp["Year"].astype(str)

    df_merged = dd.merge(df_final, df_temp, on=merge_keys, how="outer")
    df_merged.to_parquet(temp_file, overwrite=True)

    if os.path.exists(final_file):
        shutil.rmtree(final_file)
    os.rename(temp_file, final_file)
    print(f"✅ Fusion terminée pour {os.path.basename(file)}")
