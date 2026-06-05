# Instagram Automation — Mercado de Videogames

Pipeline totalmente gratuito que gera e publica conteúdo sobre games no Instagram usando IA.

## Stack

| Componente | Ferramenta | Custo |
|---|---|---|
| Geração de texto | Gemini API (google-generativeai) | Grátis (60 req/min) |
| Geração de imagem | Hugging Face Inference API (Stable Diffusion) | Grátis |
| Geração de vídeo | moviepy + gTTS + ffmpeg | Grátis |
| Postagem | Composio (Instagram Graph API oficial) | Grátis (20K calls/mês) |
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

# 4. Conectar Instagram via OAuth
python main.py --setup
# → Abra o link gerado no navegador e autorize a conta Business

# 5. Executar
python main.py --once --type foto   # um post de foto
python main.py --once --type video  # um post de vídeo
python main.py --once --dry-run     # gera conteúdo sem publicar
python main.py --cleanup            # remove mídia antiga (>7 dias)
python main.py                       # modo agendado (a cada 6h)
```

## Arquitetura

```
instagram-automation/
├── main.py              # CLI + agendador (entry point)
├── config.py            # Constantes centralizadas + validate()
├── logger.py            # Logging estruturado (níveis + timestamp)
├── exceptions.py        # Hierarquia de exceções (AppError ← ConfigError, APIError, …)
├── modules/
│   ├── text_gen.py      # Gemini: gera JSON com 5 campos validados
│   ├── image_gen.py     # Hugging Face: imagem 1080×1080 + placeholder fallback
│   ├── video_gen.py     # moviepy + gTTS: vídeo com narração em português
│   ├── instagram.py     # Composio: OAuth + criar container + publicar
│   ├── upload.py        # Upload gratuito (0x0.st / tmpfiles / file.io)
│   └── cleanup.py       # Limpeza automática de mídia antiga
├── tests/               # Testes pytest
│   ├── test_text_gen.py
│   ├── test_upload.py
│   └── test_config.py
├── .github/workflows/   # CI: ruff + pytest em cada push
├── Dockerfile           # Container multi-estágio
└── melhoria.md          # Plano de melhorias (4 rounds, 9/15 items)
```

### Fluxo de um post

1. `main.py` escolhe categoria aleatória + tipo (foto/video)
2. `text_gen.py`: chama Gemini → valida JSON → fallback se inválido
3. `image_gen.py`: gera imagem (HF ou placeholder)
4. (se vídeo) `video_gen.py`: cria vídeo com imagem + narração TTS
5. `instagram.py`: upload para URL pública → container → publish
6. Logging em cada etapa via `logger.py`

## Como obter as chaves

### GEMINI_API_KEY
- https://aistudio.google.com/apikey
- Clique em "Get API Key" → Crie uma chave gratuita

### COMPOSIO_API_KEY
1. Crie conta grátis em https://composio.dev (sem cartão de crédito)
2. Vá em **Settings → API Keys**
3. Clique **Generate API Key** e copie
4. Coloque no `.env` como `COMPOSIO_API_KEY=sua_chave_aqui`

### HF_TOKEN (opcional)
- https://huggingface.co/settings/tokens
- Necessário apenas se quiser usar modelos de imagem via Hugging Face

## Conectando o Instagram

O `python main.py --setup` gera um link de autenticação OAuth.

**Requisitos da conta Instagram:**
- Deve ser uma conta **Business** ou **Creator**
- Precisa estar vinculada a uma **Página do Facebook**
- Contas pessoais **não funcionam** com a API oficial

> Se não tiver uma conta Business, vá em Configurações → Tipo de conta no Instagram e mude para Criador ou Empresa.

## Limites gratuitos

| Recurso | Limite |
|---|---|
| Composio Free | 20.000 chamadas de ferramentas/mês |
| Gemini API | 60 requisições/minuto |
| Hugging Face Inference | Depende do modelo, geralmente 30 req/min |
| Instagram API | 25 posts a cada 24h (rolante) |

Uma chamada por post = ~3-4 tools calls (user info + criar container + verificar status + publicar). Com 20K/mês dá para ~5.000 posts.

## Troubleshooting

| Problema | Causa provável | Solução |
|---|---|---|
| `SystemExit(1)` no startup | GEMINI_API_KEY ou COMPOSIO_API_KEY ausente | Configure `.env` |
| "Instagram não conectado" | OAuth não realizado | `python main.py --setup` |
| Hugging Face lento/caindo | Serviço gratuito sob demanda | Placeholder é gerado automaticamente |
| Upload falhou | 0x0.st/tmpfiles fora do ar | Log avisa, tenta próximo serviço |
| "Container não processado" | Instagram demorou para processar | Retry automático (até 10 tentativas) |
| `ffmpeg not found` | ffmpeg não instalado | `apt install ffmpeg` ou `choco install ffmpeg` |

## Observações

- A mídia gerada (imagens/vídeos) é enviada para serviços gratuitos de hospedagem temporária (0x0.st, tmpfiles.org) para gerar URLs públicas exigidas pela API oficial do Instagram
- Se a Hugging Face estiver lenta, o script gera placeholders (gradiente + texto) como fallback
- O agendador respeita o limite diário configurado em `config.py` (`MAX_POSTS_PER_DAY`)
- Mídia com mais de 7 dias é removida automaticamente no startup do agendador ou via `--cleanup`
