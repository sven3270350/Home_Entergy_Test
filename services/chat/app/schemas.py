from pydantic import BaseModel
from typing import Optional, Dict, Any

class ChatQuery(BaseModel):
    text: str
    auth_token: str

class ChatResponse(BaseModel):
    answer: str
    data: Dict[str, Any]
    device_id: Optional[int] = None
    time_period: Optional[str] = None

class QueryResult(BaseModel):
    answer: str
    data: Dict[str, Any]
    device_id: Optional[int] = None
    time_period: Optional[str] = None 