import pandas as pd
import json

# 📁 Paramètre
csv_enrichi = "dataset_combiné_enrichi.csv"
sortie_json = "fiches_maladies.json"

# 📑 Charger le CSV enrichi
df = pd.read_csv(csv_enrichi)

# 🧠 Extraire toutes les combinaisons culture-maladie uniques
maladies_uniques = df[["culture", "maladie"]].drop_duplicates().dropna()

# 📦 Construire le dictionnaire
fiches = {}

for _, row in maladies_uniques.iterrows():
    culture = row["culture"].strip().capitalize()
    maladie = row["maladie"].strip().capitalize()

    titre = f"{culture} - {maladie}" if "saine" not in maladie.lower() and "healthy" not in maladie.lower() else f"{culture} en bonne santé"

    fiches[titre] = {
        "culture": culture,
        "description": "",
        "symptômes": "",
        "évolution": "",
        "Nom de la matière active du produit": "",
        "traitement": ""
    }

# 💾 Sauvegarde
with open(sortie_json, "w", encoding="utf-8") as f:
    json.dump(fiches, f, indent=2, ensure_ascii=False)

print(f"✅ {len(fiches)} fiches maladie générées dans '{sortie_json}'")
