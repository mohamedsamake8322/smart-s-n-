import os
import json
from pathlib import Path

def is_valid_json(line):
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False

# 📍 Chemin du fichier original
json_path = Path("C:\\plateforme-agricole-complete-v2\\besoins_des_plantes_en_nutriments.json")
clean_blocks = []

with open(json_path, "r", encoding="utf-8") as f:
    buffer = ""
    for line in f:
        stripped = line.strip()
        if not stripped:
            continue
        buffer += stripped
        try:
            obj = json.loads(buffer)
            clean_blocks.append(obj)
            buffer = ""  # Reset le buffer après chaque bloc valide
        except json.JSONDecodeError:
            buffer += " "  # Continue à accumuler

if not clean_blocks:
    print("❌ Aucun bloc JSON valide n’a été détecté.")
    exit(1)

# 🔁 Fusion logique des objets
merged = {"sources": [], "cultures": {}}
for block in clean_blocks:
    if isinstance(block, dict):
        merged["sources"].extend(block.get("sources", []))
        merged["cultures"].update(block.get("cultures", {}))

# 💾 Sauvegarde propre
with open("besoins_correcte.json", "w", encoding="utf-8") as out:
    json.dump(merged, out, indent=4, ensure_ascii=False)

print("✅ JSON fusionné à partir de blocs partiels — sauvegardé dans besoins_correcte.json")
