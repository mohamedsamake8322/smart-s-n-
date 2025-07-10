import json
import os
from google.cloud import translate
client = translate.TranslationServiceClient()

# Authentification
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\plateforme-agricole-complete-v2\plant-ai-mohamed-tpu-b154d2918738.json"
translate_client = translate.Client()

# Langues cibles
SUPPORTED_LANGUAGES = {
    "en": "English", "zh": "中文", "hi": "हिन्दी", "es": "Español", "fr": "Français",
    "sw": "Kiswahili", "ha": "Hausa", "yo": "Yorùbá", "ig": "Igbo", "am": "አማርኛ",
    "om": "Oromoo", "rw": "Kinyarwanda", "ln": "Lingála", "sn": "Shona", "tn": "Setswana",
    "st": "Sesotho", "mg": "Malagasy", "wo": "Wolof", "bm": "Bambara", "ts": "Xitsonga"
}

def translate_text(text, target_lang):
    result = translate_client.translate(text, target_language=target_lang)
    return result["translatedText"]

# Charger ton fichier de base
with open(r"C:\plateforme-agricole-complete-v2\deficies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Traduction
for element, entry in data["deficiencies"].items():
    entry["translations"] = {}
    for lang_code in SUPPORTED_LANGUAGES:
        translated = {
            "symptoms": translate_text(entry["symptoms"], lang_code),
            "deficiency": translate_text(entry["effects"]["deficiency"], lang_code),
            "excess": translate_text(entry["effects"]["excess"], lang_code),
            "correction": translate_text(entry["correction"], lang_code)
        }
        entry["translations"][lang_code] = translated

# Sauvegarde finale
with open(r"C:\plateforme-agricole-complete-v2\deficiencies_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, indent=2, ensure_ascii=False)
