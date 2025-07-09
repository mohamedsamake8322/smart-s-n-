#Pour traduire json
import json
from deep_translator import GoogleTranslator

def translate_json(obj, source_lang="fr", target_lang="en"):
    if isinstance(obj, dict):
        return {translate_json(k, source_lang, target_lang): translate_json(v, source_lang, target_lang) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [translate_json(item, source_lang, target_lang) for item in obj]
    elif isinstance(obj, str):
        return GoogleTranslator(source=source_lang, target=target_lang).translate(obj)
    else:
        return obj  # Keep numbers and other types unchanged

# Charger le fichier JSON d'origine
with open("C:\\plateforme-agricole-complete-v2\\besoins des plantes en nutriments.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Appliquer la traduction
translated_data = translate_json(raw_data)

# Sauvegarder le fichier traduit
with open("besoins_en_nutriments_en.json", "w", encoding="utf-8") as f:
    json.dump(translated_data, f, indent=4, ensure_ascii=False)

print("✅ Fichier JSON traduit en anglais avec succès.")
