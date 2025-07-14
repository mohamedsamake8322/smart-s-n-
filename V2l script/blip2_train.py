#Entraînement complet avec validation
# -*- coding: utf-8 -*-
import os
import torch
from torch.utils.data import DataLoader, random_split
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from transformers import AdamW, get_scheduler
from tqdm import tqdm
from blip2_loader import BLIP2Dataset

# 🔧 Configurations
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mapping_path = "plantdataset/image_text_mapping.json"
image_root = "plantdataset"
batch_size = 8
num_epochs = 3
lr = 5e-5

# 📦 Charge dataset
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
dataset = BLIP2Dataset(mapping_path, processor, image_root)

# 📊 Split train / val
val_ratio = 0.05
val_size = int(len(dataset) * val_ratio)
train_size = len(dataset) - val_size
train_set, val_set = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_set, batch_size=batch_size)

# 🧠 Modèle BLIP2
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b")
model.to(device)
model.train()

# ⚙️ Optimizer & scheduler
optimizer = AdamW(model.parameters(), lr=lr)
lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=0, num_training_steps=len(train_loader)*num_epochs)

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
            labels=input_ids,
            attention_mask=attention_mask
        )
        loss = outputs.loss
        loss.backward()

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    print(f"✅ Epoch {epoch+1} loss: {avg_loss:.4f}")

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
                labels=input_ids,
                attention_mask=attention_mask
            )
            val_loss += outputs.loss.item()

        avg_val = val_loss / len(val_loader)
        print(f"📉 Validation loss: {avg_val:.4f}")
    model.train()

# 💾 Sauvegarde du modèle
os.makedirs("checkpoints", exist_ok=True)
model.save_pretrained("checkpoints/blip2_agriculture_v1")
processor.save_pretrained("checkpoints/blip2_agriculture_v1")
print("✅ Modèle sauvegardé dans checkpoints/blip2_agriculture_v1")
