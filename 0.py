import pandas as pd

# Dossier des fichiers
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Liste des fichiers à vérifier avec les colonnes clés attendues pour fusion
files_info = {
    "soil_df": {
        "filename": f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv",
        "key_columns": ["ADM0_NAME", "ADM1_NAME", "ADM2_NAME"]  # Ajuste selon usage
    },
    "bio_df": {
        "filename": f"{data_dir}\\WorldClim BIO Variables V1.csv",
        "key_columns": ["ADM0_NAME", "ADM1_NAME"]
    },
    "clim_df": {
        "filename": f"{data_dir}\\WorldClim_Monthly_Fusion.csv",
        "key_columns": ["ADM0_NAME", "ADM1_NAME"]
    },
    "faostat_crop_df": {
        "filename": f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
        "key_columns": ["Area", "Year"]
    },
    "indicators_df": {
        "filename": f"{data_dir}\\agriculture_indicators_africa.csv",
        "key_columns": ["Country Name", "Year"]
    },
    "yield_df": {
        "filename": f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv",
        "key_columns": ["lon", "lat"]  # probablement pas de clé commune avec les autres
    }
}

# Chargement des DataFrames
dfs = {}
for name, info in files_info.items():
    print(f"Chargement de {name} depuis {info['filename']} ...")
    dfs[name] = pd.read_csv(info['filename'], nrows=5)  # charge juste 5 lignes pour rapidité
    print(f"Colonnes de {name} : {list(dfs[name].columns)}")
    print()

# Fonction pour tester la présence des colonnes clés entre deux DataFrames
def check_key_columns_compatibility(df1_name, df2_name, df1, df2, keys1, keys2):
    print(f"Vérification des colonnes clés entre {df1_name} et {df2_name}...")
    for k1, k2 in zip(keys1, keys2):
        in_df1 = k1 in df1.columns
        in_df2 = k2 in df2.columns
        status = "OK" if in_df1 and in_df2 else "MANQUANT"
        print(f" - Clé {k1} (df1) vs {k2} (df2) : {status}")
    print()

# Comparaison des colonnes clés entre paires importantes
pairs_to_check = [
    ("soil_df", "bio_df"),
    ("bio_df", "clim_df"),
    ("faostat_crop_df", "indicators_df"),
    ("indicators_df", "faostat_crop_df"),
    # Ajoute d'autres paires importantes pour ta fusion ici
]

for df1_name, df2_name in pairs_to_check:
    df1 = dfs[df1_name]
    df2 = dfs[df2_name]
    keys1 = files_info[df1_name]["key_columns"]
    keys2 = files_info[df2_name]["key_columns"]
    # Ajuster la longueur des clés à comparer pour éviter erreur zip si tailles différentes
    min_len = min(len(keys1), len(keys2))
    check_key_columns_compatibility(df1_name, df2_name, df1, df2, keys1[:min_len], keys2[:min_len])

print("Vérification terminée.")
