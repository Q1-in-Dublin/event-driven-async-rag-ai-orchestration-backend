from fastapi import FastAPI, Depends, Request, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import json
import uuid

from app.db.session import get_db
from app.api.schemas import SlackEventRequest
from app.api.handlers import handle_slack_event, get_request_status
from app.auth.slack_signature import verify_slack_signature
from app.auth.api_key import verify_api_key
from app.queue.producer import enqueue_request
from app.db import models
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return {"Status": "OK"}

@app.post("/slack/events")
async def slack_events(request: Request, db: Session = Depends(get_db)):
    """Receive Slack webhook event (with signature verification)."""

    # 1. Read raw body
    body = await request.body()

    # 2. Extract signature and timestamp from headers
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")

    if not timestamp or not signature:
        raise HTTPException(status_code=401, detail="Missing signature headers")

    # 3. Verify Slack signature
    if not verify_slack_signature(body, timestamp, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 4. Parse JSON
    try:
        event_data = json.loads(body.decode())
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # 5. Respond to challenge (first connection)
    if event_data.get("type") == "url_verification":
        return {"challenge": event_data.get("challenge")}

    # 6. Process actual event
    if event_data.get("type") == "event_callback":
        event = event_data.get("event", {})

        request_id = str(uuid.uuid4())
        user_id = event.get("user", "")
        channel_id = event.get("channel", "")
        text = event.get("text", "")

        try:
            # 1. Save request record to database
            request = models.Request(
                id=request_id,
                user_id=user_id,
                channel_id=channel_id,
                text=text,
                status="queued"
            )
            db.add(request)
            db.commit()

            # 2. Push message to queue
            enqueue_request(request_id, user_id, channel_id, text)
        except Exception as e:
            print(f"Error processing request: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to process request")

        # 202 Accepted (return immediately, process in background)
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={"ok": True, "request_id": request_id},
        )

    return {"ok": True}

@app.get("/requests/{request_id}")
def get_request(request_id: str, authorization: str = Header(None), db: Session = Depends(get_db)):
    """Get request status and result (with API Key authentication)."""

    # 1. Extract API Key ("Bearer <token>" format)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization.replace("Bearer ", "")

    # 2. Verify API Key
    if not verify_api_key(token):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # 3. Process request
    return get_request_status(request_id, db)
