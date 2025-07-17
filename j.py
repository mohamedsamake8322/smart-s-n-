import pandas as pd

# 📁 1. Charger les fichiers CSV
df_engrais_nutriment = pd.read_csv("FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv")
df_engrais_produit = pd.read_csv("FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv")
df_fumier = pd.read_csv("FAOSTAT_data_en_7-12-2025_fumier_de_betails.csv")
df_pesticides = pd.read_csv("FAOSTAT_data_en_7-12-2025_utilisation_des_pesticides.csv")
df_production = pd.read_csv("Production_Crops_Livestock_Afrique.csv", header=None)

# 📦 2. Garder les colonnes utiles et renommer
df_engrais_nutriment = df_engrais_nutriment[["Area", "Item", "Year", "Unit", "Value"]]
df_engrais_nutriment = df_engrais_nutriment.rename(columns={"Area": "country", "Item": "nutrient", "Year": "year"})

df_engrais_produit = df_engrais_produit[["Area", "Item", "Year", "Unit", "Value"]]
df_engrais_produit = df_engrais_produit.rename(columns={"Area": "country", "Item": "product", "Year": "year"})

df_fumier = df_fumier[["Area", "Element", "Item", "Year", "Unit", "Value"]]
df_fumier = df_fumier.rename(columns={"Area": "country", "Element": "type", "Item": "animal", "Year": "year"})

df_pesticides = df_pesticides[["Area", "Element", "Item", "Year", "Unit", "Value"]]
df_pesticides = df_pesticides.rename(columns={"Area": "country", "Element": "indicator", "Item": "type", "Year": "year"})

# 🧼 3. Nettoyage : enlever les lignes vides ou doublons
df_engrais_nutriment.dropna(inplace=True)
df_engrais_produit.dropna(inplace=True)
df_fumier.dropna(inplace=True)
df_pesticides.dropna(inplace=True)

# 📊 4. Grouper par pays et année (engrais total N par exemple)
agg_engrais = df_engrais_nutriment.groupby(["country", "year", "nutrient"]).agg({"Value": "sum"}).reset_index()
agg_pesticides = df_pesticides.groupby(["country", "year"]).agg({"Value": "sum"}).reset_index()

# 🧠 5. Fusionner engrais + pesticides
df_inputs = pd.merge(agg_engrais, agg_pesticides, on=["country", "year"], how="outer", suffixes=("_engrais", "_pesticides"))

# 💾 6. Exporter le tableau final
df_inputs.to_csv("indicateurs_agronomiques_FAOSTAT.csv", index=False)
print("✅ Export terminé : indicateurs_agronomiques_FAOSTAT.csv")
