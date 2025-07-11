import os

# 📌 Dossier à explorer
root_dir = r"C:\plateforme-agricole-complete-v2\plantdataset"

def list_dir_tree(start_path, indent=""):
    for item in os.listdir(start_path):
        item_path = os.path.join(start_path, item)
        if os.path.isdir(item_path):
            print(f"{indent}📁 {item}/")
            list_dir_tree(item_path, indent + "    ")
        else:
            print(f"{indent}📄 {item}")

# 🚀 Exécution
print(f"Structure du dossier : {root_dir}")
list_dir_tree(root_dir)
