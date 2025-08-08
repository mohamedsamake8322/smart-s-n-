import os
import pandas as pd
import dask.dataframe as dd

# 📁 Dossier et fichier
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"
faostat_file = os.path.join(
    data_dir, "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv"
)

print("📥 Scan rapide du fichier FAOSTAT...")

# Lecture échantillon
sample = pd.read_csv(faostat_file, nrows=2000)  # plus grand échantillon
sample.columns = sample.columns.str.strip()

# Détection auto des colonnes mixtes
problematic_cols = []
for col in sample.columns:
    if sample[col].dtype == object:
        try:
            pd.to_numeric(sample[col].dropna(), errors="raise")
        except Exception:
            problematic_cols.append(col)

# Colonnes connues à risque à ajouter si présentes
known_risky = ["Item Code (CPC)"]
for col in known_risky:
    if col in sample.columns and col not in problematic_cols:
        problematic_cols.append(col)

print(f"⚠️ Colonnes forcées en object : {problematic_cols}")

# Lecture Dask en forçant le type
dtype_map = {col: "object" for col in problematic_cols}

faostat_crop_df = dd.read_csv(
    faostat_file,
    assume_missing=True,
    dtype=dtype_map
)

print("✅ Chargement FAOSTAT sécurisé avec Dask.")
print(faostat_crop_df.head(3))
