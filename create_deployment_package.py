import zipfile
import os


def create_zip():
    directory_to_zip = "."  # Répertoire courant
    zip_filename = "PrecisionFarm.zip"
    exclude_files = [".replit", "__pycache__", "venv", "node_modules"]

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for foldername, subfolders, filenames in os.walk(directory_to_zip):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                # Vérifier si le fichier est à exclure
                if any(excluded in file_path for excluded in exclude_files):
                    continue
                zip_file.write(file_path,
                               os.path.relpath(file_path, directory_to_zip))

    print(f"✅ Fichier zip créé avec succès : {zip_filename}")


if __name__ == "__main__":
    create_zip()
