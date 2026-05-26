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
    python main.py --once --type video
"""

import argparse
import random
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import POST_INTERVAL_HOURS, MAX_POSTS_PER_DAY
from modules.text_gen import gerar_post, CATEGORIES
from modules.image_gen import gerar_imagem
from modules.video_gen import criar_video
from modules.instagram import postar_foto, postar_video, conectar_instagram


def pipeline_foto(category: str = None) -> bool:
    print(f"[{datetime.now()}] Gerando post de FOTO...")
    post = gerar_post(category)

    print(f"  Título: {post['titulo']}")
    img_path = gerar_imagem(post["imagem_prompt"], f"post_{int(datetime.now().timestamp())}.png")

    legenda = f"{post['titulo']}\n\n{post['legenda']}\n\n{' '.join(post['hashtags'])}"

    print(f"  Publicando foto...")
    ok = postar_foto(legenda, img_path)
    print(f"  {'✓ Publicado' if ok else '✗ Falhou'}")
    return ok


def pipeline_video(category: str = None) -> bool:
    print(f"[{datetime.now()}] Gerando post de VÍDEO...")
    post = gerar_post(category)

    print(f"  Título: {post['titulo']}")
    img_path = gerar_imagem(post["imagem_prompt"], f"video_img_{int(datetime.now().timestamp())}.png")
    video_path = criar_video(
        image_path=img_path,
        texto_narracao=post["video_script"],
        filename=f"video_{int(datetime.now().timestamp())}.mp4",
        titulo=post["titulo"],
    )

    if not video_path:
        print("  ✗ Falha ao gerar vídeo")
        return False

    legenda = f"{post['titulo']}\n\n{post['legenda']}\n\n{' '.join(post['hashtags'])}"

    print(f"  Publicando vídeo...")
    ok = postar_video(legenda, video_path)
    print(f"  {'✓ Publicado' if ok else '✗ Falhou'}")
    return ok


def executar_uma_vez(tipo: str = "foto"):
    categoria = random.choice(CATEGORIES)
    if tipo == "video":
        pipeline_video(categoria)
    else:
        pipeline_foto(categoria)


def loop_agendado():
    import schedule
    import time

    post_count = 0
    last_reset_day = datetime.now().day

    def job():
        nonlocal post_count, last_reset_day

        today = datetime.now().day
        if today != last_reset_day:
            post_count = 0
            last_reset_day = today

        if post_count >= MAX_POSTS_PER_DAY:
            print(f"[{datetime.now()}] Limite diário atingido ({MAX_POSTS_PER_DAY})")
            return

        tipo = random.choice(["foto", "foto", "video"])  # mais fotos que vídeos
        if tipo == "video":
            ok = pipeline_video()
        else:
            ok = pipeline_foto()

        if ok:
            post_count += 1

    schedule.every(POST_INTERVAL_HOURS).hours.do(job)

    print(f"🤖 Agendador iniciado — a cada {POST_INTERVAL_HOURS}h, max {MAX_POSTS_PER_DAY}/dia")
    job()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Instagram Content Pipeline")
    parser.add_argument("--setup", action="store_true", help="Conecta Instagram via OAuth")
    parser.add_argument("--once", action="store_true", help="Executa uma única vez")
    parser.add_argument("--type", choices=["foto", "video"], default="foto")
    args = parser.parse_args()

    if args.setup:
        conectar_instagram()
    elif args.once:
        executar_uma_vez(args.type)
    else:
        loop_agendado()
