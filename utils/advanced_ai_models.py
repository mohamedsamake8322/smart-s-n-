
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
from datetime import datetime, timedelta
import joblib
import warnings
warnings.filterwarnings('ignore')

class AdvancedYieldPredictor:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=200, random_state=42),
            'xgboost': xgb.XGBRegressor(n_estimators=200, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=200, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42, max_iter=1000),
            'elastic_net': ElasticNet(random_state=42)
        }
        self.scalers = {}
        self.encoders = {}
        self.is_trained = False
        self.feature_importance = {}
        self.time_series_model = None
        
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare advanced features including time series components"""
        df = data.copy()
        
        # Time-based features
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            df['day_of_year'] = df['date'].dt.dayofyear
            df['season'] = df['date'].dt.month.map({
                12: 0, 1: 0, 2: 0,  # Winter
                3: 1, 4: 1, 5: 1,   # Spring
                6: 2, 7: 2, 8: 2,   # Summer
                9: 3, 10: 3, 11: 3  # Fall
            })
            
            # Cyclical encoding for seasonal patterns
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        # Advanced agricultural features
        if all(col in df.columns for col in ['temperature', 'rainfall', 'humidity']):
            # Growing Degree Days (GDD)
            df['gdd'] = np.maximum(0, df['temperature'] - 10)  # Base temperature 10Â°C
            
            # Water stress index
            df['water_stress'] = df['rainfall'] / (df['temperature'] + 1)
            
            # Comfort index
            df['comfort_index'] = 1 / (1 + np.abs(df['temperature'] - 25) + np.abs(df['humidity'] - 70))
        
        # Soil quality index
        if all(col in df.columns for col in ['soil_ph', 'soil_nitrogen', 'soil_phosphorus']):
            df['soil_quality'] = (
                (7 - np.abs(df['soil_ph'] - 6.5)) * 0.4 +  # Optimal pH around 6.5
                (df['soil_nitrogen'] / 50) * 0.3 +          # Normalize nitrogen
                (df['soil_phosphorus'] / 30) * 0.3          # Normalize phosphorus
            )
        
        # Interaction features
        if 'temperature' in df.columns and 'rainfall' in df.columns:
            df['temp_rain_interaction'] = df['temperature'] * df['rainfall'] / 1000
        
        return df
    
    def train_ensemble_models(self, data: pd.DataFrame, target_col: str = 'yield'):
        """Train multiple models and create ensemble"""
        df = self.prepare_features(data)
        
        # Prepare target variable
        y = df[target_col].values
        
        # Prepare features
        feature_cols = [col for col in df.columns if col not in [target_col, 'date', 'crop_type']]
        X_numeric = df[feature_cols].select_dtypes(include=[np.number])
        
        # Handle categorical variables
        categorical_cols = df.select_dtypes(include=['object']).columns
        X_categorical = pd.DataFrame()
        
        for col in categorical_cols:
            if col != target_col and col != 'date':
                if col not in self.encoders:
                    self.encoders[col] = LabelEncoder()
                    X_categorical[col] = self.encoders[col].fit_transform(df[col].fillna('Unknown'))
                else:
                    X_categorical[col] = self.encoders[col].transform(df[col].fillna('Unknown'))
        
        # Combine features
        X = pd.concat([X_numeric, X_categorical], axis=1)
        
        # Scale features
        if 'scaler' not in self.scalers:
            self.scalers['scaler'] = StandardScaler()
            X_scaled = self.scalers['scaler'].fit_transform(X)
        else:
            X_scaled = self.scalers['scaler'].transform(X)
        
        # Train models
        results = {}
        
        for name, model in self.models.items():
            try:
                # Time series cross-validation
                tscv = TimeSeriesSplit(n_splits=5)
                scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='r2')
                
                # Fit on full data
                model.fit(X_scaled, y)
                
                # Store results
                results[name] = {
                    'model': model,
                    'cv_scores': scores,
                    'mean_cv_score': scores.mean(),
                    'std_cv_score': scores.std()
                }
                
                # Feature importance (if available)
                if hasattr(model, 'feature_importances_'):
                    self.feature_importance[name] = dict(zip(X.columns, model.feature_importances_))
                
            except Exception as e:
                print(f"Error training {name}: {str(e)}")
                continue
        
        self.is_trained = True
        self.feature_names = X.columns.tolist()
        return results
    
    def predict_advanced(self, input_data: dict, use_ensemble: bool = True):
        """Make advanced predictions using ensemble of models"""
        if not self.is_trained:
            return None
        
        # Convert input to DataFrame
        df = pd.DataFrame([input_data])
        df = self.prepare_features(df)
        
        # Prepare features
        feature_cols = [col for col in df.columns if col in self.feature_names]
        X = df[feature_cols]
        
        # Handle missing features
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0  # Default value for missing features
        
        X = X[self.feature_names]  # Ensure correct order
        X_scaled = self.scalers['scaler'].transform(X)
        
        predictions = {}
        weights = {}
        
        # Get predictions from all models
        for name, model in self.models.items():
            try:
                pred = model.predict(X_scaled)[0]
                predictions[name] = pred
                # Weight by cross-validation score
                weights[name] = max(0, np.mean(cross_val_score(model, X_scaled, [1], cv=3)))
            except:
                continue
        
        if use_ensemble and predictions:
            # Weighted ensemble prediction
            total_weight = sum(weights.values())
            if total_weight > 0:
                ensemble_pred = sum(pred * weights[name] for name, pred in predictions.items()) / total_weight
            else:
                ensemble_pred = np.mean(list(predictions.values()))
            
            # Calculate confidence based on model agreement
            pred_values = list(predictions.values())
            confidence = max(0, 100 - (np.std(pred_values) / np.mean(pred_values) * 100)) if pred_values else 0
            
            return {
                'ensemble_prediction': ensemble_pred,
                'individual_predictions': predictions,
                'confidence': min(100, max(0, confidence)),
                'model_weights': weights
            }
        
        return predictions

class TimeSeriesYieldAnalyzer:
    def __init__(self):
        self.seasonal_models = {}
        self.trend_model = None
        self.is_fitted = False
    
    def analyze_seasonal_patterns(self, data: pd.DataFrame, target_col: str = 'yield'):
        """Analyze seasonal patterns in yield data"""
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract seasonal components
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['season'] = df['date'].dt.month.map({
            12: 'Winter', 1: 'Winter', 2: 'Winter',
            3: 'Spring', 4: 'Spring', 5: 'Spring',
            6: 'Summer', 7: 'Summer', 8: 'Summer',
            9: 'Fall', 10: 'Fall', 11: 'Fall'
        })
        
        # Seasonal statistics
        seasonal_stats = df.groupby(['season', 'crop_type'])[target_col].agg(['mean', 'std', 'count']).reset_index()
        
        # Year-over-year trends
        yearly_trends = df.groupby(['year', 'crop_type'])[target_col].mean().reset_index()
        
        # Multi-year seasonal patterns
        multi_year_seasonal = df.groupby(['season', 'crop_type'])[target_col].mean().reset_index()
        
        return {
            'seasonal_stats': seasonal_stats,
            'yearly_trends': yearly_trends,
            'multi_year_seasonal': multi_year_seasonal
        }
    
    def forecast_yield(self, data: pd.DataFrame, periods: int = 12, target_col: str = 'yield'):
        """Forecast future yields using time series analysis"""
        df = data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Simple moving average forecast
        window_size = min(12, len(df) // 4)
        df['moving_avg'] = df[target_col].rolling(window=window_size).mean()
        
        # Trend calculation
        df['trend'] = np.arange(len(df))
        
        # Generate future dates
        last_date = df['date'].max()
        future_dates = [last_date + timedelta(days=30*i) for i in range(1, periods + 1)]
        
        # Simple forecast (can be enhanced with ARIMA, Prophet, etc.)
        last_values = df[target_col].tail(window_size).values
        trend_slope = (df[target_col].iloc[-1] - df[target_col].iloc[-window_size]) / window_size
        
        forecasts = []
        for i in range(periods):
            # Simple trend + seasonal adjustment
            base_forecast = last_values.mean() + trend_slope * i
            # Add some seasonal variation
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 12)
            forecast = base_forecast * seasonal_factor
            forecasts.append(max(0, forecast))  # Ensure non-negative
        
        return {
            'future_dates': future_dates,
            'forecasted_yields': forecasts,
            'confidence_intervals': [(f * 0.8, f * 1.2) for f in forecasts]
        }

class ScenarioModeler:
    def __init__(self):
        self.base_model = AdvancedYieldPredictor()
        self.scenarios = {}
    
    def create_scenario(self, name: str, base_conditions: dict, modifications: dict):
        """Create a scenario with modified conditions"""
        scenario_conditions = base_conditions.copy()
        scenario_conditions.update(modifications)
        
        self.scenarios[name] = {
            'conditions': scenario_conditions,
            'modifications': modifications
        }
        
        return scenario_conditions
    
    def compare_scenarios(self, scenarios: list, base_model):
        """Compare multiple scenarios and their predicted outcomes"""
        results = {}
        
        for scenario_name in scenarios:
            if scenario_name in self.scenarios:
                conditions = self.scenarios[scenario_name]['conditions']
                prediction = base_model.predict_advanced(conditions)
                
                results[scenario_name] = {
                    'conditions': conditions,
                    'prediction': prediction,
                    'modifications': self.scenarios[scenario_name]['modifications']
                }
        
        return results
    
    def optimize_conditions(self, base_conditions: dict, target_yield: float, model):
        """Find optimal conditions to achieve target yield"""
        best_conditions = base_conditions.copy()
        best_yield = 0
        
        # Simple grid search optimization
        parameters_to_optimize = {
            'fertilizer_amount': np.arange(100, 600, 50),
            'irrigation_frequency': np.arange(1, 8, 1),
            'planting_density': np.arange(0.5, 2.0, 0.1)
        }
        
        for fertilizer in parameters_to_optimize['fertilizer_amount']:
            for irrigation in parameters_to_optimize['irrigation_frequency']:
                for density in parameters_to_optimize['planting_density']:
                    test_conditions = base_conditions.copy()
                    test_conditions.update({
                        'fertilizer_amount': fertilizer,
                        'irrigation_frequency': irrigation,
                        'planting_density': density
                    })
                    
                    try:
                        prediction = model.predict_advanced(test_conditions)
                        if prediction and 'ensemble_prediction' in prediction:
                            predicted_yield = prediction['ensemble_prediction']
                            if predicted_yield > best_yield and predicted_yield <= target_yield * 1.1:
                                best_yield = predicted_yield
                                best_conditions = test_conditions.copy()
                    except:
                        continue
        
        return {
            'optimal_conditions': best_conditions,
            'predicted_yield': best_yield,
            'improvement': best_yield - model.predict_advanced(base_conditions).get('ensemble_prediction', 0)
        }

