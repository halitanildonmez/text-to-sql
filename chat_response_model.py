from pydantic import BaseModel

class ChatResponse(BaseModel):
    SQL: str
    explanation: str