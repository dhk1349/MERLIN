from pydantic import BaseModel
from typing import Dict, List

class SessionRequest(BaseModel):
    session_id: str

class ChatObject(BaseModel):
    role: str
    message: str

class ChatMessage(BaseModel):
    session_id: str
    messages: List[ChatObject]

class RetrivalCandidates(BaseModel):
    topk: List[dict]
    session_id: str


class MetaData(BaseModel):
    meta: List[dict]
    session_id: str