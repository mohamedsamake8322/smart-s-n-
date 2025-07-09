import json
import re

def nettoyer_et_formater_json(fichier_entree, fichier_sortie):
    cultures_fusionnees = {}

    with open(fichier_entree, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Séparer chaque objet JSON contenant la clé "cultures"
    pattern = r'{[^{}]*"cultures"\s*:\s*{.*?}}'
    blocs_json = re.findall(pattern, contenu, re.DOTALL)

    for bloc in blocs_json:
        try:
            json_obj = json.loads(bloc)
            for culture, contenu in json_obj["cultures"].items():
                if culture in cultures_fusionnees:
                    print(f"⚠️ Duplication détectée pour la culture : {culture}")
                cultures_fusionnees[culture] = contenu
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing d’un bloc JSON : {e}")

    resultat = { "cultures": cultures_fusionnees }

    with open(fichier_sortie, 'w', encoding='utf-8') as f_out:
        json.dump(resultat, f_out, ensure_ascii=False, indent=2)

    print(f"\n✅ Formatage terminé avec succès. Fichier sauvegardé dans : {fichier_sortie}")

# === Configuration du chemin ===
fichier_source = r"C:\plateforme-agricole-complete-v2\besoins_des_plantes_en_nutriments.json"
fichier_formate = r"C:\plateforme-agricole-complete-v2\besoins_uniformises.json"

nettoyer_et_formater_json(fichier_source, fichier_formate)
