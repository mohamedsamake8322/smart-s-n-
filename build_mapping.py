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
subdirs = ["train", "val"]
jsonl_files = [
    "maladie_dataset.jsonl",
    "fiche_stress_complete.jsonl",
    "fiche_carence_complete.jsonl"
]

image_to_text = {}

def normalize_path(p):
    return p.replace("\\", "/")

def find_image_path(relative_name):
    for subdir in subdirs:
        for root, dirs, files in os.walk(os.path.join(dataset_dir, subdir)):
            for f in files:
                if f == os.path.basename(relative_name):
                    candidate = os.path.join(root, f)
                    rel_path = os.path.relpath(candidate, dataset_dir)
                    return rel_path.replace("\\", "/")
    return None

for jsonl_file in jsonl_files:
    jsonl_path = os.path.join(dataset_dir, jsonl_file)
    if not os.path.isfile(jsonl_path):
        safe_print("[WARN] Fichier non trouvé : {}".format(jsonl_path))
        continue

    with codecs.open(jsonl_path, "r", "utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())

                # 📦 Maladie dataset
                if "image" in entry and "caption" in entry:
                    raw_path = normalize_path(entry["image"])
                    description = entry["caption"]

                # 📦 Stress & carence (listes d’images)
                elif "images" in entry and isinstance(entry["images"], list):
                    for img_entry in entry["images"]:
                        raw_path = normalize_path(img_entry.get("path") or img_entry.get("filename"))
                        annotation = img_entry.get("annotation", {})
                        description_parts = [
                            annotation.get("label", ""),
                            annotation.get("symptoms", ""),
                            annotation.get("correction", "")
                        ]
                        description = " | ".join(filter(None, description_parts))
                else:
                    continue

                resolved_path = find_image_path(raw_path)
                if resolved_path and description:
                    image_to_text[resolved_path] = description.strip()

            except Exception as e:
                safe_print("[ERROR] Ligne {} invalide dans {} → {}".format(line_num, jsonl_file, str(e)))
                continue

output_path = os.path.join(dataset_dir, "image_text_mapping.json")
try:
    with codecs.open(output_path, "w", "utf-8") as f_out:
        json.dump(image_to_text, f_out, ensure_ascii=False, indent=2)
    safe_print("[✅] Mapping créé avec {} associations.".format(len(image_to_text)))
    safe_print("[📁] Sauvegardé dans : {}".format(output_path))
except Exception as e:
    safe_print("[❌] Erreur lors de la sauvegarde : {}".format(str(e)))
