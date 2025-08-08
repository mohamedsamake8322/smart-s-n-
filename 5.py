import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

print("📥 Chargement des fichiers avec Dask...")

soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", assume_missing=True)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", assume_missing=True)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", assume_missing=True)
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv", assume_missing=True)
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", assume_missing=True)
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv", assume_missing=True)

print("✅ Fichiers chargés.")

print("🔍 Vérification et conversion des colonnes clés en string...")

def safe_str_column(df, col):
    if col in df.columns:
        return df.assign(**{col: df[col].astype("string")})
    return df

soil_df = safe_str_column(soil_df, "ADM0_NAME")
soil_df = safe_str_column(soil_df, "ADM1_NAME")

bio_df = safe_str_column(bio_df, "ADM0_NAME")
bio_df = safe_str_column(bio_df, "ADM1_NAME")

clim_df = safe_str_column(clim_df, "ADM0_NAME")
clim_df = safe_str_column(clim_df, "ADM1_NAME")

faostat_crop_df = safe_str_column(faostat_crop_df, "Area")
faostat_crop_df = safe_str_column(faostat_crop_df, "Item")
faostat_crop_df = safe_str_column(faostat_crop_df, "Year")

indicators_df = safe_str_column(indicators_df, "Country Name")
indicators_df = safe_str_column(indicators_df, "Year")

if "Area" in yield_df.columns:
    yield_df = yield_df.assign(**{"Area": yield_df["Area"].astype("string")})
if "Year" in yield_df.columns:
    yield_df = yield_df.assign(**{"Year": yield_df["Year"].astype("string")})

print("✅ Colonnes clés converties.")

print("🧮 Reconstruction des rendements FAOSTAT (Yield = Production / Area)...")

area_df = faostat_crop_df[faostat_crop_df["Element"].str.contains("Area harvested", case=False, na=False)].persist()
prod_df = faostat_crop_df[faostat_crop_df["Element"].str.contains("Production", case=False, na=False)].persist()

merged_yield_df = dd.merge(area_df, prod_df, on=["Area", "Item", "Year"], suffixes=("_area", "_prod"), how="inner")

merged_yield_df = merged_yield_df.assign(
    Yield_t_ha = merged_yield_df["Value_prod"] / merged_yield_df["Value_area"]
).persist()

print(f"✅ Rendements reconstruits : {merged_yield_df.shape[0].compute()} lignes.")

print("🔄 Harmonisation noms pays dans FAOSTAT et indicateurs...")

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

merged_yield_df = merged_yield_df.map_partitions(
    lambda df: df.assign(Area = df["Area"].replace(country_mapping))
).persist()

indicators_df = indicators_df.map_partitions(
    lambda df: df.assign(**{"Country Name": df["Country Name"].replace(country_mapping)})
).persist()

print("🔗 Fusion rendements FAOSTAT avec indicateurs agricoles...")

merged = dd.merge(
    merged_yield_df,
    indicators_df,
    left_on=["Area", "Year"],
    right_on=["Country Name", "Year"],
    how="left"
).persist()

print(f"✅ Après fusion indicateurs : {merged.shape[0].compute()} lignes.")

print("🔗 Fusion avec Bioclim...")

merged = dd.merge(
    merged,
    bio_df,
    left_on="Area",
    right_on="ADM0_NAME",
    how="left"
).persist()

print(f"✅ Après fusion Bioclim : {merged.shape[0].compute()} lignes.")

print("🔗 Fusion avec climat mensuel...")

merged = dd.merge(
    merged,
    clim_df,
    left_on=["ADM0_NAME", "ADM1_NAME"],
    right_on=["ADM0_NAME", "ADM1_NAME"],
    how="left"
).persist()

print(f"✅ Après fusion climat mensuel : {merged.shape[0].compute()} lignes.")

print("📊 Agrégation des données de sol...")

soil_agg = soil_df.groupby(["ADM0_NAME", "ADM1_NAME"]).agg({
    "mean": "mean",
    "min": "mean",
    "max": "mean",
    "stdDev": "mean"
}).reset_index().persist()

print(f"✅ Sol agrégé : {soil_agg.shape[0].compute()} lignes.")

print("🔗 Fusion avec données de sol agrégées...")

merged = dd.merge(
    merged,
    soil_agg,
    on=["ADM0_NAME", "ADM1_NAME"],
    how="left"
).persist()

print(f"✅ Après ajout sol : {merged.shape[0].compute()} lignes.")

print("🧹 Suppression des lignes sans rendement...")

merged = merged.dropna(subset=["Yield_t_ha"]).persist()

print(f"✅ Après suppression : {merged.shape[0].compute()} lignes.")

print("💾 Sauvegarde du fichier Fusion_agronomique_intelligente.csv.gz avec compression gzip...")

with ProgressBar():
    merged.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente_*.csv.gz",
                  index=False, compression="gzip", single_file=False)

print("✅ Fichier sauvegardé.")

