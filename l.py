#📁 Script d’exploration du dossier deafrica_tools
import os
import ast

def explore_deafrica_tools(path="C:/plateforme-agricole-complete-v2/deafrica-sandbox-notebooks/Tools/deafrica_tools"):
    print(f"🔍 Exploration de : {path}\n")

    for filename in os.listdir(path):
        if filename.endswith(".py"):
            print(f"📦 Fichier : {filename}")

            file_path = os.path.join(path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
            if functions:
                print("   🧪 Fonctions détectées :")
                for func in functions:
                    print(f"     - {func}")
            else:
                print("   ⚠️ Aucun def de fonction détecté.")
            print()

# Lancer l'exploration
explore_deafrica_tools()
