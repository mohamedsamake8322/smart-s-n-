from utils.disease_database import DiseaseDatabase
from utils.disease_database_extended import DISEASE_DATABASE
from deep_translator import GoogleTranslator
import json

def translate_dict(d: dict, source_lang: str = "fr", target_lang: str = "en") -> dict:
    translated = {}
    for key, value in d.items():
        try:
            if isinstance(value, str):
                translated[key] = GoogleTranslator(source=source_lang, target=target_lang).translate(value)
            elif isinstance(value, list):
                translated[key] = [
                    GoogleTranslator(source=source_lang, target=target_lang).translate(v)
                    if isinstance(v, str) else v for v in value
                ]
            else:
                translated[key] = value
        except Exception as e:
            print(f"❌ Translation failed for key '{key}': {e}")
            translated[key] = value
    return translated

# Chargement des deux bases
db1 = DiseaseDatabase().diseases_data  # dict[str, dict]
db2 = DISEASE_DATABASE                 # dict[str, dict]

# Fusion (priorité à db1)
combined = {**db2, **db1}

# Traduction de chaque entrée
translated_list = []
for key, data in combined.items():
    entry = data.copy()
    entry.setdefault("name", key)
    translated_entry = translate_dict(entry)
    translated_list.append(translated_entry)

# Sauvegarde
with open("data/all_diseases_translated.json", "w", encoding="utf-8") as f:
    json.dump(translated_list, f, ensure_ascii=False, indent=2)

print(f"✅ Fusion + traduction terminée avec {len(translated_list)} maladies.")
