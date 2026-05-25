import requests
import os
from PIL import Image
from io import BytesIO
from config import HF_TOKEN, HF_IMAGE_MODEL, IMAGES_DIR


def gerar_imagem(positive_prompt: str, filename: str) -> str | None:
    if not positive_prompt:
        positive_prompt = "Vibrant gaming setup with neon lights"

    negative_prompt = "text, watermark, signature, ugly, blurry, low quality"

    payload = {
        "inputs": positive_prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": 1080,
            "height": 1080,
            "num_inference_steps": 25,
            "guidance_scale": 7.5,
        },
    }

    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    api_url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

    response = requests.post(api_url, headers=headers, json=payload, timeout=120)

    if response.status_code != 200:
        return _gerar_placeholder(positive_prompt, filename)

    try:
        image = Image.open(BytesIO(response.content))
        image = image.resize((1080, 1080), Image.LANCZOS)

        os.makedirs(IMAGES_DIR, exist_ok=True)
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath, "PNG")
        return filepath
    except Exception:
        return _gerar_placeholder(positive_prompt, filename)


def _gerar_placeholder(topic: str, filename: str) -> str:
    from PIL import ImageDraw, ImageFont

    os.makedirs(IMAGES_DIR, exist_ok=True)
    img = Image.new("RGB", (1080, 1080), (20, 20, 40))
    draw = ImageDraw.Draw(img)

    draw.text((540, 400), topic[:40], fill=(0, 255, 100), anchor="mm")
    draw.text((540, 540), "🎮 Gaming Post", fill=(255, 255, 255), anchor="mm")

    filepath = os.path.join(IMAGES_DIR, filename)
    img.save(filepath, "PNG")
    return filepath
