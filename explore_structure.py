import os

def print_directory_tree(startpath, max_depth=5, prefix=""):
    def safe_print(s):
        try:
            print(s)
        except Exception:
            pass

    for root, dirs, files in os.walk(startpath):
        depth = root.replace(startpath, "").count(os.sep)
        if depth >= max_depth:
            continue
        indent = "│   " * depth
        safe_print(f"{indent}├── {os.path.basename(root)}/")
        for f in files:
            safe_print(f"{indent}│   └── {f}")

# Chemin vers ton projet
project_path = r"C:\plateforme-agricole-complete-v2"

print(f"\n📂 Arborescence de : {project_path}\n")
print_directory_tree(project_path)
