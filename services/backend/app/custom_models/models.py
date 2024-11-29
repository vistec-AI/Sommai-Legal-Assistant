from pydantic import BaseModel, UUID4
from enum import Enum

class ChatJobInQueueMessage(BaseModel):
    job_id: str
    chat_id: UUID4
    answer: str
    status: str

class ModelResponseStatus(Enum):
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"

class UserStatus(Enum):
    ACTIVE = "ACTIVE"

class LawReference(BaseModel):
    score: float
    text: str
    law_name: str
    url: str
    law_code: str