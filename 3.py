import pandas as pd

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📥 Chargement des fichiers
print("📥 Chargement des fichiers...")
soil_df = pd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv")
bio_df = pd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv")
clim_df = pd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv")
faostat_crop_df = pd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv")
indicators_df = pd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv")
yield_df = pd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

print("✅ Fichiers chargés.")
print(f"FAOSTAT CULTURES : {faostat_crop_df.shape}")
print(f"BIOCLIM : {bio_df.shape}")
print(f"CLIMAT MENSUEL : {clim_df.shape}")
print(f"SOIL : {soil_df.shape}")
print(f"INDICATEURS AGRICOLES : {indicators_df.shape}")
print(f"RENDEMENT RÉEL : {yield_df.shape}")

# 🧮 Reconstruction des rendements FAOSTAT
print("🧮 Reconstruction des rendements FAOSTAT...")
area_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Area harvested", case=False)].copy()
prod_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Production", case=False)].copy()

merged_yield_df = pd.merge(
    area_df,
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

# 🔍 Aperçu des colonnes
print("🔍 Colonnes disponibles :", list(final_df.columns))

# 💾 Sauvegarde
final_df.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente.csv", index=False)
print("📁 Fichier sauvegardé : Fusion_agronomique_intelligente.csv")
