import pandas as pd
import numpy as np
import os
from glob import glob

# 📁 Dossiers
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_folder = r"C:\plateforme-agricole-complete-v2\weather_final"
boua_folder = r"C:\plateforme-agricole-complete-v2\Boua"

# 1️⃣ Chargement du sol + clé de fusion latlon corrigée
soil_df = pd.read_csv(soil_path)
soil_df["Latitude"] = soil_df["y"]
soil_df["Longitude"] = soil_df["x"]
soil_df["latlon"] = soil_df["Latitude"].round(4).astype(str) + "_" + soil_df["Longitude"].round(4).astype(str)

# 2️⃣ Météo nettoyée
weather_files = [f for f in glob(os.path.join(weather_folder, "*.csv")) if "report" not in os.path.basename(f).lower()]
weather_list = []

for file in weather_files:
    try:
        df = pd.read_csv(file, low_memory=False)

        keep_cols = [c for c in df.columns if (
            "PRECTOT" in c or "WS2M" in c or "PS" in c or "IMERG" in c or
            c in ["Country", "Latitude", "Longitude", "DATE"]
        )]
        df = df[keep_cols]

        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"].astype(str).str.replace(".csv", "", regex=False), errors="coerce")
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df["year"] = df["DATE"].dt.year
        df["latlon"] = df["Latitude"].round(4).astype(str) + "_" + df["Longitude"].round(4).astype(str)
        weather_list.append(df)
    except Exception as e:
        print(f"⛔ Erreur lecture {os.path.basename(file)} : {e}")

print(f"✅ Fichiers météo retenus : {len(weather_list)}")
weather_df = pd.concat(weather_list, ignore_index=True)

weather_df["Country"] = weather_df["Country"].str.strip().str.title()
soil_df["latlon"] = soil_df["latlon"].str.strip()

weather_soil_df = pd.merge(weather_df, soil_df, on="latlon", how="inner")
print(f"📦 Fusion météo + sol : {weather_soil_df.shape[0]} lignes")

# 3️⃣ Engrais NPK
fert_nutrient = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv"))
fert_nutrient["Year"] = pd.to_numeric(fert_nutrient["Year"], errors="coerce")
fert_nutrient["Area"] = fert_nutrient["Area"].str.strip().str.title()
fert_nutrient = fert_nutrient.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
fert_nutrient = fert_nutrient.rename(columns={"Value": "Fertilizer_NPK_tonnes"})

merged_df = pd.merge(weather_soil_df, fert_nutrient, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 4️⃣ Fumier
manure_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv"))
manure_df["Year"] = pd.to_numeric(manure_df["Year"], errors="coerce")
manure_df["Area"] = manure_df["Area"].str.strip().str.title()
manure_agg = manure_df.groupby(["Area", "Year"])["Value"].sum().reset_index()
manure_agg = manure_agg.rename(columns={"Value": "Manure_N_total_kg"})

merged_df = pd.merge(merged_df, manure_agg, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 5️⃣ Pesticides
pest_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv"))
pest_df["Year"] = pd.to_numeric(pest_df["Year"], errors="coerce")
pest_df["Area"] = pest_df["Area"].str.strip().str.title()
pest_agg = pest_df.groupby(["Area", "Year", "Element"])["Value"].sum().reset_index()
pest_pivot = pest_agg.pivot_table(index=["Area", "Year"], columns="Element", values="Value").reset_index()

merged_df = pd.merge(merged_df, pest_pivot, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 6️⃣ Engrais par produit
fert_prod = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"))
fert_prod["Year"] = pd.to_numeric(fert_prod["Year"], errors="coerce")
fert_prod["Area"] = fert_prod["Area"].str.strip().str.title()
prod_agg = fert_prod.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
prod_pivot = prod_agg.pivot_table(index=["Area", "Year"], columns="Item", values="Value").reset_index()

merged_df = merged_df.drop(columns=["Area", "Year"], errors="ignore")
merged_df = pd.merge(merged_df, prod_pivot, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 7️⃣ Rendements agricoles
crop_file = os.path.join(boua_folder, "Production_Crops_Livestock_Afrique.csv")
crop_prod = pd.read_csv(crop_file, sep=",", quotechar='"', engine="python", header=None)

expected_cols = [
    "AreaCode", "M49Code", "Country", "ItemCode", "CropName",
    "ElementCode", "Element", "YearCode", "Year", "Unit",
    "Value", "Flag", "FlagDescription"
]

if crop_prod.shape[1] == len(expected_cols):
    crop_prod.columns = expected_cols
elif crop_prod.shape[1] == len(expected_cols) + 1:
    crop_prod.columns = expected_cols + ["Extra"]
    crop_prod = crop_prod.drop(columns=["Extra"], errors="ignore")
else:
    raise ValueError(f"⚠️ Format inattendu : {crop_prod.shape[1]} colonnes détectées")

crop_prod["Country"] = crop_prod["Country"].str.strip().str.title()
crop_prod["Year"] = pd.to_numeric(crop_prod["Year"], errors="coerce")
crop_prod = crop_prod[crop_prod["Element"] == "Area harvested"]

crop_prod = crop_prod.groupby(["Country", "Year", "CropName"])["Value"].sum().reset_index()
crop_prod = crop_prod.rename(columns={"Value": "Harvested_Area_ha"})

final_df = pd.merge(merged_df, crop_prod, on=["Country", "Year"], how="left")
print(f"✅ Dataset final prêt : {final_df.shape[0]} lignes, {final_df.shape[1]} colonnes")

# 💾 Sauvegarde
output_path = r"C:\plateforme-agricole-complete-v2\dataset_prediction_rendement.csv"
final_df.to_csv(output_path, index=False)
print(f"📁 Sauvegardé ici : {output_path}")
