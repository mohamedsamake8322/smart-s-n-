"""
Enterprise Data Validation Utilities
Comprehensive validation for agricultural data inputs
"""
import re
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime, date
import pandas as pd
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Standardized validation result structure"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    cleaned_data: Optional[Dict[str, Any]] = None

class DataValidator:
    """Enterprise-grade data validation system"""
    
    def __init__(self):
        self.crop_types = [
            'Maize', 'Rice', 'Wheat', 'Millet', 'Sorghum', 'Tomato', 
            'Okra', 'Peanuts', 'Cotton', 'Sugarcane', 'Cassava', 'Yam'
        ]
        
        self.soil_types = [
            'Sandy', 'Clay', 'Loamy', 'Silty', 'Peaty', 'Saline'
        ]
        
        self.growth_stages = [
            'Germination', 'Vegetative', 'Flowering', 'Fruiting', 'Maturity'
        ]
        
        self.fertilizer_types = [
            'Urea', 'NPK', 'DAP', 'Organic', 'Compost', 'Specialty'
        ]
        
        # Validation ranges
        self.ranges = {
            'temperature': (-10, 50),
            'humidity': (0, 100),
            'ph': (3.0, 12.0),
            'nitrogen': (0, 300),
            'phosphorus': (0, 200),
            'potassium': (0, 500),
            'rainfall': (0, 1000),
            'wind_speed': (0, 100),
            'solar_radiation': (0, 50),
            'latitude': (-90, 90),
            'longitude': (-180, 180),
            'area_hectares': (0.1, 10000),
            'yield': (0, 20000)
        }
    
    def validate_yield_prediction_input(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate yield prediction input data"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Required fields
        required_fields = [
            'crop_type', 'soil_type', 'temperature', 'humidity', 
            'ph', 'nitrogen', 'phosphorus', 'potassium'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
                continue
            
            # Clean and validate each field
            if field == 'crop_type':
                cleaned_value, field_errors = self._validate_crop_type(data[field])
            elif field == 'soil_type':
                cleaned_value, field_errors = self._validate_soil_type(data[field])
            elif field in ['temperature', 'humidity', 'ph', 'nitrogen', 'phosphorus', 'potassium']:
                cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
            else:
                cleaned_value = data[field]
                field_errors = []
            
            if field_errors:
                errors.extend(field_errors)
            else:
                cleaned_data[field] = cleaned_value
        
        # Optional fields validation
        optional_fields = ['rainfall', 'wind_speed', 'solar_radiation', 'growth_stage']
        for field in optional_fields:
            if field in data and data[field] is not None:
                if field == 'growth_stage':
                    cleaned_value, field_errors = self._validate_growth_stage(data[field])
                else:
                    cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
                
                if field_errors:
                    warnings.extend(field_errors)
                else:
                    cleaned_data[field] = cleaned_value
        
        # Cross-field validation
        cross_validation_errors = self._validate_yield_cross_fields(cleaned_data)
        errors.extend(cross_validation_errors)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_disease_detection_input(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate disease detection input data"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Image validation
        if 'image' not in data or data['image'] is None:
            errors.append("Image data is required for disease detection")
        else:
            image_validation = self._validate_image_data(data['image'])
            if not image_validation[0]:
                errors.extend(image_validation[1])
            else:
                cleaned_data['image'] = data['image']
        
        # Optional metadata validation
        optional_fields = ['crop_type', 'location', 'capture_date']
        for field in optional_fields:
            if field in data and data[field] is not None:
                if field == 'crop_type':
                    cleaned_value, field_errors = self._validate_crop_type(data[field])
                elif field == 'location':
                    cleaned_value, field_errors = self._validate_location(data[field])
                elif field == 'capture_date':
                    cleaned_value, field_errors = self._validate_date(data[field])
                else:
                    cleaned_value = data[field]
                    field_errors = []
                
                if field_errors:
                    warnings.extend(field_errors)
                else:
                    cleaned_data[field] = cleaned_value
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_fertilizer_input(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate fertilizer recommendation input data"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Required fields
        required_fields = [
            'crop_type', 'soil_type', 'ph', 'nitrogen', 'phosphorus', 'potassium'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
                continue
            
            # Validate each field
            if field == 'crop_type':
                cleaned_value, field_errors = self._validate_crop_type(data[field])
            elif field == 'soil_type':
                cleaned_value, field_errors = self._validate_soil_type(data[field])
            elif field in ['ph', 'nitrogen', 'phosphorus', 'potassium']:
                cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
            else:
                cleaned_value = data[field]
                field_errors = []
            
            if field_errors:
                errors.extend(field_errors)
            else:
                cleaned_data[field] = cleaned_value
        
        # Optional fields
        optional_fields = ['growth_stage', 'temperature', 'humidity', 'area_hectares']
        for field in optional_fields:
            if field in data and data[field] is not None:
                if field == 'growth_stage':
                    cleaned_value, field_errors = self._validate_growth_stage(data[field])
                elif field in ['temperature', 'humidity', 'area_hectares']:
                    cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
                else:
                    cleaned_value = data[field]
                    field_errors = []
                
                if field_errors:
                    warnings.extend(field_errors)
                else:
                    cleaned_data[field] = cleaned_value
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_weather_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate weather data input"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Required fields for weather data
        required_fields = ['temperature', 'humidity']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required weather field: {field}")
                continue
            
            cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
            if field_errors:
                errors.extend(field_errors)
            else:
                cleaned_data[field] = cleaned_value
        
        # Optional weather fields
        optional_fields = ['rainfall', 'wind_speed', 'pressure', 'solar_radiation']
        for field in optional_fields:
            if field in data and data[field] is not None:
                cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
                if field_errors:
                    warnings.extend(field_errors)
                else:
                    cleaned_data[field] = cleaned_value
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_farm_location(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate farm location data"""
        errors = []
        warnings = []
        cleaned_data = {}
        
        # Required fields
        required_fields = ['name', 'latitude', 'longitude']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required location field: {field}")
                continue
            
            if field == 'name':
                cleaned_value, field_errors = self._validate_farm_name(data[field])
            elif field in ['latitude', 'longitude']:
                cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
            else:
                cleaned_value = data[field]
                field_errors = []
            
            if field_errors:
                errors.extend(field_errors)
            else:
                cleaned_data[field] = cleaned_value
        
        # Optional fields
        optional_fields = ['area_hectares', 'soil_type', 'crop_type']
        for field in optional_fields:
            if field in data and data[field] is not None:
                if field == 'area_hectares':
                    cleaned_value, field_errors = self._validate_numeric_range(data[field], field)
                elif field == 'soil_type':
                    cleaned_value, field_errors = self._validate_soil_type(data[field])
                elif field == 'crop_type':
                    cleaned_value, field_errors = self._validate_crop_type(data[field])
                else:
                    cleaned_value = data[field]
                    field_errors = []
                
                if field_errors:
                    warnings.extend(field_errors)
                else:
                    cleaned_data[field] = cleaned_value
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned_data if len(errors) == 0 else None
        )
    
    def validate_dataset(self, df: pd.DataFrame, required_columns: List[str]) -> ValidationResult:
        """Validate uploaded dataset"""
        errors = []
        warnings = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("Dataset is empty")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        # Check required columns
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check data types and ranges
        for column in df.columns:
            if column in self.ranges:
                # Validate numeric ranges
                numeric_errors = self._validate_column_ranges(df, column)
                if numeric_errors:
                    warnings.extend(numeric_errors)
            
            # Check for missing values
            missing_count = df[column].isnull().sum()
            if missing_count > 0:
                missing_percentage = (missing_count / len(df)) * 100
                if missing_percentage > 20:
                    errors.append(f"Column '{column}' has {missing_percentage:.1f}% missing values")
                elif missing_percentage > 5:
                    warnings.append(f"Column '{column}' has {missing_percentage:.1f}% missing values")
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"Dataset contains {duplicate_count} duplicate rows")
        
        # Check data size
        if len(df) < 10:
            warnings.append("Dataset is very small (< 10 rows) - results may not be reliable")
        elif len(df) > 100000:
            warnings.append("Dataset is very large (> 100k rows) - processing may be slow")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data={'row_count': len(df), 'column_count': len(df.columns)}
        )
    
    def _validate_crop_type(self, value: Any) -> Tuple[str, List[str]]:
        """Validate crop type"""
        errors = []
        
        if not isinstance(value, str):
            return str(value), ["Crop type must be a string"]
        
        value = value.strip().title()
        
        if value not in self.crop_types:
            errors.append(f"Invalid crop type: {value}. Valid options: {', '.join(self.crop_types)}")
            # Try to find similar crop type
            similar = self._find_similar_string(value, self.crop_types)
            if similar:
                errors.append(f"Did you mean '{similar}'?")
        
        return value, errors
    
    def _validate_soil_type(self, value: Any) -> Tuple[str, List[str]]:
        """Validate soil type"""
        errors = []
        
        if not isinstance(value, str):
            return str(value), ["Soil type must be a string"]
        
        value = value.strip().title()
        
        if value not in self.soil_types:
            errors.append(f"Invalid soil type: {value}. Valid options: {', '.join(self.soil_types)}")
            similar = self._find_similar_string(value, self.soil_types)
            if similar:
                errors.append(f"Did you mean '{similar}'?")
        
        return value, errors
    
    def _validate_growth_stage(self, value: Any) -> Tuple[str, List[str]]:
        """Validate growth stage"""
        errors = []
        
        if not isinstance(value, str):
            return str(value), ["Growth stage must be a string"]
        
        value = value.strip().title()
        
        if value not in self.growth_stages:
            errors.append(f"Invalid growth stage: {value}. Valid options: {', '.join(self.growth_stages)}")
            similar = self._find_similar_string(value, self.growth_stages)
            if similar:
                errors.append(f"Did you mean '{similar}'?")
        
        return value, errors
    
    def _validate_numeric_range(self, value: Any, field_name: str) -> Tuple[float, List[str]]:
        """Validate numeric value within acceptable range"""
        errors = []
        
        # Convert to float
        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            return 0.0, [f"{field_name} must be a numeric value"]
        
        # Check for invalid values
        if np.isnan(numeric_value) or np.isinf(numeric_value):
            return 0.0, [f"{field_name} contains invalid numeric value"]
        
        # Check range
        if field_name in self.ranges:
            min_val, max_val = self.ranges[field_name]
            if numeric_value < min_val or numeric_value > max_val:
                errors.append(f"{field_name} must be between {min_val} and {max_val}")
        
        # Additional field-specific validations
        if field_name == 'ph':
            if numeric_value < 4.0 or numeric_value > 10.0:
                errors.append("pH value is outside typical agricultural range (4.0-10.0)")
        elif field_name == 'humidity':
            if numeric_value > 100:
                errors.append("Humidity cannot exceed 100%")
        elif field_name in ['nitrogen', 'phosphorus', 'potassium']:
            if numeric_value < 0:
                errors.append(f"{field_name} cannot be negative")
        
        return numeric_value, errors
    
    def _validate_image_data(self, image_data: Any) -> Tuple[bool, List[str]]:
        """Validate image data"""
        errors = []
        
        if image_data is None:
            errors.append("Image data is required")
            return False, errors
        
        # Check if it's a file-like object
        if hasattr(image_data, 'read'):
            # File upload object
            if hasattr(image_data, 'name'):
                filename = image_data.name.lower()
                valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    errors.append(f"Invalid image format. Supported formats: {', '.join(valid_extensions)}")
            
            # Check file size (if available)
            if hasattr(image_data, 'size') and image_data.size:
                max_size = 10 * 1024 * 1024  # 10MB
                if image_data.size > max_size:
                    errors.append("Image file is too large (max 10MB)")
        
        # Check if it's a numpy array
        elif isinstance(image_data, np.ndarray):
            if len(image_data.shape) not in [2, 3]:
                errors.append("Image array must be 2D or 3D")
            elif len(image_data.shape) == 3 and image_data.shape[2] not in [1, 3, 4]:
                errors.append("Image must have 1, 3, or 4 channels")
        
        return len(errors) == 0, errors
    
    def _validate_location(self, location_data: Any) -> Tuple[Dict[str, float], List[str]]:
        """Validate location data"""
        errors = []
        cleaned_location = {}
        
        if not isinstance(location_data, dict):
            return {}, ["Location must be a dictionary with latitude and longitude"]
        
        # Validate latitude
        if 'latitude' not in location_data:
            errors.append("Missing latitude in location data")
        else:
            lat, lat_errors = self._validate_numeric_range(location_data['latitude'], 'latitude')
            errors.extend(lat_errors)
            if not lat_errors:
                cleaned_location['latitude'] = lat
        
        # Validate longitude
        if 'longitude' not in location_data:
            errors.append("Missing longitude in location data")
        else:
            lon, lon_errors = self._validate_numeric_range(location_data['longitude'], 'longitude')
            errors.extend(lon_errors)
            if not lon_errors:
                cleaned_location['longitude'] = lon
        
        return cleaned_location, errors
    
    def _validate_date(self, date_value: Any) -> Tuple[str, List[str]]:
        """Validate date value"""
        errors = []
        
        if isinstance(date_value, str):
            # Try to parse date string
            try:
                parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                return parsed_date.isoformat(), []
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_value, '%Y-%m-%d')
                    return parsed_date.isoformat(), []
                except ValueError:
                    errors.append("Invalid date format. Use YYYY-MM-DD or ISO format")
        elif isinstance(date_value, (datetime, date)):
            return date_value.isoformat(), []
        else:
            errors.append("Date must be a string or datetime object")
        
        return str(date_value), errors
    
    def _validate_farm_name(self, name: Any) -> Tuple[str, List[str]]:
        """Validate farm name"""
        errors = []
        
        if not isinstance(name, str):
            return str(name), ["Farm name must be a string"]
        
        name = name.strip()
        
        if len(name) < 2:
            errors.append("Farm name must be at least 2 characters long")
        elif len(name) > 100:
            errors.append("Farm name must be less than 100 characters")
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', name):
            errors.append("Farm name contains invalid characters")
        
        return name, errors
    
    def _validate_yield_cross_fields(self, data: Dict[str, Any]) -> List[str]:
        """Cross-field validation for yield prediction"""
        errors = []
        
        # Check NPK balance
        if all(nutrient in data for nutrient in ['nitrogen', 'phosphorus', 'potassium']):
            n = data['nitrogen']
            p = data['phosphorus']
            k = data['potassium']
            
            # Basic NPK ratio checks
            if n > 0 and p > 0:
                np_ratio = n / p
                if np_ratio > 10:
                    errors.append("Nitrogen to Phosphorus ratio is very high - may cause imbalance")
                elif np_ratio < 1:
                    errors.append("Phosphorus is very high relative to Nitrogen")
        
        # Check temperature-humidity relationship
        if 'temperature' in data and 'humidity' in data:
            temp = data['temperature']
            humidity = data['humidity']
            
            if temp > 35 and humidity > 80:
                errors.append("High temperature and high humidity combination may stress crops")
            elif temp < 10 and humidity > 90:
                errors.append("Low temperature and high humidity may promote disease")
        
        return errors
    
    def _validate_column_ranges(self, df: pd.DataFrame, column: str) -> List[str]:
        """Validate column values against acceptable ranges"""
        warnings = []
        
        if column not in self.ranges:
            return warnings
        
        min_val, max_val = self.ranges[column]
        
        # Check numeric column
        if pd.api.types.is_numeric_dtype(df[column]):
            out_of_range = df[(df[column] < min_val) | (df[column] > max_val)]
            if len(out_of_range) > 0:
                percentage = (len(out_of_range) / len(df)) * 100
                warnings.append(
                    f"Column '{column}': {len(out_of_range)} values "
                    f"({percentage:.1f}%) outside valid range ({min_val}-{max_val})"
                )
        
        return warnings
    
    def _find_similar_string(self, target: str, options: List[str]) -> Optional[str]:
        """Find most similar string using simple similarity"""
        target_lower = target.lower()
        
        # Exact match (case insensitive)
        for option in options:
            if option.lower() == target_lower:
                return option
        
        # Partial match
        for option in options:
            if target_lower in option.lower() or option.lower() in target_lower:
                return option
        
        return None

# Global validator instance
data_validator = DataValidator()

# Convenience functions for backward compatibility
def validate_input(crop: str, ph: float, soil_type: str, 
                  growth_stage: str, temperature: float, humidity: float) -> Tuple[bool, str]:
    """Validate input (backward compatibility)"""
    data = {
        'crop_type': crop,
        'ph': ph,
        'soil_type': soil_type,
        'growth_stage': growth_stage,
        'temperature': temperature,
        'humidity': humidity,
        'nitrogen': 50,  # Default values
        'phosphorus': 25,
        'potassium': 200
    }
    
    result = data_validator.validate_yield_prediction_input(data)
    
    if result.is_valid:
        return True, "Input validation successful"
    else:
        return False, "; ".join(result.errors)

def validate_yield_input(input_data: Dict[str, Any]) -> ValidationResult:
    """Validate yield prediction input (convenience function)"""
    return data_validator.validate_yield_prediction_input(input_data)

def validate_disease_input(input_data: Dict[str, Any]) -> ValidationResult:
    """Validate disease detection input (convenience function)"""
    return data_validator.validate_disease_detection_input(input_data)
