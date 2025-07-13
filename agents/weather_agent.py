import requests
from utils.config import WEATHER_API_KEY # Make sure this imports your actual key
from controller.shared_types import HybridState

def get_weather(location: str) -> str:
    url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": WEATHER_API_KEY, "q": location, "aqi": "no"} # Use "key" and "q"

    try:
        r = requests.get(url, params=params)
        r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = r.json()

        # --- Corrected Parsing Logic ---
        current_data = data.get("current", {})
        if not current_data:
             # Handle cases where 'current' key is missing (e.g., location not found)
             return "Error: Could not retrieve current weather data."

        main_condition = current_data.get("condition", {}).get("text", "Unknown")
        temp_celsius = current_data.get("temp_c", "N/A") # Get Celsius temperature

        return f"{main_condition}, {temp_celsius}°C"
        # --- End of Corrected Parsing Logic ---

    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return f"Error: API request failed ({e})"
    except ValueError as e:
        print(f"Error parsing JSON response: {e}")
        return f"Error: Invalid API response ({e})"
    except Exception as e:
        print(f"An unexpected error occurred in get_weather: {e}")
        return f"Error: Unexpected error ({e})"

# The weather_check_agent function seems fine assuming get_weather works
def weather_check_agent():
    def _run(state: HybridState) -> HybridState:
        # Assuming state.selected_activity can be used to determine a location
        # In a real scenario, you might need a location extraction step
        info = get_weather(state.location) # Call the imported get_weather function
        state.weather_info = info
        keywords = ("clear", "sunny", "cloudy")
        state.weather_ok = any (kw in info.lower() for kw in keywords)
        return state
    return _run
    
