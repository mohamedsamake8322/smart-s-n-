import json
import time
from utils.disease_database import DiseaseDatabase
from deep_translator import GoogleTranslator

# ✅ 1. Charger la base principale
base_main = DiseaseDatabase().diseases_data

# ✅ 2. Charger la base dynamique
with open("data/extended_disease_database.json", "r", encoding="utf-8") as f:
    base_extended = json.load(f)

# ✅ 3. Fusionner les deux
combined = {**base_main, **base_extended}

# ✅ 4. Traduction avec suivi
def translate_entry(entry: dict, source="fr", target="en") -> dict:
    translated = {}
    for key, value in entry.items():
        try:
            if isinstance(value, str):
                translated[key] = GoogleTranslator(source=source, target=target).translate(value)
            elif isinstance(value, list):
                translated[key] = [
                    GoogleTranslator(source=source, target=target).translate(v)
                    if isinstance(v, str) else v for v in value
                ]
            else:
                translated[key] = value
        except Exception as e:
            print(f"❌ Erreur traduction [{key}]: {e}")
            translated[key] = value
    return translated

# ✅ 5. Traduire avec affichage progressif
translated_list = []
total = len(combined)
for i, (name, info) in enumerate(combined.items(), 1):
    print(f"[{i}/{total}] Traduction de: {name}")
    entry = info.copy()
    entry.setdefault("name", name)
    translated = translate_entry(entry)
    translated_list.append(translated)

# ✅ 6. Sauvegarde
with open("data/all_diseases_translated.json", "w", encoding="utf-8") as f:
    json.dump(translated_list, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fusion + traduction terminée avec succès ({len(translated_list)} maladies) 🎉")
