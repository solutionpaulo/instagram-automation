import os
from io import BytesIO
import requests
from PIL import Image, ImageDraw
from logger import get_logger
from config import HF_TOKEN, HF_IMAGE_MODEL, IMAGES_DIR, HF_TIMEOUT, IMAGE_WIDTH, IMAGE_HEIGHT, INFERENCE_STEPS, GUIDANCE_SCALE

log = get_logger()


def gerar_imagem(positive_prompt: str, filename: str) -> str | None:
    if not positive_prompt:
        positive_prompt = "Vibrant gaming setup with neon lights"

    negative_prompt = "text, watermark, signature, ugly, blurry, low quality"

    payload = {
        "inputs": positive_prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "width": IMAGE_WIDTH,
            "height": IMAGE_HEIGHT,
            "num_inference_steps": INFERENCE_STEPS,
            "guidance_scale": GUIDANCE_SCALE,
        },
    }

    headers = {}
    if HF_TOKEN:
        headers["Authorization"] = f"Bearer {HF_TOKEN}"

    api_url = f"https://api-inference.huggingface.co/models/{HF_IMAGE_MODEL}"

    log.info("Gerando imagem via Hugging Face...")
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=HF_TIMEOUT)
    except requests.Timeout:
        log.warning("Hugging Face timeout após %ds, gerando placeholder", HF_TIMEOUT)
        return _gerar_placeholder(positive_prompt, filename)
    except requests.ConnectionError as e:
        log.warning("Hugging Face: erro de conexão: %s", e)
        return _gerar_placeholder(positive_prompt, filename)

    if response.status_code != 200:
        log.warning("Hugging Face retornou HTTP %d, gerando placeholder", response.status_code)
        return _gerar_placeholder(positive_prompt, filename)

    try:
        image = Image.open(BytesIO(response.content))
        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.LANCZOS)

        os.makedirs(IMAGES_DIR, exist_ok=True)
        filepath = os.path.join(IMAGES_DIR, filename)
        image.save(filepath, "PNG")
        log.info("Imagem salva: %s", filepath)
        return filepath
    except Exception as e:
        log.warning("Erro ao processar imagem: %s", e)
        return _gerar_placeholder(positive_prompt, filename)


def _gerar_placeholder(topic: str, filename: str) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    img = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), (20, 20, 40))
    draw = ImageDraw.Draw(img)

    draw.text((540, 400), topic[:40], fill=(0, 255, 100), anchor="mm")
    draw.text((540, 540), "🎮 Gaming Post", fill=(255, 255, 255), anchor="mm")

    filepath = os.path.join(IMAGES_DIR, filename)
    img.save(filepath, "PNG")
    log.info("Placeholder salvo: %s", filepath)
    return filepath
