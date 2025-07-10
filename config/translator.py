import os
import json
from functools import lru_cache
from typing import Literal
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate

load_dotenv()

# Langues supportées
SUPPORTED_LANGUAGES = [
    "en", "zh", "hi", "es", "fr", "sw", "ha", "yo", "ig", "am",
    "om", "rw", "ln", "sn", "tn", "st", "mg", "wo", "bm", "ts"
]

# Chemin du cache local
CACHE_PATH = "translation_cache.json"

# Initialiser le client Google Translate
client = translate.Client.from_service_account_json(
    os.getenv("GOOGLE_KEY_PATH"),
    timeout=10
)

# Charger ou créer le cache
def init_translation_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

translation_cache = init_translation_cache()

# Sauvegarder le cache modifié
def save_cache():
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)

# Traduction avec cache intelligent
@lru_cache(maxsize=5000)
def translate_text_dynamic(text: str, lang: str = "fr") -> str:
    if lang not in SUPPORTED_LANGUAGES or lang == "fr":
        return text

    # Clé unique dans le cache
    key = f"{text}__{lang}"
    if key in translation_cache:
        return translation_cache[key]

    try:
        result = client.translate(text, target_language=lang)
        translated = result["translatedText"]
        translation_cache[key] = translated
        save_cache()
        return translated
    except Exception as e:
        print(f"[⚠️] Erreur de traduction : {e}")
        return text
