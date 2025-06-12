
import tarfile
import os
import shutil
from datetime import datetime

def create_deployment_package():
    """Crée un package complet de déploiement de la plateforme agricole"""
    
    # Nom du package avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"plateforme-agricole-deployable-{timestamp}.tar.gz"
    
    print("🚀 Création du package de déploiement...")
    
    # Fichiers et dossiers à inclure
    files_to_include = [
        'app.py',
        'pages/',
        'utils/',
        'data/',
        'models/',
        'services/',
        'backend/',
        'frontend/',
        'deployment/',
        'documentation/',
        '.streamlit/',
        'setup_requirements.txt',
        'pyproject.toml'
    ]
    
    # Créer l'archive tar.gz
    with tarfile.open(package_name, "w:gz") as tar:
        for item in files_to_include:
            if os.path.exists(item):
                print(f"📁 Ajout de {item}...")
                tar.add(item, arcname=item)
        
        # Créer un README spécial pour le déploiement
        readme_content = """# 🌾 Plateforme d'Analyse Agricole IA - Package de Déploiement

## 🚀 Déploiement Rapide sur Streamlit Cloud

### Étape 1: GitHub
1. Créez un nouveau repository sur GitHub (public)
2. Uploadez tous ces fichiers dans le repository
3. Commitez avec "Initial commit"

### Étape 2: Streamlit Cloud
1. Allez sur https://share.streamlit.io
2. Connectez votre GitHub
3. Sélectionnez votre repository
4. Fichier principal: `app.py`
5. Cliquez "Deploy!"

### Étape 3: Configuration
L'application utilise `setup_requirements.txt` pour les dépendances.
Streamlit Cloud installera automatiquement tous les packages nécessaires.

## 📱 URL de votre Application
Votre app sera disponible à: `https://[nom-choisi].streamlit.app`

## ✅ Fonctionnalités Incluses
- Dashboard agricole interactif
- Prédictions IA (Random Forest, XGBoost)
- Analyse météorologique
- Surveillance du sol
- Détection des maladies
- Upload de données CSV/Excel

## 📊 Données Incluses
- 500 enregistrements agricoles
- 365 jours de données météo
- 155 mesures de sol
- Modèles IA pré-entraînés

## 🆓 Coût Total: 0€
- GitHub: Gratuit (repository public)
- Streamlit Cloud: Gratuit
- Domaine: Inclus (.streamlit.app)

## 📞 Support
En cas de problème:
1. Vérifiez que tous les fichiers sont uploadés
2. Repository doit être PUBLIC
3. Fichier principal: app.py
4. Redéployez si nécessaire

Temps de déploiement: 2-3 minutes
"""
        
        # Créer le README temporaire
        with open("README_DEPLOYMENT.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        tar.add("README_DEPLOYMENT.md", arcname="README.md")
        
        # Nettoyer le fichier temporaire
        os.remove("README_DEPLOYMENT.md")
    
    print(f"✅ Package créé: {package_name}")
    print(f"📦 Taille: {os.path.getsize(package_name) / 1024 / 1024:.1f} MB")
    
    return package_name

if __name__ == "__main__":
    package_name = create_deployment_package()
    print(f"\n🎉 Package de déploiement prêt: {package_name}")
    print("\n📋 Instructions:")
    print("1. Téléchargez le fichier généré")
    print("2. Extrayez-le sur votre ordinateur")
    print("3. Suivez le README.md inclus pour le déploiement")
