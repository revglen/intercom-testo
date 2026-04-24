from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactRequest(BaseModel):
    role: str
    external_id: str
    email: EmailStr
    name: str

class ContactResponse(BaseModel):
    type: str
    id: str
    workspace_id: str
    external_id: Optional[str] = None
    role: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: Optional[str] = None