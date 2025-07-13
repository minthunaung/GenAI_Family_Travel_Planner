import replicate
import os
from utils.config import OPENAI_API_KEY
from image_gen.image_generator import display_image_from_url
from controller.shared_types import HybridState
from openai import OpenAI

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def photo_generation_agent(photo_idea = "Good day"):
    def _run(state: HybridState) -> HybridState:
        prompt =  state.photo_idea + " at " + state.location + " on " + state.weather_info 
        client = OpenAI(api_key=OPENAI_API_KEY)
        url = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
        )
        #print(f"Generated photo URL: {url.data[0].url}")
        state.photo_url = f"{url.data[0].url}"
        # Check if photo_url is not None before displaying
        if state.photo_url and state.photo_url.startswith("http"): # Added check for http start
          display_image_from_url(state.photo_url)
        return state
    return _run