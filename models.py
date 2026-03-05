from typing import Optional, List
from pydantic import BaseModel


class IdentifyRequest(BaseModel):
    email : Optional[str] = None
    phoneNumber : Optional[str] = None


class ContactResponse(BaseModel):
    primaryId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondIds : List[int]

class Identify(BaseModel):
    contact : ContactResponse