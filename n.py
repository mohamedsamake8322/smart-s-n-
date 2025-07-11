import os
import json

# 📁 Dossier source
fiche_dir = r"C:/plateforme-agricole-complete-v2/plantdataset/fiche_par_maladie"
output_path = os.path.join(fiche_dir, "..", "maladie_dataset.json")

# 📦 Liste fusionnée
maladie_dataset = []

# 🔁 Parcours des fichiers
for file in os.listdir(fiche_dir):
    if not file.endswith(".json"):
        continue

    file_path = os.path.join(fiche_dir, file)
    with open(file_path, encoding="utf-8") as f:
        fiche = json.load(f)

    for image in fiche.get("images", []):
        annotation = image.get("annotation")
        if not annotation:
            print(f"⚠️ Aucune annotation pour : {image.get('path', '')}")
            continue

        # Ajout sans validation stricte
        maladie_dataset.append(image)

print(f"\n📊 Images incluses : {len(maladie_dataset)}")

# 💾 Sauvegarde
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(maladie_dataset, f_out, indent=4, ensure_ascii=False)

print(f"\n✅ Fusion complète dans : {output_path}")
