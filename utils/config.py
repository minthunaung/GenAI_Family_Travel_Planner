# utils/config.py
from dotenv import load_dotenv
import os

load_dotenv()


# Check if running in Google Colab
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

if IN_COLAB:
    # Only attempt to import userdata and get secrets if in Colab

    from google.colab import userdata
    WEATHER_API_KEY = userdata.get("WEATHER_API_KEY")
    OPENAI_API_KEY = userdata.get("OpenAi_TravelPlanner_API")
    REPLICATE_API_KEY = userdata.get("Replicate_API")
    HF_API_KEY = userdata.get("HF_AccessToken")
    DB_PATH = "family_travel_planner.db" #userdata.get("DATABASE_PATH") 
    IMAGE_OUTPUT_PATH = "generated.png" #userdata.get("IMAGE_OUTPUT_PATH")
    RAG_INDEX_PATH = "family_travel_rag.index"
    print("Running in Google Colab, retrieved secrets from userdata.") # Optional: add a print statement

else:
    # If not in Colab, rely on environment variables
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_fallback_key")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "OpenAi_TravelPlanner_API")
    REPLICATE_API_KEY = os.getenv("REPLICATE_API_KEY", "your_fallback_key")
    HF_API_KEY = os.getenv("HF_API_KEY", "your_fallback_key")
    DB_PATH = os.getenv("DB_PATH", "family_travel_planner.db")    
    IMAGE_OUTPUT_PATH = os.getenv("IMAGE_OUTPUT_PATH", "generated.png")
    RAG_INDEX_PATH = os.getenv("family_travel_rag.index", "your_fallback")
    print("Not running in Google Colab, relying on environment variables.") # Optional: add a print statement
