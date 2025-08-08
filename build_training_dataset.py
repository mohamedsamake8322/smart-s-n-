import pandas as pd

data_dir = "C:\\ton\\chemin\\vers\\dossier"

files = {
    "SOIL": "Soil_AllLayers_AllAfrica-002.csv",
    "BIOCLIM": "WorldClim BIO Variables V1.csv",
    "CLIMAT MENSUEL": "WorldClim_Monthly_Fusion.csv",
    "FAOSTAT CULTURES": "CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv",
    "INDICATEURS AGRICOLES": "agriculture_indicators_africa.csv",
    "RENDEMENT RÉEL": "X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv"
}

for name, filename in files.items():
    print(f"\n📄 {name} — {filename}")
    df = pd.read_csv(f"{data_dir}\\{filename}")

    # Colonnes et types
    print("Colonnes :", list(df.columns))
    print("Types :", dict(df.dtypes))

    # Colonnes numériques
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    print("Colonnes numériques :", numeric_cols)

    # Deux premières lignes
    print(df.head(2))
