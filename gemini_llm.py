import os
from dotenv import load_dotenv
from google import genai
from PIL import Image
from io import BytesIO

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_marketing_image(prompt, output_file="marketing_image.png"):

    response = client.models.generate_images(
        model="gemini-2.5-flash-image-preview",
        prompt=prompt,
        config={
            "number_of_images": 1,
            "output_mime_type": "image/png"
        }
    )

    image_bytes = response.generated_images[0].image.image_bytes

    image = Image.open(BytesIO(image_bytes))
    image.save(output_file)

    print("✅ Image saved successfully")
    print([m.name for m in client.models.list() if "image" in m.name])