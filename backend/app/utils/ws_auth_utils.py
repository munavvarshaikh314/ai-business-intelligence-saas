import jwt
from fastapi import WebSocket
from app.config import settings


def get_user_id_from_ws(websocket: WebSocket):
    token = websocket.query_params.get("token")

    if not token:
        return None

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("user_id")
    except:
        return None