import os
import logging
from functools import lru_cache
from typing import Literal
from dotenv import load_dotenv # type: ignore
from google.cloud import translate_v2 as translate

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Toutes vos 20 langues supportées avec leur nom d'affichage
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "中文",
    "hi": "हिन्दी",
    "es": "Español",
    "fr": "Français",
    "sw": "Kiswahili",
    "ha": "Hausa",
    "yo": "Yorùbá",
    "ig": "Igbo",
    "am": "አማርኛ",
    "om": "Oromoo",
    "rw": "Kinyarwanda",
    "ln": "Lingála",
    "sn": "Shona",
    "tn": "Setswana",
    "st": "Sesotho",
    "mg": "Malagasy",
    "wo": "Wolof",
    "bm": "Bambara",
    "ts": "Xitsonga"
}

# Type hint avec toutes vos langues
SupportedLanguage = Literal[
    "en", "zh", "hi", "es", "fr", "sw", "ha",
    "yo", "ig", "am", "om", "rw", "ln", "sn",
    "tn", "st", "mg", "wo", "bm", "ts"
]

client = translate.Client.from_service_account_json(
    os.getenv("GOOGLE_KEY_PATH"),
    timeout=10  # Add timeout
)

@lru_cache(maxsize=5000)
def translate_text(
    text: str,
    target_language: SupportedLanguage = "fr"
) -> str:
    """Translate text to target language using Google Cloud Translation API.

    Args:
        text: Text to translate
        target_language: ISO 639-1 language code

    Returns:
        Translated text or original text if translation fails
    """
    if target_language == "fr":
        return text

    try:
        result = client.translate(text, target_language=target_language)
        return resultranslate_text("translatedText", selected_lang)
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return text
