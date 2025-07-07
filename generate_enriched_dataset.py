import os
import json
import pandas as pd

# 📁 Chemins
base_dir = r"C:\Users\moham\Music\plantdataset"
json_path = r"C:\plateforme-agricole-complete-v2\EN_mapping_fiches_maladies.json"

# 📖 Charger les métadonnées
with open(json_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# 📦 Collecte des données
records = []

for split in ["train", "val"]:
    split_path = os.path.join(base_dir, split)
    for class_name in os.listdir(split_path):
        class_dir = os.path.join(split_path, class_name)
        if not os.path.isdir(class_dir):
            continue

        # Récupérer les infos depuis le JSON
        fiche = metadata.get(class_name.strip())
        if not fiche:
            print(f"⚠️ Classe non trouvée dans le JSON : {class_name}")
            continue

        for img_file in os.listdir(class_dir):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            image_path = os.path.join(split, class_name, img_file)
            records.append({
                "split": split,
                "class": class_name,
                "image_path": image_path,
                "culture": fiche.get("culture", ""),
                "agent_causal": fiche.get("Agent causal", ""),
                "description": fiche.get("description", ""),
                "symptoms": fiche.get("symptoms", ""),
                "evolution": fiche.get("evolution", ""),
                "active_material": fiche.get("Name of active product material", ""),
                "treatment": fiche.get("treatment", "")
            })

# 💾 Export CSV et JSON
df = pd.DataFrame(records)
df.to_csv("plant_disease_dataset_enriched.csv", index=False, encoding="utf-8")
with open("plant_disease_dataset_enriched.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=4, ensure_ascii=False)

print(f"\n✅ {len(records)} images enrichies exportées dans :")
print("   - plant_disease_dataset_enriched.csv")
print("   - plant_disease_dataset_enriched.json")
