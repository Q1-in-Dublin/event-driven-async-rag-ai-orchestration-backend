import hmac
from app.config import settings


def verify_api_key(token: str) -> bool:
    """API Key 검증 (timing attack 방어)"""
    return hmac.compare_digest(token, settings.api_key)
