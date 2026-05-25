# Instagram Automation — Mercado de Videogames

Pipeline totalmente gratuito que gera e publica conteúdo sobre games no Instagram usando IA.

## Stack

| Componente | Ferramenta | Custo |
|---|---|---|
| Geração de texto | Gemini API (google-generativeai) | Grátis (60 req/min) |
| Geração de imagem | Hugging Face Inference API (Stable Diffusion) | Grátis |
| Geração de vídeo | moviepy + gTTS + ffmpeg | Grátis |
| Postagem | instagrapi | Grátis (risco de ban) |
| Agendamento | schedule (biblioteca Python) | Grátis |

## Setup

```bash
# 1. Clonar / entrar na pasta
cd instagram-automation

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar chaves
cp .env.example .env
# Edite .env com suas chaves

# 4. Executar
python main.py --once --type foto   # um post de foto
python main.py --once --type video  # um post de vídeo
python main.py                       # modo agendado (a cada 6h)
```

## Como obter as chaves

- **GEMINI_API_KEY**: https://aistudio.google.com/apikey
- **HF_TOKEN**: https://huggingface.co/settings/tokens
- Instagram: username/senha da conta (use conta secundária!)

## Avisos

- `instagrapi` é não-oficial — use conta secundária, risque blocking
- A Hugging Face Inference API gratuita tem fila em horários de pico
- O script gera placeholders (gradiente + texto) se a imagem falhar
