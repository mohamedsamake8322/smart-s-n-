import json
import requests
import time

# Langues cibles
SUPPORTED_LANGUAGES = [
    "en", "zh", "hi", "es", "fr", "sw", "ha", "yo", "ig", "am",
    "om", "rw", "ln", "sn", "tn", "st", "mg", "wo", "bm", "ts"
]

def libre_translate(text, target):
    try:
        response = requests.post("https://libretranslate.com/translate", json={
            "q": text,
            "source": "en",
            "target": target,
            "format": "text"
        })
        data = response.json()
        if "translatedText" in data:
            return data["translatedText"]
        elif "error" in data:
            print(f"❌ Erreur LibreTranslate ({target}): {data['error']}")
            return f"[ERROR: {data['error']}]"
        else:
            print(f"❌ Réponse inattendue ({target}):", data)
            return "[ERROR: Unexpected response]"
    except Exception as e:
        print(f"❌ Exception JSON ({target}): {e}")
        return "[ERROR: Invalid JSON]"

# Charger le fichier source
with open(r"C:\plateforme-agricole-complete-v2\EN_mapping_fiches_maladies.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Traduction par maladie
for disease_name, entry in data.items():
    entry["translations"] = {}
    for lang in SUPPORTED_LANGUAGES:
        entry["translations"][lang] = {
            "culture": libre_translate(entry["culture"], lang),
            "Agent causal": libre_translate(entry["Agent causal"], lang),
            "description": libre_translate(entry["description"], lang),
            "symptoms": libre_translate(entry["symptoms"], lang),
            "evolution": libre_translate(entry["evolution"], lang),
            "Name of active product material": libre_translate(entry["Name of active product material"], lang),
            "treatment": libre_translate(entry["treatment"], lang)
        }
        time.sleep(0.5)  # Anti-blocage entre les requêtes

# Sauvegarde finale
with open(r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies_multilingual.json", "w", encoding="utf-8") as f_out:
    json.dump(data, f_out, indent=2, ensure_ascii=False)

print("✅ Traduction terminée avec LibreTranslate.")
