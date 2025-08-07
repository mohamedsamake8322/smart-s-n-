# ━━━━━━━━━━━━ 📚 1. Import des bibliothèques ━━━━━━━━━━━━
import pandas as pd
import numpy as np
import os

# ━━━━━━━━━━━━ 📂 2. Définition du dossier local ━━━━━━━━━━━━
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# ━━━━━━━━━━━━ 📄 3. Chargement des fichiers ━━━━━━━━━━━━
ndmi = pd.read_csv(os.path.join(base_path, 'NDMI_Afrique_fusionné.csv'))
weather = pd.read_csv(os.path.join(base_path, 'WorldClim_Monthly_Fusion.csv'))
soil = pd.read_csv(os.path.join(base_path, 'Soil_AllLayers_AllAfrica-002.csv'))
culture = pd.read_csv(os.path.join(base_path, 'CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv'))
yield_data = pd.read_csv(os.path.join(base_path, "X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv"))

# ━━━━━━━━━━━━ 🧼 4. Nettoyage des colonnes ━━━━━━━━━━━━
def clean(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

ndmi = clean(ndmi)
weather = clean(weather)
soil = clean(soil)
culture = clean(culture)
yield_data = clean(yield_data)

# ━━━━━━━━━━━━ 🔗 5. Fusion des datasets ━━━━━━━━━━━━
# Fusion NDMI + météo
ndmi_weather = pd.merge(ndmi, weather, on=['adm0_name', 'adm1_name', 'adm2_name', 'year', 'month'], how='inner')

# Fusion avec sol
ndmi_weather_soil = pd.merge(ndmi_weather, soil, on=['adm0_name', 'adm1_name', 'adm2_name'], how='left')

# Fusion avec culture
ndmi_weather_soil_culture = pd.merge(ndmi_weather_soil, culture, on=['adm0_name', 'year'], how='left')

# Fusion avec rendement
final_dataset = pd.merge(ndmi_weather_soil_culture, yield_data, on=['adm0_name', 'adm1_name', 'adm2_name', 'year'], how='inner')

# ━━━━━━━━━━━━ 📤 6. Export du dataset final ━━━━━━━━━━━━
output_path = os.path.join(base_path, 'X_training_dataset_without_NDVI.csv')
final_dataset.to_csv(output_path, index=False)
print(f"✅ Dataset fusionné exporté : {output_path}")
