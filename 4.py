import dask.dataframe as dd
from dask.diagnostics import ProgressBar

data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Chargement des fichiers avec dtypes précis pour éviter erreurs
soil_df = dd.read_csv(
    f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv",
    dtype={
        "ADM0_NAME": "string",
        "ADM1_NAME": "string",
        "ADM2_NAME": "string",
        "DISP_AREA": "string",
        "STATUS": "string",
        "band_name": "string",
        "collection_id": "string",
        "extraction_date": "string",
        "layer": "string",
        "level": "string",
        "system:index": "string",
        ".geo": "string",
    }
)

bio_df = dd.read_csv(
    f"{data_dir}\\WorldClim BIO Variables V1.csv",
    dtype={
        "ADM0_NAME": "string",
        "ADM1_NAME": "string",
        "DISP_AREA": "string",
        "STATUS": "string",
        "system:index": "string",
        ".geo": "string",
    }
)

clim_df = dd.read_csv(
    f"{data_dir}\\WorldClim_Monthly_Fusion.csv",
    dtype={
        "ADM0_NAME": "string",
        "ADM1_NAME": "string",
        "DISP_AREA": "string",
        "STATUS": "string",
        "system:index": "string",
        ".geo": "string",
    }
)

faostat_crop_df = dd.read_csv(
    f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    dtype={
        "Domain Code": "string",
        "Domain": "string",
        "Area": "string",
        "Element": "string",
        "Flag": "string",
        "Flag Description": "string",
        "Item": "string",
        "Note": "string",
        "Item Code (CPC)": "float64"
    }
)

indicators_df = dd.read_csv(
    f"{data_dir}\\agriculture_indicators_africa.csv",
    dtype={
        "Country Name": "string"
    }
)

yield_df = dd.read_csv(
    f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv"
)

print("✅ Fichiers chargés")

# Reconstruction des rendements FAOSTAT
area_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Area harvested", case=False)]
prod_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Production", case=False)]

merged_yield_df = area_df.merge(
    prod_df,
    on=['Area', 'Item', 'Year'],
    suffixes=('_area', '_prod'),
    how='inner'
)

merged_yield_df['Yield_t_ha'] = merged_yield_df['Value_prod'] / merged_yield_df['Value_area']

# Harmonisation des noms de pays
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

# Fusion avec indicateurs agricoles
merged_yield_df = merged_yield_df.merge(
    indicators_df,
    left_on=['Area', 'Year'],
    right_on=['Country Name', 'Year'],
    how='left'
)

# Fusion FAOSTAT + BIOCLIM
step1_df = merged_yield_df.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')

# Fusion avec climat mensuel
step2_df = step1_df.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# Agrégation des données de sol
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'mean': 'mean',
    'min': 'mean',
    'max': 'mean',
    'stdDev': 'mean'
}).reset_index()

# Fusion avec données de sol agrégées
step3_df = step2_df.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# Nettoyage final
final_df = step3_df.dropna(subset=['Yield_t_ha'])

# Sauvegarde
with ProgressBar():
    final_df.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente.csv.gz",
                    index=False, compression='gzip', single_file=True)

print("📁 Fichier sauvegardé : Fusion_agronomique_intelligente.csv.gz")
