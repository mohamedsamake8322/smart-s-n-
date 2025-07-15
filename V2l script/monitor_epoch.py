#permet de suivre ton entraînement BLIP2 directement depuis le fichier train_robust.log
# -*- coding: utf-8 -*-
import re
from datetime import datetime

log_path = "train_robust.log"

epochs = []
train_losses = []
val_losses = []
checkpoints = []
timestamps = []

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("🧠 Epoch"):
            match = re.search(r"Epoch (\d+)/\d+", line)
            if match:
                epochs.append(int(match.group(1)))
                timestamps.append(datetime.now())

        if "Training loss:" in line:
            match = re.search(r"Training loss: ([0-9.]+)", line)
            if match:
                train_losses.append(float(match.group(1)))

        if "Validation loss:" in line:
            match = re.search(r"Validation loss: ([0-9.]+)", line)
            if match:
                val_losses.append(float(match.group(1)))

        if "Modèle sauvegardé" in line:
            match = re.search(r"checkpoints/blip2_epoch_(\d+)", line)
            if match:
                checkpoints.append(match.group(0))

# 📊 Affichage
print("\n📈 Résumé d'entraînement :\n")
print(f"{'Epoch':<6} | {'Train Loss':<12} | {'Val Loss':<10} | {'Checkpoint':<30}")
print("-"*65)

for i in range(len(train_losses)):
    epoch = epochs[i] if i < len(epochs) else f"?{i+1}"
    train = f"{train_losses[i]:.4f}" if i < len(train_losses) else "N/A"
    val = f"{val_losses[i]:.4f}" if i < len(val_losses) else "N/A"
    ckpt = checkpoints[i] if i < len(checkpoints) else "-"
    print(f"{epoch:<6} | {train:<12} | {val:<10} | {ckpt:<30}")

print("\n✅ Monitoring terminé.")
