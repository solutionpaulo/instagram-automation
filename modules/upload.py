"""Upload de arquivos de mídia para URLs públicas gratuitas.

Tenta múltiplos serviços (0x0.st, tmpfiles.org, file.io) com retry
exponencial. Retorna None se todas as tentativas falharem.
"""

import os
import time
import requests
from logger import get_logger
from config import UPLOAD_TIMEOUT, MAX_RETRIES, RETRY_DELAY

log = get_logger()


def upload_para_url_publica(file_path: str) -> str | None:
    """Faz upload de arquivo para um serviço de URL pública gratuito.

    Tenta 0x0.st → tmpfiles.org → file.io com backoff exponencial.

    Args:
        file_path: Caminho local do arquivo.

    Returns:
        URL pública do arquivo, ou None se todas as tentativas falharem.
    """
    if not os.path.exists(file_path):
        log.error("Arquivo não encontrado: %s", file_path)
        return None

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    log.info("Iniciando upload: %s (%.1f KB)", file_name, file_size / 1024)

    servicos = [
        ("0x0.st", _upload_0x0),
        ("tmpfiles.org", _upload_tmpfiles),
        ("file.io", _upload_fileio),
    ]

    for nome, fn in servicos:
        for tentativa in range(MAX_RETRIES):
            try:
                log.debug("Tentando %s (tentativa %d/%d)...", nome, tentativa + 1, MAX_RETRIES)
                url = fn(file_path, file_name)
                if url:
                    log.info("Upload concluído via %s: %s", nome, url[:80])
                    return url
                log.warning("%s retornou vazio (tentativa %d)", nome, tentativa + 1)
            except requests.Timeout:
                log.warning("%s: timeout (tentativa %d)", nome, tentativa + 1)
            except requests.ConnectionError:
                log.warning("%s: erro de conexão (tentativa %d)", nome, tentativa + 1)
            except Exception as e:
                log.warning("%s: %s (tentativa %d)", nome, e, tentativa + 1)

            if tentativa < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** tentativa)
                time.sleep(delay)

    log.error("Todas as tentativas de upload falharam para %s", file_name)
    return None


def _upload_0x0(file_path: str, file_name: str) -> str | None:
    """Upload via 0x0.st (sem autenticação, aceita qualquer arquivo)."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://0x0.st",
            files={"file": (file_name, f)},
            timeout=UPLOAD_TIMEOUT,
        )
    if resp.status_code == 200:
        return resp.text.strip()
    log.debug("0x0.st retornou HTTP %d", resp.status_code)
    return None


def _upload_tmpfiles(file_path: str, file_name: str) -> str | None:
    """Upload via tmpfiles.org (download direto via API)."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": (file_name, f)},
            timeout=UPLOAD_TIMEOUT,
        )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") and data.get("data", {}).get("url"):
            return data["data"]["url"].replace(
                "tmpfiles.org/dl/", "tmpfiles.org/api/v1/download/"
            )
    log.debug("tmpfiles.org retornou HTTP %d", resp.status_code)
    return None


def _upload_fileio(file_path: str, file_name: str) -> str | None:
    """Upload via file.io (expira em 1 dia, sem autenticação)."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://file.io",
            files={"file": (file_name, f)},
            data={"expires": "1d"},
            timeout=UPLOAD_TIMEOUT,
        )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success") and data.get("link"):
            return data["link"]
    log.debug("file.io retornou HTTP %d", resp.status_code)
    return None
