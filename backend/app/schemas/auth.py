from pydantic import BaseModel
from typing import Optional, List
import datetime

EmailStr = str

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    organization_name: Optional[str] = "Acme Global Enterprise"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    role: str = "SALES_REP"
    organization_id: int
    organization_name: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class OrganizationOut(BaseModel):
    id: int
    name: str
    slug: str
    domain: Optional[str] = None
    plan: str
    is_active: bool

    class Config:
        from_attributes = True
