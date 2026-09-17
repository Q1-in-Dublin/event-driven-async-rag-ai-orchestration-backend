import json
import redis

from app.config import settings

QUEUE_KEY = "slack:requests:queue"

redis_client = redis.from_url(settings.redis_url,decode_responses=True)

def enqueue_request(request_id: str, user_id:str, channel_id:str,text:str):
    payload = {
        "request_id": request_id,
        "user_id": user_id,
        "channel_id": channel_id,
        "text":text,
    }
    redis_client.lpush(QUEUE_KEY,json.dumps(payload))