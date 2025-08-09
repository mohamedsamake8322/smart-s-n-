import pandas as pd
import os
import re
import gc
import uuid

BASE_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset_fusionne_pour_XGBoost.csv.gz")
TEMP_DIR = os.path.join(BASE_DIR, "temp_fusion")
os.makedirs(TEMP_DIR, exist_ok=True)

FILES = [
    "Production IndicesFAOSTAT_data_en_8-8-2025.csv",
    "Value of Agricultural ProductionFAOSTAT_data_en_8-8-2025.csv",
    "Temperature change on landFAOSTAT_data_en_8-8-2025.csv",
    "Cropland Nutrient BalanceFAOSTAT_data_en_8-8-2025.csv",
    "Pesticides UseFAOSTAT_data_en_8-8-2025.csv",
    "Livestock ManureFAOSTAT_data_en_8-8-2025.csv",
    "Detailed trade matrix (fertilizers)FAOSTAT_data_en_8-8-2025.csv",
    "FertilizersbyProductFAOSTAT_data_en_7-22-2025.csv",
    "FertilizersbyNutrientFAOSTAT_data_en_8-8-2025.csv",
    "Land CoverFAOSTAT_data_en_8-8-2025.csv",
    "Land UseFAOSTAT_data_en_8-8-2025.csv",
    "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
]

def detect_keys(columns):
    country = next((c for c in columns if re.search(r"country|area|adm0|region", c, re.IGNORECASE)), None)
    year = next((c for c in columns if re.search(r"year|annee|str1_year", c, re.IGNORECASE)), None)
    return country, year

def clean_year(df, year_col):
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    return df[df[year_col].between(1900, 2100)]

def load_and_prepare(file_path):
    try:
        df = pd.read_csv(file_path, low_memory=False)
        country_col, year_col = detect_keys(df.columns)
        if not country_col or not year_col:
            print(f"⚠️ Colonnes clés manquantes dans {os.path.basename(file_path)} — ignoré")
            return None
        df.rename(columns={country_col: "country", year_col: "year"}, inplace=True)
        df = clean_year(df, "year")
        df = df.dropna(subset=["country", "year"])
        print(f"✅ {os.path.basename(file_path)} → {df.shape[0]} lignes, {df.shape[1]} colonnes")
        return df
    except Exception as e:
        print(f"❌ Erreur dans {file_path} : {e}")
        return None

def fusion_sur_disque(file1, file2, output_path):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Vérification des clés
    common_countries = set(df1["country"]).intersection(set(df2["country"]))
    common_years = set(df1["year"]).intersection(set(df2["year"]))
    if not common_countries or not common_years:
        print(f"⚠️ Pas de chevauchement entre {os.path.basename(file1)} et {os.path.basename(file2)} — fusion ignorée")
        df1.to_csv(output_path, index=False)
        return output_path

    # Supprimer les colonnes dupliquées identiques
    overlapping = set(df1.columns).intersection(set(df2.columns)) - {"country", "year"}
    for col in overlapping:
        if df1[col].equals(df2[col]):
            df2.drop(columns=[col], inplace=True)

    # Fusion avec suffixes personnalisés
    try:
        df_merged = pd.merge(
            df1,
            df2,
            on=["country", "year"],
            how="outer",
            suffixes=("_left", "_right")
        )
        df_merged.drop_duplicates(subset=["country", "year"], keep="first", inplace=True)
        df_merged.to_csv(output_path, index=False)
        gc.collect()
        return output_path
    except pd.errors.MergeError as e:
        print(f"❌ Erreur de fusion : {e}")
        df1.to_csv(output_path, index=False)
        return output_path

# 📂 Étape 1 : sauvegarde des fichiers nettoyés
temp_files = []
for filename in FILES:
    path = os.path.join(BASE_DIR, filename)
    df = load_and_prepare(path)
    if df is not None:
        temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.csv")
        df.to_csv(temp_path, index=False)
        temp_files.append(temp_path)
        gc.collect()

# 📂 Étape 2 : fusion progressive sur disque
while len(temp_files) > 1:
    f1 = temp_files.pop(0)
    f2 = temp_files.pop(0)
    merged_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}_merged.csv")
    print(f"🔗 Fusion de {os.path.basename(f1)} + {os.path.basename(f2)}")
    result_path = fusion_sur_disque(f1, f2, merged_path)
    temp_files.insert(0, result_path)
    os.remove(f1)
    os.remove(f2)

# 📂 Étape 3 : export final compressé
if temp_files:
    df_final = pd.read_csv(temp_files[0])
    df_final.to_csv(OUTPUT_FILE, index=False, compression="gzip")
    print(f"✅ Fichier final prêt pour XGBoost : {OUTPUT_FILE}")
    os.remove(temp_files[0])
else:
    print("❌ Aucun fichier n'a pu être fusionné.")
