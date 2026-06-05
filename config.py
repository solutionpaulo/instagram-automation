"""Carregamento de configuração via variáveis de ambiente (.env).

Todas as constantes da aplicação ficam centralizadas aqui.
Use validate() para falhar rapidamente no startup se chaves obrigatórias
estiverem ausentes.
"""

import os
from dotenv import load_dotenv
from logger import get_logger

load_dotenv()

log = get_logger()

# --- Obrigatório ---
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
COMPOSIO_API_KEY: str = os.getenv("COMPOSIO_API_KEY", "")

# --- Opcional ---
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
HF_IMAGE_MODEL: str = os.getenv("HF_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# --- Diretórios ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR: str = os.path.join(BASE_DIR, "assets")
IMAGES_DIR: str = os.path.join(ASSETS_DIR, "images")
VIDEOS_DIR: str = os.path.join(ASSETS_DIR, "videos")
DATA_DIR: str = os.path.join(BASE_DIR, "data")

# --- Agendamento ---
POST_INTERVAL_HOURS: int = int(os.getenv("POST_INTERVAL_HOURS", "6"))
MAX_POSTS_PER_DAY: int = int(os.getenv("MAX_POSTS_PER_DAY", "4"))

# --- API / Timeouts ---
UPLOAD_TIMEOUT: int = int(os.getenv("UPLOAD_TIMEOUT", "60"))
HF_TIMEOUT: int = int(os.getenv("HF_TIMEOUT", "120"))
GEMINI_TIMEOUT: int = int(os.getenv("GEMINI_TIMEOUT", "30"))

# --- Retry ---
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY: int = int(os.getenv("RETRY_DELAY", "10"))

# --- Geração de Imagem ---
IMAGE_WIDTH: int = 1080
IMAGE_HEIGHT: int = 1080
INFERENCE_STEPS: int = 25
GUIDANCE_SCALE: float = 7.5

# --- Composio ---
COMPOSIO_ENTITY_ID: str = os.getenv("COMPOSIO_ENTITY_ID", "instagram_bot")

# --- Cleanup ---
MEDIA_RETENTION_DAYS: int = 7


def validate() -> None:
    """Verifica se todas as variáveis obrigatórias estão configuradas.

    Sai com código 1 se GEMINI_API_KEY ou COMPOSIO_API_KEY estiverem vazias.
    """
    missing: list[str] = []
    if not GEMINI_API_KEY:
        missing.append("GEMINI_API_KEY")
    if not COMPOSIO_API_KEY:
        missing.append("COMPOSIO_API_KEY")

    if missing:
        keys = ", ".join(missing)
        log.error(
            "Variáveis obrigatórias não configuradas: %s. "
            "Copie .env.example para .env e preencha os valores.",
            keys,
        )
        raise SystemExit(1)

    log.info("Configuração validada com sucesso")
