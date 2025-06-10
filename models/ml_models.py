"""
Enterprise ML Model Management System
"""
import os
import pickle
import joblib
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import json

# ML Libraries
try:
    import tensorflow as tf
    import xgboost as xgb
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
except ImportError as e:
    logging.warning(f"Some ML libraries not available: {e}")

logger = logging.getLogger(__name__)

class ModelManager:
    """Enterprise ML model management system"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metadata = {}
        
        # Ensure models directory exists
        os.makedirs(models_dir, exist_ok=True)
        
        # Load existing models
        self.load_all_models()
    
    def load_all_models(self):
        """Load all available models from disk"""
        try:
            model_files = {
                'yield_prediction': 'yield_model.pkl',
                'disease_detection': 'disease_model.h5',
                'weather_prediction': 'weather_model.pkl',
                'fertilizer_recommendation': 'fertilizer_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                model_path = os.path.join(self.models_dir, filename)
                if os.path.exists(model_path):
                    self.load_model(model_name, model_path)
                    logger.info(f"Loaded model: {model_name}")
                else:
                    logger.warning(f"Model file not found: {model_path}")
                    
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def load_model(self, model_name: str, model_path: str) -> bool:
        """Load a specific model"""
        try:
            if model_path.endswith('.h5') or model_path.endswith('.keras'):
                # TensorFlow/Keras model
                model = tf.keras.models.load_model(model_path)
            elif model_path.endswith('.pkl'):
                # Scikit-learn/XGBoost model
                model = joblib.load(model_path)
            else:
                logger.error(f"Unsupported model format: {model_path}")
                return False
            
            self.models[model_name] = model
            
            # Load associated metadata
            metadata_path = model_path.replace('.h5', '_metadata.json').replace('.pkl', '_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    self.model_metadata[model_name] = json.load(f)
            
            # Load associated scaler/encoder if exists
            scaler_path = model_path.replace('.h5', '_scaler.pkl').replace('.pkl', '_scaler.pkl')
            if os.path.exists(scaler_path):
                self.scalers[model_name] = joblib.load(scaler_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False
    
    def save_model(self, model_name: str, model: Any, metadata: Dict = None) -> bool:
        """Save model with metadata"""
        try:
            model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            
            # Save model
            if hasattr(model, 'save'):  # TensorFlow/Keras model
                model_path = model_path.replace('.pkl', '.h5')
                model.save(model_path)
            else:  # Scikit-learn/XGBoost model
                joblib.dump(model, model_path)
            
            self.models[model_name] = model
            
            # Save metadata
            if metadata:
                metadata_path = model_path.replace('.h5', '_metadata.json').replace('.pkl', '_metadata.json')
                metadata['saved_at'] = datetime.now().isoformat()
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                self.model_metadata[model_name] = metadata
            
            logger.info(f"Model saved: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {e}")
            return False
    
    def predict_yield(self, input_data: Dict) -> Dict[str, Any]:
        """Predict crop yield"""
        try:
            if 'yield_prediction' not in self.models:
                return {'error': 'Yield prediction model not available'}
            
            model = self.models['yield_prediction']
            
            # Prepare input features
            features = self._prepare_yield_features(input_data)
            
            # Apply scaling if available
            if 'yield_prediction' in self.scalers:
                features = self.scalers['yield_prediction'].transform([features])
            else:
                features = np.array([features])
            
            # Make prediction
            prediction = model.predict(features)[0]
            
            # Calculate confidence if possible
            confidence = self._calculate_confidence(model, features)
            
            return {
                'predicted_yield': float(prediction),
                'confidence': confidence,
                'model_version': self.model_metadata.get('yield_prediction', {}).get('version', '1.0'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in yield prediction: {e}")
            return {'error': str(e)}
    
    def detect_disease(self, image_array: np.ndarray) -> Dict[str, Any]:
        """Detect plant disease from image"""
        try:
            if 'disease_detection' not in self.models:
                return {'error': 'Disease detection model not available'}
            
            model = self.models['disease_detection']
            
            # Preprocess image
            processed_image = self._preprocess_image(image_array)
            
            # Make prediction
            predictions = model.predict(processed_image)
            
            # Get class names if available
            class_names = self.model_metadata.get('disease_detection', {}).get('class_names', [])
            
            if len(class_names) > 0:
                predicted_class_idx = np.argmax(predictions[0])
                predicted_disease = class_names[predicted_class_idx]
                confidence = float(np.max(predictions[0]))
            else:
                predicted_disease = f"Class_{np.argmax(predictions[0])}"
                confidence = float(np.max(predictions[0]))
            
            return {
                'predicted_disease': predicted_disease,
                'confidence': confidence,
                'all_predictions': {
                    class_names[i] if i < len(class_names) else f"Class_{i}": float(predictions[0][i])
                    for i in range(len(predictions[0]))
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in disease detection: {e}")
            return {'error': str(e)}
    
    def recommend_fertilizer(self, input_data: Dict) -> Dict[str, Any]:
        """Recommend fertilizer based on soil and crop data"""
        try:
            if 'fertilizer_recommendation' not in self.models:
                return {'error': 'Fertilizer recommendation model not available'}
            
            model = self.models['fertilizer_recommendation']
            
            # Prepare features
            features = self._prepare_fertilizer_features(input_data)
            
            # Apply scaling/encoding if available
            if 'fertilizer_recommendation' in self.scalers:
                features = self.scalers['fertilizer_recommendation'].transform([features])
            else:
                features = np.array([features])
            
            # Make prediction
            prediction = model.predict(features)[0]
            
            # Map prediction to fertilizer type
            fertilizer_types = self.model_metadata.get('fertilizer_recommendation', {}).get('fertilizer_types', [])
            
            if len(fertilizer_types) > 0 and isinstance(prediction, (int, np.integer)):
                recommended_fertilizer = fertilizer_types[int(prediction)]
            else:
                recommended_fertilizer = str(prediction)
            
            return {
                'recommended_fertilizer': recommended_fertilizer,
                'input_analysis': self._analyze_soil_conditions(input_data),
                'application_advice': self._get_application_advice(input_data, recommended_fertilizer),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in fertilizer recommendation: {e}")
            return {'error': str(e)}
    
    def train_yield_model(self, training_data: pd.DataFrame, 
                         target_column: str = 'yield') -> Dict[str, Any]:
        """Train/retrain yield prediction model"""
        try:
            # Prepare data
            X = training_data.drop(columns=[target_column])
            y = training_data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_pred = model.predict(X_train_scaled)
            test_pred = model.predict(X_test_scaled)
            
            metrics = {
                'train_r2': r2_score(y_train, train_pred),
                'test_r2': r2_score(y_test, test_pred),
                'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                'feature_importance': dict(zip(X.columns, model.feature_importances_))
            }
            
            # Save model and scaler
            self.models['yield_prediction'] = model
            self.scalers['yield_prediction'] = scaler
            
            # Save to disk
            model_metadata = {
                'version': '2.0',
                'training_date': datetime.now().isoformat(),
                'metrics': metrics,
                'features': list(X.columns)
            }
            
            self.save_model('yield_prediction', model, model_metadata)
            
            # Save scaler
            scaler_path = os.path.join(self.models_dir, 'yield_prediction_scaler.pkl')
            joblib.dump(scaler, scaler_path)
            
            return {
                'success': True,
                'metrics': metrics,
                'model_info': model_metadata
            }
            
        except Exception as e:
            logger.error(f"Error training yield model: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_yield_features(self, input_data: Dict) -> List[float]:
        """Prepare features for yield prediction"""
        # Default feature order - adjust based on your model
        feature_keys = [
            'temperature', 'humidity', 'rainfall', 'ph', 'nitrogen',
            'phosphorus', 'potassium', 'soil_type_encoded', 'crop_type_encoded'
        ]
        
        features = []
        for key in feature_keys:
            if key in input_data:
                features.append(float(input_data[key]))
            elif key.endswith('_encoded'):
                # Handle categorical encoding
                base_key = key.replace('_encoded', '')
                if base_key in input_data:
                    encoded_value = self._encode_categorical(base_key, input_data[base_key])
                    features.append(float(encoded_value))
                else:
                    features.append(0.0)
            else:
                features.append(0.0)  # Default value
        
        return features
    
    def _prepare_fertilizer_features(self, input_data: Dict) -> List[float]:
        """Prepare features for fertilizer recommendation"""
        feature_keys = [
            'nitrogen', 'phosphorus', 'potassium', 'ph', 'temperature',
            'humidity', 'rainfall', 'crop_type_encoded'
        ]
        
        features = []
        for key in feature_keys:
            if key in input_data:
                features.append(float(input_data[key]))
            elif key.endswith('_encoded'):
                base_key = key.replace('_encoded', '')
                if base_key in input_data:
                    encoded_value = self._encode_categorical(base_key, input_data[base_key])
                    features.append(float(encoded_value))
                else:
                    features.append(0.0)
            else:
                features.append(0.0)
        
        return features
    
    def _preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """Preprocess image for disease detection"""
        # Resize to model input size (typically 224x224 for most models)
        if len(image_array.shape) == 3:
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
        
        # Normalize pixel values
        image_array = image_array.astype(np.float32) / 255.0
        
        return image_array
    
    def _encode_categorical(self, category: str, value: str) -> int:
        """Encode categorical values"""
        encoding_maps = {
            'soil_type': {'Sandy': 0, 'Clay': 1, 'Loamy': 2, 'Silty': 3},
            'crop_type': {'Maize': 0, 'Rice': 1, 'Wheat': 2, 'Tomato': 3, 'Okra': 4}
        }
        
        if category in encoding_maps and value in encoding_maps[category]:
            return encoding_maps[category][value]
        return 0  # Default encoding
    
    def _calculate_confidence(self, model: Any, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        try:
            if hasattr(model, 'predict_proba'):
                # For classification models
                probabilities = model.predict_proba(features)
                return float(np.max(probabilities))
            elif hasattr(model, 'estimators_'):
                # For ensemble models, use standard deviation
                predictions = [tree.predict(features)[0] for tree in model.estimators_]
                std_dev = np.std(predictions)
                # Convert to confidence score (lower std = higher confidence)
                confidence = max(0.0, min(1.0, 1.0 - (std_dev / np.mean(predictions))))
                return float(confidence)
            else:
                return 0.85  # Default confidence
        except:
            return 0.85
    
    def _analyze_soil_conditions(self, input_data: Dict) -> Dict[str, str]:
        """Analyze soil conditions"""
        analysis = {}
        
        if 'ph' in input_data:
            ph = float(input_data['ph'])
            if ph < 6.0:
                analysis['ph_status'] = 'Acidic - Consider lime application'
            elif ph > 8.0:
                analysis['ph_status'] = 'Alkaline - Consider sulfur application'
            else:
                analysis['ph_status'] = 'Optimal'
        
        if 'nitrogen' in input_data:
            n = float(input_data['nitrogen'])
            if n < 30:
                analysis['nitrogen_status'] = 'Low - Nitrogen fertilizer recommended'
            elif n > 100:
                analysis['nitrogen_status'] = 'High - Reduce nitrogen input'
            else:
                analysis['nitrogen_status'] = 'Adequate'
        
        return analysis
    
    def _get_application_advice(self, input_data: Dict, fertilizer: str) -> List[str]:
        """Get fertilizer application advice"""
        advice = [
            f"Apply {fertilizer} according to soil test results",
            "Split application into 2-3 doses for better uptake",
            "Apply during early growth stages for maximum benefit"
        ]
        
        if 'growth_stage' in input_data:
            stage = input_data['growth_stage']
            if stage == 'Flowering':
                advice.append("Reduce nitrogen, increase phosphorus for flowering")
            elif stage == 'Fruiting':
                advice.append("Increase potassium for fruit development")
        
        return advice
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        status = {}
        
        for model_name in ['yield_prediction', 'disease_detection', 'fertilizer_recommendation']:
            if model_name in self.models:
                metadata = self.model_metadata.get(model_name, {})
                status[model_name] = {
                    'available': True,
                    'version': metadata.get('version', 'Unknown'),
                    'last_trained': metadata.get('training_date', 'Unknown'),
                    'metrics': metadata.get('metrics', {})
                }
            else:
                status[model_name] = {
                    'available': False,
                    'error': 'Model not loaded'
                }
        
        return status

# Global model manager instance
model_manager = ModelManager()

# Convenience functions for backward compatibility
def predict_yield(input_data: Dict) -> Dict[str, Any]:
    """Predict yield (backward compatibility)"""
    return model_manager.predict_yield(input_data)

def detect_disease(image_array: np.ndarray) -> Dict[str, Any]:
    """Detect disease (backward compatibility)"""
    return model_manager.detect_disease(image_array)

def recommend_fertilizer(input_data: Dict) -> Dict[str, Any]:
    """Recommend fertilizer (backward compatibility)"""
    return model_manager.recommend_fertilizer(input_data)
