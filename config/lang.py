import os
from google.cloud import translate_v2 as translate
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

# Initialise le client Google Translate avec ta clé API
client = translate.Client.from_service_account_json(os.getenv("GOOGLE_KEY_PATH"))

# Fonction universelle de traduction
@lru_cache(maxsize=5000)
def t(texte_fr: str, langue_cible: str = "fr") -> str:
    if langue_cible == "fr":
        return texte_fr
    try:
        resultat = client.translate(texte_fr, target_language=langue_cible)
        return resultat["translatedText"]
    except Exception:
        return texte_fr
