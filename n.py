import json

# 📁 Fichiers
input_path = r"C:/plateforme-agricole-complete-v2/plantdataset/maladie_dataset.json"
output_path = r"C:/plateforme-agricole-complete-v2/plantdataset/maladie_dataset.jsonl"

# 🔄 Transformation
with open(input_path, encoding="utf-8") as f_in, open(output_path, "w", encoding="utf-8") as f_out:
    data = json.load(f_in)
    for item in data:
        annotation = item.get("annotation", {})
        caption_parts = []

        # 📝 Choix des champs
        label = annotation.get("label", "").strip()
        symptoms = annotation.get("symptoms", "").strip()
        culture = annotation.get("culture", "").strip()

        if label:
            caption_parts.append(f"Disease: {label}")
        if culture:
            caption_parts.append(f"Affects: {culture}")
        if symptoms:
            caption_parts.append(f"Symptoms: {symptoms}")

        caption = " ".join(caption_parts).strip()
        record = {
            "image": item.get("path", ""),
            "caption": caption
        }
        f_out.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"✅ Export JSONL terminé : {output_path}")
