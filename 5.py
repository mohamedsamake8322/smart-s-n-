import dask.dataframe as dd
from dask.diagnostics import ProgressBar

data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

print("📥 Chargement des fichiers avec Dask...")

# 1. Soil : colonnes utiles et dtype
soil_cols = ['ADM0_NAME', 'ADM1_NAME', 'max', 'mean', 'min', 'stdDev']
soil_dtypes = {'ADM0_NAME': 'string', 'ADM1_NAME': 'string', 'max': 'float64', 'mean': 'float64', 'min': 'float64', 'stdDev': 'float64'}
soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", usecols=soil_cols, dtype=soil_dtypes)

# 2. BioClim
bio_cols = ['ADM0_NAME', 'ADM1_NAME'] + [f'bio{str(i).zfill(2)}' for i in range(1, 20)]
bio_dtypes = {col: 'float64' for col in bio_cols[2:]}
bio_dtypes.update({'ADM0_NAME': 'string', 'ADM1_NAME': 'string'})
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", usecols=bio_cols, dtype=bio_dtypes)

# 3. Climat mensuel
clim_cols = ['ADM0_NAME', 'ADM1_NAME', 'prec', 'tavg', 'tmax', 'tmin']
clim_dtypes = {col: 'float64' for col in clim_cols[2:]}
clim_dtypes.update({'ADM0_NAME': 'string', 'ADM1_NAME': 'string'})
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", usecols=clim_cols, dtype=clim_dtypes)

# 4. FAOSTAT crops
faostat_cols = ['Area', 'Element', 'Item', 'Year', 'Value']
faostat_dtypes = {'Area': 'string', 'Element': 'string', 'Item': 'string', 'Year': 'int64', 'Value': 'float64'}
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv", usecols=faostat_cols, dtype=faostat_dtypes)

# 5. Indicateurs agricoles
indicators_cols = None  # charger tout
indicators_dtypes = {'Country Name': 'string', 'Year': 'int64'}
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", dtype=indicators_dtypes)

# Mapping pays FAOSTAT <-> indicateurs (si besoin)
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

print("🧮 Reconstruction des rendements FAOSTAT (Yield = Production / Area)...")

area_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Area harvested", case=False)]
prod_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Production", case=False)]

# Fusion area + production pour calcul yield
merged_yield_df = area_df.merge(prod_df, on=['Area', 'Item', 'Year'], suffixes=('_area', '_prod'), how='inner')

# Yield en t/ha
merged_yield_df['Yield_t_ha'] = merged_yield_df['Value_prod'] / merged_yield_df['Value_area']

print("🔄 Harmonisation noms pays dans FAOSTAT et indicateurs...")

# Conversion noms pays FAOSTAT -> EN pour fusion cohérente avec indicateurs
merged_yield_df['Area'] = merged_yield_df['Area'].replace(country_mapping)
indicators_df['Country Name'] = indicators_df['Country Name'].replace(country_mapping)

# Uniformiser colonnes clés en string (attention Dask demande ça)
merged_yield_df['Area'] = merged_yield_df['Area'].astype('string')
indicators_df['Country Name'] = indicators_df['Country Name'].astype('string')

print("🔗 Fusion rendements FAOSTAT avec indicateurs agricoles...")
merged = merged_yield_df.merge(indicators_df, left_on=['Area', 'Year'], right_on=['Country Name', 'Year'], how='left')

print("🔗 Fusion avec Bioclim...")
merged = merged.merge(bio_df, left_on=['Area', 'ADM1_NAME'], right_on=['ADM0_NAME', 'ADM1_NAME'], how='left')

print("🔗 Fusion avec climat mensuel...")
merged = merged.merge(clim_df, left_on=['ADM0_NAME', 'ADM1_NAME'], right_on=['ADM0_NAME', 'ADM1_NAME'], how='left')

print("📊 Agrégation des données sol...")
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'max': 'mean',
    'mean': 'mean',
    'min': 'mean',
    'stdDev': 'mean',
}).reset_index()

print("🔗 Fusion avec données sol agrégées...")
merged = merged.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

print("🧹 Nettoyage : suppression lignes sans rendement...")
final_df = merged.dropna(subset=['Yield_t_ha'])

print("💾 Sauvegarde du résultat compressé...")
with ProgressBar():
    final_df.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente.csv.gz", index=False, compression='gzip', single_file=True)

print("✅ Traitement terminé avec succès.")
