# 🧠 Étape 1 : Générer un squelette JSON enrichi
import json

# Charger les noms traduits (ex: classes_traduites.json)
with open("classes_traduites.json", "r", encoding="utf-8") as f:
    maladies = json.load(f)

# Générer la structure enrichie
base_connaissance = {}

for nom in maladies:
    culture = nom.split(" ")[0] if " " in nom else ""
    base_connaissance[nom] = {
        "culture": culture,
        "description": "",
        "symptômes": "",
        "évolution": "",
        "traitement": ""
    }

# Sauvegarder
with open("maladies_enrichies.json", "w", encoding="utf-8") as f:
    json.dump(base_connaissance, f, ensure_ascii=False, indent=4)

print("✅ Fichier 'maladies_enrichies.json' généré.")
