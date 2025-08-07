import pandas as pd

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📄 Chargement des fichiers
soil_df = pd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv")
bio_df = pd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv")
clim_df = pd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv")
faostat_df = pd.read_csv(f"{data_dir}\\FAOSTAT_data_en_8-7-2025.csv")
yield_df = pd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

# 🎯 Filtrage FAOSTAT pour le rendement
faostat_yield = faostat_df[faostat_df['Element'] == 'Yield'].copy()

# 🧭 Dictionnaire de correspondance des noms de pays
country_mapping = {
    "Algérie": "Algeria",
    "Angola": "Angola",
    "Bénin": "Benin",
    "Botswana": "Botswana",
    "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi",
    "Cabo Verde": "Cape Verde",
    "Cameroun": "Cameroon",
    "République centrafricaine": "CAR",
    "Tchad": "Chad",
    "Comores": "Comoros",
    "République du Congo": "Congo",
    "République démocratique du Congo": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Djibouti": "Djibouti",
    "Égypte": "Egypt",
    "Guinée équatoriale": "Equatorial Guinea",
    "Érythrée": "Eritrea",
    "Eswatini": "Swaziland",
    "Éthiopie": "Ethiopia",
    "Gabon": "Gabon",
    "Gambie": "The Gambia",
    "Ghana": "Ghana",
    "Guinée": "Guinea",
    "Guinée-Bissau": "Guinea Bissau",
    "Kenya": "Kenya",
    "Lesotho": "Lesotho",
    "Libéria": "Liberia",
    "Libye": "Libya",
    "Madagascar": "Madagascar",
    "Malawi": "Malawi",
    "Mali": "Mali",
    "Mauritanie": "Mauritania",
    "Maurice": "Mauritius",
    "Maroc": "Morocco",
    "Mozambique": "Mozambique",
    "Namibie": "Namibia",
    "Niger": "Niger",
    "Nigéria": "Nigeria",
    "Rwanda": "Rwanda",
    "Sao Tomé-et-Principe": "Sao Tome and Principe",
    "Sénégal": "Senegal",
    "Seychelles": "Seychelles",
    "Sierra Leone": "Sierra Leone",
    "Somalie": "Somalia",
    "Afrique du Sud": "South Africa",
    "Soudan du Sud": "South Sudan",
    "Soudan": "Sudan",
    "Tanzanie": "Tanzania",
    "Togo": "Togo",
    "Tunisie": "Tunisia",
    "Ouganda": "Uganda",
    "Zambie": "Zambia",
    "Zimbabwe": "Zimbabwe",
}

# 🔄 Remplacement des noms FAOSTAT
faostat_yield['Area'] = faostat_yield['Area'].replace(country_mapping)

# 🔗 Fusion FAOSTAT + BIOCLIM
merged_df = faostat_yield.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')

# 🔗 Fusion avec climat mensuel
merged_df = merged_df.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# 🔗 Fusion avec données de sol
merged_df = merged_df.merge(soil_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# 📊 Vérification des pays non appariés
faostat_countries = set(faostat_yield['Area'].unique())
bioclim_countries = set(bio_df['ADM0_NAME'].unique())
missing = faostat_countries - bioclim_countries
print("🌍 Pays non appariés :", missing)

# 🧼 Nettoyage final
final_df = merged_df.dropna(subset=['Value'])  # garder les lignes avec rendement FAOSTAT

# 📈 Aperçu
print("✅ Fusion terminée. Dimensions :", final_df.shape)
print("🔍 Colonnes disponibles :", list(final_df.columns))
