from pydantic import BaseModel
from typing import Optional

class SlackEventRequest(BaseModel):
    event_id: str
    user_id: str
    channel_id: str
    text: str
    timestamp: str

class SlackEventResponse(BaseModel):
    request_id: str
    status: str

class RequestStatusResponse(BaseModel):
    request_id: str
    status: str
    llm_response: Optional[str] = None
