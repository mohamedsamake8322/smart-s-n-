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

# Chargement du fichier
with open(source_path, "r", encoding="utf-8") as f:
    fiches = json.load(f)

translated = {}
total = len(fiches)

# Traduction avec suivi
for i, (maladie, infos) in enumerate(fiches.items(), 1):
    print(f"🔄 [{i}/{total}] Traduction de : {maladie}")
    translated_name = translate_text(maladie)
    translated_infos = {}
    for fr_key, value in infos.items():
        en_key = champ_mapping.get(fr_key, fr_key)
        translated_value = translate_text(value)
        translated_infos[en_key] = translated_value
        print(f"   ↳ Champ « {fr_key} » traduit.")
    translated[translated_name] = translated_infos

# Sauvegarde
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(translated, f_out, indent=2, ensure_ascii=False)

print("\n✅ Traduction terminée. Fichier créé :", output_path)
