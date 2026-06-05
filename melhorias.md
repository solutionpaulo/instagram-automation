# Plano de Melhorias — Instagram Automation

## 🔴 Round 1 — Crítico (Segurança + Confiabilidade)

| Item | Status | Descrição |
|------|--------|-----------|
| 1.1 | ⬜ | `.gitignore` seguro — `.env`, `assets/`, `__pycache__/`, `*.pyc`, `*.mp4`, `*.png`, `*.mp3` |
| 1.2 | ⬜ | `config.validate()` — falha no startup se chaves obrigatórias ausentes |
| 1.3 | ⬜ | Logging estruturado (`logging` module) com níveis e cores |
| 1.4 | ⬜ | Criar diretórios `assets/images/`, `assets/videos/` automaticamente |
| 1.5 | ⬜ | Upload service: retry com backoff, health check prévio, fallback mais robusto |
| 1.6 | ⬜ | Timeouts e retries configuráveis via `config.py` (não hardcoded) |

## 🟡 Round 2 — Qualidade de Código

| Item | Status | Descrição |
|------|--------|-----------|
| 2.1 | ⬜ | Type hints em todos os módulos |
| 2.2 | ⬜ | Hierarquia de exceções customizadas (`AppError`, `ConfigError`, `APIError`, `UploadError`) |
| 2.3 | ⬜ | Extrair constantes mágicas para `config.py` (INFERENCE_STEPS, GUIDANCE_SCALE, etc.) |
| 2.4 | ⬜ | Melhor fallback do Gemini JSON (validação de campos obrigatórios) |
| 2.5 | ⬜ | Ruff config (`ruff.toml` ou `pyproject.toml`) |

## 🟠 Round 3 — Funcionalidades

| Item | Status | Descrição |
|------|--------|-----------|
| 3.1 | ⬜ | Modo `--dry-run` — gera conteúdo mas não posta (mostra o que seria postado) |
| 3.2 | ⬜ | Modo `--preview` — mostra o post completo antes de publicar |
| 3.3 | ⬜ | Testes com pytest (pelo menos upload, text_gen, image_gen) |
| 3.4 | ⬜ | Cleanup automático de mídia antiga (>7 dias) |
| 3.5 | ⬜ | `.github/workflows/ci.yml` — roda testes + lint em todo push |

## 🟢 Round 4 — Extras

| Item | Status | Descrição |
|------|--------|-----------|
| 4.1 | ⬜ | Dockerfile multi-estágio |
| 4.2 | ⬜ | Docstrings em todas as funções públicas |
| 4.3 | ⬜ | README com seção de arquitetura e troubleshooting |
