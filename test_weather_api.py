from utils.weather_api import WeatherAPI  # Importer la classe

# Instanciation de WeatherAPI
weather_api = WeatherAPI()

# Vérifier si la clé API est bien chargée
print("🔍 OPENWEATHER_API_KEY chargée :", weather_api.openweather_api_key)
