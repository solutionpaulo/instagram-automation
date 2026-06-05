"""
Pipeline automatizado de conteúdo para Instagram:
1. Gera texto + prompt visual via Gemini
2. Gera imagem via Hugging Face (ou placeholder)
3. Gera vídeo curto com narração TTS
4. Publica no Instagram via Composio (API oficial)

Uso:
    python main.py                          # põe no agendador
    python main.py --setup                  # conecta Instagram via OAuth
    python main.py --once --type foto       # executa uma vez
    python main.py --once --type video      # executa uma vez (vídeo)
    python main.py --once --dry-run         # gera conteúdo sem publicar
    python main.py --cleanup                # remove mídia antiga
    python main.py --log-level DEBUG        # log detalhado
"""

import argparse
import os
import random
import sys
import time
from datetime import datetime

from logger import get_logger, setup_logger

log = get_logger()


def _ensure_dirs() -> None:
    from config import ASSETS_DIR, IMAGES_DIR, VIDEOS_DIR, DATA_DIR
    for d in [ASSETS_DIR, IMAGES_DIR, VIDEOS_DIR, DATA_DIR]:
        os.makedirs(d, exist_ok=True)
    log.debug("Diretórios verificados/criados")


def _ensure_deps() -> None:
    try:
        from config import GEMINI_API_KEY, COMPOSIO_API_KEY, POST_INTERVAL_HOURS, MAX_POSTS_PER_DAY, validate
        validate()
        log.info(
            "Intervalo: %dh | Máx/dia: %d | Gemini: %s... | Composio: %s...",
            POST_INTERVAL_HOURS,
            MAX_POSTS_PER_DAY,
            GEMINI_API_KEY[:6],
            COMPOSIO_API_KEY[:6],
        )
    except ImportError as e:
        log.error("Dependência ausente: %s. Execute 'pip install -r requirements.txt'", e)
        sys.exit(1)


def _mostrar_preview(post: dict, img_path: str | None, video_path: str | None = None) -> None:
    """Exibe o conteúdo gerado no terminal antes da publicação."""
    log.info("=" * 60)
    log.info("PREVIEW DO POST")
    log.info("=" * 60)
    log.info("Título:     %s", post["titulo"])
    log.info("Legenda:    %s", post["legenda"])
    log.info("Hashtags:   %s", " ".join(post["hashtags"]))
    log.info("Imagem:     %s", img_path or "N/A")
    if video_path:
        log.info("Vídeo:      %s", video_path)
    log.info("-" * 60)


def pipeline_foto(category: str | None = None, dry_run: bool = False) -> bool:
    from modules.text_gen import gerar_post, CATEGORIES
    from modules.image_gen import gerar_imagem
    from modules.instagram import postar_foto

    if category is None:
        category = random.choice(CATEGORIES)

    log.info("Gerando post de FOTO (categoria: %s)...", category)
    post = gerar_post(category)

    log.info("Título: %s", post["titulo"])
    ts = int(datetime.now().timestamp())
    img_path = gerar_imagem(post["imagem_prompt"], f"post_{ts}.png")

    legenda = f"{post['titulo']}\n\n{post['legenda']}\n\n{' '.join(post['hashtags'])}"

    if dry_run:
        _mostrar_preview(post, img_path)
        log.info("(dry-run) Post NÃO foi publicado")
        return True

    log.info("Publicando foto...")
    ok = postar_foto(legenda, img_path)
    log.info("%s", "✓ Publicado com sucesso" if ok else "✗ Falha ao publicar")
    return ok


def pipeline_video(category: str | None = None, dry_run: bool = False) -> bool:
    from modules.text_gen import gerar_post, CATEGORIES
    from modules.image_gen import gerar_imagem
    from modules.video_gen import criar_video
    from modules.instagram import postar_video

    if category is None:
        category = random.choice(CATEGORIES)

    log.info("Gerando post de VÍDEO (categoria: %s)...", category)
    post = gerar_post(category)

    log.info("Título: %s", post["titulo"])
    ts = int(datetime.now().timestamp())
    img_path = gerar_imagem(post["imagem_prompt"], f"video_img_{ts}.png")
    video_path = criar_video(
        image_path=img_path,
        texto_narracao=post["video_script"],
        filename=f"video_{ts}.mp4",
        titulo=post["titulo"],
    )

    if not video_path:
        log.error("Falha ao gerar vídeo")
        return False

    legenda = f"{post['titulo']}\n\n{post['legenda']}\n\n{' '.join(post['hashtags'])}"

    if dry_run:
        _mostrar_preview(post, img_path, video_path)
        log.info("(dry-run) Post NÃO foi publicado")
        return True

    log.info("Publicando vídeo...")
    ok = postar_video(legenda, video_path)
    log.info("%s", "✓ Publicado com sucesso" if ok else "✗ Falha ao publicar")
    return ok


def executar_uma_vez(tipo: str = "foto", dry_run: bool = False) -> None:
    if dry_run:
        log.info("=== MODO DRY RUN — Nada será publicado ===")

    from modules.text_gen import CATEGORIES
    categoria = random.choice(CATEGORIES)
    if tipo == "video":
        pipeline_video(categoria, dry_run=dry_run)
    else:
        pipeline_foto(categoria, dry_run=dry_run)


def loop_agendado() -> None:
    import schedule

    from config import POST_INTERVAL_HOURS, MAX_POSTS_PER_DAY
    from modules.cleanup import limpar_midia_antiga

    post_count = 0
    last_reset_day = datetime.now().day

    def job():
        nonlocal post_count, last_reset_day

        today = datetime.now().day
        if today != last_reset_day:
            post_count = 0
            last_reset_day = today

        if post_count >= MAX_POSTS_PER_DAY:
            log.warning("Limite diário atingido (%d)", MAX_POSTS_PER_DAY)
            return

        tipo = random.choice(["foto", "foto", "video"])
        if tipo == "video":
            ok = pipeline_video()
        else:
            ok = pipeline_foto()

        if ok:
            post_count += 1

    schedule.every(POST_INTERVAL_HOURS).hours.do(job)

    log.info("Agendador iniciado — a cada %dh, máx %d/dia", POST_INTERVAL_HOURS, MAX_POSTS_PER_DAY)

    # Cleanup semanal no startup
    limpar_midia_antiga()
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Instagram Content Pipeline")
    parser.add_argument("--setup", action="store_true", help="Conecta Instagram via OAuth")
    parser.add_argument("--once", action="store_true", help="Executa uma única vez")
    parser.add_argument("--type", choices=["foto", "video"], default="foto")
    parser.add_argument("--dry-run", action="store_true", help="Gera conteúdo mas não publica")
    parser.add_argument("--cleanup", action="store_true", help="Remove mídia gerada antiga")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARN", "ERROR"], default=None)
    args = parser.parse_args()

    if args.log_level:
        setup_logger(level=args.log_level)

    _ensure_dirs()
    _ensure_deps()

    if args.setup:
        from modules.instagram import conectar_instagram
        conectar_instagram()
    elif args.cleanup:
        from modules.cleanup import limpar_midia_antiga
        removidos = limpar_midia_antiga()
        log.info("Cleanup concluído: %d arquivo(s) removido(s)", removidos)
    elif args.once:
        executar_uma_vez(args.type, dry_run=args.dry_run)
    else:
        loop_agendado()


if __name__ == "__main__":
    main()
