from tensorflow.keras.models import load_model
import os

# ðŸ”¹ DÃ©finition des chemins
MODEL_PATH_H5 = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"
MODEL_PATH_KERAS = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"

# ðŸ” VÃ©rification du dossier de sauvegarde
os.makedirs(os.path.dirname(MODEL_PATH_KERAS), exist_ok=True)

# âœ… Charger le modÃ¨le existant `.keras`
model = load_model(MODEL_PATH_H5)

# ðŸ”„ Sauvegarder en `.keras`
model.save(MODEL_PATH_KERAS)

print(f"âœ… ModÃ¨le converti et enregistrÃ© sous {MODEL_PATH_KERAS}")

