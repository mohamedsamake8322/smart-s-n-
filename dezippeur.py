import zipfile
import time
import os

start = time.time()

zip_path = r"C:\plateforme-agricole-complete-v2\plantdataset.zip"
extract_to = r"H:\My Drive\My drive"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    file_list = zip_ref.namelist()
    total = len(file_list)

    for i, file in enumerate(file_list, 1):
        zip_ref.extract(file, extract_to)
        print(f"[{i}/{total}] {file} extrait")

end = time.time()
print(f"\n✅ Décompression terminée en {end - start:.2f} secondes.")
