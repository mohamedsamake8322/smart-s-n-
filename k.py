import os
import json

# 📁 Chemin vers le dossier train
train_path = r"C:\plateforme-agricole-complete-v2\plantdataset\train"

def nettoyer_nom(nom):
    """Renvoie un nom lisible : majuscules, espaces, accents corrigés"""
    nom = nom.replace("_", " ")
    nom = nom.replace("  ", " ").strip()
    nom = nom.lower()

    remplacements = {
        "tomato": "Tomate",
        "potato": "Pomme de terre",
        "apple": "Pomme",
        "grape": "Raisin",
        "maize": "Maïs",
        "corn (maize)": "Maïs",
        "peach": "Pêcher",
        "pepper, bell": "Poivron",
        "raspberry": "Framboisier",
        "soybean": "Soja",
        "orange": "Oranger",
        "blueberry": "Myrtille",
        "squash": "Courge",
        "strawberry": "Fraisier",
        "cashew": "Anacardier",
        "cherry (including sour)": "Cerisier",
        "leaf": "feuille",
        "spot": "tache",
        "blight": "brûlure",
        "healthy": "en bonne santé"
    }

    for mot, traduction in remplacements.items():
        nom = nom.replace(mot, traduction)

    # Mettre la première lettre en majuscule
    return nom[0].upper() + nom[1:]

# 🔍 Générer le mapping
dossiers = sorted([d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d))])
mapping = {}

for dossier in dossiers:
    label_lisible = nettoyer_nom(dossier)
    mapping[label_lisible] = {
        "culture": "",
        "description": "",
        "symptômes": "",
        "évolution":"",
        "Nom de la matière active du produit":"",
        "traitement": ""
    }

# 💾 Sauvegarde
with open("mapping_fiches_maladies.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"✅ {len(mapping)} fiches générées dans 'mapping_fiches_maladies.json'")
