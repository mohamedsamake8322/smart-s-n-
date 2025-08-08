import os
import pandas as pd
import dask.dataframe as dd

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📄 Fichier FAOSTAT
faostat_file = os.path.join(
    data_dir, "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv"
)

print("📥 Scan rapide du fichier FAOSTAT pour détecter les colonnes mixtes...")

# Lecture échantillon
sample = pd.read_csv(faostat_file, nrows=500)

# Nettoyage des noms de colonnes (pour éviter les soucis d'espaces)
sample.columns = sample.columns.str.strip()

# Détection des colonnes mixtes
problematic_cols = []
for col in sample.columns:
    if sample[col].dtype == object:
        # Si la colonne contient au moins un élément non numérique
        try:
            pd.to_numeric(sample[col].dropna(), errors="raise")
        except Exception:
            problematic_cols.append(col)

print(f"⚠️ Colonnes mixtes détectées ({len(problematic_cols)}) :", problematic_cols)

# 📥 Lecture complète avec Dask en forçant les colonnes détectées en string
dtype_map = {col: "object" for col in problematic_cols}

faostat_crop_df = dd.read_csv(
    faostat_file,
    assume_missing=True,
    dtype=dtype_map
)

print("✅ Chargement FAOSTAT sécurisé avec Dask.")
print(faostat_crop_df.head(3))
