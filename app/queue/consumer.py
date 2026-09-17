import json

from app.queue.producer import QUEUE_KEY, redis_client

def dequeue_request(timeout: int = 0)-> dict | None:
    result = redis_client.brpop(QUEUE_KEY,timeout=timeout)
    if result is None:
        return None

    _, raw = result
    return json.loads(raw)