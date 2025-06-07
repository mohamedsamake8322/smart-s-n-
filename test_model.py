import torch
import timm
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
# Charger le modèle entraîné
MODEL_PATH = "C:/Mah fah/plant_disease_model.pth"
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_classes = 4  # Ajuste selon ton dataset

model = timm.create_model("efficientnet_b4", pretrained=False)
model.classifier = nn.Linear(model.classifier.in_features, num_classes)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

# Transformer l'image pour la prédiction
def predict_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((300, 300)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path)
    image = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        output = model(image)
        _, predicted = torch.max(output, 1)

    return predicted.item()

# Test avec une image
image_path = "C:/Mah fah/IMG_20240720_103446_512.jpg"
prediction = predict_image(image_path)
print(f"🌱 Maladie détectée : {prediction}")
