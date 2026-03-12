from pydantic import BaseModel

class ErrorAnalysis(BaseModel):
    root_cause: str
    explanation: str
    suggested_fix: str
