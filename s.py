import os
import requests
import subprocess

def telecharger_repos(org="PlantVillage", dossier="plantvillage_repos"):
    os.makedirs(dossier, exist_ok=True)
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        repos = requests.get(url).json()
        if not repos:
            break
        for r in repos:
            name = r["name"]
            clone_url = r["clone_url"]
            path = os.path.join(dossier, name)
            if not os.path.exists(path):
                subprocess.run(["git", "clone", clone_url, path])
                print(f"✅ Cloné : {name}")
        page += 1

telecharger_repos()
