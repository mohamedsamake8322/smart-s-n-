import os
import zipfile
import requests
from tqdm import tqdm

def download_and_extract(url, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    filename = url.split('/')[-1] + ".zip"
    zip_path = os.path.join(dest_folder, filename)

    # Téléchargement du fichier
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(zip_path, 'wb') as f, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        for data in response.iter_content(1024):
            f.write(data)
            bar.update(len(data))

    # Extraction
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    os.remove(zip_path)

# À TOI DE JOUER : ajoute ici tes URLs directes vers les fichiers zip
dataset_urls = [
    # Remplace ces liens par les liens directs des fichiers ZIP (pas les pages web)
    # Exemples fictifs :
    # "https://data.mendeley.com/public-files/tywbtsjrjv/1/file.zip",
    # "https://kaggle.com/.../plantdisease.zip"
]

for url in dataset_urls:
    download_and_extract(url, "datasets")
