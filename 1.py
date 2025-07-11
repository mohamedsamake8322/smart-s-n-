import json
import os

# 📁 Chemin du fichier
file_path = r"C:\plateforme-agricole-complete-v2\plantdataset\EN_mapping_fiches_maladies.json"
output_path = file_path.replace(".json", "_with_emojis.json")

# 🌟 Dictionnaire d'emojis par champ (avec clé exacte)
emojis = {
    "culture": "🌱",
    "causal_agent": "🦠",
    "description": "📝",
    "symptoms": "⚠️",
    "evolution": "🔁",
    "Name of active product material": "💊",
    "treatment": "🛠️"
}

# 🔄 Charger le JSON
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# ✨ Ajouter les emojis aux champs concernés
for disease, info in data.items():
    for key, emoji in emojis.items():
        value = info.get(key)
        if isinstance(value, str) and not value.startswith(emoji):
            info[key] = f"{emoji} {value}"

# 💾 Sauvegarder dans un nouveau fichier
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Emojis ajoutés avec succès ! Fichier sauvegardé sous : {output_path}")
