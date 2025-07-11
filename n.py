import os
import json

# 📁 Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
input_path = os.path.join(base_path, "fiche_carence_complete.json")
output_path = os.path.join(base_path, "fiche_carence_complete.jsonl")

# 📖 Charger le fichier fusionné
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 📤 Sauvegarder au format JSONL
with open(output_path, "w", encoding="utf-8") as f_out:
    for key, fiche in data.items():
        fiche["carence"] = key  # Ajoute le nom de la carence comme champ
        f_out.write(json.dumps(fiche, ensure_ascii=False) + "\n")

print(f"✅ Conversion vers JSONL terminée : {output_path}")
