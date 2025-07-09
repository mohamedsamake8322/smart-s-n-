import json
import os

# Répartition par défaut basée sur guides agronomiques
REPARTITION_PAR_ELEMENT = {
    "N": [("Tallaison", 0.25), ("Montaison", 0.20), ("Floraison", 0.25), ("Remplissage_du_grain", 0.20)],
    "P2O5": [("Germination", 0.30), ("Floraison", 0.30)],
    "K2O": [("Tallaison", 0.20), ("Floraison", 0.25), ("Remplissage_du_grain", 0.35)],
    "Zn": [("Germination", 0.30), ("Floraison", 0.20)],
    "B": [("Floraison", 0.20), ("Remplissage_du_grain", 0.15)],
    "MgO": [("Tallaison", 0.10), ("Remplissage_du_grain", 0.20)],
    "S": [("Montaison", 0.25)]
}

SOURCES = [
    "Haifa Group – Maize Nutrition Guide",
    "FAO Bulletin 38",
    "ICRISAT – Nutrient Partitioning Studies"
]

def generer_fractionnement(stades_cles):
    fractionnement = {}
    for element, repartition in REPARTITION_PAR_ELEMENT.items():
        for stade, ratio in repartition:
            if stade in stades_cles or any(element.startswith(e) for e in stades_cles.get(stade, [])):
                if stade not in fractionnement:
                    fractionnement[stade] = {}
                fractionnement[stade][element] = ratio
    return fractionnement

def construire_db(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        besoins_data = json.load(f)

    phased_db = {}
    for bloc in besoins_data:
        for culture, data in bloc["cultures"].items():
            stades_cles = data.get("stades_cles", {})
            nom_commun = data.get("nom_commun", culture.replace("_", " ").capitalize())
            fractionnement = generer_fractionnement(stades_cles)
            if fractionnement:
                phased_db[culture] = {
                    "nom_commun": nom_commun,
                    "fractionnement": fractionnement,
                    "note": "Les pourcentages représentent la part approximative de l'élément à appliquer à chaque phase. À corriger selon sol, climat, disponibilité des engrais.",
                    "sources": SOURCES
                }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(phased_db, f, indent=2, ensure_ascii=False)

# 📌 CHEMIN PERSONNALISÉ
INPUT_PATH = r"C:\plateforme-agricole-complete-v2\besoins des plantes en nutriments.json"
OUTPUT_PATH = r"C:\plateforme-agricole-complete-v2\fertilization_phased_db.json"

construire_db(INPUT_PATH, OUTPUT_PATH)
