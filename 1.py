#✅ Script de chargement, nettoyage et filtrage du fichier FAO
import pandas as pd

# 🧱 Définir les noms de colonnes FAOSTAT (14 colonnes total)
column_names = [
    "domain_code", "domain", "country", "item_code", "item",
    "element_code", "element", "year_code", "year",
    "unit", "value", "flag", "extra1", "extra2"
]

# 📥 Lecture du fichier avec gestion des virgules dans les champs texte
df_fao = pd.read_csv(
    "Production_Crops_Livestock_Afrique.csv",
    sep=",",
    quotechar='"',
    names=column_names,
    header=None,
    engine="python",
    encoding="utf-8"
)

# 🧼 Nettoyage de la colonne 'element' pour normalisation
df_fao["element"] = df_fao["element"].astype(str).str.strip().str.lower()

# 🎯 Filtrer uniquement les lignes de type 'production'
df_fao = df_fao[df_fao["element"] == "production"]

# 🔁 Renommer les colonnes principales pour le modèle
df_fao = df_fao.rename(columns={
    "country": "country",
    "year": "year",
    "item": "culture",
    "value": "yield_target"
})

# 🎓 Conversion des types de données utiles
df_fao["year"] = pd.to_numeric(df_fao["year"], errors="coerce")
df_fao["yield_target"] = pd.to_numeric(df_fao["yield_target"], errors="coerce")

# 🧪 Vérification finale
print("\n✅ Aperçu des données prêtes pour le modèle :")
print(df_fao[["country", "year", "culture", "yield_target"]].head())
print(f"\n📊 Total lignes utiles : {len(df_fao)}")
