import os
import pandas as pd
import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# 🔧 Fusion sécurisée avec gestion des types et des clés
def safe_merge(df1, df2, keys=None, left_on=None, right_on=None, how="left", verbose=True):
    """
    Fusionne deux Dask DataFrames en harmonisant les types et en vérifiant les clés.

    Args:
        df1, df2: Dask DataFrames à fusionner
        keys: Liste de colonnes communes pour la fusion
        left_on, right_on: Colonnes spécifiques pour fusion asymétrique
        how: Type de jointure
        verbose: Affiche les diagnostics

    Returns:
        dd.DataFrame fusionné
    """
    if keys:
        left_keys = right_keys = keys
    elif left_on and right_on:
        left_keys = left_on
        right_keys = right_on
    else:
        raise ValueError("❌ Spécifie 'keys' ou 'left_on' et 'right_on'")

    # Vérification des colonnes
    missing_df1 = [k for k in left_keys if k not in df1.columns]
    missing_df2 = [k for k in right_keys if k not in df2.columns]
    if missing_df1 or missing_df2:
        raise KeyError(f"❌ Clés manquantes : df1={missing_df1}, df2={missing_df2}")

    # Harmonisation des types
    for lk, rk in zip(left_keys, right_keys):
        if df1[lk].dtype != df2[rk].dtype:
            if verbose:
                print(f"⚠️ Type mismatch '{lk}' vs '{rk}' — conversion en string")
            df1[lk] = df1[lk].astype(str)
            df2[rk] = df2[rk].astype(str)

    # Fusion
    if keys:
        merged = dd.merge(df1, df2, on=keys, how=how)
    else:
        merged = dd.merge(df1, df2, left_on=left_on, right_on=right_on, how=how)

    if verbose:
        print(f"✅ Fusion réussie avec méthode '{how}' sur {left_keys if keys else left_on} ↔ {right_on}")
    return merged

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"
print("📥 Chargement des fichiers avec Dask...")

soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", assume_missing=True)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", assume_missing=True)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", assume_missing=True)

# --- 🔍 Scan sécurisé FAOSTAT ---
faostat_file = os.path.join(data_dir, "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv")
print("📥 Scan rapide du fichier FAOSTAT...")
sample = pd.read_csv(faostat_file, nrows=500)
sample.columns = sample.columns.str.strip()

problematic_cols = []
for col in sample.columns:
    if sample[col].dtype == object:
        try:
            pd.to_numeric(sample[col].dropna(), errors="raise")
        except Exception:
            problematic_cols.append(col)

extra_force = ["Item Code (CPC)"]
for col in extra_force:
    if col in sample.columns and col not in problematic_cols:
        problematic_cols.append(col)

print(f"⚠️ Colonnes forcées en object : {problematic_cols}")
dtype_map = {col: "object" for col in problematic_cols}
faostat_crop_df = dd.read_csv(faostat_file, assume_missing=True, dtype=dtype_map)
print("✅ Chargement FAOSTAT sécurisé avec Dask.")

indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", assume_missing=True)
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv", assume_missing=True)

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
merged_yield_df = merged_yield_df.assign(Yield_t_ha = merged_yield_df["Value_prod"] / merged_yield_df["Value_area"])

# --- 🔄 Harmonisation pays ---
print("🔄 Harmonisation noms pays...")
country_mapping = {
    "Algérie": "Algeria", "Angola": "Angola", "Bénin": "Benin", "Botswana": "Botswana",
    "Burkina Faso": "Burkina Faso", "Burundi": "Burundi", "Cabo Verde": "Cape Verde",
    "Cameroun": "Cameroon", "République centrafricaine": "CAR", "Tchad": "Chad",
    "Comores": "Comoros", "République du Congo": "Congo", "République démocratique du Congo": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast", "Djibouti": "Djibouti", "Égypte": "Egypt",
    "Guinée équatoriale": "Equatorial Guinea", "Érythrée": "Eritrea", "Eswatini": "Swaziland",
    "Éthiopie": "Ethiopia", "Gabon": "Gabon", "Gambie": "The Gambia", "Ghana": "Ghana",
    "Guinée": "Guinea", "Guinée-Bissau": "Guinea Bissau", "Kenya": "Kenya", "Lesotho": "Lesotho",
    "Libéria": "Liberia", "Libye": "Libya", "Madagascar": "Madagascar", "Malawi": "Malawi",
    "Mali": "Mali", "Mauritanie": "Mauritania", "Maurice": "Mauritius", "Maroc": "Morocco",
    "Mozambique": "Mozambique", "Namibie": "Namibia", "Niger": "Niger", "Nigéria": "Nigeria",
    "Rwanda": "Rwanda", "Sao Tomé-et-Principe": "Sao Tome and Principe", "Sénégal": "Senegal",
    "Seychelles": "Seychelles", "Sierra Leone": "Sierra Leone", "Somalie": "Somalia",
    "Afrique du Sud": "South Africa", "Soudan du Sud": "South Sudan", "Soudan": "Sudan",
    "Tanzanie": "Tanzania", "Togo": "Togo", "Tunisie": "Tunisia", "Ouganda": "Uganda",
    "Zambie": "Zambia", "Zimbabwe": "Zimbabwe",
}
merged_yield_df = merged_yield_df.map_partitions(lambda df: df.assign(Area=df["Area"].replace(country_mapping)))
indicators_df = indicators_df.map_partitions(lambda df: df.assign(**{"Country Name": df["Country Name"].replace(country_mapping)}))

# --- 🔗 Fusions progressives ---
print("🔗 Fusion avec indicateurs agricoles...")
merged = safe_merge(merged_yield_df, indicators_df, left_on=["Area", "Year"], right_on=["Country Name", "Year"])

wanted_bio = ["bio01", "bio12", "bio15"]
available_bio = [col for col in wanted_bio if col in bio_df.columns]
missing_bio = [col for col in wanted_bio if col not in bio_df.columns]
if missing_bio:
    print(f"⚠️ Colonnes manquantes dans BIOCLIM : {missing_bio}")
bio_df = bio_df[["ADM0_NAME", "ADM1_NAME"] + available_bio]

merged = dd.merge(merged, bio_df, left_on="Area", right_on="ADM0_NAME", how="left")

print("🔗 Fusion avec climat mensuel...")
clim_df = clim_df[["ADM0_NAME", "ADM1_NAME", "tavg", "prec"]]  # exemple colonnes utiles
merged = dd.merge(merged, clim_df, on=["ADM0_NAME", "ADM1_NAME"], how="left")

print("📊 Agrégation sol...")
soil_agg = soil_df.groupby(["ADM0_NAME", "ADM1_NAME"]).agg({
    "mean": "mean", "min": "mean", "max": "mean", "stdDev": "mean"
}).reset_index()
merged = dd.merge(merged, soil_agg, on=["ADM0_NAME", "ADM1_NAME"], how="left")
merged = safe_merge(merged, soil_agg, keys=["ADM0_NAME", "ADM1_NAME"])
print("🧹 Suppression lignes sans rendement...")
merged = merged.dropna(subset=["Yield_t_ha"])

# --- 💾 Sauvegarde lazy ---
print("💾 Sauvegarde fusion finale...")
with ProgressBar():
    merged.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente_*.csv.gz", index=False, compression="gzip")
print("✅ Sauvegarde terminée.")
