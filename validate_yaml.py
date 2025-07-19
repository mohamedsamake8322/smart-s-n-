import yaml
import sys

def validate_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print("✅ Fichier YAML valide :")
        print(f"Nom du produit : {data.get('name', 'inconnu')}")
        print(f"Bandes disponibles : {[m['name'] for m in data.get('measurements', [])]}")
    except yaml.YAMLError as exc:
        print("❌ Erreur de parsing YAML :")
        print(exc)
    except FileNotFoundError:
        print("❌ Fichier introuvable :", file_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage : python validate_yaml.py <chemin_du_fichier.yaml>")
    else:
        validate_yaml(sys.argv[1])
