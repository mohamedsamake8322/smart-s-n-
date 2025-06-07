import sqlite3
import os
import pandas as pd
from datetime import datetime
import logging
from flask_jwt_extended import jwt_required, get_jwt_identity
import functools

# 🔹 Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 📌 Dynamic path for `history.db`
DB_FILE = os.path.join(os.path.dirname(__file__), "history.db")

# === DATABASE INITIALIZATION ===
def init_db():
    """Initializes the SQLite database with optimized indexes and constraints."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    features TEXT NOT NULL,
                    predicted_yield REAL NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_username ON predictions (username);
                CREATE INDEX IF NOT EXISTS idx_timestamp ON predictions (timestamp);

                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    name TEXT NOT NULL,
                    note TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS field_location (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    total_predictions INTEGER DEFAULT 0,
                    avg_yield REAL DEFAULT 0.0,
                    last_prediction TEXT DEFAULT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_user_analytics ON analytics (username);
            """)
            conn.commit()
            logger.info("✅ Database successfully initialized!")
    except sqlite3.Error as e:
        logger.error(f"🚨 Database initialization error: {e}")

# === DECORATOR TO HANDLE DATABASE ERRORS ===
def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"🚨 SQL Error: {e}")
            return None
    return wrapper

# === SECURE PREDICTION RECORDING + STATISTICS ===
@jwt_required()
@handle_db_errors
def save_prediction(features, predicted_yield):
    """Records a prediction and updates user statistics."""
    username = get_jwt_identity()
    timestamp = datetime.now().isoformat()
    features_str = ",".join(map(str, features))

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (username, features, predicted_yield, timestamp)
            VALUES (?, ?, ?, ?)
        """, (username, features_str, predicted_yield, timestamp))

        # 📊 Update statistics
        cursor.execute("""
            INSERT INTO analytics (username, total_predictions, avg_yield, last_prediction)
            VALUES (?, 1, ?, ?) 
            ON CONFLICT(username)
            DO UPDATE SET 
                total_predictions = total_predictions + 1,
                avg_yield = (avg_yield * (total_predictions - 1) + ?) / total_predictions,
                last_prediction = ?
        """, (username, predicted_yield, timestamp, predicted_yield, timestamp))

        conn.commit()
        logger.info(f"✅ Prediction recorded and statistics updated for {username}")

# === RETRIEVE PREDICTIONS WITH FILTERING AND ANALYSIS ===
@jwt_required()
@handle_db_errors
def get_user_predictions(limit=10):
    """Retrieves the user's latest predictions."""
    username = get_jwt_identity()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT features, predicted_yield, timestamp
            FROM predictions
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (username, limit))

        rows = cursor.fetchall()
        logger.info(f"✅ Retrieved {len(rows)} predictions for {username}")

        return [
            {"Features": row[0].split(","), "Predicted Yield": row[1], "Timestamp": row[2]}
            for row in rows
        ]

# === SECURE OBSERVATION RECORDING ===
@handle_db_errors
def save_observation(user, name, note):
    """Records an observation with protection against SQL injection."""
    timestamp = datetime.now().isoformat()
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO observations (user, name, note, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user, name, note, timestamp))

        conn.commit()
        logger.info(f"✅ Observation recorded for {user}: {name}")

# === MULTI-USER LOCATION RECORDING ===
@handle_db_errors
def save_location(user, lat, lon):
    """Records a location with multi-user support and SQL optimization."""
    timestamp = datetime.now().isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO field_location (user, latitude, longitude, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user, lat, lon, timestamp))

        conn.commit()
        logger.info(f"✅ Location recorded for {user}: ({lat}, {lon})")

# === RETRIEVE USAGE STATISTICS ===
@jwt_required()
@handle_db_errors
def get_user_analytics():
    """Retrieves the user's prediction statistics."""
    username = get_jwt_identity()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT total_predictions, avg_yield, last_prediction
            FROM analytics
            WHERE username = ?
        """, (username,))

        row = cursor.fetchone()
        return {
            "Total Predictions": row[0] if row else 0,
            "Average Yield": row[1] if row else 0.0,
            "Last Prediction": row[2] if row else "No Data"
        }

logger.info("🚀 Database and advanced management operational!")
if __name__ == "__main__":
    init_db()
