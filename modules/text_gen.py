from config import GEMINI_API_KEY

CATEGORIES = [
    "notícia quente do mercado de games",
    "lançamento de jogo",
    "curiosidade sobre videogames",
    "dica de jogo indie",
    "comparação de consoles",
    "história dos games",
    "análise rápida de gameplay",
    "tendência do setor (e-sports, cloud gaming, etc)",
]

PROMPT_TEMPLATE = """Você é um criador de conteúdo para Instagram sobre o mercado de videogames.
Gere um post completo seguindo o tema: {category}.

Responda APENAS no formato JSON abaixo, sem markdown, sem código extra:

{{
  "titulo": "Título chamativo do post",
  "legenda": "Texto curto e envolvente (máx 200 caracteres) para usar como legenda do post. Inclua call-to-action como 'Comente o que achou!' ou 'Salve para ler depois'",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "imagem_prompt": "Descrição detalhada em inglês para gerar uma imagem no Stable Diffusion que ilustre este post. Inclua estilo, cores e elementos.",
  "video_script": "Roteiro curto de 20-30 segundos para narração em português falando sobre o tema do post de forma dinâmica."
}}"""


_client = None


def _get_client():
    global _client
    if _client is None:
        from google import genai
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY não configurada. "
                "Copie .env.example para .env e adicione sua chave."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def gerar_post(category: str = None) -> dict:
    if category is None:
        import random
        category = random.choice(CATEGORIES)

    client = _get_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT_TEMPLATE.format(category=category),
    )

    import json
    import re

    raw = response.text.strip()

    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "titulo": "Novidade no Mundo dos Games",
            "legenda": raw[:200],
            "hashtags": ["#games", "#videogames", "#gaming", "#gameon", "#mercado"],
            "imagem_prompt": "Vibrant gaming setup with neon lights, controller and monitor",
            "video_script": raw[:300],
        }
