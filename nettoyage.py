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

# 🧼 Nettoyage générique et robuste
# 📂 Liste des fichiers ignorés
ignored_files = []

def clean_dask_df(df, name):
    # 🔁 Supprimer les colonnes dupliquées par nom
    df = df.loc[:, ~df.columns.duplicated()]

    # Nettoyage des noms de colonnes
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    # Renommage intelligent
    df = df.rename(columns={
        'Year': 'Year',
        'Area': 'ADM0_NAME',
        'Area_Code_(M49)': 'ADM0_CODE',
        'Year_Code': 'Year_Code'  # conservé si utile, mais ignoré pour la fusion
    })

    print(f"📋 Colonnes dans {name} : {list(df.columns)}")

    # Harmonisation des noms de pays
    if 'ADM0_NAME' in df.columns:
        df['ADM0_NAME'] = df['ADM0_NAME'].str.strip().apply(lambda x: country_mapping.get(x, x), meta=('ADM0_NAME', 'object'))

    # Conversion de l'année en numérique
    if 'Year' in df.columns:
        df['Year'] = dd.to_numeric(df['Year'], errors='coerce')

    # Vérification des colonnes clés
    if 'ADM0_NAME' not in df.columns or 'Year' not in df.columns:
        print(f"⚠️ {name} ne contient pas ADM0_NAME ou Year — il sera ignoré pour la fusion.")
        ignored_files.append(name)

    return df



# 📊 Chargement des fichiers
dataframes = {}
for key, filename in files.items():
    path = os.path.join(data_dir, filename)
    try:
        df = dd.read_csv(path, dtype={'Item_Code_(CPC)': 'object'}, assume_missing=True)
        df_clean = clean_dask_df(df, key)
        dataframes[key] = df_clean
        print(f"✅ {key} chargé avec {df_clean.shape[0].compute():,} lignes")
    except Exception as e:
        print(f"❌ Erreur chargement {key} : {e}")


def fusion_progressive(dfs, name):
    """Fusion sécurisée des DataFrames par thème"""
    print(f"\n🔗 Fusion progressive du bloc {name}...")
    required_cols = {"ADM0_NAME", "Year"}

    # Garder uniquement les DF ayant les colonnes nécessaires
    dfs_valid = [df for df in dfs if required_cols.issubset(df.columns)]
    if not dfs_valid:
        print(f"⚠️ Aucun fichier valide pour le bloc {name}")
        return None

    fused = dfs_valid[0]
    total = len(dfs_valid)

    for i, df in enumerate(dfs_valid[1:], start=2):
        fused = fused.merge(df, how="outer", on=["ADM0_NAME", "Year"])
        print(f"🔄 Progression fusion {name} : {int((i/total)*100)}%")
        time.sleep(0.2)

    return fused


# 🧩 Fusion par blocs
df_climate = fusion_progressive(
    [dataframes[k] for k in ['chirps', 'smap', 'land_cover', 'land_use'] if k in dataframes],
    "climat"
)

df_production = fusion_progressive(
    [dataframes[k] for k in ['production', 'manure'] if k in dataframes],
    "production"
)

# 🧬 Fusion finale
if df_climate is not None and df_production is not None:
    df_final = (
        df_climate
        .merge(df_production, on=["ADM0_NAME", "Year"], how="left")
        .merge(
            dataframes.get('gedi', dd.from_pandas(pd.DataFrame(), npartitions=1)),
            on=["ADM0_NAME"], how="left"
        )
    )

    # 🧮 Conversion en Pandas
    print("\n🧮 Conversion en pandas pour entraînement...")
    df_final_pd = df_final.compute()

    # 📊 Rapport final
    print(f"\n🧬 Colonnes finales : {list(df_final_pd.columns)}")
    print("\n📉 Valeurs manquantes par colonne :")
    print(df_final_pd.isna().sum().sort_values(ascending=False))

    # 💾 Sauvegarde
    output_path = os.path.join(data_dir, "dataset_rendement_prepared.csv.gz")
    df_final_pd.to_csv(output_path, index=False, compression="gzip")
    print(f"\n✅ Fichier sauvegardé : {output_path}")
else:
    print("❌ Fusion finale impossible : blocs manquants.")

# 📁 Fichiers ignorés
if ignored_files:
    print(f"\n📁 Fichiers ignorés pour la fusion : {', '.join(ignored_files)}")
