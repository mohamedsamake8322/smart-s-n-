import os
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

print("📥 Chargement des fichiers avec Dask...")

soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", assume_missing=True)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", assume_missing=True)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", assume_missing=True)

# --- 🔍 Scan sécurisé FAOSTAT ---
faostat_file = os.path.join(data_dir, "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv")
print("📥 Scan rapide du fichier FAOSTAT...")

# Lecture échantillon pour détecter colonnes mixtes
sample = pd.read_csv(faostat_file, nrows=500)
sample.columns = sample.columns.str.strip()

problematic_cols = []
for col in sample.columns:
    if sample[col].dtype == object:
        try:
            pd.to_numeric(sample[col].dropna(), errors="raise")
        except Exception:
            problematic_cols.append(col)

# Colonnes à forcer
extra_force = ["Item Code (CPC)"]
for col in extra_force:
    if col in sample.columns and col not in problematic_cols:
        problematic_cols.append(col)

print(f"⚠️ Colonnes forcées en object : {problematic_cols}")

dtype_map = {col: "object" for col in problematic_cols}
faostat_crop_df = dd.read_csv(faostat_file, assume_missing=True, dtype=dtype_map)
print("✅ Chargement FAOSTAT sécurisé avec Dask.")

indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", assume_missing=True)
yield_df = dd.read_csv(
    f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv",
    assume_missing=True
)

# --- 🔍 Conversion colonnes clés ---
def safe_str_column(df, col):
    if col in df.columns:
        return df.assign(**{col: df[col].astype("string")})
    return df

for df in [soil_df, bio_df, clim_df]:
    df = safe_str_column(df, "ADM0_NAME")
    df = safe_str_column(df, "ADM1_NAME")

faostat_crop_df = safe_str_column(faostat_crop_df, "Area")
faostat_crop_df = safe_str_column(faostat_crop_df, "Item")
faostat_crop_df = safe_str_column(faostat_crop_df, "Year")

indicators_df = safe_str_column(indicators_df, "Country Name")
indicators_df = safe_str_column(indicators_df, "Year")

yield_df = safe_str_column(yield_df, "Area")
yield_df = safe_str_column(yield_df, "Year")

print("✅ Colonnes clés converties.")

# --- 🧮 Reconstruction rendements ---
print("🧮 Reconstruction des rendements FAOSTAT...")
area_df = faostat_crop_df[faostat_crop_df["Element"].str.contains("Area harvested", case=False, na=False)]
prod_df = faostat_crop_df[faostat_crop_df["Element"].str.contains("Production", case=False, na=False)]

merged_yield_df = dd.merge(area_df, prod_df, on=["Area", "Item", "Year"], suffixes=("_area", "_prod"), how="inner")
merged_yield_df = merged_yield_df.assign(
    Yield_t_ha = merged_yield_df["Value_prod"] / merged_yield_df["Value_area"]
)

# --- 🔄 Harmonisation pays ---
print("🔄 Harmonisation noms pays...")
country_mapping = {
    "Algérie": "Algeria", "Bénin": "Benin", "République centrafricaine": "CAR",
    "République du Congo": "Congo", "République démocratique du Congo": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast", "Égypte": "Egypt", "Guinée équatoriale": "Equatorial Guinea",
    "Érythrée": "Eritrea", "Eswatini": "Swaziland", "Éthiopie": "Ethiopia", "Gambie": "The Gambia",
    "Guinée-Bissau": "Guinea Bissau", "Libéria": "Liberia", "Maurice": "Mauritius",
    "Mozambique": "Mozambique", "Namibie": "Namibia", "Nigéria": "Nigeria",
    "Sao Tomé-et-Principe": "Sao Tome and Principe", "Soudan du Sud": "South Sudan",
    "Tanzanie": "Tanzania"
}
merged_yield_df = merged_yield_df.map_partitions(
    lambda df: df.assign(Area=df["Area"].replace(country_mapping))
)
indicators_df = indicators_df.map_partitions(
    lambda df: df.assign(**{"Country Name": df["Country Name"].replace(country_mapping)})
)

# --- 🔗 Fusions progressives sans persist ---
print("🔗 Fusion avec indicateurs agricoles...")
merged = dd.merge(
    merged_yield_df,
    indicators_df,
    left_on=["Area", "Year"],
    right_on=["Country Name", "Year"],
    how="left"
)

print("🔗 Fusion avec Bioclim...")
bio_df = bio_df[["ADM0_NAME", "ADM1_NAME", "bio1", "bio12", "bio15"]]  # limiter colonnes
merged = dd.merge(merged, bio_df, left_on="Area", right_on="ADM0_NAME", how="left")

print("🔗 Fusion avec climat mensuel...")
clim_df = clim_df[["ADM0_NAME", "ADM1_NAME", "tavg", "prec"]]  # exemple colonnes utiles
merged = dd.merge(merged, clim_df, on=["ADM0_NAME", "ADM1_NAME"], how="left")

print("📊 Agrégation sol...")
soil_agg = soil_df.groupby(["ADM0_NAME", "ADM1_NAME"]).agg({
    "mean": "mean", "min": "mean", "max": "mean", "stdDev": "mean"
}).reset_index()
merged = dd.merge(merged, soil_agg, on=["ADM0_NAME", "ADM1_NAME"], how="left")

print("🧹 Suppression lignes sans rendement...")
merged = merged.dropna(subset=["Yield_t_ha"])

# --- 💾 Sauvegarde lazy ---
print("💾 Sauvegarde fusion finale...")
with ProgressBar():
    merged.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente_*.csv.gz", index=False, compression="gzip")
print("✅ Sauvegarde terminée.")
