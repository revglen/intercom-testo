from pydantic import BaseModel
from typing import Optional

class FromUser(BaseModel):
    type: str = "user"
    id: str

class RequestConversation(BaseModel):
    from_user: FromUser
    body: str

    def to_intercom(self):
        return {
            "from": self.from_user.dict(),
            "body": self.body
        }
    
class ConversationResponse(BaseModel):
    type: str
    id: str
    created_at: int
    updated_at: Optional[int] = None

class ReplyConversationRequest(BaseModel):
    message_type: str = "comment"
    type: str = "user"
    intercom_user_id: str
    body: str