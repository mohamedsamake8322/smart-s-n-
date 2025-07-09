import os
import json

from pathlib import Path

def flatten_cultures(cultures_dict, result=None):
    if result is None:
        result = {}
    for key, data in cultures_dict.items():
        if key == "cultures":
            flatten_cultures(data, result)
        else:
            result[key] = data
            if "cultures" in data:
                flatten_cultures(data["cultures"], result)
                del data["cultures"]
    return result

# 📍 Chemin vers le fichier source
json_path = Path("C:\\plateforme-agricole-complete-v2\\besoins_des_plantes_en_nutriments.json")

# ✅ Vérifier si le fichier existe
if not json_path.exists():
    print(f"❌ Fichier introuvable : {json_path}")
    exit(1)

# 🧠 Charger le contenu JSON intelligemment
with open(json_path, "r", encoding="utf-8") as f:
    try:
        raw_data = json.load(f)
    except json.JSONDecodeError:
        # Essai : plusieurs objets ? les regrouper en une seule structure
        f.seek(0)
        all_lines = f.readlines()
        multiple = [json.loads(line) for line in all_lines if line.strip()]
        # Fusionner dans un seul dictionnaire si possible
        raw_data = {"sources": [], "cultures": {}}
        for block in multiple:
            raw_data["sources"].extend(block.get("sources", []))
            raw_data["cultures"].update(block.get("cultures", {}))

# 🧹 Appliquer le flatten sur les cultures
clean_cultures = flatten_cultures(raw_data.get("cultures", {}))

# 📦 Nouveau format structuré
clean_data = {
    "sources": raw_data.get("sources", []),
    "cultures": clean_cultures
}

# 💾 Sauvegarde du fichier propre
with open("besoins_correcte.json", "w", encoding="utf-8") as f:
    json.dump(clean_data, f, indent=4, ensure_ascii=False)

print("✅ JSON unifié et restructuré enregistré avec succès → besoins_correcte.json")
