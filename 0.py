import dask.dataframe as dd

# 📁 Chemin vers les données
data_dir = r"C:\plateforme-agricole-complete-v2\SmartSènè"

def check_and_cast_columns(df, cols):
    """Vérifie la présence des colonnes, les crée si absentes, et convertit en string"""
    for col in cols:
        if col not in df.columns:
            print(f"⚠️ Colonne manquante ajoutée : {col}")
            df[col] = ""
        df[col] = df[col].astype("string")
    return df

print("📥 Chargement des fichiers avec Dask...")
soil_df = dd.read_csv(f"{data_dir}\\Soil_AllLayers_AllAfrica-002.csv", assume_missing=True)
bio_df = dd.read_csv(f"{data_dir}\\WorldClim BIO Variables V1.csv", assume_missing=True)
clim_df = dd.read_csv(f"{data_dir}\\WorldClim_Monthly_Fusion.csv", assume_missing=True)
faostat_crop_df = dd.read_csv(f"{data_dir}\\CropsandlivestockproductsFAOSTAT_data_en_7-22-2025.csv", assume_missing=True)
indicators_df = dd.read_csv(f"{data_dir}\\agriculture_indicators_africa.csv", assume_missing=True)
yield_df = dd.read_csv(f"{data_dir}\\X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv", assume_missing=True)

print("✅ Fichiers chargés.")

# Colonnes clés à vérifier
cols_adm = ["ADM0_NAME", "ADM1_NAME"]
cols_area = ["Area", "Year"]
cols_country = ["Country Name", "Year"]

print("🔍 Vérification et conversion des colonnes clés en string...")

# Soil, Bio, Clim doivent avoir ADM0_NAME et ADM1_NAME
soil_df = check_and_cast_columns(soil_df, cols_adm)
bio_df = check_and_cast_columns(bio_df, cols_adm)
clim_df = check_and_cast_columns(clim_df, cols_adm)

# FAOSTAT et Yield : 'Area', 'Year', 'Item' (pour FAOSTAT) à convertir aussi
faostat_crop_df["Area"] = faostat_crop_df["Area"].astype("string")
faostat_crop_df["Year"] = faostat_crop_df["Year"].astype("int64")
faostat_crop_df["Item"] = faostat_crop_df["Item"].astype("string")

# Conversion colonne 'Area' dans yield_df si elle existe
if "Area" in yield_df.columns:
    yield_df["Area"] = yield_df["Area"].astype("string")

# Indicators : 'Country Name', 'Year' en string et int
indicators_df["Country Name"] = indicators_df["Country Name"].astype("string")
indicators_df["Year"] = indicators_df["Year"].astype("int64")

print("✅ Colonnes clés converties.")

print("⏳ Forçage d'inférence des métadonnées avec .head() sur chaque dataframe...")
print("soil_df", soil_df.head(3))
print("bio_df", bio_df.head(3))
print("clim_df", clim_df.head(3))
print("faostat_crop_df", faostat_crop_df.head(3))
print("indicators_df", indicators_df.head(3))
print("yield_df", yield_df.head(3))

# Tu peux maintenant continuer ta logique fusion en Dask
# Exemple simple : fusion test entre faostat_crop_df et indicators_df sur Area/Country Name et Year

print("🔗 Test fusion FAOSTAT & indicateurs...")

test_merge = faostat_crop_df.merge(
    indicators_df,
    left_on=["Area", "Year"],
    right_on=["Country Name", "Year"],
    how="left"
)

print(test_merge.head(5))  # affiche les 5 premières lignes fusionnées

print("✅ Test fusion OK, tu peux maintenant procéder avec les autres merges en Dask.")

# --- Fin script de vérification et prépa Dask ---
