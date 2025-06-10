"""
Enterprise Weather Service Integration
"""
import os
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    """Weather data structure"""
    date: str
    temperature_max: float
    temperature_min: float
    humidity: float
    rainfall: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    pressure: Optional[float] = None
    uv_index: Optional[float] = None

class WeatherService:
    """Enterprise weather service with multiple provider support"""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY", "")
        self.base_urls = {
            "openweather": "https://api.openweathermap.org/data/2.5",
            "weatherapi": "https://api.weatherapi.com/v1",
            "visualcrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
        }
        self.default_provider = "openweather"
        self.cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def get_current_weather(self, latitude: float, longitude: float, 
                           provider: str = None) -> Dict[str, Any]:
        """Get current weather conditions"""
        try:
            provider = provider or self.default_provider
            cache_key = f"current_{latitude}_{longitude}_{provider}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            if provider == "openweather":
                data = self._get_openweather_current(latitude, longitude)
            elif provider == "weatherapi":
                data = self._get_weatherapi_current(latitude, longitude)
            else:
                data = self._get_openweather_current(latitude, longitude)  # Fallback
            
            # Cache the result
            self.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return {'error': str(e)}
    
    def get_weather_forecast(self, latitude: float, longitude: float, 
                           days: int = 7, provider: str = None) -> Dict[str, Any]:
        """Get weather forecast"""
        try:
            provider = provider or self.default_provider
            cache_key = f"forecast_{latitude}_{longitude}_{days}_{provider}"
            
            # Check cache
            if self._is_cached(cache_key):
                return self.cache[cache_key]['data']
            
            if provider == "openweather":
                data = self._get_openweather_forecast(latitude, longitude, days)
            elif provider == "weatherapi":
                data = self._get_weatherapi_forecast(latitude, longitude, days)
            else:
                data = self._get_openweather_forecast(latitude, longitude, days)
            
            # Cache the result
            self.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return {'error': str(e)}
    
    def get_historical_weather(self, latitude: float, longitude: float,
                              start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical weather data"""
        try:
            # For simplicity, using Visual Crossing API which supports historical data
            url = f"{self.base_urls['visualcrossing']}/{latitude},{longitude}/{start_date}/{end_date}"
            
            params = {
                'key': self.api_key,
                'unitGroup': 'metric',
                'include': 'days',
                'elements': 'datetime,tempmax,tempmin,humidity,precip,windspeed,solarradiation'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the data
            processed_data = []
            for day in data.get('days', []):
                weather_point = WeatherData(
                    date=day.get('datetime'),
                    temperature_max=day.get('tempmax', 0),
                    temperature_min=day.get('tempmin', 0),
                    humidity=day.get('humidity', 0),
                    rainfall=day.get('precip', 0),
                    wind_speed=day.get('windspeed', 0),
                    solar_radiation=day.get('solarradiation')
                )
                processed_data.append(weather_point.__dict__)
            
            return {
                'success': True,
                'data': processed_data,
                'location': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical weather: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_openweather_current(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather from OpenWeatherMap"""
        url = f"{self.base_urls['openweather']}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'success': True,
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'location': data['name'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_openweather_forecast(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Get forecast from OpenWeatherMap"""
        url = f"{self.base_urls['openweather']}/forecast"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'cnt': min(days * 8, 40)  # 3-hour intervals, max 5 days
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Process forecast data
        daily_forecasts = {}
        for item in data['list']:
            date = datetime.fromtimestamp(item['dt']).date().isoformat()
            
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'date': date,
                    'temperatures': [],
                    'humidity': [],
                    'rainfall': 0,
                    'wind_speeds': [],
                    'descriptions': []
                }
            
            daily_forecasts[date]['temperatures'].append(item['main']['temp'])
            daily_forecasts[date]['humidity'].append(item['main']['humidity'])
            daily_forecasts[date]['wind_speeds'].append(item['wind']['speed'])
            daily_forecasts[date]['descriptions'].append(item['weather'][0]['description'])
            
            if 'rain' in item:
                daily_forecasts[date]['rainfall'] += item['rain'].get('3h', 0)
        
        # Aggregate daily data
        forecast_list = []
        for date, day_data in list(daily_forecasts.items())[:days]:
            forecast_list.append({
                'date': date,
                'temperature_max': max(day_data['temperatures']),
                'temperature_min': min(day_data['temperatures']),
                'temperature_avg': sum(day_data['temperatures']) / len(day_data['temperatures']),
                'humidity': sum(day_data['humidity']) / len(day_data['humidity']),
                'rainfall': day_data['rainfall'],
                'wind_speed': sum(day_data['wind_speeds']) / len(day_data['wind_speeds']),
                'description': max(set(day_data['descriptions']), key=day_data['descriptions'].count)
            })
        
        return {
            'success': True,
            'forecast': forecast_list,
            'location': {
                'latitude': lat,
                'longitude': lon
            }
        }
    
    def _get_weatherapi_current(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get current weather from WeatherAPI"""
        url = f"{self.base_urls['weatherapi']}/current.json"
        params = {
            'key': self.api_key,
            'q': f"{lat},{lon}",
            'aqi': 'no'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'success': True,
            'temperature': data['current']['temp_c'],
            'humidity': data['current']['humidity'],
            'pressure': data['current']['pressure_mb'],
            'wind_speed': data['current']['wind_kph'] / 3.6,  # Convert to m/s
            'description': data['current']['condition']['text'],
            'icon': data['current']['condition']['icon'],
            'location': data['location']['name'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_weatherapi_forecast(self, lat: float, lon: float, days: int) -> Dict[str, Any]:
        """Get forecast from WeatherAPI"""
        url = f"{self.base_urls['weatherapi']}/forecast.json"
        params = {
            'key': self.api_key,
            'q': f"{lat},{lon}",
            'days': min(days, 10),  # WeatherAPI supports up to 10 days
            'aqi': 'no',
            'alerts': 'no'
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        forecast_list = []
        for day in data['forecast']['forecastday'][:days]:
            forecast_list.append({
                'date': day['date'],
                'temperature_max': day['day']['maxtemp_c'],
                'temperature_min': day['day']['mintemp_c'],
                'temperature_avg': day['day']['avgtemp_c'],
                'humidity': day['day']['avghumidity'],
                'rainfall': day['day']['totalprecip_mm'],
                'wind_speed': day['day']['maxwind_kph'] / 3.6,  # Convert to m/s
                'description': day['day']['condition']['text'],
                'uv_index': day['day']['uv']
            })
        
        return {
            'success': True,
            'forecast': forecast_list,
            'location': {
                'latitude': lat,
                'longitude': lon,
                'name': data['location']['name']
            }
        }
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is cached and still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cached_time < self.cache_duration
    
    def calculate_growing_degree_days(self, temperature_data: List[Dict], 
                                    base_temp: float = 10.0) -> List[Dict]:
        """Calculate Growing Degree Days (GDD)"""
        gdd_data = []
        cumulative_gdd = 0
        
        for day in temperature_data:
            daily_avg = (day.get('temperature_max', 0) + day.get('temperature_min', 0)) / 2
            daily_gdd = max(0, daily_avg - base_temp)
            cumulative_gdd += daily_gdd
            
            gdd_data.append({
                'date': day.get('date'),
                'daily_gdd': daily_gdd,
                'cumulative_gdd': cumulative_gdd,
                'daily_avg_temp': daily_avg
            })
        
        return gdd_data
    
    def analyze_weather_patterns(self, weather_data: List[Dict]) -> Dict[str, Any]:
        """Analyze weather patterns for agricultural insights"""
        if not weather_data:
            return {'error': 'No weather data provided'}
        
        df = pd.DataFrame(weather_data)
        
        analysis = {
            'temperature_analysis': {
                'avg_temp_max': df['temperature_max'].mean(),
                'avg_temp_min': df['temperature_min'].mean(),
                'temperature_range': df['temperature_max'].max() - df['temperature_min'].min(),
                'heat_stress_days': len(df[df['temperature_max'] > 35]),  # Days > 35°C
                'frost_risk_days': len(df[df['temperature_min'] < 2])     # Days < 2°C
            },
            'rainfall_analysis': {
                'total_rainfall': df['rainfall'].sum(),
                'avg_daily_rainfall': df['rainfall'].mean(),
                'rainy_days': len(df[df['rainfall'] > 0.1]),
                'heavy_rain_days': len(df[df['rainfall'] > 10]),
                'dry_spell_max': self._calculate_max_dry_spell(df['rainfall'].tolist())
            },
            'humidity_analysis': {
                'avg_humidity': df['humidity'].mean(),
                'high_humidity_days': len(df[df['humidity'] > 80]),
                'low_humidity_days': len(df[df['humidity'] < 40])
            },
            'agricultural_insights': self._generate_agricultural_insights(df)
        }
        
        return analysis
    
    def _calculate_max_dry_spell(self, rainfall_data: List[float]) -> int:
        """Calculate maximum consecutive dry days"""
        max_dry_spell = 0
        current_dry_spell = 0
        
        for rain in rainfall_data:
            if rain < 0.1:  # Less than 0.1mm considered dry
                current_dry_spell += 1
                max_dry_spell = max(max_dry_spell, current_dry_spell)
            else:
                current_dry_spell = 0
        
        return max_dry_spell
    
    def _generate_agricultural_insights(self, df: pd.DataFrame) -> List[str]:
        """Generate agricultural insights from weather data"""
        insights = []
        
        # Temperature insights
        avg_temp = (df['temperature_max'] + df['temperature_min']).mean() / 2
        if avg_temp > 30:
            insights.append("High temperatures may stress crops - consider irrigation")
        elif avg_temp < 15:
            insights.append("Cool temperatures may slow crop growth")
        
        # Rainfall insights
        total_rain = df['rainfall'].sum()
        if total_rain < 25:  # Less than 25mm per week
            insights.append("Low rainfall - irrigation may be needed")
        elif total_rain > 100:  # More than 100mm per week
            insights.append("High rainfall - monitor for waterlogging and disease")
        
        # Humidity insights
        avg_humidity = df['humidity'].mean()
        if avg_humidity > 85:
            insights.append("High humidity increases disease risk - improve ventilation")
        elif avg_humidity < 30:
            insights.append("Low humidity may cause plant stress")
        
        return insights
    
    def get_weather_alerts(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get weather alerts and warnings"""
        try:
            # This would typically integrate with weather alert services
            # For now, return a basic structure
            return {
                'success': True,
                'alerts': [],
                'warnings': [],
                'advisories': []
            }
        except Exception as e:
            logger.error(f"Error fetching weather alerts: {e}")
            return {'error': str(e), 'success': False}

# Global weather service instance
weather_service = WeatherService()

# Convenience functions for backward compatibility
def fetch_weather_data(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch weather data (backward compatibility)"""
    return weather_service.get_current_weather(latitude, longitude)

def get_weather_forecast(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """Get weather forecast (backward compatibility)"""
    return weather_service.get_weather_forecast(latitude, longitude, days)
