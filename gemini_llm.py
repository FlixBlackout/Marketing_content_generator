import os
import base64
import re
import requests
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()


def get_available_image_models(api_key):
    """
    Fetch available image generation models from OpenRouter API
    """
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        
        models_data = response.json()
        image_models = []
        
        for model in models_data.get("data", []):
            model_id = model.get("id", "")
            # Look for image generation models
            image_keywords = ["flux", "stable-diffusion", "sdxl", "dall-e", "imagen"]
            if any(keyword in model_id.lower() for keyword in image_keywords):
                image_models.append(model_id)
        
        return image_models if image_models else [
            "black-forest-labs/flux-1-schnell-free",
            "openai/dall-e-3",
        ]
    except:
        # Fallback models if API call fails
        return [
            "black-forest-labs/flux-1-schnell-free",
            "openai/dall-e-3",
        ]


def generate_marketing_image_openrouter(
    prompt: str,
    output_file: str = "marketing_image.png",
    width: int = 1024,
    height: int = 1024,
):
    """
    Generate image using OpenRouter API
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env file")

    print(f"🎨 Generating image with OpenRouter...")
    
    # Get available models dynamically
    available_models = get_available_image_models(api_key)
    print(f"🔍 Found {len(available_models)} image models to try")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Image Generator"
    }
    
    last_error = None
    
    for i, model_id in enumerate(available_models, 1):
        try:
            print(f"🔄 Trying model {i}/{len(available_models)}: {model_id}")
            
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if response.status_code in [400, 402]:
                error_data = response.json()
                print(f"   ⚠️  Skipped: {error_data.get('error', {}).get('message', 'Error')}")
                last_error = error_data
                continue
                
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # Try to find and download image URL
                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                urls = re.findall(url_pattern, content)
                
                for img_url in urls:
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', 'image', 'oaidalleapiprodscus']):
                        try:
                            img_response = requests.get(img_url, timeout=30)
                            img_response.raise_for_status()
                            img = Image.open(BytesIO(img_response.content))
                            img = img.resize((width, height), Image.LANCZOS)
                            img.save(output_file)
                            print(f"✅ Success! Image saved: {output_file}")
                            return output_file
                        except:
                            continue
                
                # Try base64 if URL failed
                clean_content = content.replace("```", "").strip()
                patterns = [
                    r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)',
                    r'^([A-Za-z0-9+/=]{100,})$',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, clean_content, re.MULTILINE | re.DOTALL)
                    if match:
                        try:
                            base64_str = match.group(1)
                            img_data = base64.b64decode(base64_str)
                            img = Image.open(BytesIO(img_data))
                            img = img.resize((width, height), Image.LANCZOS)
                            img.save(output_file)
                            print(f"✅ Success! Image saved: {output_file}")
                            return output_file
                        except:
                            continue
                            
        except Exception as e:
            print(f"   ⚠️  Error: {str(e)}")
            continue
    
    raise RuntimeError(f"OpenRouter: All {len(available_models)} models failed")


def generate_marketing_image_huggingface(
    prompt: str,
    output_file: str = "marketing_image.png",
    width: int = 1024,
    height: int = 1024,
):
    """
    Generate image using HuggingFace Inference API (Free alternative)
    Get API key at: https://huggingface.co/settings/tokens
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError(
            "HUGGINGFACE_API_KEY not found. "
            "Get a free key at: https://huggingface.co/settings/tokens"
        )

    print(f"🎨 Generating image with HuggingFace (free)...")
    
    # Try multiple models
    models = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
    ]
    
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": "blurry, low quality, distorted",
            "num_inference_steps": 30,
        }
    }
    
    for model in models:
        try:
            print(f"🔄 Trying: {model}")
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            if response.status_code == 503:
                print("   ⚠️  Model loading, waiting 20s...")
                import time
                time.sleep(20)
                response = requests.post(api_url, headers=headers, json=payload, timeout=120)
            
            response.raise_for_status()
            
            img = Image.open(BytesIO(response.content))
            img = img.resize((width, height), Image.LANCZOS)
            img.save(output_file)
            print(f"✅ Success! Image saved: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"   ⚠️  Failed: {str(e)}")
            continue
    
    raise RuntimeError("HuggingFace: All models failed")


def generate_marketing_image(
    prompt: str,
    output_file: str = "marketing_image.png",
    width: int = 1024,
    height: int = 1024,
):
    """
    Generate marketing image - tries multiple providers for reliability
    
    Required in .env:
      OPENROUTER_API_KEY=sk-or-v1-... (get at https://openrouter.ai/keys)
      or
      HUGGINGFACE_API_KEY=hf_... (get at https://huggingface.co/settings/tokens)
    """
    
    print(f"⏳ Generating: '{prompt[:60]}...'")
    
    # Try HuggingFace first (truly free)
    if os.getenv("HUGGINGFACE_API_KEY"):
        try:
            return generate_marketing_image_huggingface(prompt, output_file, width, height)
        except Exception as e:
            print(f"\n⚠️  HuggingFace failed: {str(e)}")
    
    # Try OpenRouter as fallback
    if os.getenv("OPENROUTER_API_KEY"):
        try:
            return generate_marketing_image_openrouter(prompt, output_file, width, height)
        except Exception as e:
            print(f"\n⚠️  OpenRouter failed: {str(e)}")
    
    # If both fail, provide helpful error
    raise RuntimeError(
        "\n❌ Image generation failed.\n\n"
        "💡 Solutions:\n"
        "1. Add to your .env file:\n"
        "   HUGGINGFACE_API_KEY=hf_... (recommended, free)\n"
        "   Get at: https://huggingface.co/settings/tokens\n\n"
        "   OR\n\n"
        "   OPENROUTER_API_KEY=sk-or-v1-...\n"
        "   Get at: https://openrouter.ai/keys\n\n"
        "2. Make sure you have internet connection\n"
        "3. Check API keys are valid"
    )


# For backward compatibility
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Enter image prompt: ")
    
    try:
        generate_marketing_image(prompt)
        print("\n✨ Done!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")