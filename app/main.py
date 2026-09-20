from fastapi import FastAPI,Depends
from sqlalchemy.orm import Session 

from app.db.session import get_db
from app.api.schemas import SlackEventRequest
from app.api.handlers import handle_slack_event, get_request_status
from app.db import models
from app.db.session import Base, engine

Base.metadata.create_all(bind=engine)

app  = FastAPI()

@app.get("/health")
def health():
    return {"Status" : "OK"}

@app.post("/slack/events", status_code=202)
def slack_events(event: SlackEventRequest, db: Session = Depends(get_db)):
    """Receive Slack webhook event."""
    return handle_slack_event(event, db)

@app.get("/requests/{request_id}")
def get_request(request_id: str, db: Session = Depends(get_db)):
    """Get request status and result."""
    return get_request_status(request_id, db)
