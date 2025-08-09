import pandas as pd
import os
import re
from functools import reduce

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
    "GEDI_Mangrove_CSV.csv",
    "CHIRPS_DAILY_PENTAD.csv",
    "SMAP_SoilMoisture.csv",
    "X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv"
]

def detect_keys(columns):
    """Détecte les colonnes 'country' et 'year' même si elles ont des noms différents."""
    country = next((c for c in columns if re.search(r"country|area|adm0|region", c, re.IGNORECASE)), None)
    year = next((c for c in columns if re.search(r"year|annee|str1_year", c, re.IGNORECASE)), None)
    return country, year

def clean_year(df, year_col):
    """Nettoie les années invalides et convertit en entier."""
    df[year_col] = pd.to_numeric(df[year_col], errors="coerce")
    df = df[df[year_col].between(1900, 2100)]
    return df

def load_and_prepare(file_path):
    """Charge un fichier CSV et prépare les colonnes clés."""
    try:
        df = pd.read_csv(file_path)
        country_col, year_col = detect_keys(df.columns)
        if not country_col or not year_col:
            print(f"⚠️ Colonnes clés manquantes dans {os.path.basename(file_path)}")
            return None
        df.rename(columns={country_col: "country", year_col: "year"}, inplace=True)
        df = clean_year(df, "year")
        df = df.dropna(subset=["country", "year"])
        return df
    except Exception as e:
        print(f"❌ Erreur dans {file_path} : {e}")
        return None

# 📂 Lecture et préparation des fichiers
dataframes = []
for filename in FILES:
    path = os.path.join(BASE_DIR, filename)
    print(f"🔍 Lecture de {filename}")
    df = load_and_prepare(path)
    if df is not None:
        dataframes.append(df)

# 🔗 Fusion intelligente sur 'country' et 'year'
print("🔗 Fusion des fichiers...")
df_final = reduce(lambda left, right: pd.merge(left, right, on=["country", "year"], how="outer"), dataframes)

# 🧹 Nettoyage final
print("🧹 Suppression des doublons...")
df_final.drop_duplicates(subset=["country", "year"], keep="first", inplace=True)

# 💾 Exportation
print("💾 Sauvegarde du fichier fusionné...")
df_final.to_csv(OUTPUT_FILE, index=False, compression="gzip")
print(f"✅ Fichier final prêt pour XGBoost : {OUTPUT_FILE}")
