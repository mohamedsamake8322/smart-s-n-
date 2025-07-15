import pandas as pd
import numpy as np
from glob import glob
import os

# 📁 Dossiers source
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_folder = r"C:\plateforme-agricole-complete-v2\weather_by_country"
boua_folder = r"C:\plateforme-agricole-complete-v2\Boua"

# 1️⃣ Sol
soil_df = pd.read_csv(soil_path)
soil_df["latlon"] = soil_df["y"].round(4).astype(str) + "_" + soil_df["x"].round(4).astype(str)

# 2️⃣ Météo — Lecture filtrée et normalisation
weather_list = []
weather_files = glob(os.path.join(weather_folder, "*.csv"))

for file in weather_files:
    try:
        df = pd.read_csv(file, sep=",", engine="python", low_memory=False)

        # ✔️ Corriger colonne Longitude s’il y a ".csv"
        if "Longitude" in df.columns:
            df["Longitude"] = df["Longitude"].astype(str).str.replace(".csv", "", regex=False)
            df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        if all(col in df.columns for col in ["DATE", "Latitude", "Longitude"]):
            df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
            df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
            df["latlon"] = df["Latitude"].round(4).astype(str) + "_" + df["Longitude"].round(4).astype(str)
            df["year"] = df["DATE"].dt.year

            if df.shape[1] < 150:
                weather_list.append(df)
            else:
                print(f"⚠️ Trop de colonnes ({df.shape[1]}), ignoré : {os.path.basename(file)}")
        else:
            print(f"❌ Colonnes essentielles manquantes dans {os.path.basename(file)}")

    except Exception as e:
        print(f"⛔ Erreur lecture {os.path.basename(file)} : {e}")

# ➕ Fusion météo + sol
weather_df = pd.concat(weather_list, ignore_index=True)
weather_soil_df = pd.merge(weather_df, soil_df, on="latlon", how="inner")

# 3️⃣ Engrais par nutriment
fert_nutrient = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv"))
fert_nutrient["Year"] = pd.to_numeric(fert_nutrient["Year"], errors="coerce")
fert_nutrient = fert_nutrient.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
fert_nutrient = fert_nutrient.rename(columns={"Value": "Fertilizer_NPK_tonnes"})
merged_df = pd.merge(weather_soil_df, fert_nutrient, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 4️⃣ Fumier de bétail
manure_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv"))
manure_df["Year"] = pd.to_numeric(manure_df["Year"], errors="coerce")
manure_agg = manure_df.groupby(["Area", "Year"])["Value"].sum().reset_index()
manure_agg = manure_agg.rename(columns={"Value": "Manure_N_total_kg"})
merged_df = pd.merge(merged_df, manure_agg, on=["Country", "Year"], how="left")

# 5️⃣ Pesticides
pest_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv"))
pest_df["Year"] = pd.to_numeric(pest_df["Year"], errors="coerce")
pest_agg = pest_df.groupby(["Area", "Year", "Element"])["Value"].sum().reset_index()
pest_pivot = pest_agg.pivot_table(index=["Area", "Year"], columns="Element", values="Value").reset_index()
merged_df = pd.merge(merged_df, pest_pivot, left_on=["Country", "Year"], right_on=["Area", "Year"], how="left")

# 6️⃣ Engrais par produit
fert_prod = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"))
fert_prod["Year"] = pd.to_numeric(fert_prod["Year"], errors="coerce")
prod_agg = fert_prod.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
prod_pivot = prod_agg.pivot_table(index=["Area", "Year"], columns="Item", values="Value").reset_index()
merged_df = pd.merge(merged_df, prod_pivot, left_on=["Country", "Year"], right_on=["Area", "Year"], how="left")

# 7️⃣ Rendement agricole
crop_prod = pd.read_csv(os.path.join(boua_folder, "Production_Crops_Livestock_Afrique.csv"), header=None)
crop_prod.columns = ["AreaCode", "M49Code", "Country", "ItemCode", "CropName", "ElementCode", "Element", "YearCode", "Year", "Unit", "Value", "Flag", "FlagDescription"]
crop_prod["Year"] = pd.to_numeric(crop_prod["Year"], errors="coerce")
crop_prod = crop_prod[crop_prod["Element"] == "Area harvested"]
crop_prod = crop_prod.groupby(["Country", "Year", "CropName"])["Value"].sum().reset_index()
crop_prod = crop_prod.rename(columns={"Value": "Harvested_Area_ha"})

# ➕ Fusion finale
final_df = pd.merge(merged_df, crop_prod, on=["Country", "Year"], how="left")

# 💾 Sauvegarde finale
output_path = r"C:\plateforme-agricole-complete-v2\dataset_prediction_rendement.csv"
final_df.to_csv(output_path, index=False)
print(f"✅ Dataset fusionné sauvegardé ici : {output_path}")
