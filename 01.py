import pandas as pd

# 📥 Lecture rapide de quelques lignes pour analyser les types
sample = pd.read_csv(
    f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    nrows=500  # suffisant pour détecter les colonnes mixtes
)

# 🔍 Détection des colonnes à problème (mélange de nombres et texte)
problematic_cols = []
for col in sample.columns:
    if sample[col].dtype == object:
        # Vérifie si certaines valeurs ne sont pas numériques
        try:
            pd.to_numeric(sample[col].dropna(), errors="raise")
        except Exception:
            problematic_cols.append(col)

print("⚠️ Colonnes mixtes détectées :", problematic_cols)

# 📥 Lecture avec Dask en forçant ces colonnes en string
import dask.dataframe as dd

dtype_map = {col: "object" for col in problematic_cols}
faostat_crop_df = dd.read_csv(
    f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    assume_missing=True,
    dtype=dtype_map
)

print("✅ Chargement FAOSTAT sécurisé.")
