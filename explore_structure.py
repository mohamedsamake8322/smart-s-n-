import os

def save_directory_tree(startpath, output_file, max_depth=5):
    def safe_write(line):
        try:
            f.write(line + "\n")
        except Exception:
            pass

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"📂 Arborescence de : {startpath}\n\n")
        for root, dirs, files in os.walk(startpath):
            depth = root.replace(startpath, "").count(os.sep)
            if depth >= max_depth:
                continue
            indent = "│   " * depth
            safe_write(f"{indent}├── {os.path.basename(root)}/")
            for file_name in files:
                safe_write(f"{indent}│   └── {file_name}")

# Chemin vers ton projet
project_path = r"C:\plateforme-agricole-complete-v2"
output_file = "arborescence.txt"

save_directory_tree(project_path, output_file)

print(f"✅ Arborescence sauvegardée dans {output_file}")
