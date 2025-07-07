import os
import json
import pandas as pd
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# 📁 Chemins
base_dir = r"C:\Users\moham\Music\plantdataset"
json_path = r"C:\plateforme-agricole-complete-v2\EN_mapping_fiches_maladies.json"

# 📖 Charger les métadonnées maladies
with open(json_path, "r", encoding="utf-8") as f:
    metadata = json.load(f)

# 💡 Charger BLIP pour générer les captions
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

def generate_caption(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(image, return_tensors="pt").to(device)
        out = model.generate(**inputs)
        return processor.decode(out[0], skip_special_tokens=True)
    except Exception as e:
        return f"error: {str(e)}"

records = []

for split in ["train", "val"]:
    split_path = os.path.join(base_dir, split)
    for class_name in os.listdir(split_path):
        class_dir = os.path.join(split_path, class_name)
        if not os.path.isdir(class_dir):
            continue

        # Récupérer les fiches maladies
        fiche = metadata.get(class_name.strip())
        if not fiche:
            print(f"⚠️ Classe non trouvée dans le JSON : {class_name}")
            continue

        for img_file in os.listdir(class_dir):
            if not img_file.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path_rel = os.path.join(split, class_name, img_file)
            img_path_abs = os.path.join(base_dir, img_path_rel)

            caption = generate_caption(img_path_abs)

            records.append({
                "split": split,
                "class": class_name,
                "image_path": img_path_rel.replace("\\", "/"),
                "caption": caption,
                "culture": fiche.get("culture", ""),
                "agent_causal": fiche.get("Agent causal", ""),
                "description": fiche.get("description", ""),
                "symptoms": fiche.get("symptoms", ""),
                "evolution": fiche.get("evolution", ""),
                "active_material": fiche.get("Name of active product material", ""),
                "treatment": fiche.get("treatment", "")
            })

# 📄 Enregistrement CSV + JSON
df = pd.DataFrame(records)
df.to_csv("plant_disease_dataset_with_captions.csv", index=False, encoding="utf-8")
with open("plant_disease_dataset_with_captions.json", "w", encoding="utf-8") as f:
    json.dump(records, f, indent=4, ensure_ascii=False)

print(f"\n✅ Dataset enrichi avec captions générées automatiquement :")
print("   - plant_disease_dataset_with_captions.csv")
print("   - plant_disease_dataset_with_captions.json")
