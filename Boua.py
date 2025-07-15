import pandas as pd
import os
from glob import glob

# 📁 Dossiers d'entrée
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_folder = r"C:\Users\moham\Music\3\worldclim"
boua_folder = r"C:\plateforme-agricole-complete-v2\Boua"
clim_res_path = os.path.join(weather_folder, "worldclim_comparatif_resolutions.csv")

# 1️⃣ Chargement des données de sol
soil_df = pd.read_csv(soil_path)
soil_df["Latitude"] = soil_df["y"]
soil_df["Longitude"] = soil_df["x"]
soil_df["latlon"] = soil_df["Latitude"].round(4).astype(str) + "_" + soil_df["Longitude"].round(4).astype(str)
soil_df["latlon"] = soil_df["latlon"].str.strip()

# 2️⃣ Chargement des moyennes météo multi-résolution
if os.path.exists(clim_res_path):
    clim_avg_df = pd.read_csv(clim_res_path)
    clim_avg_df["mois"] = clim_avg_df["mois"].astype(int)
    clim_avg_df["Country"] = clim_avg_df["pays"].str.strip().str.title()
else:
    clim_avg_df = pd.DataFrame()
    print("⚠️ Fichier météo comparatif non trouvé.")

# 3️⃣ Météo brute (exclure les fichiers worldclim)
weather_files = [f for f in glob(os.path.join(weather_folder, "*.csv"))
                 if "report" not in f.lower() and "comparatif" not in f.lower() and "worldclim" not in f.lower()]
weather_df = pd.DataFrame()
print(f"✅ Fichiers météo ponctuels : {len(weather_files)}")

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
        df["month"] = df["DATE"].dt.month
        df["Country"] = df["Country"].str.strip().str.title()
        df["latlon"] = df["Latitude"].round(4).astype(str) + "_" + df["Longitude"].round(4).astype(str)
        weather_df = pd.concat([weather_df, df], ignore_index=True)
        print(f"📥 Météo traitée : {os.path.basename(file)}")
    except Exception as e:
        print(f"⛔ Erreur lecture {os.path.basename(file)} : {e}")

# 4️⃣ Fusion météo ponctuelle + sol
if not weather_df.empty:
    weather_soil_df = pd.merge(weather_df, soil_df, on="latlon", how="inner")
    print(f"📦 Fusion météo + sol : {weather_soil_df.shape[0]} lignes")
else:
    weather_soil_df = pd.DataFrame()
    print("⚠️ Données météo spatiales absentes.")

# 5️⃣ Intrants - engrais NPK
fert_nutrient = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv"))
fert_nutrient["Year"] = pd.to_numeric(fert_nutrient["Year"], errors="coerce")
fert_nutrient["Area"] = fert_nutrient["Area"].str.strip().str.title()
fert_nutrient = fert_nutrient.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
fert_nutrient = fert_nutrient.rename(columns={"Value": "Fertilizer_NPK_tonnes"})

# 6️⃣ Intrants - fumier
manure_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv"))
manure_df["Year"] = pd.to_numeric(manure_df["Year"], errors="coerce")
manure_df["Area"] = manure_df["Area"].str.strip().str.title()
manure_agg = manure_df.groupby(["Area", "Year"])["Value"].sum().reset_index()
manure_agg = manure_agg.rename(columns={"Value": "Manure_N_total_kg"})

# 7️⃣ Intrants - pesticides
pest_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv"))
pest_df["Year"] = pd.to_numeric(pest_df["Year"], errors="coerce")
pest_df["Area"] = pest_df["Area"].str.strip().str.title()
pest_agg = pest_df.groupby(["Area", "Year", "Element"])["Value"].sum().reset_index()
pest_pivot = pest_agg.pivot_table(index=["Area", "Year"], columns="Element", values="Value").reset_index()

# 8️⃣ Intrants - engrais par produit
fert_prod = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"))
fert_prod["Year"] = pd.to_numeric(fert_prod["Year"], errors="coerce")
fert_prod["Area"] = fert_prod["Area"].str.strip().str.title()
prod_agg = fert_prod.groupby(["Area", "Year", "Item"])["Value"].sum().reset_index()
prod_pivot = prod_agg.pivot_table(index=["Area", "Year"], columns="Item", values="Value").reset_index()

# 🔗 Fusion des intrants et météo + sol
merged_df = weather_soil_df.copy() if not weather_soil_df.empty else pd.DataFrame()
if not merged_df.empty:
    merged_df = pd.merge(merged_df, fert_nutrient, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")
    merged_df = pd.merge(merged_df, manure_agg, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")
    merged_df = pd.merge(merged_df, pest_pivot, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")
    merged_df = pd.merge(merged_df, prod_pivot, left_on=["Country", "year"], right_on=["Area", "Year"], how="left")
    merged_df = merged_df.drop(columns=["Area", "Year"], errors="ignore")
else:
    print("⚠️ Fusion intrants ignorée : données météo+sol absentes.")

# 🔗 Fusion avec données météo multi-résolution
if not clim_avg_df.empty and not merged_df.empty:
    merged_df = pd.merge(merged_df, clim_avg_df, left_on=["Country", "month"], right_on=["Country", "mois"], how="left")
    merged_df = merged_df.drop(columns=["pays", "mois"], errors="ignore")

# 9️⃣ Données de rendement agricole
crop_file = os.path.join(boua_folder, "Production_Crops_Livestock_Afrique.csv")
crop_prod = pd.read_csv(crop_file, sep=",", quotechar='"', engine="python", header=None)

expected_cols = [
    "AreaCode", "M49Code", "Country", "ItemCode", "CropName",
    "ElementCode", "Element", "YearCode", "Year", "Unit",
    "Value", "Flag", "FlagDescription"
]

if crop_prod.shape[1] in [len(expected_cols), len(expected_cols) + 1]:
    crop_prod.columns = expected_cols + ["Extra"] if crop_prod.shape[1] > len(expected_cols) else expected_cols
    crop_prod = crop_prod.drop(columns=["Extra"], errors="ignore")
else:
    raise ValueError(f"⚠️ Format inattendu dans le fichier de rendements : {crop_prod.shape[1]} colonnes.")

crop_prod["Country"] = crop_prod["Country"].str.strip().str.title()
crop_prod["Year"] = pd.to_numeric(crop_prod["Year"], errors="coerce")
crop_prod = crop_prod[crop_prod["Element"] == "Area harvested"]
crop_prod = crop_prod.groupby(["Country", "Year", "CropName"])["Value"].sum().reset_index()
crop_prod = crop_prod.rename(columns={"Value": "Harvested_Area_ha"})

final_df = pd.merge(merged_df, crop_prod, on=["Country", "Year"], how="left")
print(f"✅ Dataset final prêt : {final_df.shape[0]} lignes, {final_df.shape[1]} colonnes")

# 💾 Sauvegarde du jeu de données enrichi
output_path = r"C:\plateforme-agricole-complete-v2\dataset_prediction_rendement.csv"
final_df.to_csv(output_path, index=False)

print(f"📁 Fichier complet sauvegardé ici : {output_path}")
