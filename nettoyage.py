import dask.dataframe as dd
import pandas as pd
import os
import time

# 📁 Dossier des fichiers
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 📦 Liste des fichiers à charger
files = {
    "chirps": "CHIRPS_DAILY_PENTAD.csv",
    "nutrient_balance": "Cropland Nutrient BalanceFAOSTAT_data_en_8-8-2025.csv",
    "trade_matrix": "Detailed trade matrix (fertilizers)FAOSTAT_data_en_8-8-2025.csv",
    "fert_nutrient": "FertilizersbyNutrientFAOSTAT_data_en_8-8-2025.csv",
    "fert_product": "FertilizersbyProductFAOSTAT_data_en_7-22-2025.csv",
    "gedi": "GEDI_Mangrove_CSV.csv",
    "land_cover": "Land CoverFAOSTAT_data_en_8-8-2025.csv",
    "land_use": "Land UseFAOSTAT_data_en_8-8-2025.csv",
    "smap": "SMAP_SoilMoisture.csv",
    "production": "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv",
    "manure": "Livestock ManureFAOSTAT_data_en_8-8-2025.csv",
    "resources": "X_land_water_cleanedRessources en terres et en eau.csv"
}

# 🌍 Mapping pays
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

# 🧼 Nettoyage générique
def clean_dask_df(df, name, country_col='Area', year_col='Year'):
    df = df.rename(columns=lambda x: x.strip().replace(' ', '_'))
    print(f"📋 Colonnes dans {name} : {list(df.columns)}")
    if country_col in df.columns:
        df[country_col] = df[country_col].str.strip().map(country_mapping).fillna(df[country_col])
    if year_col in df.columns:
        df[year_col] = dd.to_numeric(df[year_col], errors='coerce')
    return df

# 📊 Chargement des fichiers
dataframes = {}
for key, filename in files.items():
    path = os.path.join(data_dir, filename)
    try:
        df = dd.read_csv(path, assume_missing=True)
        df_clean = clean_dask_df(df, key)
        dataframes[key] = df_clean
        print(f"✅ {key} chargé avec {df_clean.shape[0].compute():,} lignes")
    except Exception as e:
        print(f"❌ Erreur chargement {key} : {e}")

# 🔗 Fusion thématique
def fusion_progressive(dfs, name):
    print(f"\n🔗 Fusion progressive du bloc {name}...")
    total = len(dfs)
    fused = dfs[0]
    for i, df in enumerate(dfs[1:], start=2):
        fused = fused.merge(df, how="outer", on=["ADM0_NAME", "Year"])
        print(f"🔄 Progression fusion {name} : {int((i/total)*100)}%")
        time.sleep(0.2)
    return fused

df_climate = fusion_progressive([
    dataframes['chirps'],
    dataframes['smap'],
    dataframes['land_cover'],
    dataframes['land_use']
], "climat")

df_production = fusion_progressive([
    dataframes['production'],
    dataframes['manure']
], "production")

df_final = (
    df_climate
    .merge(df_production, on=["ADM0_NAME", "Year"], how="left")
    .merge(dataframes['gedi'], on=["ADM0_NAME"], how="left")
)

# 🧮 Conversion en pandas
print("\n🧮 Conversion en pandas pour entraînement...")
df_final_pd = df_final.compute()

# 💾 Sauvegarde compressée
output_path = os.path.join(data_dir, "dataset_rendement_prepared.csv.gz")
df_final_pd.to_csv(output_path, index=False, compression="gzip")
print(f"✅ Fichier sauvegardé : {output_path}")
