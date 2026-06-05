class AppError(Exception):
    """Erro base da aplicação."""


class ConfigError(AppError):
    """Erro de configuração (env vars ausentes ou inválidas)."""


class APIError(AppError):
    """Erro em chamada de API externa (Gemini, Hugging Face, etc.)."""


class UploadError(AppError):
    """Erro no upload de mídia para serviços de hospedagem."""


class InstagramError(AppError):
    """Erro na interação com a API do Instagram via Composio."""


class ImageGenError(AppError):
    """Erro na geração de imagem."""


class VideoGenError(AppError):
    """Erro na geração de vídeo."""


class TextGenError(AppError):
    """Erro na geração de texto via Gemini."""
