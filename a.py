# -*- coding: utf-8 -*-
import os
import json
from PIL import Image

# 📂 Dossiers
root_dir = "plantdataset"
train_dir = os.path.join(root_dir, "train")
val_dir = os.path.join(root_dir, "val")
json_path = os.path.join(root_dir, "image_text_mapping.json")

# 🧠 Chargement du JSON avec réparation manuelle
def load_json_safe(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print("JSON invalide :", e)
        print("💡 Corrige manuellement les guillemets ou les virgules finales.")
        return {}

# 🧼 Supprime les images corrompues
def clean_images(folder):
    print(f"\n🧪 Scan des images dans : {folder}")
    total, deleted = 0, 0
    for subdir, _, files in os.walk(folder):
        for fname in files:
            path = os.path.join(subdir, fname)
            total += 1
            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception:
                print(f"❌ Supprimée : {path}")
                os.remove(path)
                deleted += 1
    print(f"✅ {total - deleted}/{total} images valides")

# 🔍 Vérifie les correspondances JSON ↔ fichiers
def validate_mapping(mapping, image_dirs):
    all_images = set()
    for d in image_dirs:
        for subdir, _, files in os.walk(d):
            for f in files:
                rel_path = os.path.relpath(os.path.join(subdir, f), root_dir)
                all_images.add(rel_path)

    json_keys = set(mapping.keys())
    missing = json_keys - all_images
    unused = all_images - json_keys

    print(f"\n📊 Vérification du mapping JSON")
    print(f"🔹 Total clés JSON : {len(json_keys)}")
    print(f"🔹 Total images trouvées : {len(all_images)}")
    print(f"❌ Clés JSON sans image : {len(missing)}")
    print(f"⚠️ Images non référencées : {len(unused)}")

    if missing:
        print("\n❌ Clés JSON sans image :")
        for m in list(missing)[:10]:
            print("  -", m)
    if unused:
        print("\n⚠️ Images non référencées :")
        for u in list(unused)[:10]:
            print("  -", u)

# 🚀 Exécution
if __name__ == "__main__":
    mapping = load_json_safe(json_path)
    clean_images(train_dir)
    clean_images(val_dir)
    if mapping:
        validate_mapping(mapping, [train_dir, val_dir])









































# -*- coding: utf-8 -*-
import os
import torch
from torch.utils.data import DataLoader, random_split
from transformers import (
    Blip2Processor,
    Blip2ForConditionalGeneration,
    AdamW,
    get_scheduler
)
from tqdm import tqdm
from PIL import Image
from blip2_loader import BLIP2Dataset

# 📂 Nettoie récursivement tous les sous-dossiers
def clean_corrupted_images(root_dir):
    print(f"🧪 Scan des images dans : {root_dir}")
    total, corrupted = 0, 0
    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            path = os.path.join(subdir, fname)
            total += 1
            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception:
                corrupted += 1
                print(f"❌ Supprimée : {path}")
                os.remove(path)
    print(f"✅ {total - corrupted}/{total} images valides\n")

# 🔧 Configurations
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mapping_path = "plantdataset/image_text_mapping.json"
image_root = "plantdataset/train"
batch_size = 16
num_epochs = 15
lr = 3e-5

# 🧼 Nettoyage du dossier d'images
clean_corrupted_images("plantdataset/train")
clean_corrupted_images("plantdataset/val")

# 📦 Charge le processor et le dataset
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
dataset = BLIP2Dataset(mapping_path, processor, image_root)

# 📊 Split automatique train / validation
val_ratio = 0.05
val_size = int(len(dataset) * val_ratio)
train_size = len(dataset) - val_size
train_set, val_set = random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size)

# 🧠 Charge le modèle
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")
model.to(device)
model.train()

# ⚙️ Optimizer & scheduler
optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
lr_scheduler = get_scheduler("cosine", optimizer=optimizer, num_warmup_steps=0, num_training_steps=len(train_loader)*num_epochs)

# 🔁 Boucle d'entraînement
for epoch in range(num_epochs):
    print(f"\n🧠 Epoch {epoch+1}/{num_epochs}")
    total_loss = 0.0

    for batch in tqdm(train_loader, desc="Training"):
        pixel_values = batch["pixel_values"].to(device)
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model(
            pixel_values=pixel_values,
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=input_ids
        )
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"✅ Epoch {epoch+1} Training loss: {avg_loss:.4f}")

    # 📊 Validation
    model.eval()
    with torch.no_grad():
        val_loss = 0.0
        for batch in tqdm(val_loader, desc="Validation"):
            pixel_values = batch["pixel_values"].to(device)
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = model(
                pixel_values=pixel_values,
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )
            val_loss += outputs.loss.item()

        avg_val = val_loss / len(val_loader)
        print(f"📉 Epoch {epoch+1} Validation loss: {avg_val:.4f}")
    model.train()

    # 💾 Sauvegarde par epoch
    checkpoint_path = f"checkpoints/blip2_epoch_{epoch+1}"
    os.makedirs(checkpoint_path, exist_ok=True)
    model.save_pretrained(checkpoint_path)
    processor.save_pretrained(checkpoint_path)
    print(f"💾 Modèle sauvegardé : {checkpoint_path}")





#Nouveau
# -*- coding: utf-8 -*-
import os
import torch
from torch.utils.data import DataLoader, random_split
from transformers import (
    Blip2Processor,
    Blip2ForConditionalGeneration,
    AdamW,
    get_scheduler
)
from tqdm import tqdm
from PIL import Image
from blip2_loader import BLIP2Dataset

# 📂 Nettoie récursivement tous les sous-dossiers
def clean_corrupted_images(root_dir):
    print(f"🧪 Scan des images dans : {root_dir}")
    total, corrupted = 0, 0
    for subdir, _, files in os.walk(root_dir):
        for fname in files:
            path = os.path.join(subdir, fname)
            total += 1
            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception:
                corrupted += 1
                print(f"❌ Supprimée : {path}")
                os.remove(path)
    print(f"✅ {total - corrupted}/{total} images valides\n")

# 🔧 Configurations
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mapping_path = "plantdataset/image_text_mapping.json"
image_root = "plantdataset"
batch_size = 16
num_epochs = 15
lr = 3e-5

# 🧼 Nettoyage des images corrompues
clean_corrupted_images(os.path.join(image_root, "train"))
clean_corrupted_images(os.path.join(image_root, "val"))

# 📦 Chargement du processor et du dataset
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
dataset = BLIP2Dataset(mapping_path, processor, image_root)

# 📊 Séparation train / val
val_ratio = 0.05
val_size = int(len(dataset) * val_ratio)
train_size = len(dataset) - val_size
train_set, val_set = random_split(dataset, [train_size, val_size])
train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size)

# 🧠 Initialisation du modèle
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")
model.to(device)
model.train()

# ⚙️ Optimizer et scheduler
optimizer = AdamW(model.parameters(), lr=lr, weight_decay=0.01)
lr_scheduler = get_scheduler("cosine", optimizer=optimizer, num_warmup_steps=0, num_training_steps=len(train_loader)*num_epochs)

# 🔁 Entraînement
for epoch in range(num_epochs):
    print(f"\n🧠 Epoch {epoch+1}/{num_epochs}")
    total_loss = 0.0

    for batch in tqdm(train_loader, desc="Training"):
        pixel_values = batch["pixel_values"].to(device)
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)

        outputs = model(
            pixel_values=pixel_values,
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=input_ids
        )
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"✅ Epoch {epoch+1} Training loss: {avg_loss:.4f}")

    # 📊 Validation
    model.eval()
    with torch.no_grad():
        val_loss = 0.0
        for batch in tqdm(val_loader, desc="Validation"):
            pixel_values = batch["pixel_values"].to(device)
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)

            outputs = model(
                pixel_values=pixel_values,
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )
            val_loss += outputs.loss.item()

        avg_val = val_loss / len(val_loader)
        print(f"📉 Epoch {epoch+1} Validation loss: {avg_val:.4f}")
    model.train()

    # 💾 Sauvegarde du modèle
    checkpoint_path = f"checkpoints/blip2_epoch_{epoch+1}"
    os.makedirs(checkpoint_path, exist_ok=True)
    model.save_pretrained(checkpoint_path)
    processor.save_pretrained(checkpoint_path)
    print(f"💾 Modèle sauvegardé : {checkpoint_path}")
