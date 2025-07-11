import os
import json

# 📁 Chemins
base_path = r"C:/Users/moham/Documents/2"
json_path = os.path.join(base_path, "stress_multilingual.json")
output_dir = os.path.join(base_path, "fiche_par_stress")
os.makedirs(output_dir, exist_ok=True)

# 📖 Charger le JSON
with open(json_path, encoding="utf-8") as f:
    stress_data = json.load(f).get("abiotic_stress", {})

# 🔄 Traitement pour chaque stress
for key, content in stress_data.items():
    folder_name = key.strip()
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.isdir(folder_path):
        print(f"⚠️ Dossier introuvable pour : {folder_name}")
        continue

    # 🧠 Annotation commune à toutes les images
    annotation = {
        "type": "stress",
        "label": content.get("name", ""),
        "symptoms": content.get("symptoms", ""),
        "effects": content.get("effects", {}),
        "impact_on_yield": content.get("impact_on_yield", ""),
        "correction": content.get("correction", ""),
        "translations": content.get("translations", {})
    }

    fiche = {
        "code": key,
        "label": content.get("name", ""),
        "images": []
    }

    # 📸 Annoter chaque image
    for img in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, img)):
            fiche["images"].append({
                "filename": img,
                "path": os.path.join(folder_name, img),
                "annotation": annotation
            })

    # 💾 Sauvegarde JSON
    out_path = os.path.join(output_dir, f"{folder_name}.json")
    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(fiche, f_out, indent=4, ensure_ascii=False)

    print(f"✅ Fiche annotée : {folder_name}")

print(f"\n🎯 Toutes les fiches stress annotées sont dans : {output_dir}")
