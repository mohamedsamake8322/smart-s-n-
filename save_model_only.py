from tensorflow import keras

model = keras.models.load_model("model/efficientnet_resnet.keras", compile=False)
model.save("model/efficientnet_resnet.keras", save_format="keras")
print("✅ Modèle resauvegardé avec succès")
