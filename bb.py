import json
import os
from deep_translator import GoogleTranslator

# Dossier contenant les fichiers JSON
folder_path = r"C:\plateforme-agricole-complete-v2"

# Noms des fichiers
files = ["mapping_fiches_maladies.json", "repartition_maladies_afrique.json"]

# Fonction récursive de traduction
def translate_content(content):
    if isinstance(content, dict):
        return {translate_content(k): translate_content(v) for k, v in content.items()}
    elif isinstance(content, list):
        return [translate_content(item) for item in content]
    elif isinstance(content, str):
        try:
            return GoogleTranslator(source='auto', target='en').translate(text=content)
        except Exception as e:
            print(f"Erreur de traduction: {e}")
            return content
    else:
        return content

# Traitement des fichiers
for file_name in files:
    file_path = os.path.join(folder_path, file_name)

    # Charger le contenu JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Traduire le contenu
    translated_data = translate_content(data)

    # Enregistrer le résultat dans un nouveau fichier
    translated_file_path = os.path.join(folder_path, f"EN_{file_name}")
    with open(translated_file_path, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, ensure_ascii=False, indent=2)

    print(f"{file_name} traduit et sauvegardé sous {translated_file_path}")
