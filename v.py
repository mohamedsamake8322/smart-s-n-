import pandas as pd
import os

boua_folder = r"C:\plateforme-agricole-complete-v2\Boua"
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
weather_sample = r"C:\plateforme-agricole-complete-v2\weather_final\weather_Angola.csv"  # ⬅️ change ce nom si nécessaire

def show_info(df, name, country_col="Country", year_col="Year"):
    print(f"\n📦 {name}")
    print(f"➡️ Lignes : {df.shape[0]}")
    print(f"🧬 Colonnes : {list(df.columns)}")
    if country_col in df.columns:
        print(f"🌍 Exemples pays : {df[country_col].dropna().unique()[:5]}")
    if year_col in df.columns:
        print(f"📆 Exemples années : {sorted(df[year_col].dropna().unique()[:5])}")

# 🌱 Sol
soil_df = pd.read_csv(soil_path, nrows=500)
show_info(soil_df, "Sol", country_col=None, year_col=None)

# 🌦️ Météo (échantillon)
weather_df = pd.read_csv(weather_sample, nrows=500)
weather_df["year"] = pd.to_datetime(weather_df["DATE"], errors="coerce").dt.year
show_info(weather_df, "Météo")

# 🧪 Engrais NPK
npk_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv"))
show_info(npk_df, "Engrais NPK")

# 💩 Fumier
manure_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv"))
show_info(manure_df, "Fumier")

# ☠️ Pesticides
pest_df = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv"))
show_info(pest_df, "Pesticides")

# 🧪 Engrais par produit
fert_prod = pd.read_csv(os.path.join(boua_folder, "FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"))
show_info(fert_prod, "Engrais par produit")

# 🌾 Rendements agricoles
crop_file = os.path.join(boua_folder, "Production_Crops_Livestock_Afrique.csv")
crop_prod = pd.read_csv(crop_file, sep=",", quotechar='"', engine="python", header=None)
print(f"\n🌾 Rendements agricoles (brut) : {crop_prod.shape[0]} lignes, {crop_prod.shape[1]} colonnes")
print("📋 Première ligne :")
print(crop_prod.iloc[0].tolist())
