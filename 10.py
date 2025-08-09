import pandas as pd
import os
import gzip

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

# 🧼 Nettoyage personnalisé
def clean_custom_df(df, name):
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = df.columns.str.strip().str.replace(r'\s+', '_', regex=True)

    rename_map = {
        "chirps": {"EXP1_YEAR": "Year"},
        "smap": {"EXP1_YEAR": "Year"},
        "trade_matrix": {"Reporter_Countries": "ADM0_NAME"},
        "production": {"Area": "ADM0_NAME"},
        "manure": {"Area": "ADM0_NAME"},
        "land_use": {"Area": "ADM0_NAME"},
        "land_cover": {"Area": "ADM0_NAME"},
        "fert_nutrient": {"Area": "ADM0_NAME"},
        "fert_product": {"Area": "ADM0_NAME"},
        "nutrient_balance": {"Area": "ADM0_NAME"}
    }

    if name in rename_map:
        df = df.rename(columns=rename_map[name])
    elif name == "resources":
        print(f"⚠️ {name} n’a ni ADM0_NAME ni Year — fusion latérale uniquement")
    elif name == "gedi":
        print(f"⚠️ {name} n’a pas de colonne Year — fusion latérale uniquement")

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

# 🔗 Fusion thématique
df_base = dataframes.get("chirps")
df_smap = dataframes.get("smap")
df_production = dataframes.get("production")

if df_base is None or df_smap is None or df_production is None:
    raise ValueError("❌ Fichiers critiques manquants : chirps, smap ou production")

df_climat = df_base.merge(df_smap, on=["ADM0_NAME", "Year"], how="outer")
df_climat_prod = df_climat.merge(df_production, on=["ADM0_NAME", "Year"], how="outer")
print(f"🔗 Fusion climat + production → {df_climat_prod.shape}")

# 🔗 Fusion latérale GEDI
if "gedi" in dataframes:
    df_climat_prod = df_climat_prod.merge(dataframes["gedi"], on="ADM0_NAME", how="left")
    print(f"🔗 Fusion GEDI → {df_climat_prod.shape}")

# 🔗 Fusion latérale optimisée pour resources
if "resources" in dataframes:
    df_resources = dataframes["resources"]
    df_resources = df_resources.loc[:, ~df_resources.columns.duplicated()]
    df_resources_reduced = df_resources.groupby("ADM0_NAME").mean(numeric_only=True).reset_index()
    df_climat_prod = df_climat_prod.merge(df_resources_reduced, on="ADM0_NAME", how="left")
    print(f"🔗 Fusion resources (réduite) → {df_climat_prod.shape}")

# 🔗 Fusion finale avec les autres fichiers thématiques
for key, df in dataframes.items():
    if key not in ["chirps", "smap", "production", "gedi", "resources"] and key not in ignored_files:
        try:
            df_climat_prod = df_climat_prod.merge(df, on=["ADM0_NAME", "Year"], how="outer")
            print(f"🔗 Fusion {key} → {df_climat_prod.shape}")
        except Exception as e:
            print(f"❌ Erreur fusion {key} : {e}")

# 📐 Dimensions finales
n_rows = len(df_climat_prod)
print(f"📐 Dimensions du DataFrame final : {df_climat_prod.shape}")

# 💾 Sauvegarde compressée avec suivi de progression
print(f"📦 Export en cours vers : {output_path}")
chunk_size = 10000
with gzip.open(output_path, "wt", encoding="utf-8") as gzfile:
    for i in range(0, n_rows, chunk_size):
        chunk = df_climat_prod.iloc[i:i+chunk_size]
        header = (i == 0)
        chunk.to_csv(gzfile, index=False, header=header, mode="a")
        progress = min(100, int((i + chunk_size) / n_rows * 100))
        print(f"🔄 Progression export : {progress}%")

print(f"✅ Export terminé : {output_path}")
