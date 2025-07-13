import pandas as pd
import json

def convert_csv_to_jsonl(csv_path, jsonl_path, caption_lang="bm"):
    df = pd.read_csv(csv_path)

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            item = {
                "image": row["file_name"],            # Chemin relatif ou absolu vers l'image
                "caption": row[f"caption_{caption_lang}"],  # Caption en bambara ou français
                "class": row["match_class"]           # Nom de la classe associée
            }
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ Conversion terminée → {jsonl_path} ({len(df)} lignes)")

# Génère les fichiers d'entraînement et validation
convert_csv_to_jsonl("captions_train_full.csv", "train_data.jsonl", caption_lang="bm")
convert_csv_to_jsonl("captions_val_full.csv", "val_data.jsonl", caption_lang="bm")



























from transformers import BlipProcessor, BlipForConditionalGeneration, Trainer, TrainingArguments
from datasets import load_dataset, Dataset
import torch
import os, json
from PIL import Image
from transformers import AutoProcessor
# 📂 Chemins vers tes données
train_path = "train_data.jsonl"
val_path = "val_data.jsonl"

# 🔧 Paramètres de fine-tuning
model_name = "Salesforce/blip2-opt-2.7b"
output_dir = "sene-blip2.keras"
num_train_epochs = 3
per_device_train_batch_size = 4
per_device_eval_batch_size = 4


processor = AutoProcessor.from_pretrained(model_name)
model = BlipForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)


# 🗂️ Charger les données JSONL en Dataset Hugging Face
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return Dataset.from_list(data)

train_dataset = load_jsonl(train_path)
val_dataset   = load_jsonl(val_path)

# 📸 Prétraitement images + captions
def preprocess(example):
    image = Image.open(example["image"]).convert("RGB")
    inputs = processor(images=image, text=example["caption"], return_tensors="pt", padding="max_length", truncation=True)
    example["pixel_values"] = inputs["pixel_values"][0]
    example["labels"] = inputs["input_ids"][0]
    return example

train_dataset = train_dataset.map(preprocess)
val_dataset   = val_dataset.map(preprocess)

# ⚙️ Entraînement
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="epoch",
    num_train_epochs=num_train_epochs,
    per_device_train_batch_size=per_device_train_batch_size,
    per_device_eval_batch_size=per_device_eval_batch_size,
    save_strategy="epoch",
    logging_dir="./logs",
    save_total_limit=1,
    load_best_model_at_end=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

trainer.train()

# 💾 Export final
model.save_pretrained(output_dir)
print(f"✅ Modèle Sènè exporté dans : {output_dir}")


















from transformers import Blip2Processor, Blip2ForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset
import torch
import os, json
from PIL import Image

# 📂 Chemins vers tes données
train_path = "train_data.jsonl"
val_path = "val_data_fixed.jsonl"


# 🔧 Paramètres de fine-tuning
model_name = "Salesforce/blip2-opt-2.7b"
output_dir = "sene-blip2.keras"
num_train_epochs = 3
per_device_train_batch_size = 4
per_device_eval_batch_size = 4

# 🧠 Chargement du modèle et du processor adaptés BLIP2
processor = Blip2Processor.from_pretrained(model_name)
model = Blip2ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)

# 🗂️ Charger les données JSONL
def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return Dataset.from_list(data)

train_dataset = load_jsonl(train_path)
val_dataset   = load_jsonl(val_path)

# 📸 Prétraitement images + captions
def preprocess(example):
    image = Image.open(example["image"]).convert("RGB")
    inputs = processor(images=image, text=example["caption"], return_tensors="pt", padding="max_length", truncation=True)
    example["pixel_values"] = inputs["pixel_values"][0]
    example["input_ids"] = inputs["input_ids"][0]
    return example

train_dataset = train_dataset.map(preprocess)
val_dataset   = val_dataset.map(preprocess)

# 🧪 Préparer les colonnes pour le Trainer
train_dataset.set_format(type="torch", columns=["pixel_values", "input_ids"])
val_dataset.set_format(type="torch", columns=["pixel_values", "input_ids"])

# ⚙️ Config de l'entraînement
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="epoch",
    num_train_epochs=num_train_epochs,
    per_device_train_batch_size=per_device_train_batch_size,
    per_device_eval_batch_size=per_device_eval_batch_size,
    save_strategy="epoch",
    logging_dir="./logs",
    save_total_limit=1,
    load_best_model_at_end=True
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

trainer.train()

# 💾 Export final
model.save_pretrained(output_dir)
print(f"✅ Modèle Sènè BLIP2 exporté dans : {output_dir}")


