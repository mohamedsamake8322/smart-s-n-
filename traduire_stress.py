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

# Charger le fichier source des stress
with open(r"C:\plateforme-agricole-complete-v2\stress.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Traduction multilingue pour chaque type de stress
for stress_type, entry in data["abiotic_stress"].items():
    entry["translations"] = {}
    for lang_code in SUPPORTED_LANGUAGES:
        entry["translations"][lang_code] = {
            "symptoms": translate_text(entry["symptoms"], lang_code),
            "low_effect": translate_text(entry["effects"].get("low_temperature", entry["effects"].get("deficiency", "")), lang_code),
            "high_effect": translate_text(entry["effects"].get("high_temperature", entry["effects"].get("excess", "")), lang_code),
            "impact_on_yield": translate_text(entry["impact_on_yield"], lang_code),
            "correction": translate_text(entry["correction"], lang_code)
        }

# Sauvegarde finale
with open(r"C:\plateforme-agricole-complete-v2\stress_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, indent=2, ensure_ascii=False)
