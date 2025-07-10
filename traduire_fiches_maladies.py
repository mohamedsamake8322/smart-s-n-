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
with open(r"C:\plateforme-agricole-complete-v2\EN_mapping_fiches_maladies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Traduction multilingue
for disease_name, entry in data.items():
    entry["translations"] = {}
    for lang_code in SUPPORTED_LANGUAGES:
        entry["translations"][lang_code] = {
            "culture": translate_text(entry["culture"], lang_code),
            "Agent causal": translate_text(entry["Agent causal"], lang_code),
            "description": translate_text(entry["description"], lang_code),
            "symptoms": translate_text(entry["symptoms"], lang_code),
            "evolution": translate_text(entry["evolution"], lang_code),
            "Name of active product material": translate_text(entry["Name of active product material"], lang_code),
            "treatment": translate_text(entry["treatment"], lang_code)
        }

# Sauvegarde finale
with open(r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, indent=2, ensure_ascii=False)
