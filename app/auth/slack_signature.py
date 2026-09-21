import hmac
import hashlib
import time
from app.config import settings


def verify_slack_signature(
    request_body: bytes,
    timestamp: str,
    signature: str
) -> bool:
    """Verify Slack webhook signature (timestamp freshness + HMAC)"""

    # 1. Check timestamp freshness (5 minutes max, replay attack protection)
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > 300:  # 5 minutes = 300 seconds
            return False
    except (ValueError, TypeError):
        return False

    # 2. Verify HMAC
    sig_basestring = f"v0:{timestamp}:{request_body.decode()}"
    computed_sig = "v0=" + hmac.new(
        settings.slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    # 3. Timing attack protection (using compare_digest)
    return hmac.compare_digest(computed_sig, signature)
