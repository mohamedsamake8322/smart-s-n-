# ━━━━━━━━━━━━ 📚 1. Import des bibliothèques ━━━━━━━━━━━━
import pandas as pd
import numpy as np
import os

# ━━━━━━━━━━━━ 📂 2. Définition du dossier local ━━━━━━━━━━━━
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# ━━━━━━━━━━━━ 📄 3. Chargement + nettoyage des fichiers ━━━━━━━━━━━━
def load_and_clean_csv(file_name):
    path = os.path.join(base_path, file_name)
    if not os.path.exists(path):
        print(f"❌ Fichier non trouvé : {path}")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    print(f"✅ Fichier chargé : {file_name} | Colonnes : {len(df.columns)}")
    return df

ndmi = load_and_clean_csv('NDMI_Afrique_fusionné.csv')
weather = load_and_clean_csv('WorldClim_Monthly_Fusion.csv')
soil = load_and_clean_csv('Soil_AllLayers_AllAfrica-002.csv')
culture = load_and_clean_csv('CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv')
yield_data = load_and_clean_csv("X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")

# ━━━━━━━━━━━━ 📊 4. Affichage des colonnes ━━━━━━━━━━━━
print("\n📋 Liste des colonnes par dataset :")
datasets = {'NDMI': ndmi, 'Weather': weather, 'Soil': soil, 'Culture': culture, 'Yield': yield_data}
for name, df in datasets.items():
    print(f"  - {name}: {df.columns.tolist()}")

# ━━━━━━━━━━━━ 🔧 5. Fonction de fusion avec colonnes communes ━━━━━━━━━━━━
def smart_merge(df1, df2, how='inner', label=''):
    common_cols = list(set(df1.columns) & set(df2.columns))
    if not common_cols:
        print(f"⚠️ Aucune colonne commune pour fusion avec {label} !")
        return df1
    print(f"\n🔗 Fusion avec {label} sur colonnes : {common_cols}")
    merged = pd.merge(df1, df2, on=common_cols, how=how)
    # Vérifier les doublons
    if merged.duplicated().any():
        nb_duplicates = merged.duplicated().sum()
        print(f"⚠️ {nb_duplicates} doublons détectés dans la fusion avec {label}")
    else:
        print(f"✅ Aucun doublon détecté dans la fusion avec {label}")
    return merged

# ━━━━━━━━━━━━ 🔗 6. Fusions successives ━━━━━━━━━━━━
ndmi_weather = smart_merge(ndmi, weather, how='inner', label='météo')
ndmi_weather_soil = smart_merge(ndmi_weather, soil, how='left', label='sol')
ndmi_weather_soil_culture = smart_merge(ndmi_weather_soil, culture, how='left', label='culture')
final_dataset = smart_merge(ndmi_weather_soil_culture, yield_data, how='inner', label='rendement')

# ━━━━━━━━━━━━ 🧼 7. Vérification finale ━━━━━━━━━━━━
print("\n📌 Vérification finale du dataset fusionné :")
print(f"🧾 Forme : {final_dataset.shape[0]} lignes × {final_dataset.shape[1]} colonnes")
missing = final_dataset.isnull().sum()
missing_cols = missing[missing > 0]
if not missing_cols.empty:
    print("⚠️ Colonnes avec valeurs manquantes :")
    print(missing_cols)
else:
    print("✅ Aucune valeur manquante détectée.")

# ━━━━━━━━━━━━ 📤 8. Export du dataset final ━━━━━━━━━━━━
output_path = os.path.join(base_path, 'X_training_dataset_without_NDVI.csv')
final_dataset.to_csv(output_path, index=False)
print(f"\n✅ Dataset fusionné exporté avec succès : {output_path}")
