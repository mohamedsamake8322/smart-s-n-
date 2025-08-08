import dask.dataframe as dd
from dask.diagnostics import ProgressBar

# 📁 Dossier des données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Colonnes essentielles pour chaque dataset
faostat_cols = ['Area', 'Item', 'Year', 'Element', 'Value']
indicators_cols = [
    'Country Name', 'Year',
    'Fertilizer consumption (kilograms per hectare of arable land)',
    'Agricultural land (% of land area)'
]
bioclim_cols = ['ADM0_NAME'] + [f'bio{i:02d}' for i in range(1, 20)]
clim_cols = ['ADM0_NAME', 'ADM1_NAME', 'prec', 'tavg', 'tmax', 'tmin']
soil_cols = ['ADM0_NAME', 'ADM1_NAME', 'mean', 'min', 'max', 'stdDev']

print("📥 Chargement des fichiers avec colonnes ciblées et types explicites...")

faostat_crop_df = dd.read_csv(
    f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    usecols=faostat_cols,
    dtype={
        'Area': 'string', 'Item': 'string', 'Year': 'int64',
        'Element': 'string', 'Value': 'float64'
    }
)

indicators_df = dd.read_csv(
    f"{data_dir}\\agriculture_indicators_africa.csv",
    usecols=indicators_cols,
    dtype={
        'Country Name': 'string', 'Year': 'int64',
        'Fertilizer consumption (kilograms per hectare of arable land)': 'float64',
        'Agricultural land (% of land area)': 'float64'
    }
)

bio_df = dd.read_csv(
    f"{data_dir}\\WorldClim BIO Variables V1.csv",
    usecols=bioclim_cols,
    dtype={**{'ADM0_NAME': 'string'}, **{f'bio{i:02d}': 'float64' for i in range(1, 20)}}
)

clim_df = dd.read_csv(
    f"{data_dir}\\WorldClim_Monthly_Fusion.csv",
    usecols=clim_cols,
    dtype={
        'ADM0_NAME': 'string', 'ADM1_NAME': 'string',
        'prec': 'float64', 'tavg': 'float64', 'tmax': 'float64', 'tmin': 'float64'
    }
)

soil_df = dd.read_csv(
    f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv",
    usecols=soil_cols,
    dtype={
        'ADM0_NAME': 'string', 'ADM1_NAME': 'string',
        'mean': 'float64', 'min': 'float64', 'max': 'float64', 'stdDev': 'float64'
    }
)

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
print(f"✅ Rendements reconstruits : {merged_yield_df.shape}")

# 🔗 Fusion avec indicateurs agricoles
print("🔗 Fusion avec indicateurs agricoles...")
merged = merged_yield_df.merge(
    indicators_df,
    left_on=['Area', 'Year'],
    right_on=['Country Name', 'Year'],
    how='left'
)
print(f"✅ Après fusion indicateurs : {merged.shape}")

# 🔗 Fusion avec Bioclim
print("🔗 Fusion avec Bioclim...")
merged = merged.merge(bio_df, left_on='Area', right_on='ADM0_NAME', how='left')
print(f"✅ Après fusion Bioclim : {merged.shape}")

# 🔗 Fusion avec climat mensuel
print("🔗 Fusion avec climat mensuel...")
merged = merged.merge(clim_df, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
print(f"✅ Après fusion climat mensuel : {merged.shape}")

# 📊 Agrégation des données de sol
print("📊 Agrégation des données de sol...")
soil_agg = soil_df.groupby(['ADM0_NAME', 'ADM1_NAME']).agg({
    'mean': 'mean',
    'min': 'mean',
    'max': 'mean',
    'stdDev': 'mean'
}).reset_index()
print(f"✅ Sol agrégé : {soil_agg.shape}")

# 🔗 Fusion avec données de sol agrégées
print("🔗 Fusion avec données de sol agrégées...")
merged = merged.merge(soil_agg, on=['ADM0_NAME', 'ADM1_NAME'], how='left')
print(f"✅ Après fusion sol : {merged.shape}")

# 🧹 Nettoyage final : suppression des lignes sans rendement
final_df = merged.dropna(subset=['Yield_t_ha'])
print(f"🧹 Après suppression lignes sans rendement : {final_df.shape}")

# 💾 Sauvegarde partitionnée (plusieurs fichiers CSV compressés)
print("💾 Sauvegarde en plusieurs fichiers CSV compressés...")
with ProgressBar():
    final_df.to_csv(
        f"{data_dir}\\Fusion_agronomique_intelligente_*.csv.gz",
        index=False,
        compression='gzip'
    )

print("📁 Sauvegarde terminée.")
