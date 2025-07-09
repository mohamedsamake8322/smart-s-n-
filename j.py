import json

def flatten_cultures(cultures_dict, result=None):
    if result is None:
        result = {}
    for key, data in cultures_dict.items():
        if key == "cultures":
            flatten_cultures(data, result)
        else:
            result[key] = data
            # Si sous-élément "cultures" existe, traiter récursivement
            if "cultures" in data:
                flatten_cultures(data["cultures"], result)
                del data["cultures"]  # Nettoyage
    return result

# Charger le fichier JSON original
with open("besoins_des_plantes_en_nutriments.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Appliquer le nettoyage
clean_cultures = flatten_cultures(raw_data.get("cultures", {}))

# Reconstruire le JSON corrigé
clean_data = {
    "sources": raw_data.get("sources", []),
    "cultures": clean_cultures
}

# Sauvegarder le nouveau fichier
with open("besoins_correcte.json", "w", encoding="utf-8") as f:
    json.dump(clean_data, f, indent=4, ensure_ascii=False)

print("✅ Fichier JSON corrigé enregistré avec succès.")
