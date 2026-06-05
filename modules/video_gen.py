"""Geração de vídeos com imagem + narração TTS.

Combina uma imagem de fundo com título sobreposto e narração em português
via gTTS. Usa moviepy para renderização.
"""

import os
from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from gtts import gTTS
from logger import get_logger
from config import VIDEOS_DIR

log = get_logger()


def criar_video(
    image_path: str,
    texto_narracao: str,
    filename: str,
    titulo: str | None = None,
) -> str | None:
    """Gera vídeo com imagem de fundo, título sobreposto e narração TTS.

    Args:
        image_path: Caminho da imagem de fundo.
        texto_narracao: Texto para narração TTS em português.
        filename: Nome do arquivo de saída (ex: video_1234567890.mp4).
        titulo: Título opcional sobreposto no vídeo.

    Returns:
        Caminho do arquivo de vídeo salvo, ou None em caso de falha.
    """
    os.makedirs(VIDEOS_DIR, exist_ok=True)

    audio_path = _gerar_audio(texto_narracao, filename)
    if not audio_path:
        log.error("Falha ao gerar áudio TTS")
        return None

    duracao = _estimar_duracao(texto_narracao)
    log.info("Renderizando vídeo (%.1fs)...", duracao)

    clip = ImageClip(image_path, duration=duracao)
    clip = clip.set_fps(24)

    audio = AudioFileClip(audio_path)
    clip = clip.set_audio(audio)

    if titulo:
        txt = TextClip(
            txt=titulo.upper(),
            fontsize=48,
            color="white",
            font="sans-serif",
            stroke_color="black",
            stroke_width=2,
            size=clip.size,
            align="center",
            duration=duracao,
        )
        txt = txt.set_position(("center", 100))
        clip = CompositeVideoClip([clip, txt])

    output_path = os.path.join(VIDEOS_DIR, filename)
    try:
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            threads=2,
            verbose=False,
            logger=None,
        )
        log.info("Vídeo salvo: %s", output_path)
        return output_path
    except Exception as e:
        log.error("Erro ao renderizar vídeo: %s", e)
        return None
    finally:
        audio.close()
        clip.close()


def _gerar_audio(texto: str, filename: str) -> str | None:
    """Gera arquivo de áudio TTS em português via gTTS."""
    try:
        tts = gTTS(text=texto, lang="pt", slow=False)
        audio_path = os.path.join(VIDEOS_DIR, filename.replace(".mp4", ".mp3"))
        tts.save(audio_path)
        log.debug("Áudio salvo: %s", audio_path)
        return audio_path
    except Exception as e:
        log.error("Erro ao gerar áudio TTS: %s", e)
        return None


def _estimar_duracao(texto: str) -> float:
    """Estima a duração do vídeo baseada na contagem de palavras (mín. 5s)."""
    palavras = len(texto.split())
    return max(palavras / 3.5, 5.0)
