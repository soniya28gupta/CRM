from pydantic import BaseModel
from typing import Optional, List
import datetime

EmailStr = str

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    account_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    tags: Optional[str] = ""
    notes: Optional[str] = ""

class ContactCreate(ContactBase):
    pass

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    account_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    tags: Optional[str] = None
    notes: Optional[str] = None

class ContactOut(ContactBase):
    id: int
    org_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    account_name: Optional[str] = None
    assigned_to_name: Optional[str] = None

    class Config:
        from_attributes = True

class ContactPagination(BaseModel):
    items: List[ContactOut]
    total: int
    page: int
    page_size: int
    total_pages: int
