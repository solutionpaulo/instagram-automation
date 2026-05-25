import os
from moviepy.video.VideoClip import ImageClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from gtts import gTTS
from config import VIDEOS_DIR


def criar_video(
    image_path: str,
    texto_narracao: str,
    filename: str,
    titulo: str = None,
) -> str | None:
    os.makedirs(VIDEOS_DIR, exist_ok=True)

    audio_path = _gerar_audio(texto_narracao, filename)
    if not audio_path:
        return None

    duracao = _estimar_duracao(texto_narracao)
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
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        threads=2,
        verbose=False,
        logger=None,
    )

    audio.close()
    clip.close()

    return output_path


def _gerar_audio(texto: str, filename: str) -> str | None:
    try:
        tts = gTTS(text=texto, lang="pt", slow=False)
        audio_path = os.path.join(VIDEOS_DIR, filename.replace(".mp4", ".mp3"))
        tts.save(audio_path)
        return audio_path
    except Exception:
        return None


def _estimar_duracao(texto: str) -> float:
    palavras = len(texto.split())
    return max(palavras / 3.5, 5.0)
