import json
import os
from google.cloud import translate

# Authentification
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\plateforme-agricole-complete-v2\plant-ai-mohamed-tpu-b154d2918738.json"
client = translate.TranslationServiceClient()

# Infos projet
project_id = "plant-ai-mohamed-tpu"
location = "global"
parent = f"projects/{project_id}/locations/{location}"

# Langues cibles
SUPPORTED_LANGUAGES = {
    "en": "English", "zh": "中文", "hi": "हिन्दी", "es": "Español", "fr": "Français",
    "sw": "Kiswahili", "ha": "Hausa", "yo": "Yorùbá", "ig": "Igbo", "am": "አማርኛ",
    "om": "Oromoo", "rw": "Kinyarwanda", "ln": "Lingála", "sn": "Shona", "tn": "Setswana",
    "st": "Sesotho", "mg": "Malagasy", "wo": "Wolof", "bm": "Bambara", "ts": "Xitsonga"
}

def translate_text(text, target_lang):
    response = client.translate_text(
        contents=[text],
        target_language_code=target_lang,
        parent=parent,
        mime_type="text/plain"
    )
    return response.translations[0].translated_text

# Charger le fichier source
with open(r"C:\plateforme-agricole-complete-v2\EN_repartition_maladies_afrique.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Structure de sortie
translated_data = {}

for disease_name, countries in data.items():
    translated_data[disease_name] = {
        "regions": countries,
        "translations": {}
    }
    for lang_code in SUPPORTED_LANGUAGES:
        translated_name = translate_text(disease_name, lang_code)
        translated_data[disease_name]["translations"][lang_code] = translated_name

# Sauvegarde finale
with open(r"C:\plateforme-agricole-complete-v2\repartition_maladies_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(translated_data, f_out, indent=2, ensure_ascii=False)
