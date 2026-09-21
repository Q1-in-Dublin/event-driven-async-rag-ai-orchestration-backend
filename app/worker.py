import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.queue.consumer import dequeue_request, acknowledge_message, initialize_consumer_group
from app.db.session import SessionLocal
from app.db.models import Request
from app.graph.nodes import build_graph


def worker_loop():
    """Continuously dequeue and process requests with Redis Streams."""
    # Initialize consumer group
    initialize_consumer_group()

    graph = build_graph()
    print("Worker started, listening for requests...")

    while True:
        payload = dequeue_request(timeout=2)

        if payload is None:
            continue

        request_id = payload["request_id"]
        user_id = payload["user_id"]
        channel_id = payload["channel_id"]
        user_text = payload["text"]
        message_id = payload.get("_message_id")

        print(f"Processing request {request_id}: {user_text}")

        db = SessionLocal()
        try:
            # Update status to processing
            request = db.query(Request).filter(Request.id == request_id).first()
            if request:
                request.status = "processing"
                db.commit()

            state = {
                "request_id": request_id,
                "user_id": user_id,
                "channel_id": channel_id,
                "user_text": user_text,
            }
            result = graph.invoke(state, config={"recursion_limit": 25})

            # Acknowledge message after successful processing
            if message_id:
                acknowledge_message(message_id)

            print(f"Request {request_id} completed")
        except Exception as e:
            print(f"Error processing request {request_id}: {e}")
            request = db.query(Request).filter(Request.id == request_id).first()
            if request:
                request.status = "failed"
                db.commit()
            # Don't acknowledge on error - message will be re-tried
        finally:
            db.close()

if __name__=="__main__":
    worker_loop()