import xgboost as xgb
import joblib
import os
import logging
import joblib
model = joblib.load("yield_model_v3.pkl")  # Load the corrected model

# ✅ Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 🔍 Checking model file
model_path = "yield_model.pkl"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"🚨 Error: The file {model_path} was not found.")

# 🚀 Loading the model
logger.info("🔄 Loading XGBoost model...")
model = joblib.load(model_path)

# 🔹 Checking `get_booster()`
if not hasattr(model, "get_booster"):
    raise AttributeError("🚨 Error: The loaded object does not have a booster. Verify the model type.")

# 🔄 Converting and saving the model
logger.info("🔄 Converting and saving the model...")
booster = model.get_booster()
booster.save_model("yield_model_v3.json")  # New JSON save
joblib.dump(model, "yield_model_v3.pkl", compress=3)  # Save as pickle

logger.info("✅ Model successfully saved in JSON and Pickle formats!")
