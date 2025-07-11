import os
import json

# 📁 Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
output_dir = os.path.join(base_path, "fiche_par_maladie")
json_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
os.makedirs(output_dir, exist_ok=True)

# 📖 Charger le JSON
with open(json_path, encoding="utf-8") as f:
    disease_data = json.load(f)

# 🔄 Normalisation
def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ")

# 🔁 Créer un mapping des clés normalisées
json_keys = {normalize(k): k for k in disease_data}

# 📦 Traitement des dossiers
for subset in ["train", "val"]:
    subset_path = os.path.join(base_path, subset)
    if not os.path.exists(subset_path):
        continue

    for folder in os.listdir(subset_path):
        folder_path = os.path.join(subset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        norm_name = normalize(folder)
        json_key = json_keys.get(norm_name)
        if not json_key:
            print(f"⚠️ Pas de fiche pour : {folder}")
            continue

        fiche_data = disease_data.get(json_key, {})
        annotation = {
            "type": "disease",
            "label": json_key,
            "culture": fiche_data.get("culture", ""),
            "agent_causal": fiche_data.get("Agent causal", ""),
            "description": fiche_data.get("description", ""),
            "symptoms": fiche_data.get("symptoms", ""),
            "evolution": fiche_data.get("evolution", ""),
            "active_material": fiche_data.get("Name of active product material", ""),
            "treatment": fiche_data.get("treatment", "")
        }

        # 📸 Annoter chaque image
        images = []
        for img in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, img)):
                images.append({
                    "filename": img,
                    "path": os.path.join(subset, folder, img),
                    "annotation": annotation
                })

        # 💾 Sauvegarde
        fiche = {
            "dossier": folder,
            "json_key": json_key,
            "images": images
        }
        out_path = os.path.join(output_dir, f"{folder}.json")
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(fiche, f_out, indent=4, ensure_ascii=False)

        print(f"✅ Fiche annotée : {folder}")

print(f"\n🎯 Toutes les fiches maladies enrichies sont dans : {output_dir}")
