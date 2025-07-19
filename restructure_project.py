import os

def print_directory_tree(startpath, max_depth=6):
    """
    Affiche l'arborescence du projet et génère un fichier Markdown compatible Windows.
    """
    lines = []
    for root, dirs, files in os.walk(startpath):
        depth = root.replace(startpath, "").count(os.sep)
        if depth > max_depth:
            continue
        indent = "│   " * depth
        lines.append(f"{indent}├── {os.path.basename(root)}/")
        for f in files:
            lines.append(f"{indent}│   └── {f}")

    manifest_path = os.path.join(startpath, "project_manifest.md")
    try:
        with open(manifest_path, "w", encoding="utf-8-sig") as f:
            f.write("# Arborescence du projet SènèSmart\n\n")
            f.write("\n".join(lines))
        print(f"✅ Arborescence enregistrée dans : {manifest_path}")
    except Exception as e:
        print(f"❌ Erreur lors de l’écriture du fichier : {e}")

# Lance le scan à partir de ce chemin
if __name__ == "__main__":
    chemin_du_projet = r"C:\plateforme-agricole-complete-v2"
    print_directory_tree(chemin_du_projet)
