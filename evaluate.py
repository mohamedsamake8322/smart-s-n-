import pandas as pd
import logging
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.linear_model import LinearRegression

# ✅ Logging configuration for tracking
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def evaluate_model(model, df):
    """Evaluates the model's performance using MAE and R²."""
    
    required_cols = ["Temperature", "Humidity", "Precipitation", "pH", "Fertilizer", "Yield"]
    
    # 🔹 Checking for required columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"🚨 Missing columns: {missing_cols}. Required: {required_cols}")
    
    X = df[["Temperature", "Humidity", "Precipitation", "pH", "Fertilizer"]]
    y = df["Yield"]

    # 🔍 Encoding "Fertilizer" only if necessary
    if "Fertilizer" in X.columns and X["Fertilizer"].dtype == object:
        X = pd.get_dummies(X, columns=["Fertilizer"])
    
    # 🔹 Checking before prediction
    try:
        y_pred = model.predict(X)
    except Exception as e:
        logger.error(f"🚨 Error during prediction: {e}")
        raise RuntimeError("🚨 Prediction failed. Check the model and data.")

    # 📊 Calculating metrics
    mae = mean_absolute_error(y, y_pred)
    r2 = r2_score(y, y_pred)

    logger.info(f"✅ Evaluation complete - MAE: {mae:.4f}, R²: {r2:.4f}")

    return mae, r2

# ✅ Example use case
if __name__ == "__main__":
    # Exemple fictif
    data = {
        "Temperature": [25, 30, 20],
        "Humidity": [60, 55, 70],
        "Precipitation": [10, 5, 0],
        "pH": [6.5, 6.8, 7.0],
        "Fertilizer": ["Urea", "Compost", "Urea"],
        "Yield": [2.5, 2.7, 2.0]
    }
    df = pd.DataFrame(data)

    # Dummy model
    df_encoded = pd.get_dummies(df[["Temperature", "Humidity", "Precipitation", "pH", "Fertilizer"]], columns=["Fertilizer"])
    model = LinearRegression().fit(df_encoded, df["Yield"])

    # Call evaluation
    evaluate_model(model, df)
