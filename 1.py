#📦 SCRIPT : Préparation complète du dataset modélisable
import pandas as pd

# ============================
# 🧪 ÉTAPE 1 : Données météo
# ============================

df_meteo = pd.read_csv("merged_weather_africa.csv", parse_dates=["date"])
df_meteo["year"] = df_meteo["date"].dt.year

# Agrégation par pays, année, lat/lon et variable météo
df_meteo_agg = df_meteo.groupby(["country", "year", "latitude", "longitude", "variable"])["value"].mean().reset_index()

# Pivot pour avoir une colonne par variable météo
df_meteo_pivot = df_meteo_agg.pivot_table(
    index=["country", "year", "latitude", "longitude"],
    columns="variable",
    values="value"
).reset_index()

# ============================
# 🌱 ÉTAPE 2 : Fertilisants & Pesticides
# ============================

# Engrais (Production, Import, Export)
df_engrais = pd.read_csv("Fertilizers by Nutrient FAOSTAT_data_en_7-18-2025.csv", encoding="utf-8", quotechar='"')
df_engrais = df_engrais[df_engrais["Element"].str.strip().isin(["Production", "Import quantity", "Export quantity"])]
df_engrais["Area"] = df_engrais["Area"].str.strip()
df_engrais["Year"] = pd.to_numeric(df_engrais["Year"], errors="coerce")
df_engrais["Value"] = pd.to_numeric(df_engrais["Value"], errors="coerce")

df_engrais_pivot = df_engrais.pivot_table(
    index=["Area", "Year"],
    columns="Element",
    values="Value",
    aggfunc="sum"
).reset_index().rename(columns={"Area": "country", "Year": "year"})

# Pesticides
df_pest = pd.read_csv("Pesticides Use FAOSTAT_data_en_7-18-2025.csv", encoding="utf-8", quotechar='"')
df_pest = df_pest[df_pest["Element"].str.strip() == "Agricultural Use"]
df_pest["Area"] = df_pest["Area"].str.strip()
df_pest["Year"] = pd.to_numeric(df_pest["Year"], errors="coerce")
df_pest["Value"] = pd.to_numeric(df_pest["Value"], errors="coerce")
df_pest = df_pest.rename(columns={"Area": "country", "Year": "year", "Value": "pesticides_use"})
df_pest = df_pest[["country", "year", "pesticides_use"]]

# Fusion intrants
df_intrants = pd.merge(df_engrais_pivot, df_pest, on=["country", "year"], how="outer")

# ============================
# 🌾 ÉTAPE 3 : Rendement FAOSTAT
# ============================

df_fao = pd.read_csv("FAOSTAT_data_en_7-18-2025.csv", encoding="utf-8", quotechar='"')
df_fao["Element"] = df_fao["Element"].astype(str).str.strip().str.lower()
df_fao["Area"] = df_fao["Area"].astype(str).str.strip()
df_fao["Item"] = df_fao["Item"].astype(str).str.strip()
df_fao["Year"] = pd.to_numeric(df_fao["Year"], errors="coerce")
df_fao["Value"] = pd.to_numeric(df_fao["Value"], errors="coerce")

df_yield = df_fao[df_fao["Element"] == "yield"]
df_yield = df_yield.rename(columns={
    "Area": "country",
    "Year": "year",
    "Item": "culture",
    "Value": "yield_target"
}).dropna(subset=["yield_target"])

# ============================
# 🔗 Fusion complète
# ============================

df_base = pd.merge(df_meteo_pivot, df_intrants, on=["country", "year"], how="left")
df_final = pd.merge(df_base, df_yield[["country", "year", "culture", "yield_target"]], on=["country", "year"], how="left")

# ============================
# 🧼 Nettoyage final
# ============================

df_final = df_final.dropna(subset=["yield_target"])
df_final.to_csv("dataset_agricole_prepared.csv", index=False)

print(f"✅ Dataset final enregistré avec {len(df_final)} lignes !")
print(df_final.head())
