import os
import json

# 📁 Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
input_dir = os.path.join(base_path, "file_by_stress")
output_path = os.path.join(base_path, "fiche_stress_complete.json")

# 📦 Dictionnaire fusionné
fiche_by_stress = {}

# 🔁 Parcours des fichiers JSON
for file_name in os.listdir(input_dir):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(input_dir, file_name)
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    key = os.path.splitext(file_name)[0]  # "salinity" depuis "salinity.json"
    fiche_by_stress[key] = data

# 💾 Sauvegarde du fichier fusionné
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(fiche_by_stress, f_out, indent=4, ensure_ascii=False)

print(f"✅ Fichier fusionné sauvegardé dans : {output_path}")
