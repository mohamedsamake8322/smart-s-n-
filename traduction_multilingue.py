import json
from google.cloud import translate_v2 as translate

# 📍 Chemin vers ton fichier de clé API JSON téléchargé depuis Google Console
CHEMIN_CLE = "C:/plateforme-agricole-complete-v2/plant-ai-mohamed-tpu-b154d2918738.json"
 # Ex: "mon_projet_plantai_tpu.json"

# Liste des langues cibles (codes ISO 639-1)
LANGUES_CIBLES = [
  "en", "zh", "hi", "es", "fr",  # Monde
  "sw", "ha", "yo", "ig", "am", "om", "rw", "ln", "sn", "tn",
  "st", "mg", "wo", "bm", "ts"  # Afrique
]

def charger_textes(fichier_json):
    with open(fichier_json, "r", encoding="utf-8") as f:
        return json.load(f)

def sauvegarder_resultat(data, fichier_sortie):
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def traduire_interface(source_texts):
    client = translate.Client.from_service_account_json(CHEMIN_CLE)
    resultats = {}

    for clé, texte in source_texts.items():
        resultats[clé] = {}
        for langue in LANGUES_CIBLES:
            traduction = client.translate(texte, target_language=langue)
            resultats[clé][langue] = traduction["translatedText"]

    return resultats

# 🔁 Utilisation du script
if __name__ == "__main__":
    fichiersource = "interface_fr.json"
    fichierfinal = "interface_multilangue.json"

    textes = charger_textes(fichiersource)
    traductions = traduire_interface(textes)
    sauvegarder_resultat(traductions, fichierfinal)

    print("✅ Traduction terminée. Fichier généré :", fichierfinal)
