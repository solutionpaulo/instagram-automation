import time
from composio import Composio
from config import COMPOSIO_API_KEY, COMPOSIO_ENTITY_ID
from modules.upload import upload_para_url_publica

MAX_RETRIES = 5
RETRY_DELAY = 10


def _get_composio():
    if not COMPOSIO_API_KEY:
        raise ValueError(
            "COMPOSIO_API_KEY não configurada. "
            "Crie uma conta grátis em https://composio.dev e coloque a chave no .env"
        )
    composio = Composio(api_key=COMPOSIO_API_KEY)
    return composio.get_entity(COMPOSIO_ENTITY_ID)


def conectar_instagram():
    """Inicia o fluxo OAuth para conectar a conta Instagram Business."""
    entity = _get_composio()
    connection = entity.initiate_connection("instagram")
    url = connection.redirect_url
    print("=" * 60)
    print("ABRA O LINK ABAIXO NO NAVEGADOR PARA AUTORIZAR:")
    print(url)
    print("=" * 60)
    print("\nApós autorizar, a conexão será salva automaticamente.")
    return url


def _get_ig_user_id(entity) -> str | None:
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
            print(f"  ⏳ Erro ao obter user info (tentativa {attempt + 1}): {e}")
            if "connection" in str(e).lower() and "active" in str(e).lower():
                print("  🔗 Instagram não conectado. Execute conectar_instagram() primeiro.")
                return None
            time.sleep(RETRY_DELAY)
    return None


def _criar_e_publicar(entity, ig_user_id: str, media_url: str, legenda: str, is_video: bool = False):
    # Fase 1: criar container
    action = "INSTAGRAM_CREATE_MEDIA_CONTAINER"
    params = {
        "caption": legenda,
        "ig_user_id": ig_user_id,
    }
    if is_video:
        params["video_url"] = media_url
    else:
        params["image_url"] = media_url

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
                break
        except Exception as e:
            print(f"  ⏳ Erro ao criar container (tentativa {attempt + 1}): {e}")
            time.sleep(RETRY_DELAY * (attempt + 1))
    else:
        return False

    # Fase 2: aguardar processamento
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
                break
        except Exception:
            pass
        time.sleep(RETRY_DELAY)

    # Fase 3: publicar
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
                return True
        except Exception as e:
            print(f"  ⏳ Erro ao publicar (tentativa {attempt + 1}): {e}")
            time.sleep(RETRY_DELAY)
    return False


def postar_foto(legenda: str, image_path: str) -> bool:
    entity = _get_composio()

    ig_user_id = _get_ig_user_id(entity)
    if not ig_user_id:
        return False

    print("  📤 Fazendo upload da imagem para URL pública...")
    public_url = upload_para_url_publica(image_path)
    if not public_url:
        print("  ✗ Não foi possível obter URL pública para a imagem")
        return False
    print(f"  ✅ Upload concluído: {public_url[:60]}...")

    return _criar_e_publicar(entity, ig_user_id, public_url, legenda, is_video=False)


def postar_video(legenda: str, video_path: str) -> bool:
    entity = _get_composio()

    ig_user_id = _get_ig_user_id(entity)
    if not ig_user_id:
        return False

    print("  📤 Fazendo upload do vídeo para URL pública...")
    public_url = upload_para_url_publica(video_path)
    if not public_url:
        print("  ✗ Não foi possível obter URL pública para o vídeo")
        return False
    print(f"  ✅ Upload concluído: {public_url[:60]}...")

    return _criar_e_publicar(entity, ig_user_id, public_url, legenda, is_video=True)
