from pydantic import BaseModel
from typing import Optional, List
import datetime

EmailStr = str

# Real Estate Schemas
class PropertyBase(BaseModel):
    title: str
    property_type: str = "Apartment"
    price: float
    bedrooms: int = 2
    bathrooms: int = 2
    area_sqft: float = 1200.0
    location: str
    status: str = "Available"
    project_id: Optional[int] = None
    assigned_broker_id: Optional[int] = None

class PropertyCreate(PropertyBase):
    pass

class PropertyOut(PropertyBase):
    id: int
    org_id: int
    project_name: Optional[str] = None
    broker_name: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class SiteVisitCreate(BaseModel):
    property_id: int
    visitor_name: str
    visitor_phone: str
    scheduled_at: datetime.datetime
    lead_id: Optional[int] = None
    contact_id: Optional[int] = None
    feedback: Optional[str] = ""

class SiteVisitOut(BaseModel):
    id: int
    property_id: int
    property_title: Optional[str] = None
    visitor_name: str
    visitor_phone: str
    scheduled_at: datetime.datetime
    lead_id: Optional[int] = None
    contact_id: Optional[int] = None
    status: str
    feedback: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class PropertyBookingCreate(BaseModel):
    property_id: int
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    booking_amount: float
    agreed_price: float

class PropertyBookingOut(BaseModel):
    id: int
    property_id: int
    property_title: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    booking_amount: float
    agreed_price: float
    status: str
    booking_date: datetime.datetime

    class Config:
        from_attributes = True

# EdTech Schemas
class CourseBase(BaseModel):
    title: str
    category: str = "Computer Science"
    duration_weeks: int = 12
    fee: float = 999.0
    instructor: str = "Staff"
    is_active: bool = True

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    org_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class StudentApplicationCreate(BaseModel):
    course_id: int
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    education_level: str = "Undergraduate"
    notes: Optional[str] = ""

class StudentApplicationOut(BaseModel):
    id: int
    course_id: int
    course_title: Optional[str] = None
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    stage: str
    education_level: str
    notes: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# BFSI Schemas
class ClientPortfolioBase(BaseModel):
    client_name: str
    client_email: EmailStr
    portfolio_type: str = "Wealth Management"
    total_asset_value: float = 50000.0
    risk_profile: str = "Moderate"
    status: str = "Active"

class ClientPortfolioCreate(ClientPortfolioBase):
    pass

class ClientPortfolioOut(ClientPortfolioBase):
    id: int
    org_id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# Healthcare Schemas
class HealthcareProviderBase(BaseModel):
    name: str
    specialty: str = "General Medicine"
    department: str = "Outpatient"
    contact_phone: Optional[str] = None
    availability_hours: str = "09:00 AM - 05:00 PM"
    is_active: bool = True

class HealthcareProviderCreate(HealthcareProviderBase):
    pass

class HealthcareProviderOut(HealthcareProviderBase):
    id: int
    org_id: int

    class Config:
        from_attributes = True

class AppointmentCreate(BaseModel):
    provider_id: int
    patient_name: str
    patient_phone: str
    patient_email: Optional[EmailStr] = None
    appointment_time: datetime.datetime
    reason_for_visit: str
    notes: Optional[str] = ""

class AppointmentOut(BaseModel):
    id: int
    provider_id: int
    provider_name: Optional[str] = None
    patient_name: str
    patient_phone: str
    appointment_time: datetime.datetime
    reason_for_visit: str
    status: str
    notes: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# E-Commerce Schemas
class EcommerceOrderOut(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    order_value: float
    item_count: int
    order_status: str
    shipping_address: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class SupportTicketCreate(BaseModel):
    customer_email: EmailStr
    subject: str
    priority: str = "MEDIUM"
    details: str

class SupportTicketOut(BaseModel):
    id: int
    ticket_number: str
    customer_email: str
    subject: str
    priority: str
    status: str
    details: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# B2B SaaS Schemas
class SaaSProposalCreate(BaseModel):
    prospect_company: str
    contact_person: str
    contact_email: EmailStr
    contract_term_months: int = 12
    annual_recurring_revenue: float = 24000.0
    plan_tier: str = "Enterprise Tier"

class SaaSProposalOut(SaaSProposalCreate):
    id: int
    org_id: int
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class SubscriptionOut(BaseModel):
    id: int
    company_name: str
    mrr: float
    plan_name: str
    seats: int
    start_date: datetime.datetime
    renewal_date: datetime.datetime
    status: str

    class Config:
        from_attributes = True
