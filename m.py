import json
import os
from deep_translator import GoogleTranslator  # pip install deep-translator

# Chemin vers le fichier source
source_path = r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies.json"
output_path = r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies_en.json"

# Clés à traduire (et leur version anglaise)
champ_mapping = {
    "culture": "crop",
    "Agent causal": "causal agent",
    "description": "description",
    "symptômes": "symptoms",
    "évolution": "development",
    "Nom de la matière active du produit": "active ingredient",
    "traitement": "treatment"
}

# Fonction de traduction individuelle
def translate_text(text):
    if isinstance(text, str) and text.strip():
        return GoogleTranslator(source='fr', target='en').translate(text)
    return text

# Traduction de chaque fiche
with open(source_path, "r", encoding="utf-8") as f:
    fiches = json.load(f)

translated = {}

for maladie, infos in fiches.items():
    translated_name = translate_text(maladie)
    translated_infos = {}
    for fr_key, value in infos.items():
        en_key = champ_mapping.get(fr_key, fr_key)
        translated_infos[en_key] = translate_text(value)
    translated[translated_name] = translated_infos

# Sauvegarde dans un nouveau fichier
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(translated, f_out, indent=2, ensure_ascii=False)

print("Traduction terminée. Fichier créé :", output_path)
