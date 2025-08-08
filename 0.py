import dask.dataframe as dd

# 📁 Chemin vers les données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

def check_and_cast_columns(df, cols):
    """Vérifie la présence des colonnes, les crée si absentes, et convertit en string"""
    for col in cols:
        if col not in df.columns:
            print(f"⚠️ Colonne manquante ajoutée : {col}")
            # Créer une colonne vide en string
            df[col] = ""
        # Conversion forcée en string via map_partitions (pour Dask)
        df = df.map_partitions(lambda pdf: pdf.assign(**{col: pdf[col].astype("string")}))
    return df

print("📥 Chargement des fichiers avec Dask...")

soil_dtype = {
    "ADM1_NAME": "object",
    "ADM2_NAME": "object",
    "DISP_AREA": "object",
    "STATUS": "object",
}
bio_dtype = {
    "ADM0_NAME": "object",
    "ADM1_NAME": "object",
}
clim_dtype = {
    "ADM0_NAME": "object",
    "ADM1_NAME": "object",
}

soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", assume_missing=True, dtype=soil_dtype)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", assume_missing=True, dtype=bio_dtype)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", assume_missing=True, dtype=clim_dtype)
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv", assume_missing=True)
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", assume_missing=True)
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv", assume_missing=True)

print("✅ Fichiers chargés.")

# Colonnes clés à vérifier
cols_adm = ["ADM0_NAME", "ADM1_NAME"]

print("🔍 Vérification et conversion des colonnes clés en string...")

soil_df = check_and_cast_columns(soil_df, cols_adm)
bio_df = check_and_cast_columns(bio_df, cols_adm)
clim_df = check_and_cast_columns(clim_df, cols_adm)

# FAOSTAT colonnes clés : convertir avec map_partitions
faostat_crop_df = faostat_crop_df.map_partitions(
    lambda pdf: pdf.assign(
        Area=pdf["Area"].astype("string"),
        Year=pdf["Year"].astype("int64"),
        Item=pdf["Item"].astype("string"),
    )
)

if "Area" in yield_df.columns:
    yield_df = yield_df.map_partitions(lambda pdf: pdf.assign(Area=pdf["Area"].astype("string")))

indicators_df = indicators_df.map_partitions(
    lambda pdf: pdf.assign(
        **{
            "Country Name": pdf["Country Name"].astype("string"),
            "Year": pdf["Year"].astype("int64"),
        }
    )
)

print("✅ Colonnes clés converties.")

print("⏳ Forçage d'inférence des métadonnées avec .head() sur chaque dataframe...")

print("soil_df\n", soil_df.head(3))
print("bio_df\n", bio_df.head(3))
print("clim_df\n", clim_df.head(3))
print("faostat_crop_df\n", faostat_crop_df.head(3))
print("indicators_df\n", indicators_df.head(3))
print("yield_df\n", yield_df.head(3))

print("🔗 Test fusion FAOSTAT & indicateurs...")

test_merge = faostat_crop_df.merge(
    indicators_df,
    left_on=["Area", "Year"],
    right_on=["Country Name", "Year"],
    how="left"
)

print(test_merge.head(5))  # affiche les 5 premières lignes fusionnées

print("✅ Test fusion OK, tu peux maintenant procéder avec les autres merges en Dask.")
