import json
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Request, Result
from app.queue.producer import enqueue_request
from app.api.schemas import SlackEventRequest, SlackEventResponse, RequestStatusResponse

def handle_slack_event(event: SlackEventRequest, db: Session)-> SlackEventResponse:
    """
    Receive slack event , save to db enque for processing
    Request_id = str(uuid.uuid4())
    """

    request_id = str(uuid.uuid4())
    # Save to requests table
    request_obj = Request(
        id = request_id,
        user_id = event.user_id,
        channel_id = event.channel_id,
        text = event.text,
        status="queued"
    )
    db.add(request_obj)
    db.commit()

    # Enqueue for processing
    enqueue_request(request_id, event.user_id, event.channel_id, event.text)

    return SlackEventResponse(request_id=request_id, status="queued")

def get_request_status(request_id: str, db: Session) -> RequestStatusResponse:
    """Get request status and result."""
    request_obj = db.query(Request).filter(Request.id == request_id).first()
    
    if not request_obj:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Get result if available
    result = db.query(Result).filter(Result.request_id == request_id).first()
    llm_response = result.llm_response if result else None
    
    return RequestStatusResponse(
        request_id=request_id,
        status=request_obj.status,
        llm_response=llm_response
    )