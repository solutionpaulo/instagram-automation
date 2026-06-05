# Plano de Melhorias — Instagram Automation

## 🔴 Round 1 — Crítico (Segurança + Confiabilidade) ✅

| Item | Status | Descrição |
|------|--------|-----------|
| 1.1 | ✅ | `.gitignore` seguro — `.env`, `assets/`, `*.pyc`, `*.mp4`, `*.png`, `*.mp3` |
| 1.2 | ✅ | `config.validate()` — falha no startup se chaves obrigatórias ausentes |
| 1.3 | ✅ | Logging estruturado (`logging` + `logger.py`) com níveis e timestamps |
| 1.4 | ✅ | Criar diretórios `assets/`, `assets/images/`, `assets/videos/` automaticamente |
| 1.5 | ✅ | Upload service: retry com backoff exponencial, timeouts configuráveis |
| 1.6 | ✅ | Timeouts e retries configuráveis via `config.py` / `.env` |

## 🟡 Round 2 — Qualidade de Código ✅

| Item | Status | Descrição |
|------|--------|-----------|
| 2.1 | ✅ | Type hints em todos os módulos |
| 2.2 | ✅ | `exceptions.py` — `AppError`, `ConfigError`, `APIError`, `UploadError`, etc. |
| 2.3 | ✅ | Constantes extraídas para `config.py` (INFERENCE_STEPS, GUIDANCE_SCALE, etc.) |
| 2.4 | ✅ | Gemini JSON: validação de 5 campos obrigatórios + fallback contextual |
| 2.5 | ✅ | Ruff config (`ruff.toml`) — py311, 120 chars |

## 🟠 Round 3 — Funcionalidades ✅

| Item | Status | Descrição |
|------|--------|-----------|
| 3.1 | ✅ | Modo `--dry-run` — gera conteúdo mas não posta |
| 3.2 | ✅ | Modo `--preview` — mostra o post completo (`_mostrar_preview`) antes de publicar |
| 3.3 | ✅ | Testes com pytest (text_gen, upload, config) |
| 3.4 | ✅ | `modules/cleanup.py` + `--cleanup` — remove mídia >7 dias |
| 3.5 | ✅ | `.github/workflows/ci.yml` — roda ruff + pytest em todo push |

## 🟢 Round 4 — Extras ✅

| Item | Status | Descrição |
|------|--------|-----------|
| 4.1 | ✅ | Dockerfile multi-estágio (python:3.12-slim + ffmpeg) |
| 4.2 | ✅ | Docstrings em todas as funções públicas e módulos |
| 4.3 | ✅ | README com seção de arquitetura, fluxo e troubleshooting |
