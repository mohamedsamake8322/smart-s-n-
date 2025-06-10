"""
Enterprise Database Management
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Enterprise-grade database manager with connection pooling and error handling"""
    
    def __init__(self, db_path: str = "smart_sene_enterprise.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """Initialize all database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    prediction_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    prediction_result TEXT NOT NULL,
                    confidence_score REAL,
                    model_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Farm locations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS farm_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    area_hectares REAL,
                    soil_type TEXT,
                    crop_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Weather data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_id INTEGER,
                    date DATE NOT NULL,
                    temperature_max REAL,
                    temperature_min REAL,
                    humidity REAL,
                    rainfall REAL,
                    wind_speed REAL,
                    solar_radiation REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (location_id) REFERENCES farm_locations (id)
                )
            """)
            
            # Disease detections table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS disease_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    location_id INTEGER,
                    image_path TEXT,
                    detected_disease TEXT,
                    confidence_score REAL,
                    severity_level TEXT,
                    treatment_recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (location_id) REFERENCES farm_locations (id)
                )
            """)
            
            # Model performance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    model_version TEXT NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall REAL,
                    f1_score REAL,
                    training_date TIMESTAMP,
                    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # System logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def save_prediction(self, user_id: int, prediction_type: str, 
                       input_data: Dict, result: Dict, confidence: float = None,
                       model_version: str = "1.0") -> int:
        """Save prediction results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO predictions 
                (user_id, prediction_type, input_data, prediction_result, confidence_score, model_version)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, prediction_type, json.dumps(input_data), 
                  json.dumps(result), confidence, model_version))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_predictions(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Get user's prediction history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM predictions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            predictions = []
            for row in cursor.fetchall():
                predictions.append({
                    'id': row['id'],
                    'prediction_type': row['prediction_type'],
                    'input_data': json.loads(row['input_data']),
                    'prediction_result': json.loads(row['prediction_result']),
                    'confidence_score': row['confidence_score'],
                    'model_version': row['model_version'],
                    'created_at': row['created_at']
                })
            return predictions
    
    def save_farm_location(self, user_id: int, name: str, lat: float, lon: float,
                          area: float = None, soil_type: str = None, 
                          crop_type: str = None) -> int:
        """Save farm location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO farm_locations 
                (user_id, name, latitude, longitude, area_hectares, soil_type, crop_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, lat, lon, area, soil_type, crop_type))
            conn.commit()
            return cursor.lastrowid
    
    def get_farm_locations(self, user_id: int) -> List[Dict]:
        """Get user's farm locations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM farm_locations WHERE user_id = ?
            """, (user_id,))
            
            locations = []
            for row in cursor.fetchall():
                locations.append(dict(row))
            return locations
    
    def save_weather_data(self, location_id: int, weather_data: Dict) -> int:
        """Save weather data for a location"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather_data 
                (location_id, date, temperature_max, temperature_min, humidity, 
                 rainfall, wind_speed, solar_radiation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (location_id, weather_data.get('date'),
                  weather_data.get('temp_max'), weather_data.get('temp_min'),
                  weather_data.get('humidity'), weather_data.get('rainfall'),
                  weather_data.get('wind_speed'), weather_data.get('solar_radiation')))
            conn.commit()
            return cursor.lastrowid
    
    def get_weather_history(self, location_id: int, days: int = 30) -> pd.DataFrame:
        """Get weather history for analysis"""
        with self.get_connection() as conn:
            query = """
                SELECT * FROM weather_data 
                WHERE location_id = ? 
                ORDER BY date DESC 
                LIMIT ?
            """
            return pd.read_sql_query(query, conn, params=(location_id, days))
    
    def save_disease_detection(self, user_id: int, location_id: int,
                              image_path: str, disease: str, confidence: float,
                              severity: str = None, recommendations: str = None) -> int:
        """Save disease detection results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO disease_detections 
                (user_id, location_id, image_path, detected_disease, confidence_score,
                 severity_level, treatment_recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, location_id, image_path, disease, confidence, 
                  severity, recommendations))
            conn.commit()
            return cursor.lastrowid
    
    def get_disease_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get disease detection history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dd.*, fl.name as location_name 
                FROM disease_detections dd
                LEFT JOIN farm_locations fl ON dd.location_id = fl.id
                WHERE dd.user_id = ?
                ORDER BY dd.created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            detections = []
            for row in cursor.fetchall():
                detections.append(dict(row))
            return detections
    
    def save_model_performance(self, model_name: str, model_version: str,
                              metrics: Dict) -> int:
        """Save model performance metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO model_performance 
                (model_name, model_version, accuracy, precision_score, recall, f1_score, training_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (model_name, model_version, metrics.get('accuracy'),
                  metrics.get('precision'), metrics.get('recall'),
                  metrics.get('f1_score'), datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def get_model_performance_history(self, model_name: str) -> pd.DataFrame:
        """Get model performance over time"""
        with self.get_connection() as conn:
            query = """
                SELECT * FROM model_performance 
                WHERE model_name = ? 
                ORDER BY evaluation_date DESC
            """
            return pd.read_sql_query(query, conn, params=(model_name,))
    
    def log_user_action(self, user_id: int, action: str, details: str = None,
                       ip_address: str = None, user_agent: str = None):
        """Log user actions for audit trail"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs 
                (user_id, action, details, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action, details, ip_address, user_agent))
            conn.commit()
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Get system analytics data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total predictions
            cursor.execute("SELECT COUNT(*) as total FROM predictions")
            total_predictions = cursor.fetchone()['total']
            
            # Active users (logged in last 30 days)
            cursor.execute("""
                SELECT COUNT(*) as active FROM users 
                WHERE last_login > datetime('now', '-30 days')
            """)
            active_users = cursor.fetchone()['active']
            
            # Disease detections this month
            cursor.execute("""
                SELECT COUNT(*) as monthly FROM disease_detections 
                WHERE created_at > datetime('now', '-30 days')
            """)
            monthly_detections = cursor.fetchone()['monthly']
            
            # Farm locations
            cursor.execute("SELECT COUNT(*) as total FROM farm_locations")
            total_locations = cursor.fetchone()['total']
            
            return {
                'total_predictions': total_predictions,
                'active_users': active_users,
                'monthly_detections': monthly_detections,
                'total_locations': total_locations
            }

# Global database instance
db_manager = DatabaseManager()

# Convenience functions for backward compatibility
def init_db():
    """Initialize database"""
    return db_manager.init_database()

def save_prediction(user_id: int, prediction_type: str, input_data: Dict, 
                   result: Dict, confidence: float = None) -> int:
    """Save prediction (backward compatibility)"""
    return db_manager.save_prediction(user_id, prediction_type, input_data, 
                                    result, confidence)

def get_user_predictions(user_id: int, limit: int = 100) -> List[Dict]:
    """Get user predictions (backward compatibility)"""
    return db_manager.get_user_predictions(user_id, limit)
