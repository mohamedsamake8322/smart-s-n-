import json
import os

# 📁 Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
input_path = os.path.join(base_path, "fiche_stress_complete.json")
output_path = os.path.join(base_path, "fiche_stress_complete.jsonl")

# 📖 Charger les données JSON
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 📤 Écrire ligne par ligne au format JSONL
with open(output_path, "w", encoding="utf-8") as f_out:
    for key, content in data.items():
        # Optionnel : inclure la clé comme un champ
        content["stress_type"] = key
        f_out.write(json.dumps(content, ensure_ascii=False) + "\n")

print(f"✅ Conversion terminée : {output_path}")
