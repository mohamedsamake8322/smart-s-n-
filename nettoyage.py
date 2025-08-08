import os
import time
import pandas as pd
import dask.dataframe as dd
from tabulate import tabulate

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
ignored_files = []
log_info = []

def clean_dask_df(df, name):
    """Nettoyage et harmonisation d'un DataFrame Dask avec logs détaillés"""

    # 🔍 Log avant nettoyage
    cols_before = list(df.columns)
    rows_before = df.shape[0].compute()
    log_entry = {
        "Fichier": name,
        "Colonnes_initiales": cols_before,
        "Lignes_initiales": rows_before,
        "Colonnes_manquantes": [],
        "Statut": "OK"
    }

    # 🔁 Supprimer les colonnes dupliquées
    df = df.loc[:, ~df.columns.duplicated()]

    # 🧹 Nettoyage noms colonnes
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    # 📛 Renommage
    rename_map = {
        'Year_Code': 'Year',
        'Area': 'ADM0_NAME',
        'Area_Code_(M49)': 'ADM0_CODE'
    }
    df = df.rename(columns={col: rename_map.get(col, col) for col in df.columns})

    # 🌍 Harmonisation noms de pays
    if 'ADM0_NAME' in df.columns:
        df['ADM0_NAME'] = df['ADM0_NAME'].astype(str).str.strip().apply(
            lambda x: country_mapping.get(x, x),
            meta=('ADM0_NAME', 'object')
        )

    # 🔢 Conversion année
    if 'Year' in df.columns:
        df['Year'] = dd.to_numeric(df['Year'], errors='coerce')

    # 📌 Vérif colonnes clés
    required_cols = {'ADM0_NAME', 'Year'}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        log_entry["Colonnes_manquantes"] = list(missing_cols)
        log_entry["Statut"] = "Ignoré"
        ignored_files.append(name)

    log_info.append(log_entry)
    return df


def fusion_progressive(dfs, name):
    """Fusion sécurisée des DataFrames avec logs"""
    print(f"\n🔗 Fusion progressive du bloc {name}...")
    required_cols = {"ADM0_NAME", "Year"}

    dfs_valid = [df for df in dfs if required_cols.issubset(df.columns)]
    if not dfs_valid:
        print(f"⚠️ Aucun fichier valide pour le bloc {name}")
        return None

    fused = dfs_valid[0]
    print(f"   ➡️ Départ : {fused.shape[0].compute():,} lignes / {len(fused.columns)} colonnes")
    total = len(dfs_valid)

    for i, df in enumerate(dfs_valid[1:], start=2):
        before_rows = fused.shape[0].compute()
        fused = fused.merge(df, how="outer", on=["ADM0_NAME", "Year"])
        after_rows = fused.shape[0].compute()
        print(f"   🔄 Fusion {i}/{total} : {before_rows:,} ➡ {after_rows:,} lignes")
        time.sleep(0.2)

    print(f"   ✅ Bloc {name} final : {fused.shape[0].compute():,} lignes / {len(fused.columns)} colonnes")
    return fused


# 📊 Chargement des fichiers
dataframes = {}
for key, filename in files.items():
    path = os.path.join(data_dir, filename)
    try:
        df = dd.read_csv(path, dtype={'Item_Code_(CPC)': 'object'}, assume_missing=True)
        df_clean = clean_dask_df(df, key)
        dataframes[key] = df_clean
        print(f"✅ {key} chargé ({df_clean.shape[0].compute():,} lignes)")
    except Exception as e:
        print(f"❌ Erreur chargement {key} : {e}")


# 🧩 Fusions par blocs
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

    print("\n🧮 Conversion en pandas...")
    df_final_pd = df_final.compute()

    print(f"\n🧬 Colonnes finales : {list(df_final_pd.columns)}")
    print("\n📉 Valeurs manquantes par colonne :")
    print(df_final_pd.isna().sum().sort_values(ascending=False))

    output_path = os.path.join(data_dir, "dataset_rendement_prepared.csv.gz")
    df_final_pd.to_csv(output_path, index=False, compression="gzip")
    print(f"\n✅ Fichier sauvegardé : {output_path}")
else:
    print("❌ Fusion finale impossible : blocs manquants.")


# 📋 Rapport final
print("\n📋 Rapport fichiers :")
rapport_df = pd.DataFrame(log_info)
print(tabulate(rapport_df, headers="keys", tablefmt="pretty", showindex=False))

if ignored_files:
    print(f"\n📁 Fichiers ignorés : {', '.join(ignored_files)}")
