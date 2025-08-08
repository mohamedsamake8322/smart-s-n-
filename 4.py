import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Dtypes forcés pour éviter les conflits float/object
dtype_fix = {
    "ADM0_NAME": "string",
    "ADM1_NAME": "string",
    "ADM2_NAME": "string",
    "DISP_AREA": "string",
    "STATUS": "string",
    "Area": "string",
    "Country Name": "string"
}

# 📥 Chargement des fichiers
print("📥 Chargement des fichiers...")
soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", dtype=dtype_fix)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", dtype=dtype_fix)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", dtype=dtype_fix)
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv", dtype=dtype_fix)
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", dtype=dtype_fix)
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv", dtype=dtype_fix)

print("✅ Fichiers chargés.")

# 🧮 Reconstruction des rendements FAOSTAT
print("🧮 Reconstruction des rendements FAOSTAT...")
area_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Area harvested", case=False)]
prod_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Production", case=False)]

merged_yield_df = area_df.merge(
    prod_df,
    on=['Area', 'Item', 'Year'],
    suffixes=('_area', '_prod'),
    how='inner'
)
merged_yield_df['Yield_t_ha'] = merged_yield_df['Value_prod'] / merged_yield_df['Value_area']
print("✅ Rendements reconstruits :", merged_yield_df.shape)

# 🔄 Harmonisation des noms de pays
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

merged_yield_df['Area'] = merged_yield_df['Area'].replace(country_mapping)
indicators_df['Country Name'] = indicators_df['Country Name'].replace(country_mapping)

# 🔗 Fusion avec les indicateurs agricoles
print("🔗 Fusion avec les indicateurs agricoles...")
merged_yield_df = merged_yield_df.merge(
    indicators_df,
    left_on=['Area', 'Year'],
    right_on=['Country Name', 'Year'],
    how='left'
)
print("✅ Après ajout des indicateurs agricoles :", merged_yield_df.shape)

# 🔗 Fusion FAOSTAT + BIOCLIM
print("🔗 Fusion FAOSTAT + BIOCLIM...")
step1_df = merged_yield_df.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')
print("✅ Après FAOSTAT + BIOCLIM :", step1_df.shape)

# 🔗 Fusion avec climat mensuel
print("🔗 Fusion avec climat mensuel...")
step2_df = step1_df.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
print("✅ Après ajout climat mensuel :", step2_df.shape)

# 📊 Agrégation intelligente des données de sol
print("📊 Agrégation intelligente des données de sol...")
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'mean': 'mean',
    'min': 'mean',
    'max': 'mean',
    'stdDev': 'mean'
}).reset_index()
print("✅ Données de sol agrégées :", soil_agg.shape)

# 🔗 Fusion avec données de sol agrégées
print("🔗 Fusion avec données de sol agrégées...")
step3_df = step2_df.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
print("✅ Après ajout sol (agrégé) :", step3_df.shape)

# 🧹 Nettoyage final
final_df = step3_df.dropna(subset=['Yield_t_ha'])
print("🧹 Après suppression des lignes sans rendement :", final_df.shape)

# 🔍 Harmonisation finale des types pour export
for col in ["ADM2_NAME", "DISP_AREA", "STATUS"]:
    if col in final_df.columns:
        final_df[col] = final_df[col].astype("string")

print("🔍 Colonnes disponibles :", list(final_df.columns))

# 💾 Sauvegarde avec barre de progression
print("💾 Sauvegarde du fichier Fusion_agronomique_intelligente.csv.gz...")
with ProgressBar():
    final_df.to_csv(
        f"{data_dir}\\Fusion_agronomique_intelligente.csv.gz",
        index=False, compression='gzip', single_file=True
    )

print("📁 Fichier sauvegardé : Fusion_agronomique_intelligente.csv.gz")
