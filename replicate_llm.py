import os
from dotenv import load_dotenv
from replicate import Client
import requests
from PIL import Image
from io import BytesIO

load_dotenv()

client = Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

OUTPUT_FOLDER = "generated_images"


def get_next_filename():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    existing_files = [
        f for f in os.listdir(OUTPUT_FOLDER)
        if f.startswith("marketing_image_") and f.endswith(".png")
    ]

    if not existing_files:
        return os.path.join(OUTPUT_FOLDER, "marketing_image_1.png")

    numbers = [
        int(f.split("_")[-1].split(".")[0])
        for f in existing_files
    ]

    next_number = max(numbers) + 1
    return os.path.join(OUTPUT_FOLDER, f"marketing_image_{next_number}.png")


def generate_marketing_image(prompt):

    output = client.run(
        "black-forest-labs/flux-2-pro",
        input={
            "prompt": prompt,
            "width": 1024,
            "height": 1024
        }
    )

    image_url = output.url

    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    output_file = get_next_filename()
    image.save(output_file)

    print("✅ Image saved successfully:", output_file)

    return output_file
