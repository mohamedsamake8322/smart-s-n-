import pandas as pd
import os

# 📂 Dossier contenant tous les fichiers
BASE_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# --- 1. Liste des fichiers FAOSTAT ---
files_faostat = [
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
]

# --- 2. Chargement et concaténation FAOSTAT ---
print("📥 Chargement et concaténation des fichiers FAOSTAT...")
dfs = []
for fname in files_faostat:
    path = os.path.join(BASE_DIR, fname)
    print(f"  - Chargement {fname} ...")
    df = pd.read_csv(path, dtype=str)  # dtype=str pour éviter problème de type
    dfs.append(df)

faostat_full = pd.concat(dfs, ignore_index=True)
print(f"✅ FAOSTAT fusionné, total lignes : {len(faostat_full)}")

# --- 3. Chargement CHIRPS et SMAP ---
print("📥 Chargement CHIRPS et SMAP...")
chirps_path = os.path.join(BASE_DIR, "CHIRPS_DAILY_PENTAD.csv")
smap_path = os.path.join(BASE_DIR, "SMAP_SoilMoisture.csv")

chirps = pd.read_csv(chirps_path, dtype=str)
smap = pd.read_csv(smap_path, dtype=str)

# --- 4. Harmonisation colonnes clés et noms pays ---
print("🔄 Harmonisation des noms de colonnes...")

# Fonction de nettoyage simple des noms de pays
country_mapping = {
    "Algérie": "Algeria", "Bénin": "Benin", "République démocratique du Congo": "DR Congo",
    # Ajoute ici tous les autres mappings nécessaires
}

def harmonize_countries(df, col_name):
    df[col_name] = df[col_name].replace(country_mapping)
    return df

# FAOSTAT
faostat_full = harmonize_countries(faostat_full, "Area")
faostat_full.rename(columns={"Area": "country", "Year": "year"}, inplace=True)

# CHIRPS
chirps.rename(columns={"ADM0_NAME": "country", "STR1_YEAR": "year"}, inplace=True)
chirps = harmonize_countries(chirps, "country")

# SMAP
smap.rename(columns={"ADM0_NAME": "country", "STR1_YEAR": "year", "mean": "soil_moisture"}, inplace=True)
smap = harmonize_countries(smap, "country")

# --- 5. Conversion des colonnes clés en type compatible ---
print("🔄 Conversion des colonnes 'year' en int...")
for df in [faostat_full, chirps, smap]:
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype('Int64')

# --- 6. Fusion FAOSTAT + CHIRPS + SMAP ---
print("🔗 Fusion des datasets...")
df_merged = pd.merge(faostat_full, chirps, on=["country", "year"], how="left", suffixes=('', '_chirps'))
df_merged = pd.merge(df_merged, smap, on=["country", "year"], how="left", suffixes=('', '_smap'))

print(f"✅ Fusion terminée, lignes au total : {len(df_merged)}")

# --- 7. Sauvegarde finale compressée ---
output_path = os.path.join(BASE_DIR, "FAOSTAT_CHIRPS_SMAP_merged.csv.gz")
print(f"💾 Sauvegarde compressée vers {output_path} ...")
df_merged.to_csv(output_path, index=False, compression='gzip')

print("🎉 Script terminé avec succès !")
