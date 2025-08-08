import os
import pandas as pd
import gzip

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"
output_dir = os.path.join(data_dir, "Fusion_segmentée")
os.makedirs(output_dir, exist_ok=True)

# 📥 Chargement des fichiers
print("📥 Chargement des fichiers...")
soil_df = pd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv")
bio_df = pd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv")
clim_df = pd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv")
faostat_crop_df = pd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv")
indicators_df = pd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv")
yield_df = pd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

# 🧮 Reconstruction des rendements FAOSTAT
area_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Area harvested", case=False)].copy()
prod_df = faostat_crop_df[faostat_crop_df['Element'].str.contains("Production", case=False)].copy()
merged_yield_df = pd.merge(area_df, prod_df, on=['Area', 'Item', 'Year'], suffixes=('_area', '_prod'), how='inner')
merged_yield_df['Yield_t_ha'] = merged_yield_df['Value_prod'] / merged_yield_df['Value_area']

# 🔄 Harmonisation des noms de pays
country_mapping = { ... }  # (reprend ton dictionnaire complet ici)
merged_yield_df['Area'] = merged_yield_df['Area'].replace(country_mapping)
indicators_df['Country Name'] = indicators_df['Country Name'].replace(country_mapping)

# 🔗 Fusion avec les indicateurs agricoles
merged_yield_df = merged_yield_df.merge(indicators_df, left_on=['Area', 'Year'], right_on=['Country Name', 'Year'], how='left')

# 🔗 Fusion FAOSTAT + BIOCLIM + CLIMAT MENSUEL
step1_df = merged_yield_df.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')
step2_df = step1_df.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# 📊 Agrégation des données de sol
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'mean': 'mean', 'min': 'mean', 'max': 'mean', 'stdDev': 'mean'
}).reset_index()
step3_df = step2_df.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')

# 🧹 Nettoyage final
final_df = step3_df.dropna(subset=['Yield_t_ha'])

# 🧼 Suppression des colonnes inutiles
cols_to_drop = [col for col in final_df.columns if 'system:index' in col or '.geo' in col or 'Flag' in col or 'Note' in col]
final_df.drop(columns=cols_to_drop, inplace=True)

# 💾 Sauvegarde principale compressée
main_file = os.path.join(data_dir, "Fusion_agronomique_intelligente.csv.gz")
final_df.to_csv(main_file, index=False, compression='gzip')
print(f"✅ Fichier principal sauvegardé : {main_file}")

# 📂 Segmentation par culture
print("📂 Segmentation par culture...")
summary = []
for crop in final_df['Item'].dropna().unique():
    subset = final_df[final_df['Item'] == crop]
    file_name = f"{crop.replace(' ', '_')}.csv.gz"
    file_path = os.path.join(output_dir, file_name)
    subset.to_csv(file_path, index=False, compression='gzip')
    summary.append({'Culture': crop, 'Lignes': len(subset), 'Fichier': file_name})

# 📊 Sauvegarde du résumé
summary_df = pd.DataFrame(summary)
summary_df.to_csv(os.path.join(output_dir, "Résumé_segmentations.csv"), index=False)
print("📁 Résumé des segmentations sauvegardé.")
