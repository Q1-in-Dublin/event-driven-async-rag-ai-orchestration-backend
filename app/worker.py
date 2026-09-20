import json
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.queue.consumer import dequeue_request
from app.db.session import SessionLocal
from app.db.models import Request
from app.graph.nodes import build_graph


def worker_loop():
    """Continuously dequeue and process requests."""
    graph = build_graph()
    print("Worker started, listening for requests...")

    while True:
        payload = dequeue_request(timeout=2)

        if payload is None:
            continue

        request_id = payload["request_id"]
        user_text = payload["text"]
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
                "user_text": user_text,
            }
            result = graph.invoke(state, config={"recursion_limit": 25})
            # Status is already set to "done" by save_result node
            print(f"Request {request_id} completed")
        except Exception as e:
            print(f"Error processing request {request_id}: {e}")
            request = db.query(Request).filter(Request.id == request_id).first()
            if request:
                request.status = "failed"
                db.commit()
        finally:
            db.close()

if __name__=="__main__":
    worker_loop()