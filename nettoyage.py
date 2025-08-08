import dask.dataframe as dd
import pandas as pd
import xgboost as xgb
import shap

# 🌍 Mapping pays (à adapter selon ton contexte)
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

# 🧼 Fonction de nettoyage
def clean_dask_df(df, country_col='Area', year_col='Year'):
    df = df.rename(columns=lambda x: x.strip().replace(' ', '_'))
    if country_col in df.columns:
        df[country_col] = df[country_col].str.strip().map(country_mapping).fillna(df[country_col])
    if year_col in df.columns:
        df[year_col] = dd.to_numeric(df[year_col], errors='coerce')
    return df

# 📁 Chargement des fichiers
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

# 📊 Chargement et nettoyage
dataframes = {}
for key, path in files.items():
    try:
        df = dd.read_csv(path, assume_missing=True)
        df_clean = clean_dask_df(df)
        dataframes[key] = df_clean
        print(f"✅ {key} loaded with shape {df_clean.shape}")
    except Exception as e:
        print(f"❌ Error loading {key}: {e}")

# 🔗 Fusions thématiques
df_climate = (
    dataframes['chirps']
    .merge(dataframes['smap'], on=['ADM0_NAME', 'Year'], how='outer')
    .merge(dataframes['land_cover'], on=['ADM0_NAME', 'Year'], how='outer')
    .merge(dataframes['land_use'], on=['ADM0_NAME', 'Year'], how='outer')
)

df_fertilization = (
    dataframes['fert_product']
    .merge(dataframes['fert_nutrient'], on=['Area', 'Item', 'Year'], how='outer')
    .merge(dataframes['trade_matrix'], on=['Area', 'Item', 'Year'], how='outer')
    .merge(dataframes['nutrient_balance'], on=['Area', 'Item', 'Year'], how='outer')
)

df_production = (
    dataframes['production']
    .merge(dataframes['manure'], on=['Area', 'Item', 'Year'], how='outer')
)

df_resources = dataframes['resources']
df_gedi = dataframes['gedi']

# 🧠 Fusion finale pour prédiction de rendement
df_final = (
    df_climate
    .merge(df_production, on=['ADM0_NAME', 'Year'], how='left')
    .merge(df_gedi, on=['ADM0_NAME'], how='left')
)

# 🧮 Conversion en pandas
df_final_pd = df_final.compute()
df_fertilization_pd = df_fertilization.compute()

# 🧪 Entraînement XGBoost
X = df_final_pd.drop(columns=["Yield_t_ha"], errors='ignore')
y = df_final_pd["Yield_t_ha"]
model = xgb.XGBRegressor()
model.fit(X, y)

# 📈 SHAP
explainer = shap.Explainer(model)
shap_values = explainer(X)
shap.plots.beeswarm(shap_values)

# 💾 Sauvegarde
df_final_pd.to_csv("dataset_rendement_prepared.csv", index=False)
df_fertilization_pd.to_csv("dataset_fertilisation_prepared.csv", index=False)
