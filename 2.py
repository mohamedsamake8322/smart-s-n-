import pandas as pd

# 📥 Chargement du fichier FAOSTAT
df_fao = pd.read_csv(
    "FAOSTAT_data_en_7-18-2025.csv",
    sep=",",
    quotechar='"',
    encoding="utf-8"
)

# 🧼 Nettoyage des colonnes
df_fao["Element"] = df_fao["Element"].astype(str).str.strip().str.lower()
df_fao["Area"] = df_fao["Area"].astype(str).str.strip()
df_fao["Item"] = df_fao["Item"].astype(str).str.strip()
df_fao["Year"] = pd.to_numeric(df_fao["Year"], errors="coerce")
df_fao["Value"] = pd.to_numeric(df_fao["Value"], errors="coerce")

# 🎯 Filtrage des lignes correspondant à 'yield'
df_yield = df_fao[df_fao["Element"] == "yield"]

# 🔁 Renommer les colonnes principales
df_yield = df_yield.rename(columns={
    "Area": "country",
    "Year": "year",
    "Item": "culture",
    "Value": "yield_target"
})

# 🧪 Nettoyage final : suppression des lignes sans données
df_yield = df_yield.dropna(subset=["yield_target"])

# 🔍 Aperçu des premières lignes exploitables
print("\n✅ Aperçu des lignes de rendement exploitables :")
print(df_yield[["country", "year", "culture", "yield_target"]].head())

# 📊 Résumé statistique
print(f"\n📦 Total lignes 'yield' valides : {len(df_yield)}")
print("\n📈 Statistiques descriptives du rendement :")
print(df_yield["yield_target"].describe())
