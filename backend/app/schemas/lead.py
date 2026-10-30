from pydantic import BaseModel
from typing import Optional, List
import datetime

EmailStr = str

class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    lead_source: str = "Website"
    industry: str = "Technology"
    status: str = "NEW"
    priority: str = "MEDIUM"
    estimated_value: float = 0.0
    tags: Optional[str] = ""
    notes: Optional[str] = ""
    assigned_to_id: Optional[int] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    lead_source: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_value: Optional[float] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None
    lead_score: Optional[int] = None
    score_explanation: Optional[str] = None

class LeadConvert(BaseModel):
    create_account: bool = True
    account_name: Optional[str] = None
    create_deal: bool = True
    deal_name: Optional[str] = None
    deal_value: Optional[float] = None

class LeadOut(LeadBase):
    id: int
    org_id: int
    lead_score: int
    score_explanation: str
    converted_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    assigned_to_name: Optional[str] = None

    class Config:
        from_attributes = True

class LeadPagination(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    page_size: int
    total_pages: int
