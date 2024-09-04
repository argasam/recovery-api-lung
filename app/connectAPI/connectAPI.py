import aiohttp
from io import BytesIO
import base64
import json
import re
from PIL import Image

from app.connectAPI.removeSuffix import clean_api_response

# Load Secrets from JSON    
with open("app/secrets.json") as f:
    secrets = json.load(f)

# Constants
LLAVA_URL = secrets["LLAVA_URL"]  # Replace with your actual LLaVA API URL

async def query_llava_api(image: BytesIO, prompt: str):
    # Ensure the image is in JPEG format
    image.seek(0)
    pil_image = Image.open(image)
    jpeg_buffer = BytesIO()
    pil_image.save(jpeg_buffer, format="JPEG")
    jpeg_buffer.seek(0)

    # Prepare the form data
    form_data = aiohttp.FormData()
    form_data.add_field('image', jpeg_buffer, filename='image.jpg', content_type='image/jpeg')
    form_data.add_field('prompt', prompt)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(f"{LLAVA_URL}/generate", data=form_data) as response:
                if response.status == 200:
                    response_text = await response.text()
                    # Parse the JSON response
                    response_json = json.loads(response_text.strip())
                    # Extract and return only the generated text
                    return response_json.get("generated_text", "")
                else:
                    error_detail = await response.text()
                    raise ValueError(f"API request failed with status {response.status}: {error_detail}")
        except aiohttp.ClientError as e:
            raise ValueError(f"Network error occurred: {str(e)}")