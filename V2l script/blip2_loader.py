# -*- coding: utf-8 -*-##
#(✅ Résultat de blip2_loader.py
#Tu as :📦 Chargé ton fichier image_text_mapping.json contenant +107 000 paires image ↔ texte

#🖼️ Transformé les images en tenseurs Torch (3×224×224) prêts pour BLIP2

#🧠 Tokenisé les descriptions agricoles avec Blip2Processor du modèle Hugging Face

#🧪 Testé la structure de tes batchs (visuel + langage) avec un batch de 8 exemples

#✅ Confirmé que l’environnement Python 3 est bien configuré avec tous les packages nécessaires

#🎯 Objectif atteint
#Tu as validé que ton dataset peut nourrir un modèle BLIP2 — avec des images lisibles, des descriptions précises, et un format compatible pour l’entraînement.

#🛠️ Et comme tout a tourné sans erreur, on peut maintenant passer en toute confiance à l’étape suivante : l’entraînement du modèle avec blip2_train.py, puis l’export final vers .keras ou .pt.

#Tu veux que je te l’écrive tout de suite pour lancer le vrai moteur ? Je peux même y intégrer un mode debug en --test si tu veux garder le contrôle sur les premières itérations 💥)
import os
import json
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from transformers import Blip2Processor

class BLIP2Dataset(Dataset):
    def __init__(self, mapping_path, processor, image_root, max_samples=None):
        with open(mapping_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.processor = processor
        self.image_root = image_root
        self.entries = list(self.data.items())

        if max_samples:
            self.entries = self.entries[:max_samples]

        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor()
        ])

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, idx):
        rel_path, text = self.entries[idx]
        full_path = os.path.join(self.image_root, rel_path)

        image = Image.open(full_path).convert("RGB")
        pixel_values = self.processor.image_processor(image, return_tensors="pt").pixel_values[0]
        inputs = self.processor.tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=128)

        return {
            "pixel_values": pixel_values,
            "input_ids": inputs.input_ids[0],
            "attention_mask": inputs.attention_mask[0],
            "caption": text
        }

# 🔧 Usage
if __name__ == "__main__":
    from transformers import Blip2Processor

    dataset_path = "plantdataset/image_text_mapping.json"
    image_root = "plantdataset"
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")

    ds = BLIP2Dataset(dataset_path, processor, image_root, max_samples=1000)
    loader = DataLoader(ds, batch_size=8, shuffle=True)

    for batch in loader:
        print("pixel_values", batch["pixel_values"].shape)
        print("input_ids", batch["input_ids"].shape)
        print("caption", batch["caption"][0])
        break
