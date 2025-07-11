from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import torch

# 📁 Chemin vers une image de ton dataset
img_path = "C:/plateforme-agricole-complete-v2/plantdataset/train/Thrips/img_001.jpg"

# 🧠 Charger le modèle BLIP2-OPT
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", device_map="auto", torch_dtype=torch.float16)

# 🖼️ Charger l'image
image = Image.open(img_path).convert("RGB")

# 🗣️ Prompt de test
prompt = "Describe the symptoms of the plant disease in this image."

# 🔁 Préparation
inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda", torch.float16)

# 🚀 Génération
generated_ids = model.generate(**inputs, max_new_tokens=50)
caption = processor.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

print(f"🧠 Caption générée : {caption}")
