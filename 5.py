import dask.dataframe as dd
import pandas as pd

data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

print("📥 Chargement des fichiers avec Dask...")

soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv")
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv")
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv")
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv")
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv")
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

print("🧮 Reconstruction des rendements FAOSTAT (Yield = Production / Area)...")

# Préparer FAOSTAT: filtrer culture, et calcul rendement (yield)
faostat_crop_df = faostat_crop_df.rename(columns={
    'Area': 'Area',
    'Year': 'Year',
    'Element': 'Element',
    'Value': 'Value'
})

# Produire tables production et surface cultivée
production = faostat_crop_df[faostat_crop_df['Element'] == 'Production']
area = faostat_crop_df[faostat_crop_df['Element'] == 'Area harvested']

# On fait merge production x area sur Area et Year
prod_area = production.merge(area, on=['Area', 'Year'], suffixes=('_prod', '_area'))
# Calcul yield = production / area (colonne 'Value_prod' et 'Value_area')
prod_area = prod_area.assign(yield_value = prod_area['Value_prod'] / prod_area['Value_area'])

# Garder colonnes d'intérêt : Area, Year, yield_value
yield_df_faostat = prod_area[['Area', 'Year', 'yield_value']]

print("🔄 Harmonisation noms pays dans FAOSTAT et indicateurs...")

# Harmoniser noms pays (exemple simple, adapte selon tes données)
def harmonize_country_names(df, col_name):
    mapping = {
        "Côte d'Ivoire": "Ivory Coast",
        "Democratic Republic of the Congo": "DR Congo",
        "United Republic of Tanzania": "Tanzania",
        # ajoute ici les autres mappings nécessaires
    }
    return df.map_partitions(lambda pdf: pdf.replace({col_name: mapping}), meta=df)

yield_df_faostat['Area'] = harmonize_country_names(yield_df_faostat['Area'], 'Area')
indicators_df['Country Name'] = harmonize_country_names(indicators_df['Country Name'], 'Country Name')

print("🔗 Fusion rendements FAOSTAT avec indicateurs agricoles...")

merged = yield_df_faostat.merge(
    indicators_df,
    left_on=['Area', 'Year'],
    right_on=['Country Name', 'Year'],
    how='left'
)

print("🔄 Ajout des colonnes géographiques ADM0_NAME et ADM1_NAME à partir de bio_df...")

# Extraire mapping unique (Area → ADM0_NAME, ADM1_NAME) depuis bio_df (en mode pandas pour éviter soucis Dask)
mapping_geo = bio_df[['ADM0_NAME', 'ADM1_NAME']].drop_duplicates().compute()

# Extraire la liste unique des pays pour Area dans merged (pandas)
area_unique = merged['Area'].drop_duplicates().compute()

# Construire table de correspondance simple Area → ADM0_NAME (en supposant que ADM0_NAME correspond au nom pays FAOSTAT)
# ATTENTION : adapter cette correspondance selon tes données réelles.
mapping_area_adm0 = pd.DataFrame({
    'Area': area_unique,
    'ADM0_NAME': area_unique  # Hypothèse que Area = ADM0_NAME sinon il faut un mapping précis ici
})

# Convertir en Dask
mapping_area_adm0_dd = dd.from_pandas(mapping_area_adm0, npartitions=1)

# Fusionner dans merged pour ajouter ADM0_NAME
merged = merged.merge(mapping_area_adm0_dd, on='Area', how='left')

# Fusionner ensuite pour ajouter ADM1_NAME via bio_df (on merge sur ADM0_NAME)
# Pour ça on prend bio_df subset (ADM0_NAME, ADM1_NAME) unique
bio_geo_sub = bio_df[['ADM0_NAME', 'ADM1_NAME']].drop_duplicates()

merged = merged.merge(
    bio_geo_sub,
    on=['ADM0_NAME'],
    how='left',
    suffixes=('', '_bio')
)

print("🔗 Fusion avec Bioclim...")

merged = merged.merge(
    bio_df,
    on=['ADM0_NAME', 'ADM1_NAME'],
    how='left',
    suffixes=('', '_bio')
)

print("🔗 Fusion avec climat mensuel...")

merged = merged.merge(
    clim_df,
    on=['ADM0_NAME', 'ADM1_NAME'],
    how='left',
    suffixes=('', '_clim')
)

print("🔗 Fusion avec soil_df...")

merged = merged.merge(
    soil_df,
    on=['ADM0_NAME', 'ADM1_NAME'],
    how='left',
    suffixes=('', '_soil')
)

print("🔗 Fusion avec rendement réel (yield_df)...")

merged = merged.merge(
    yield_df,
    left_on=['lon', 'lat'],
    right_on=['lon', 'lat'],
    how='left'
)

print("💾 Sauvegarde du fichier fusionné compressé...")

merged.to_csv(f"{data_dir}\\Fusion_agronomique_intelligente.csv.gz", compression='gzip', single_file=True, index=False)

print("✅ Terminé avec succès !")
