import torch
from diffusers import StableDiffusionPipeline
import os
#This function is to display the image 
from PIL import Image
import requests
from io import BytesIO
from IPython.display import display

def generate_image(prompt: str, output_path="generated.png") -> str:
    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
    image = pipe(prompt).images[0]
    image.save(output_path)
    return f"Image saved to {output_path}"



def display_image_from_url(image_url):
    """
    Fetches an image from a given URL and displays it in the notebook.

    Args:
        image_url (str): The URL of the image to display.
    """
    #print(f"Fetching image from URL: {image_url}")

    try:
        # Fetch the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Open the image using Pillow
        img = Image.open(BytesIO(response.content))

        resized_img = img.resize((512, 512))

        # Display the image in the notebook output
        display(resized_img)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
    except Exception as e:
        print(f"An error occurred while processing the image: {e}")