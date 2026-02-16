import os
from dotenv import load_dotenv
from replicate import Client
import requests
from PIL import Image
from io import BytesIO

load_dotenv()

client = Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def generate_marketing_image(prompt, output_file="marketing_image.png"):

    output = client.run(
        "lucataco/sdxl-lightning",
        input={
            "prompt": prompt,
            "width": 1024,
            "height": 1024
        }
    )
    return output[0]

    # 🔥 Handle FileOutput correctly
    image_url = output.url

    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    image.save(output_file)

    print("✅ Image saved successfully:", output_file)
