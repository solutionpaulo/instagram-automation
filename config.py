import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
VIDEOS_DIR = os.path.join(ASSETS_DIR, "videos")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

POST_INTERVAL_HOURS = 6
MAX_POSTS_PER_DAY = 4

COMPOSIO_ENTITY_ID = "instagram_bot"
