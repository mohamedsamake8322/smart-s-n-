import json
import requests
import time

API_KEY = "bf46e370-3a4a-4338-8a79-d9aba6c289ed:fx"  # Remplace par ta clé DeepL API

SUPPORTED_LANGUAGES = [
    "en", "zh", "hi", "es", "fr", "sw", "ha", "yo", "ig", "am",
    "om", "rw", "ln", "sn", "tn", "st", "mg", "wo", "bm", "ts"
]

def deepl_translate(text, target_lang):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": API_KEY,
        "text": text,
        "source_lang": "EN",
        "target_lang": target_lang.upper()
    }
    try:
        response = requests.post(url, data=params)
        result = response.json()
        return result["translations"][0]["text"]
    except Exception as e:
        print(f"❌ DeepL ERROR ({target_lang}): {e}")
        return f"[ERROR: {e}]"

# Charger les fiches
with open(r"C:\plateforme-agricole-complete-v2\EN_mapping_fiches_maladies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for disease_name, entry in data.items():
    entry["translations"] = {}
    for lang in SUPPORTED_LANGUAGES:
        entry["translations"][lang] = {
            "culture": deepl_translate(entry["culture"], lang),
            "Agent causal": deepl_translate(entry["Agent causal"], lang),
            "description": deepl_translate(entry["description"], lang),
            "symptoms": deepl_translate(entry["symptoms"], lang),
            "evolution": deepl_translate(entry["evolution"], lang),
            "Name of active product material": deepl_translate(entry["Name of active product material"], lang),
            "treatment": deepl_translate(entry["treatment"], lang)
        }
        time.sleep(0.5)  # anti-blocage entre les requêtes

# Sauvegarde
with open(r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, indent=2, ensure_ascii=False)

print("✅ Traduction DeepL terminée !")
