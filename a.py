import dask.dataframe as dd
import os

# 📂 Chemin du dossier contenant les fichiers
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📜 Liste des fichiers CSV à fusionner
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

# Colonnes inutiles à supprimer si présentes
colonnes_a_supprimer = ["system:index", ".geo", "collection_id", "extraction_date", "band_name", "layer", "level"]

# Fonction pour charger et préparer un fichier
def charger_et_preparer(chemin):
    df = dd.read_csv(chemin, assume_missing=True)  # assume_missing = meilleure compatibilité

    # Suppression colonnes inutiles
    df = df.drop(columns=[c for c in colonnes_a_supprimer if c in df.columns], errors="ignore")

    # Harmonisation du nom des colonnes de l'année
    for col in df.columns:
        if "YEAR" in col.upper():
            df = df.rename(columns={col: "Year"})

    # Harmonisation noms colonnes pays/région
    if "ADM0_NAME" not in df.columns:
        df["ADM0_NAME"] = None
    if "ADM1_NAME" not in df.columns:
        df["ADM1_NAME"] = None

    return df

# 📌 Chargement et fusion progressive
df_final = None

for fichier in fichiers:
    chemin_fichier = os.path.join(base_path, fichier)
    print(f"📥 Traitement : {fichier}")
    df_temp = charger_et_preparer(chemin_fichier)

    if df_final is None:
        df_final = df_temp
    else:
        # Fusion externe sur les clés
        df_final = df_final.merge(df_temp, on=["ADM0_NAME", "ADM1_NAME", "Year"], how="outer")

# 💾 Sauvegarde finale (Parquet recommandé)
output_path = os.path.join(base_path, "fusion_agronomique_dask.parquet")
df_final.to_parquet(output_path, engine="pyarrow", compression="snappy")

print(f"✅ Fusion terminée. Fichier sauvegardé : {output_path}")
