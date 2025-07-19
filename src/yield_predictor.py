from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

def train_model(df):
    features = ["production", "pesticides_use", "ndvi_mean"]
    X = df[features]
    y = df["yield_target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=8)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    r2 = r2_score(y_test, y_pred)

    print(f"📊 Modèle entraîné — RMSE: {rmse:.2f}, R²: {r2:.2f}")
    return model

def predict_yield(model, df):
    features = ["production", "pesticides_use", "ndvi_mean"]
    return model.predict(df[features])
