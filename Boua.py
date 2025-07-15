import pandas as pd
import numpy as np
import os
from glob import glob

# 📁 Dossiers
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_folder = r"C:\plateforme-agricole-complete-v2\weather_final"
boua_folder = r"C:\plateforme-agricole-complete-v2\Boua"

# 1️⃣ Sol
soil_df = pd.read_csv(soil_path)
soil_df["latlon"] = soil_df["y"].round(4).astype(str) + "_" + soil_df["x"].round(4).astype(str)

# 2️⃣ Météo nettoyée
weather_files = [f for f in glob(os.path.join(weather_folder, "*.csv")) if "report" not in os.path.basename(f).lower()]
weather_list = []

for file in weather_files:
    try:
        df = pd.read_csv(file, low_memory=False)
        keep_cols = [c for c in df.columns if ("PRECTOT" in c or "WS2M" in c or "PS" in c or "IMERG" in c or c in ["Country", "Latitude", "Longitude", "DATE"])]
        df = df[keep_cols]

        if "DATE" not in df.columns or df.shape[1] < 5 or df.shape[1] > 100:
            print(f"❌ Structure suspecte — ignoré : {os.path.basename(file)} ({df.shape[1]} colonnes)")
            continue

        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"].astype(str).str.replace(".csv", "", regex=False), errors="coerce")
        df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce")
        df["year"] = df["DATE"].dt.year
        df["latlon"] = df["Latitude"].round(4).astype(str) + "_" + df["Longitude"].round(4).astype(str)
        weather_list.append(df)

    except Exception as e:
        print(f"⛔ Erreur lecture {os.path.basename(file)} : {e}")

print(f"✅ Fichiers météo retenus pour fusion : {len(weather_list)}")
common_cols = set.intersection(*(set(df.columns) for df in weather_list))
weather_list = [df[list(common_cols)] for df in weather_list]
print(f"🎯 Colonnes communes retenues : {len(common_cols)}")

weather_df = pd.concat(weather_list, ignore_index=True)
print(f"🧮 Lignes dans weather_df : {weather_df.shape[0]}")

weather_soil_df = pd.merge(weather_df, soil_df, on="latlon", how="inner")
print(f"🧮 Lignes après fusion sol : {weather_soil_df.shape[0]}")
print(f"📋 Pays météo/sol : {weather_soil_df['Country'].dropna().unique()[:5]}")
print(f"📋 Années météo/sol : {weather_soil_df['year'].dropna().unique()[:5]}")

# 3️⃣ Engrais NPK
fert_nutrient = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv"))
fert_nutrient["Year"] = pd.to_numeric(fert_nutrient["Year"], errors="coerce")
fert_nutrient = fert_nutrient.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
fert_nutrient = fert_nutrient.rename(columns={"Value": "Fertilizer_NPK_tonnes"})
merged_df = pd.merge(weather_soil_df, fert_nutrient, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 4️⃣ Fumier
manure_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv"))
manure_df["Year"] = pd.to_numeric(manure_df["Year"], errors="coerce")
manure_agg = manure_df.groupby(["Area", "Year"])["Value"].sum().reset_index()
manure_agg = manure_agg.rename(columns={"Value": "Manure_N_total_kg"})
merged_df = pd.merge(merged_df, manure_agg, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 5️⃣ Pesticides
pest_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv"))
pest_df["Year"] = pd.to_numeric(pest_df["Year"], errors="coerce")
pest_agg = pest_df.groupby(["Area", "Year", "Element"])["Value"].sum().reset_index()
pest_pivot = pest_agg.pivot_table(index=["Area", "Year"], columns="Element", values="Value").reset_index()
merged_df = pd.merge(merged_df, pest_pivot, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")

# 6️⃣ Engrais par produit
fert_prod = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"))
fert_prod["Year"] = pd.to_numeric(fert_prod["Year"], errors="coerce")
prod_agg = fert_prod.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
merged_df = merged_df.drop(columns=["Area", "Year"], errors="ignore")
prod_pivot = prod_agg.pivot_table(index=["Area", "Year"], columns="Item", values="Value").reset_index()
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

# 📊 Vérification rapide
print(f"🧪 crop_prod total avant filtre : {crop_prod.shape[0]}")
print(f"🔎 Valeurs 'Element' : {crop_prod['Element'].dropna().unique()[:5]}")

# ✅ Filtrage par libellé (et non par code)
crop_prod = crop_prod[crop_prod["Element"] == "Area harvested"]

print(f"🌱 crop_prod après filtre 'Area harvested' : {crop_prod.shape[0]}")
print(f"📋 Pays crop_prod : {crop_prod['Country'].dropna().unique()[:5]}")
print(f"📋 Années crop_prod : {crop_prod['Year'].dropna().unique()[:5]}")

# 🧮 Agrégation
crop_prod = crop_prod.groupby(["Country", "Year", "CropName"])["Value"].sum().reset_index()
crop_prod = crop_prod.rename(columns={"Value": "Harvested_Area_ha"})

# 🔗 Diagnostic de jointure
print("🔗 Pays communs avec merged_df :")
print(set(merged_df["Country"].dropna()) & set(crop_prod["Country"].dropna()))
print("🔗 Années communes :")
print(set(merged_df["year"].dropna()) & set(crop_prod["Year"].dropna()))

# 🔁 Fusion finale
final_df = pd.merge(merged_df, crop_prod, on=["Country", "Year"], how="left")
print(f"✅ Lignes finales dans dataset : {final_df.shape[0]}")

# 💾 Sauvegarde
output_path = r"C:\plateforme-agricole-complete-v2\dataset_prediction_rendement.csv"
final_df.to_csv(output_path, index=False)
print(f"✅ Dataset fusionné sauvegardé ici : {output_path}")
