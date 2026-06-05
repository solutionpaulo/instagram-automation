import os
import time
from logger import get_logger
from config import ASSETS_DIR, MEDIA_RETENTION_DAYS

log = get_logger()

EXTENSIONS = (".png", ".mp4", ".mp3")


def limpar_midia_antiga() -> int:
    """Remove arquivos de mídia mais antigos que MEDIA_RETENTION_DAYS.

    Returns:
        Número de arquivos removidos.
    """
    if not os.path.exists(ASSETS_DIR):
        log.debug("Diretório %s não existe, nada a limpar", ASSETS_DIR)
        return 0

    agora = time.time()
    corte = agora - (MEDIA_RETENTION_DAYS * 86400)
    removidos = 0

    for root, dirs, files in os.walk(ASSETS_DIR):
        for nome in files:
            if not nome.lower().endswith(EXTENSIONS):
                continue
            caminho = os.path.join(root, nome)
            try:
                mtime = os.path.getmtime(caminho)
                if mtime < corte:
                    os.remove(caminho)
                    removidos += 1
                    log.debug("Removido: %s", caminho)
            except OSError as e:
                log.warning("Erro ao remover %s: %s", caminho, e)

    if removidos:
        log.info("Cleanup: %d arquivo(s) removido(s) (>%d dias)", removidos, MEDIA_RETENTION_DAYS)
    else:
        log.debug("Cleanup: nenhum arquivo antigo encontrado")

    return removidos
