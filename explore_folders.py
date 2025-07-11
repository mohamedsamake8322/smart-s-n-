import os

# 📁 Dossier racine à explorer
root_dir = r"C:\plateforme-agricole-complete-v2\plantdataset"

def print_folder_tree(path, indent=""):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print(f"{indent}📁 {item}")
            print_folder_tree(item_path, indent + "    ")

# 🚀 Exécution
print(f"Structure du dossier : {root_dir}")
print_folder_tree(root_dir)
