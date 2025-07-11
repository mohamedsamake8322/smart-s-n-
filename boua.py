#Mapper carence
import os
import json

# 📁 Chemins
base_path = r"C:/Users/moham/Documents/1"
json_path = os.path.join(base_path, "deficiencies_multilingual.json")
output_dir = os.path.join(base_path, "fiche_par_carence")
os.makedirs(output_dir, exist_ok=True)

# 📖 Charger le JSON
with open(json_path, encoding="utf-8") as f:
    data = json.load(f).get("deficiencies", {})

# 🔄 Normalisation
def normalize(name):
    return name.lower().strip()

# 📦 Traitement
for key, content in data.items():
    folder_name = key.strip()
    folder_path = os.path.join(base_path, folder_name)
    if not os.path.isdir(folder_path):
        continue

    fiche = {
        "element": content.get("element", ""),
        "code": key,
        "symptoms": content.get("symptoms", ""),
        "effects": content.get("effects", {}),
        "correction": content.get("correction", ""),
        "translations": content.get("translations", {}),
        "images": []
    }

    # 📸 Ajouter les images du dossier
    for img in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, img)):
            fiche["images"].append({
                "filename": img,
                "path": os.path.join(folder_name, img)
            })

    # 💾 Sauvegarde
    out_path = os.path.join(output_dir, f"{folder_name}.json")
    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(fiche, f_out, indent=4, ensure_ascii=False)

print(f"✅ Fiches de carences générées dans : {output_dir}")
