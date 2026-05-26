import os
import requests


def upload_para_url_publica(file_path: str) -> str | None:
    """
    Faz upload de um arquivo local para um serviço gratuito
    e retorna uma URL pública acessível.
    Tenta múltiplos serviços como fallback.
    """
    if not os.path.exists(file_path):
        return None

    file_name = os.path.basename(file_path)

    servicos = [
        _upload_0x0,
        _upload_tmpfiles,
        _upload_fileio,
    ]

    erros = []
    for servico in servicos:
        try:
            url = servico(file_path, file_name)
            if url:
                return url
        except Exception as e:
            erros.append(f"{servico.__name__}: {e}")

    print(f"  ✗ Falha ao fazer upload do arquivo. Erros: {'; '.join(erros)}")
    return None


def _upload_0x0(file_path: str, file_name: str) -> str | None:
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://0x0.st",
            files={"file": (file_name, f)},
            timeout=60,
        )
    if resp.status_code == 200:
        return resp.text.strip()
    return None


def _upload_tmpfiles(file_path: str, file_name: str) -> str | None:
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": (file_name, f)},
            timeout=60,
        )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("status") and data.get("data", {}).get("url"):
            return data["data"]["url"].replace(
                "tmpfiles.org/dl/", "tmpfiles.org/api/v1/download/"
            )
    return None


def _upload_fileio(file_path: str, file_name: str) -> str | None:
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://file.io",
            files={"file": (file_name, f)},
            data={"expires": "1d"},
            timeout=60,
        )
    if resp.status_code == 200:
        data = resp.json()
        if data.get("success") and data.get("link"):
            return data["link"]
    return None
