import pandas as pd
import os

# 📂 Chemin vers ton fichier final
BASE_PATH = r"C:\plateforme-agricole-complete-v2\merged_outputs"
FILE = "final_dataset.csv.gz"
FULL_PATH = os.path.join(BASE_PATH, FILE)

print("📥 Chargement du fichier...")
df = pd.read_csv(FULL_PATH, dtype=str, low_memory=False)

print(f"\n✅ Dataset chargé : {df.shape[0]:,} lignes × {df.shape[1]:,} colonnes")

# 📌 Aperçu des colonnes
print("\n📌 Colonnes disponibles :")
print(df.columns.tolist())

# 🔍 Types de données (tout est object ici, mais utile à convertir après)
print("\n🔎 Types de données :")
print(df.dtypes.value_counts())

# 🧼 Valeurs manquantes
print("\n🧼 Colonnes avec valeurs manquantes :")
missing = df.isna().sum().sort_values(ascending=False)
print(missing[missing > 0].head(10))

# 🧮 Détection des colonnes numériques candidates
numeric_cols = [col for col in df.columns if col.lower() in ["lon", "lat", "fusion_yld", "fusion_prd", "max", "value", "mean_ndvi", "mean_ndmi"]]
df_num = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

print("\n📊 Statistiques de base sur les colonnes numériques :")
print(df_num.describe().transpose().round(2))

# 🌍 Pays présents
if "adm0_name" in df.columns:
    print("\n🌍 Pays présents :")
    print(df["adm0_name"].dropna().unique())

# 🌾 Recherche de la colonne "culture"
culture_col = None
for col in df.columns:
    if "cult" in col.lower():
        culture_col = col
        break

if culture_col:
    print(f"\n🌾 Cultures (colonne détectée : '{culture_col}') :")
    print(df[culture_col].dropna().unique())
else:
    print("\n🚫 Colonne liée à la culture non trouvée.")

# 🗓️ Mois couverts
if "month" in df.columns:
    print("\n🗓️ Mois couverts :")
    print(df["month"].dropna().unique())

# ⚠️ Outliers NDVI / climat
if "mean_ndvi" in df_num.columns:
    outliers = df_num[df_num["mean_ndvi"] > 1.2]
    print(f"\n⚠️ NDVI > 1.2 : {len(outliers)} lignes suspectes")

if "value" in df_num.columns:
    negatives = df_num[df_num["value"] < 0]
    print(f"\n⚠️ Valeurs < 0 : {len(negatives)} lignes (ex: précipitations négatives ?)")

# 🧼 Doublons
dup_count = df.duplicated().sum()
print(f"\n📎 Doublons détectés : {dup_count} lignes")

print("\n✅ Exploration terminée.")
