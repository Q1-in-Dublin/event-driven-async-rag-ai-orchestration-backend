import json
import redis
import sys

from app.config import settings

STREAM_KEY = "slack:requests"
CONSUMER_GROUP = "ai-workers"

redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def enqueue_request(request_id: str, user_id: str, channel_id: str, text: str):
    """Enqueue request to Redis Streams"""
    payload = {
        "request_id": request_id,
        "user_id": user_id,
        "channel_id": channel_id,
        "text": text,
    }
    try:
        # XADD: Add message to stream
        message_id = redis_client.xadd(STREAM_KEY, payload)
        print(f"[ENQUEUE] Added to stream {STREAM_KEY}: {message_id}", file=sys.stderr)
    except Exception as e:
        print(f"[ENQUEUE] Error: {e}", file=sys.stderr)
        raise