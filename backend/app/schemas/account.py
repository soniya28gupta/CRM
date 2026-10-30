from pydantic import BaseModel
from typing import Optional, List
import datetime

EmailStr = str

class AccountBase(BaseModel):
    name: str
    industry: str = "Technology"
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company_size: Optional[str] = "10-50"
    assigned_to_id: Optional[int] = None
    description: Optional[str] = ""
    tags: Optional[str] = ""

class AccountCreate(AccountBase):
    pass

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    company_size: Optional[str] = None
    assigned_to_id: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[str] = None

class AccountOut(AccountBase):
    id: int
    org_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    assigned_to_name: Optional[str] = None
    contacts_count: int = 0
    deals_count: int = 0
    total_deal_value: float = 0.0

    class Config:
        from_attributes = True

class AccountPagination(BaseModel):
    items: List[AccountOut]
    total: int
    page: int
    page_size: int
    total_pages: int
