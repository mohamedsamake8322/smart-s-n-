import pandas as pd
import os
import re
import gc

# 📁 Dossier contenant les fichiers CSV
BASE_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"
OUTPUT_FILE = os.path.join(BASE_DIR, "dataset_fusionne_pour_XGBoost.csv.gz")

# 📌 Liste des fichiers à fusionner
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
    df = df[df[year_col].between(1900, 2100)]
    return df

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
def fusion_securisee(df1, df2):
    """Fusionne deux DataFrames uniquement si les clés se chevauchent."""
    common_countries = set(df1["country"]).intersection(set(df2["country"]))
    common_years = set(df1["year"]).intersection(set(df2["year"]))
    if not common_countries or not common_years:
        print("⚠️ Pas de chevauchement sur 'country' ou 'year' — fusion ignorée")
        return df1
    return pd.merge(df1, df2, on=["country", "year"], how="outer")

# 📂 Lecture et fusion progressive sécurisée
df_final = None
for i, filename in enumerate(FILES, start=1):
    path = os.path.join(BASE_DIR, filename)
    print(f"🔍 Lecture de {filename}")
    df = load_and_prepare(path)
    if df is None:
        continue

    if df_final is None:
        df_final = df
    else:
        print(f"🔄 Fusion {i}/{len(FILES)} — avant : {df_final.shape}")
        df_final = fusion_securisee(df_final, df)
        print(f"✅ Fusion {i} terminée — après : {df_final.shape}")
        gc.collect()


# 🧹 Nettoyage final
if df_final is not None:
    print("🧹 Suppression des doublons...")
    df_final.drop_duplicates(subset=["country", "year"], keep="first", inplace=True)

    print("💾 Sauvegarde du fichier fusionné...")
    df_final.to_csv(OUTPUT_FILE, index=False, compression="gzip")
    print(f"✅ Fichier final prêt pour XGBoost : {OUTPUT_FILE}")
else:
    print("❌ Aucun fichier n'a pu être fusionné.")
