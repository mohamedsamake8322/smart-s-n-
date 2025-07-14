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

# 📂 Supprime les images corrompues
def clean_corrupted_images(image_dir):
    print(f"🧪 Vérification des images dans : {image_dir}")
    total = 0
    corrupted = 0
    for fname in os.listdir(image_dir):
        path = os.path.join(image_dir, fname)
        total += 1
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception:
            corrupted += 1
            print(f"⚠️ Image corrompue supprimée : {fname}")
            os.remove(path)
    print(f"✅ Nettoyage terminé — {total - corrupted}/{total} images valides\n")

# 🔧 Configurations
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mapping_path = "plantdataset/image_text_mapping.json"
image_root = "plantdataset/images"
batch_size = 16
num_epochs = 15
lr = 3e-5

# 🧼 Nettoyage du dossier image
clean_corrupted_images(image_root)

# 📦 Charge le dataset
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
dataset = BLIP2Dataset(mapping_path, processor, image_root)

# 📊 Split train / validation
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

    # 💾 Sauvegarde par epoch
    checkpoint_path = f"checkpoints/blip2_epoch_{epoch+1}"
    os.makedirs(checkpoint_path, exist_ok=True)
    model.save_pretrained(checkpoint_path)
    processor.save_pretrained(checkpoint_path)
    print(f"💾 Modèle sauvegardé : {checkpoint_path}")
