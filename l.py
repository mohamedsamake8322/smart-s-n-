import json
from pathlib import Path

# 📁 Chemin vers le fichier brut
fichier_source = Path("C:\\plateforme-agricole-complete-v2\\besoins_des_plantes_en_nutriments.json")

cultures = {}
sources = []

with open(fichier_source, "r", encoding="utf-8") as f:
    buffer = ""
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue
        buffer += stripped
        try:
            obj = json.loads(buffer)
            if "cultures" in obj:
                for nom_culture, data in obj["cultures"].items():
                    cultures[nom_culture] = data
                    if "sources" in data:
                        sources.extend(data["sources"])
            buffer = ""
        except json.JSONDecodeError:
            buffer += " "

# 🧹 Nettoyage éventuel des sources (optionnel)
sources_uniques = sorted(set(sources))

# 📦 Structure finale
resultat = {
    "sources": sources_uniques,
    "cultures": cultures
}

# 💾 Sauvegarde
with open("besoins_correcte.json", "w", encoding="utf-8") as f:
    json.dump(resultat, f, indent=4, ensure_ascii=False)

print("✅ Fichier fusionné enregistré avec succès : besoins_correcte.json")
