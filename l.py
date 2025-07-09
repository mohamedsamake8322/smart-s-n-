import re
def corriger_json_multiblocs(fichier_entree, fichier_sortie):
    with open(fichier_entree, 'r', encoding='utf-8') as f:
        contenu = f.read()

    # On sépare les blocs JSON qui commencent par {"cultures":
    blocs = re.split(r'(?=\{\s*"cultures"\s*:)', contenu.strip())

    # Nettoyer, supprimer virgules en trop, etc.
    blocs_nettoyes = []
    for bloc in blocs:
        bloc = bloc.strip()
        if bloc.endswith(','):
            bloc = bloc[:-1]
        blocs_nettoyes.append(bloc)

    # Recomposition
    contenu_valide = '[\n' + ',\n'.join(blocs_nettoyes) + '\n]'

    with open(fichier_sortie, 'w', encoding='utf-8') as f:
        f.write(contenu_valide)

    print(f"✅ Fichier corrigé écrit dans : {fichier_sortie}")

# Exemple d’utilisation
corriger_json_multiblocs(
    r"C:\plateforme-agricole-complete-v2\besoins_des_plantes_en_nutriments.json",
    r"C:\plateforme-agricole-complete-v2\besoins_correctement_formates.json"
)
