"""Integração com Instagram via Composio (API oficial).

Fluxo: OAuth → upload de mídia → criar container → verificar status → publicar.
Requer uma conta Instagram Business conectada via `--setup`.
"""

from composio import Composio
from logger import get_logger
from config import COMPOSIO_API_KEY, COMPOSIO_ENTITY_ID, MAX_RETRIES, RETRY_DELAY, UPLOAD_TIMEOUT
from modules.upload import upload_para_url_publica

log = get_logger()


def _get_composio():
    """Retorna entidade Composio autenticada (singleton)."""
    if not COMPOSIO_API_KEY:
        log.error(
            "COMPOSIO_API_KEY não configurada. "
            "Copie .env.example para .env e adicione a chave."
        )
        raise ValueError("COMPOSIO_API_KEY não configurada")
    composio = Composio(api_key=COMPOSIO_API_KEY)
    return composio.get_entity(COMPOSIO_ENTITY_ID)


def conectar_instagram():
    """Inicia o fluxo OAuth para conectar uma conta Instagram Business.

    Exibe o link de autorização no terminal. A conexão é salva
    automaticamente pelo Composio após a autorização no navegador.
    """
    entity = _get_composio()
    connection = entity.initiate_connection("instagram")
    url = connection.redirect_url
    log.info("=" * 60)
    log.info("ABRA O LINK ABAIXO NO NAVEGADOR PARA AUTORIZAR:")
    log.info(url)
    log.info("=" * 60)
    log.info("Após autorizar, a conexão será salva automaticamente.")
    return url


def _get_ig_user_id(entity) -> str | None:
    """Obtém o ID do usuário Instagram via API do Composio."""
    for attempt in range(MAX_RETRIES):
        try:
            result = entity.execute(
                action_name="INSTAGRAM_GET_USER_INFO",
                params={},
            )
            if result and "data" in result:
                data = result["data"]
                if isinstance(data, dict):
                    return data.get("id") or data.get("ig_user_id")
                return str(data)
        except Exception as e:
            log.warning("Erro ao obter user info (tentativa %d): %s", attempt + 1, e)
            if "connection" in str(e).lower() and "active" in str(e).lower():
                log.error("Instagram não conectado. Execute --setup primeiro.")
                return None
            time.sleep(RETRY_DELAY)
    return None


def _criar_e_publicar(entity, ig_user_id: str, media_url: str, legenda: str, is_video: bool = False):
    """Cria container, aguarda processamento e publica no Instagram."""
    import time

    action = "INSTAGRAM_CREATE_MEDIA_CONTAINER"
    params = {
        "caption": legenda,
        "ig_user_id": ig_user_id,
    }
    if is_video:
        params["video_url"] = media_url
    else:
        params["image_url"] = media_url

    container_id = None
    for attempt in range(MAX_RETRIES):
        try:
            result = entity.execute(action_name=action, params=params)
            if not result:
                continue
            data = result.get("data") or result
            if isinstance(data, dict):
                container_id = data.get("id") or data.get("container_id")
            else:
                container_id = str(data)
            if container_id:
                log.debug("Container criado: %s", container_id)
                break
        except Exception as e:
            log.warning("Erro ao criar container (tentativa %d): %s", attempt + 1, e)
            time.sleep(RETRY_DELAY * (attempt + 1))

    if not container_id:
        log.error("Falha ao criar container após %d tentativas", MAX_RETRIES)
        return False

    for attempt in range(MAX_RETRIES * 2):
        try:
            status = entity.execute(
                action_name="INSTAGRAM_GET_POST_STATUS",
                params={"ig_container_id": container_id},
            )
            status_data = status.get("data") or status
            if isinstance(status_data, dict):
                status_code = status_data.get("status_code") or status_data.get("status", "")
            else:
                status_code = str(status_data)
            if "FINISHED" in status_code.upper():
                log.debug("Container processado: %s", container_id)
                break
        except Exception:
            pass
        time.sleep(RETRY_DELAY)

    for attempt in range(MAX_RETRIES):
        try:
            result = entity.execute(
                action_name="INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH",
                params={
                    "ig_user_id": ig_user_id,
                    "creation_id": container_id,
                },
            )
            if result:
                log.info("Post publicado com sucesso! ID: %s", container_id)
                return True
        except Exception as e:
            log.warning("Erro ao publicar (tentativa %d): %s", attempt + 1, e)
            time.sleep(RETRY_DELAY)

    log.error("Falha ao publicar container %s", container_id)
    return False


def postar_foto(legenda: str, image_path: str) -> bool:
    """Faz upload e publica uma foto no Instagram.

    Returns:
        True se publicado com sucesso.
    """
    entity = _get_composio()
    ig_user_id = _get_ig_user_id(entity)
    if not ig_user_id:
        return False

    log.info("Fazendo upload da imagem para URL pública...")
    public_url = upload_para_url_publica(image_path)
    if not public_url:
        log.error("Não foi possível obter URL pública para a imagem")
        return False

    return _criar_e_publicar(entity, ig_user_id, public_url, legenda, is_video=False)


def postar_video(legenda: str, video_path: str) -> bool:
    """Faz upload e publica um vídeo no Instagram.

    Returns:
        True se publicado com sucesso.
    """
    entity = _get_composio()
    ig_user_id = _get_ig_user_id(entity)
    if not ig_user_id:
        return False

    log.info("Fazendo upload do vídeo para URL pública...")
    public_url = upload_para_url_publica(video_path)
    if not public_url:
        log.error("Não foi possível obter URL pública para o vídeo")
        return False

    return _criar_e_publicar(entity, ig_user_id, public_url, legenda, is_video=True)
