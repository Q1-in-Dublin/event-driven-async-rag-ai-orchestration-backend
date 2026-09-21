import hmac
from app.config import settings


def verify_api_key(token: str) -> bool:
    """Verify API key (timing-attack safe)"""
    return hmac.compare_digest(token, settings.api_key)
