# -*- coding: utf-8 -*-
import json
import os
import sys
import codecs

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("utf-8", errors="ignore"))

dataset_dir = "plantdataset"
jsonl_files = [
    "maladie_dataset_converted.jsonl",
    "fiche_stress_complete_converted.jsonl",
    "fiche_carence_complete_converted.jsonl"
]

# 🔍 Index : {basename → relative_path}
indexed_images = {}
for subdir in ["train", "val"]:
    for root, dirs, files in os.walk(os.path.join(dataset_dir, subdir)):
        for f in files:
            path_rel = os.path.relpath(os.path.join(root, f), dataset_dir)
            indexed_images[f.lower()] = path_rel.replace("\\", "/")

safe_print("[INFO] Indexation terminée : {} fichiers trouvés.".format(len(indexed_images)))

image_to_text = {}

def normalize_path(p):
    return os.path.basename(p.replace("\\", "/")).lower()

for jsonl_file in jsonl_files:
    jsonl_path = os.path.join(dataset_dir, jsonl_file)
    if not os.path.isfile(jsonl_path):
        safe_print("[WARN] Fichier non trouvé : {}".format(jsonl_path))
        continue

    with codecs.open(jsonl_path, "r", "utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())

                # 💡 maladie_dataset
                if "image" in entry and "caption" in entry:
                    raw_name = normalize_path(entry["image"])
                    description = entry["caption"]

                    resolved = indexed_images.get(raw_name)
                    if resolved and description:
                        image_to_text[resolved] = description.strip()

                # 💡 fiche_carence / fiche_stress
                elif "images" in entry and isinstance(entry["images"], list):
                    for img_entry in entry["images"]:
                        raw_name = normalize_path(img_entry.get("path") or img_entry.get("filename"))
                        annotation = img_entry.get("annotation", {})
                        desc_parts = [
                            annotation.get("label", ""),
                            annotation.get("symptoms", ""),
                            annotation.get("correction", "")
                        ]
                        description = " | ".join(filter(None, desc_parts))
                        resolved = indexed_images.get(raw_name)
                        if resolved and description:
                            image_to_text[resolved] = description.strip()

            except Exception as e:
                safe_print("[ERROR] Ligne {} invalide dans {} → {}".format(line_num, jsonl_file, str(e)))
                continue

# 🔧 Pré-nettoyage Unicode avant sauvegarde
def unicode_clean(data):
    cleaned = {}
    for k, v in data.items():
        try:
            k_utf = k.decode("utf-8") if isinstance(k, str) else k
            v_utf = v.decode("utf-8") if isinstance(v, str) else v
            cleaned[k_utf] = v_utf
        except:
            cleaned[k] = v
    return cleaned

output_path = os.path.join(dataset_dir, "image_text_mapping.json")
try:
    safe_data = unicode_clean(image_to_text)
    with codecs.open(output_path, "w", "utf-8") as f_out:
        json.dump(safe_data, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
    safe_print("[✅] Mapping créé avec {} associations.".format(len(safe_data)))
    safe_print("[📁] Sauvegardé dans : {}".format(output_path))
except Exception as e:
    safe_print("[❌] Erreur lors de la sauvegarde : {}".format(str(e)))
