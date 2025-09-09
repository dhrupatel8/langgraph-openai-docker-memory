from typing import List, Literal, Optional
from pydantic import BaseModel
Role = Literal["system", "user", "assistant"]
class ChatMessage(BaseModel):
    role: Role
    content: str
class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: Optional[bool] = False
class ChatResponse(BaseModel):
    message: ChatMessage
    messages: List[ChatMessage]
    session_id: str
