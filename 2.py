import pandas as pd

# 🔁 Chargement du fichier FAOSTAT
df_fao = pd.read_csv(
    "FAOSTAT_data_en_7-18-2025.csv",
    sep=",",
    quotechar='"',
    encoding="utf-8"
)

# 🧼 Nettoyage de la colonne 'Element'
df_fao["Element"] = df_fao["Element"].astype(str).str.strip().str.lower()

# 🎯 Filtrage sur les lignes correspondant à "production"
df_production = df_fao[df_fao["Element"] == "production"]

# 🔁 Renommer les colonnes principales
df_production = df_production.rename(columns={
    "Area": "country",
    "Year": "year",
    "Item": "culture",
    "Value": "yield_target"
})

# 🎓 Conversion des types
df_production["year"] = pd.to_numeric(df_production["year"], errors="coerce")
df_production["yield_target"] = pd.to_numeric(df_production["yield_target"], errors="coerce")

# 📊 Aperçu
print("\n✅ Lignes filtrées pour la production :")
print(df_production[["country", "year", "culture", "yield_target"]].head())

print(f"\n📦 Nombre total de lignes « production » : {len(df_production)}")
