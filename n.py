import json
import os
from deep_translator import deep-translatorlator, exceptions

# 📁 Fichiers
source_path = r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies.json"
output_path = r"C:\plateforme-agricole-complete-v2\mapping_fiches_maladies_en.json"

# 🏷️ Clés à traduire
champ_mapping = {
    "culture": "crop",
    "Agent causal": "causal agent",
    "description": "description",
    "symptômes": "symptoms",
    "évolution": "development",
    "Nom de la matière active du produit": "active ingredient",
    "traitement": "treatment"
}

# 🌐 Fonction de traduction sécurisée
def translate_text(text):
    if isinstance(text, str) and text.strip():
        try:
            return deep-translatorlator(source='fr', target='en').translate(text)
        except exceptions.TranslationNotFound as e:
            print(f"⚠️ Traduction introuvable : « {text} » → conservé tel quel.")
        except Exception as e:
            print(f"⚠️ Erreur inattendue sur « {text} » → {e}")
    return text  # On renvoie le texte original si vide ou en cas d’erreur

# 📥 Charger le fichier source
with open(source_path, "r", encoding="utf-8") as f:
    fiches = json.load(f)

translated = {}
total = len(fiches)

# 🔄 Boucle de traduction
for i, (maladie, infos) in enumerate(fiches.items(), 1):
    print(f"\n🔄 [{i}/{total}] Traduction de : {maladie}")
    translated_name = translate_text(maladie)
    translated_infos = {}
    for fr_key, value in infos.items():
        en_key = champ_mapping.get(fr_key, fr_key)
        translated_value = translate_text(value)
        translated_infos[en_key] = translated_value
        print(f"   ↳ Champ « {fr_key} » traduit.")
    translated[translated_name] = translated_infos

# 💾 Sauvegarde
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(translated, f_out, indent=2, ensure_ascii=False)

print(f"\n✅ Traduction terminée. Fichier enregistré dans : {output_path}")
