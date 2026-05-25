import os
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

SESSION_FILE = "session.json"
MAX_RETRIES = 3


def _login() -> Client | None:
    cl = Client()

    if os.path.exists(SESSION_FILE):
        try:
            cl.load_settings(SESSION_FILE)
            cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            cl.get_timeline_feed()
            return cl
        except LoginRequired:
            os.remove(SESSION_FILE)

    try:
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.dump_settings(SESSION_FILE)
        return cl
    except Exception:
        return None


def postar_foto(legenda: str, image_path: str) -> bool:
    cl = _login()
    if not cl:
        return False

    for attempt in range(MAX_RETRIES):
        try:
            cl.photo_upload(image_path, legenda)
            return True
        except ClientError as e:
            if "rate" in str(e).lower():
                time.sleep(300 * (attempt + 1))
                continue
            return False
    return False


def postar_video(legenda: str, video_path: str) -> bool:
    cl = _login()
    if not cl:
        return False

    for attempt in range(MAX_RETRIES):
        try:
            cl.video_upload(video_path, legenda)
            return True
        except ClientError as e:
            if "rate" in str(e).lower():
                time.sleep(300 * (attempt + 1))
                continue
            return False
    return False
