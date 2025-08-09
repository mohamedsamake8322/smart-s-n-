import pandas as pd
import dask.dataframe as dd
import os

# 📁 Dossier des fichiers
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"
output_path = os.path.join(data_dir, "dataset_rendement_pandas.csv.gz")

# 📛 Fichiers ignorés
ignored_files = []

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

# 📦 Liste des fichiers à charger
files = {
    "chirps": "CHIRPS_DAILY_PENTAD.csv",
    "smap": "SMAP_SoilMoisture.csv",
    "production": "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv",
    "gedi": "GEDI_Mangrove_CSV.csv",
    "resources": "X_land_water_cleanedRessources en terres et en eau.csv"
}

# 🧼 Nettoyage personnalisé
def clean_custom_df(df, name):
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = df.columns.str.strip().str.replace(r'\s+', '_', regex=True)

    rename_map = {
        "chirps": {"EXP1_YEAR": "Year"},
        "smap": {"EXP1_YEAR": "Year"},
        "production": {"Area": "ADM0_NAME"}
    }

    if name in rename_map:
        df = df.rename(columns=rename_map[name])

    if "ADM0_NAME" in df.columns:
        df["ADM0_NAME"] = df["ADM0_NAME"].map(country_mapping)

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    if "ADM0_NAME" not in df.columns or "Year" not in df.columns:
        ignored_files.append(name)
        print(f"⚠️ {name} ignoré pour fusion thématique")

    return df

# 📊 Chargement des fichiers
dataframes = {}
for key, filename in files.items():
    path = os.path.join(data_dir, filename)
    try:
        df = pd.read_csv(path, low_memory=False)
        df_clean = clean_custom_df(df, key)
        dataframes[key] = df_clean
        print(f"✅ {key} chargé avec {len(df_clean):,} lignes")
    except Exception as e:
        print(f"❌ Erreur chargement {key} : {e}")

# 🔗 Fusion thématique avec Pandas
df_base = dataframes.get("chirps")
df_smap = dataframes.get("smap")
df_production = dataframes.get("production")

if df_base is None or df_smap is None or df_production is None:
    raise ValueError("❌ Fichiers critiques manquants : chirps, smap ou production")

df_climat = df_base.merge(df_smap, on=["ADM0_NAME", "Year"], how="outer")
df_climat_prod = df_climat.merge(df_production, on=["ADM0_NAME", "Year"], how="outer")
print(f"🔗 Fusion climat + production → {df_climat_prod.shape}")

# 🔄 Conversion en Dask pour fusion latérale
dd_climat_prod = dd.from_pandas(df_climat_prod, npartitions=10)

# 🔗 Fusion latérale GEDI
if "gedi" in dataframes:
    df_gedi = dataframes["gedi"]
    dd_gedi = dd.from_pandas(df_gedi, npartitions=1)
    dd_climat_prod = dd_climat_prod.merge(dd_gedi, on="ADM0_NAME", how="left")
    print("🔗 Fusion GEDI réussie")

# 🔗 Fusion latérale resources (réduite)
if "resources" in dataframes:
    df_resources = dataframes["resources"]
    df_resources = df_resources.loc[:, ~df_resources.columns.duplicated()]
    df_resources_reduced = df_resources.groupby("ADM0_NAME").mean(numeric_only=True).reset_index()
    dd_resources = dd.from_pandas(df_resources_reduced, npartitions=1)
    dd_climat_prod = dd_climat_prod.merge(dd_resources, on="ADM0_NAME", how="left")
    print("🔗 Fusion resources réussie")

# 💾 Export compressé avec suivi
print(f"📦 Export compressé en cours vers : {output_path}")
dd_climat_prod.to_csv(output_path, single_file=True, index=False, compression="gzip")
print(f"✅ Export terminé : {output_path}")
