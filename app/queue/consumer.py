from redis.exceptions import ResponseError
from app.queue.producer import STREAM_KEY, CONSUMER_GROUP, redis_client


def initialize_consumer_group():
    """Create consumer group if it doesn't exist"""
    try:
        redis_client.xgroup_create(STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True)
    except ResponseError as e:
        # Group already exists
        if "BUSYGROUP" not in str(e):
            raise


def dequeue_request(timeout: int = 0) -> dict | None:
    """Dequeue request from Redis Streams using consumer group"""
    try:
        # XREADGROUP: Read messages from consumer group
        messages = redis_client.xreadgroup(
            CONSUMER_GROUP,
            "worker-1",  # consumer name
            {STREAM_KEY: ">"},  # > means new messages
            count=1,
            block=timeout * 1000 if timeout else 0
        )

        if not messages:
            return None

        stream_key, message_list = messages[0]
        if not message_list:
            return None

        message_id, payload = message_list[0]

        # Store message_id for later acknowledgment
        payload["_message_id"] = message_id

        return payload
    except Exception as e:
        print(f"[DEQUEUE] Error: {e}")
        return None


def acknowledge_message(message_id: str):
    """Acknowledge message after successful processing"""
    try:
        redis_client.xack(STREAM_KEY, CONSUMER_GROUP, message_id)
    except Exception as e:
        print(f"[ACK] Error: {e}")