from tensorflow.keras.applications.efficientnet import preprocess_input
import numpy as np

# Dummy image (batch of 1, 224x224x3)
image = np.random.randint(0, 256, size=(1, 224, 224, 3)).astype("float32")

# Try preprocessing
preprocessed = preprocess_input(image)

print("EfficientNet preprocessing works ✅")
print("Output shape:", preprocessed.shape)
