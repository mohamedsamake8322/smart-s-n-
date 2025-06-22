# 🛠️ Astuce pratique : Renommer les dossiers automatiquement
import os
import json

path_dataset = r"C:\Downloads\archive\农作物病虫害数据集"
mapping = {}

for dossier in os.listdir(path_dataset):
    nom_chinois = dossier
    nom_ascii = f"classe_{len(mapping)}"
    os.rename(os.path.join(path_dataset, dossier), os.path.join(path_dataset, nom_ascii))
    mapping[nom_ascii] = nom_chinois

# Sauvegarder le mapping
with open("mapping_dossiers.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=4)
