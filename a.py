import dask.dataframe as dd
import os

# 📂 Chemin du dossier
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📜 Liste des fichiers
fichiers = [
    "Soil_AllLayers_AllAfrica-002.csv",
    "GEDI_Mangrove_CSV.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
    "WorldClim BIO Variables V1.csv",
    "WAPOR_All_Variables_Merged.csv",
    "NDMI_Afrique_fusionné.csv",
    "WorldClim_Monthly_Fusion.csv"
]

# Colonnes à supprimer si présentes
colonnes_a_supprimer = ["system:index", ".geo", "collection_id", "extraction_date", "band_name", "layer", "level"]

def charger_et_preparer(chemin):
    df = dd.read_csv(chemin, assume_missing=True)

    # Suppression colonnes inutiles
    df = df.drop(columns=[c for c in colonnes_a_supprimer if c in df.columns], errors="ignore")

    # Harmonisation colonne Year
    col_year = None
    for col in df.columns:
        if "YEAR" in col.upper():
            col_year = col
            break
    if col_year:
        df = df.rename(columns={col_year: "Year"})
    else:
        df["Year"] = None  # colonne vide si absente

    # Harmonisation noms colonnes ADM0/ADM1
    if "ADM0_NAME" not in df.columns:
        df["ADM0_NAME"] = None
    if "ADM1_NAME" not in df.columns:
        df["ADM1_NAME"] = None

    return df

# 📌 Fusion progressive
df_final = None

for fichier in fichiers:
    chemin_fichier = os.path.join(base_path, fichier)
    print(f"📥 Traitement : {fichier}")
    df_temp = charger_et_preparer(chemin_fichier)

    if df_final is None:
        df_final = df_temp
    else:
        df_final = df_final.merge(df_temp, on=["ADM0_NAME", "ADM1_NAME", "Year"], how="outer")

# 💾 Sauvegarde finale en Parquet (rapide et compact)
output_path = os.path.join(base_path, "fusion_agronomique_dask.parquet")
df_final.to_parquet(output_path, engine="pyarrow", compression="snappy")

print(f"✅ Fusion terminée. Fichier sauvegardé : {output_path}")
