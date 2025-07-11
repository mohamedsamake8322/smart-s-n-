# produire un seul json des maladies
import os
import json

# 📁 Dossier source
fiche_dir = r"C:/plateforme-agricole-complete-v2/plantdataset/fiche_par_maladie"
output_path = os.path.join(fiche_dir, "..", "maladie_dataset.json")

# 📦 Liste fusionnée
maladie_dataset = []

# 🔍 Fonction de validation
def is_valid_annotation(annotation):
    required_keys = ["type", "label", "symptoms", "correction"]
    return all(k in annotation and annotation[k] for k in required_keys)

# 🔁 Parcours des fichiers
for file in os.listdir(fiche_dir):
    if not file.endswith(".json"):
        continue

    file_path = os.path.join(fiche_dir, file)
    with open(file_path, encoding="utf-8") as f:
        fiche = json.load(f)

    for image in fiche.get("images", []):
        annotation = image.get("annotation", {})
        if not is_valid_annotation(annotation):
            print(f"⚠️ Annotation incomplète pour : {image.get('path', '')}")
            continue

        maladie_dataset.append(image)

print(f"📊 Total d'images annotées valides : {len(maladie_dataset)}")

# 💾 Sauvegarde
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(maladie_dataset, f_out, indent=4, ensure_ascii=False)

print(f"\n✅ Dataset global généré : {output_path}")
