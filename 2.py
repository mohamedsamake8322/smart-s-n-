#Script de fusion simplifié
import pandas as pd

# Chargement des fichiers
soil_df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\Soil_AllLayers_AllAfrica-002.csv")
bio_df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\WorldClim BIO Variables V1.csv")
clim_df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\WorldClim_Monthly_Fusion.csv")
faostat_df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\FAOSTAT_data_en_8-7-2025.csv")
yield_df = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

# Filtrage FAOSTAT pour le rendement
faostat_yield = faostat_df[faostat_df['Element'] == 'Yield']

# Fusion par pays et culture
merged_df = faostat_yield.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')
merged_df = merged_df.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
merged_df = merged_df.merge(soil_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# Ajout des rendements réels si coordonnées disponibles
yield_df['lat'] = yield_df['lat'].round(2)
yield_df['lon'] = yield_df['lon'].round(2)
merged_df['lat'] = merged_df['Shape_Area'].round(2)  # à adapter selon source
merged_df['lon'] = merged_df['Shape_Leng'].round(2)
merged_df = merged_df.merge(yield_df, on=['lat', 'lon'], how='left')

# Nettoyage final
final_df = merged_df.dropna(subset=['Value'])  # garder les lignes avec rendement FAOSTAT

print("✅ Fusion terminée. Dimensions :", final_df.shape)
