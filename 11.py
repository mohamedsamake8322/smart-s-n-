import json

# Charger le rapport existant
with open("C:/plateforme-agricole-complete-v2/plantdataset/maladie_matching_report.json", encoding="utf-8") as f:
    report = json.load(f)

# Seuil de confiance
THRESHOLD = 80
custom_map = {}

for folder_name, info in report.items():
    if info["status"] == "defined":
        custom_map[folder_name] = info["matched_name"]
    elif info["status"] == "undefined":
        en_score = info["suggestion_from_EN"]["score"]
        fr_score = info["suggestion_from_FR"]["score"]

        # Choix de la meilleure correspondance
        if en_score >= THRESHOLD or fr_score >= THRESHOLD:
            suggestion = (
                info["suggestion_from_EN"]["match"]
                if en_score >= fr_score
                else info["suggestion_from_FR"]["match"]
            )
            custom_map[folder_name] = suggestion

# Sauvegarde du mapping personnalisé
output_path = "C:/plateforme-agricole-complete-v2/plantdataset/custom_mapping.json"
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(custom_map, f_out, indent=4, ensure_ascii=False)

print(f"✅ Mapping personnalisé enregistré dans : {output_path}")
