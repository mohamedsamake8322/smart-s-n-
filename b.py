import pandas as pd
import os

data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_file = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")

spei = pd.read_csv(spei_file)
modis = pd.read_csv(modis_file)

# Normaliser les colonnes
spei.columns = spei.columns.str.lower()
modis.columns = modis.columns.str.lower()

# Id uniques
spei_ids = spei['adm2_id'].unique()
modis_ids = modis['adm2_id'].unique()

# Créer un dataframe pour le mapping
mapping_df = pd.DataFrame({'spei_id': spei_ids})

# Tenter un mapping via les noms si disponible
if 'adm2_name' in modis.columns:
    modis_map = modis[['adm2_id', 'adm2_name']].drop_duplicates().set_index('adm2_id')['adm2_name']
    mapping_df['modis_name'] = mapping_df['spei_id'].map(modis_map)

# Pour les ids non trouvés, garder l'id comme fallback
mapping_df['modis_id'] = mapping_df['spei_id']
mapping_df['modis_name'] = mapping_df['modis_name'].fillna(mapping_df['spei_id'])

# Sauvegarde
out_file = os.path.join(data_path, "spei_to_modis_mapping.csv")
mapping_df.to_csv(out_file, index=False)
print(f"[SAVED] {out_file} ({len(mapping_df)} lignes)")
