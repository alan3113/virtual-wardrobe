from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return hasher.verify(password, hashed)


def make_token(user_id: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    return jwt.encode({'sub': user_id, 'exp': expiry}, settings.secret_key, algorithm='HS256')


def token_subject(token: str) -> str:
    payload = jwt.decode(token, settings.secret_key, algorithms=['HS256'])
    return payload['sub']
