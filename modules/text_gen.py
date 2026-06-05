import json
import random
import re
from typing import Any

from google import genai
from logger import get_logger
from config import GEMINI_API_KEY
from exceptions import ConfigError, TextGenError

log = get_logger()

CATEGORIES: list[str] = [
    "notícia quente do mercado de games",
    "lançamento de jogo",
    "curiosidade sobre videogames",
    "dica de jogo indie",
    "comparação de consoles",
    "história dos games",
    "análise rápida de gameplay",
    "tendência do setor (e-sports, cloud gaming, etc)",
]

PROMPT_TEMPLATE: str = """Você é um criador de conteúdo para Instagram sobre o mercado de videogames.
Gere um post completo seguindo o tema: {category}.

Responda APENAS no formato JSON abaixo, sem markdown, sem código extra:

{{
  "titulo": "Título chamativo do post",
  "legenda": "Texto curto e envolvente (máx 200 caracteres) para usar como legenda do post. Inclua call-to-action como 'Comente o que achou!' ou 'Salve para ler depois'",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "imagem_prompt": "Descrição detalhada em inglês para gerar uma imagem no Stable Diffusion que ilustre este post. Inclua estilo, cores e elementos.",
  "video_script": "Roteiro curto de 20-30 segundos para narração em português falando sobre o tema do post de forma dinâmica."
}}"""

_REQUIRED_FIELDS: list[str] = ["titulo", "legenda", "hashtags", "imagem_prompt", "video_script"]

_client: Any | None = None


def _get_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ConfigError(
                "GEMINI_API_KEY não configurada. "
                "Copie .env.example para .env e adicione sua chave."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _parse_json(raw: str) -> dict | None:
    json_match = re.search(r"\{.*\}", raw, re.DOTALL)
    if json_match:
        raw = json_match.group()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _validate_post(data: dict) -> bool:
    for field in _REQUIRED_FIELDS:
        if field not in data or not data[field]:
            log.warning("Campo ausente no JSON do Gemini: %s", field)
            return False
    if not isinstance(data.get("hashtags"), list):
        log.warning("hashtags não é uma lista")
        return False
    return True


def _fallback_post(category: str) -> dict:
    log.warning("Usando fallback genérico para categoria: %s", category)
    return {
        "titulo": f"🔥 {category.upper()} — Fique por dentro!",
        "legenda": (
            f"O mercado de games não para! Falando sobre {category.lower()}. "
            f"O que você acha desse tema? Comente abaixo! 👇"
            f"\n\nSalve para ler depois e compartilhe com quem curte games! 🎮"
        ),
        "hashtags": ["#games", "#videogames", "#gaming", "#gameon", "#mercadodegames"],
        "imagem_prompt": f"Vibrant neon-lit gaming setup with controller, keyboard and monitor, cyberpunk style, {category}, 8k",
        "video_script": (
            f"Fala, galera! Hoje vamos falar sobre {category.lower()}. "
            f"Essa é uma daquelas notícias que todo gamer precisa saber. "
            f"O mercado está cada vez mais aquecido e cheio de novidades. "
            f"Conta aqui nos comentários o que você achou! Até a próxima!"
        ),
    }


def gerar_post(category: str | None = None) -> dict:
    if category is None:
        category = random.choice(CATEGORIES)

    client = _get_client()
    log.info("Gerando post via Gemini (categoria: %s)...", category)

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=PROMPT_TEMPLATE.format(category=category),
        )
        raw = response.text.strip()
        log.debug("Resposta Gemini (primeiros 200 chars): %s...", raw[:200])

        parsed = _parse_json(raw)
        if parsed and _validate_post(parsed):
            log.info("Post gerado com sucesso via Gemini")
            return parsed

        log.warning("Gemini retornou JSON inválido, usando fallback")
    except Exception as e:
        log.error("Erro na chamada Gemini: %s", e)

    return _fallback_post(category)
