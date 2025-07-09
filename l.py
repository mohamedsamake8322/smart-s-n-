import json

def uniformiser_json_agronomique(fichier_entree, fichier_sortie):
    cultures_fusionnees = {}

    # Lecture du fichier brut (avec plusieurs objets JSON à la suite)
    with open(fichier_entree, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # Séparation approximative des blocs JSON par heuristique
    blocs = contenu.split('}\n{')
    blocs = [b if b.startswith('{') else '{' + b for b in blocs]
    blocs = [b if b.endswith('}') else b + '}' for b in blocs]

    for bloc in blocs:
        try:
            json_obj = json.loads(bloc)
            if "cultures" in json_obj:
                for culture, contenu in json_obj["cultures"].items():
                    cultures_fusionnees[culture] = contenu
        except json.JSONDecodeError as e:
            print(f"❌ Erreur lors du parsing JSON d’un bloc : {e}")

    # Structure uniforme
    resultat = { "cultures": cultures_fusionnees }

    # Sauvegarde du JSON final propre
    with open(fichier_sortie, 'w', encoding='utf-8') as f_out:
        json.dump(resultat, f_out, ensure_ascii=False, indent=2)

    print(f"✅ Fichier nettoyé et restructuré enregistré dans : {fichier_sortie}")

# Exécution directe
fichier_source = r"C:\plateforme-agricole-complete-v2\besoins_des_plantes_en_nutriments.json"
fichier_destination = r"C:\plateforme-agricole-complete-v2\besoins_uniformises.json"

uniformiser_json_agronomique(fichier_source, fichier_destination)
