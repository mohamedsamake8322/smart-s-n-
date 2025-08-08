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
# 🧼 Nettoyage personnalisé
def clean_custom_df(df, name):
    df = df.loc[:, ~df.columns.duplicated()]
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    # 🎯 Renommage spécifique
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

    print(f"📊 Types dans {name} : {df.dtypes.to_dict()}")

    # 🌍 Harmonisation des pays
    if "ADM0_NAME" in df.columns:
        df["ADM0_NAME"] = df["ADM0_NAME"].map(country_mapping, meta=('ADM0_NAME', 'object'))


    # 📅 Conversion de l’année
    if "Year" in df.columns:
        try:
            df["Year"] = dd.to_numeric(df["Year"], errors="coerce")
        except AttributeError:
            df["Year"] = df["Year"].astype(float)

    # 📋 Log des colonnes
    print(f"📋 Colonnes dans {name} : {list(df.columns)}")

    # 📛 Vérification des clés
    if "ADM0_NAME" not in df.columns or "Year" not in df.columns:
        ignored_files.append(name)
        print(f"⚠️ {name} ignoré pour fusion thématique")

    return df

# 📊 Chargement des fichiers
dataframes = {}
for key, filename in files.items():
    path = os.path.join(data_dir, filename)
    try:
        forced_dtypes = {
            "Item_Code": "object",
            "Item_Code_(CPC)": "object",
            "Item Code (CPC)": "object",
            "Area_Code_(M49)": "object",
            "Reporter_Country_Code_(M49)": "object",
            "Partner_Country_Code_(M49)": "object"
        }

        df = dd.read_csv(path, assume_missing=True, dtype=forced_dtypes)
        df_clean = clean_custom_df(df, key)
        dataframes[key] = df_clean

        n_rows = df_clean.shape[0]
        n_rows = n_rows.compute() if hasattr(n_rows, "compute") else n_rows
        print(f"✅ {key} chargé avec {n_rows:,} lignes")

    except Exception as e:
        print(f"❌ Erreur chargement {key} : {e}")

# 📄 Rapport des colonnes
def generate_column_report(dataframes, output_path="rapport_colonnes.csv"):
    rows = []
    for name, df in dataframes.items():
        try:
            cols = df.columns
            types = df.dtypes
            fusionnable = "✅" if {"ADM0_NAME", "Year"}.issubset(cols) else "❌"
            for col in cols:
                rows.append({
                    "Fichier": name,
                    "Colonne": col,
                    "Type": str(types[col]),
                    "Fusionnable": fusionnable
                })
        except Exception as e:
            rows.append({
                "Fichier": name,
                "Colonne": "❌ Erreur",
                "Type": str(e),
                "Fusionnable": "❌"
            })

    df_report = pd.DataFrame(rows)
    df_report.to_csv(os.path.join(data_dir, output_path), index=False)
    print(f"\n📄 Rapport colonnes sauvegardé : {output_path}")

# 🔗 Fusion thématique
# 🔗 Fusion thématique progressive
def fusion_progressive(dfs, name, verbose=True):
    print(f"\n🔗 Fusion progressive du bloc {name}...")
    required_cols = {"ADM0_NAME", "Year"}
    dfs_valid = [df for df in dfs if required_cols.issubset(df.columns)]

    if not dfs_valid:
        print(f"⚠️ Aucun fichier valide pour le bloc {name}")
        return None

    fused = dfs_valid[0]
    total = len(dfs_valid)

    for i, df in enumerate(dfs_valid[1:], start=2):
        fused = fused.merge(df, how="outer", on=["ADM0_NAME", "Year"], suffixes=("", f"_{name}_{i}"))
        if verbose:
            print(f"🔄 Progression fusion {name} : {int((i / total) * 100)}%")
            time.sleep(0.2)

    return fused

# 🧩 Fusion par blocs
df_climate = fusion_progressive(
    [dataframes[k] for k in ['chirps', 'smap', 'land_cover', 'land_use'] if k in dataframes],
    "climat"
)

df_production = fusion_progressive(
    [dataframes[k] for k in ['production', 'manure', 'fert_nutrient', 'fert_product', 'nutrient_balance'] if k in dataframes],
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

    # 🧮 Conversion en pandas pour entraînement
    print("\n🧮 Conversion en pandas pour entraînement...")
    df_final_pd = df_final.persist().compute()

    # ✅ Log de confirmation
    n_rows, n_cols = df_final_pd.shape
    print(f"\n✅ Fusion finale réussie : {n_rows:,} lignes, {n_cols} colonnes")
    print(f"📋 Colonnes fusionnées (extrait) : {df_final_pd.columns.tolist()[:15]} ...")

    # 📉 Valeurs manquantes
    missing = df_final_pd.isna().sum().sort_values(ascending=False)
    missing_nonzero = missing[missing > 0]
    if not missing_nonzero.empty:
        print("\n📉 Valeurs manquantes par colonne :")
        print(missing_nonzero)
    else:
        print("\n✅ Aucune valeur manquante détectée.")

    # 💾 Sauvegarde du fichier final
    output_path = os.path.join(data_dir, "dataset_rendement_prepared.csv.gz")
    df_final_pd.to_csv(output_path, index=False, compression="gzip")
    print(f"\n✅ Fichier sauvegardé : {output_path}")
else:
    print("❌ Fusion finale impossible : blocs manquants.")

# 📁 Fichiers ignorés
if ignored_files:
    print(f"\n📁 Fichiers ignorés pour la fusion : {', '.join(ignored_files)}")
else:
    print("\n📁 Tous les fichiers ont été pris en compte dans la fusion.")
