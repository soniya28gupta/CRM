import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin

# =========================================================================
# MODULE A: REAL ESTATE AND CONSTRUCTION
# =========================================================================

class RealEstateProject(Base, TimestampMixin):
    __tablename__ = "real_estate_projects"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    project_type = Column(String(100), default="Residential", nullable=False)  # Residential, Commercial, Mixed
    status = Column(String(50), default="Under Construction", nullable=False)  # Planning, Under Construction, Ready to Move
    total_units = Column(Integer, default=0, nullable=False)
    available_units = Column(Integer, default=0, nullable=False)
    description = Column(Text, default="", nullable=False)

    properties = relationship("Property", back_populates="project", cascade="all, delete-orphan")


class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("real_estate_projects.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    property_type = Column(String(100), default="Apartment", nullable=False)  # Apartment, Villa, Plot, Commercial Office
    price = Column(Float, default=0.0, nullable=False)
    bedrooms = Column(Integer, default=2, nullable=False)
    bathrooms = Column(Integer, default=2, nullable=False)
    area_sqft = Column(Float, default=1200.0, nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(String(50), default="Available", nullable=False)  # Available, Reserved, Sold
    assigned_broker_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project = relationship("RealEstateProject", back_populates="properties")
    broker = relationship("User", foreign_keys=[assigned_broker_id])
    site_visits = relationship("SiteVisit", back_populates="property")
    bookings = relationship("PropertyBooking", back_populates="property")


class SiteVisit(Base, TimestampMixin):
    __tablename__ = "site_visits"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="CASCADE"), nullable=True)
    scheduled_at = Column(DateTime, nullable=False)
    visitor_name = Column(String(255), nullable=False)
    visitor_phone = Column(String(50), nullable=False)
    status = Column(String(50), default="Scheduled", nullable=False)  # Scheduled, Completed, Cancelled, No-Show
    feedback = Column(Text, default="", nullable=False)
    conducted_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    property = relationship("Property", back_populates="site_visits")


class PropertyBooking(Base, TimestampMixin):
    __tablename__ = "property_bookings"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    booking_amount = Column(Float, default=0.0, nullable=False)
    agreed_price = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="Booked", nullable=False)  # Booked, Payment Pending, Confirmed, Cancelled
    booking_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    property = relationship("Property", back_populates="bookings")


# =========================================================================
# MODULE B: EDTECH AND TRAINING
# =========================================================================

class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="Computer Science", nullable=False)
    duration_weeks = Column(Integer, default=12, nullable=False)
    fee = Column(Float, default=999.0, nullable=False)
    instructor = Column(String(255), default="Staff", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class StudentApplication(Base, TimestampMixin):
    __tablename__ = "student_applications"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    applicant_name = Column(String(255), nullable=False)
    applicant_email = Column(String(255), nullable=False)
    applicant_phone = Column(String(50), nullable=False)
    counsellor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    stage = Column(String(50), default="Inquiry", nullable=False)  # Inquiry, Counselling, Demo Attended, Applied, Enrolled, Dropped
    education_level = Column(String(100), default="Undergraduate", nullable=False)
    notes = Column(Text, default="", nullable=False)

    course = relationship("Course")
    counsellor = relationship("User", foreign_keys=[counsellor_id])


class DemoSession(Base, TimestampMixin):
    __tablename__ = "demo_sessions"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    instructor_name = Column(String(255), nullable=False)
    meeting_link = Column(String(500), default="https://meet.google.com/xyz", nullable=False)
    attendee_count = Column(Integer, default=0, nullable=False)

    course = relationship("Course")


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    student_name = Column(String(255), nullable=False)
    student_email = Column(String(255), nullable=False)
    student_phone = Column(String(50), nullable=False)
    amount_paid = Column(Float, default=0.0, nullable=False)
    payment_status = Column(String(50), default="Paid", nullable=False)  # Paid, Partial, Overdue
    enrollment_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    course = relationship("Course")


# =========================================================================
# MODULE C: BFSI AND FINANCE
# =========================================================================

class ClientPortfolio(Base, TimestampMixin):
    __tablename__ = "client_portfolios"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    portfolio_type = Column(String(100), default="Wealth Management", nullable=False)  # Wealth Management, Retail Insurance, Mutual Funds, Corporate Banking
    total_asset_value = Column(Float, default=50000.0, nullable=False)
    risk_profile = Column(String(50), default="Moderate", nullable=False)  # Conservative, Moderate, Aggressive
    status = Column(String(50), default="Active", nullable=False)
    relationship_manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    manager = relationship("User", foreign_keys=[relationship_manager_id])


class DocumentChecklist(Base, TimestampMixin):
    __tablename__ = "document_checklists"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("client_portfolios.id", ondelete="CASCADE"), nullable=False)
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(100), default="ID_PROOF", nullable=False)  # ID_PROOF, INCOME_STATEMENT, KYC, TAX_RETURN
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_notes = Column(Text, default="", nullable=False)

    portfolio = relationship("ClientPortfolio")


class Renewal(Base, TimestampMixin):
    __tablename__ = "renewals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_id = Column(Integer, ForeignKey("client_portfolios.id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String(255), nullable=False)
    renewal_due_date = Column(DateTime, nullable=False)
    renewal_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(50), default="Upcoming", nullable=False)  # Upcoming, Notified, Renewed, Lapsed

    portfolio = relationship("ClientPortfolio")


# =========================================================================
# MODULE D: HEALTHCARE
# =========================================================================

class HealthcareProvider(Base, TimestampMixin):
    __tablename__ = "healthcare_providers"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    specialty = Column(String(100), default="General Medicine", nullable=False)
    department = Column(String(100), default="Outpatient", nullable=False)
    contact_phone = Column(String(50), nullable=True)
    availability_hours = Column(String(100), default="09:00 AM - 05:00 PM", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)


class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_id = Column(Integer, ForeignKey("healthcare_providers.id", ondelete="CASCADE"), nullable=False)
    patient_name = Column(String(255), nullable=False)
    patient_phone = Column(String(50), nullable=False)
    patient_email = Column(String(255), nullable=True)
    appointment_time = Column(DateTime, nullable=False)
    reason_for_visit = Column(String(255), nullable=False)
    status = Column(String(50), default="Confirmed", nullable=False)  # Confirmed, In Consultation, Completed, Cancelled
    notes = Column(Text, default="", nullable=False)

    provider = relationship("HealthcareProvider")


class PatientFollowUp(Base, TimestampMixin):
    __tablename__ = "patient_follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False)
    follow_up_date = Column(DateTime, nullable=False)
    instructions = Column(Text, default="", nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)

    appointment = relationship("Appointment")


# =========================================================================
# MODULE E: E-COMMERCE AND D2C
# =========================================================================

class EcommerceOrder(Base, TimestampMixin):
    __tablename__ = "ecommerce_orders"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    order_value = Column(Float, default=0.0, nullable=False)
    item_count = Column(Integer, default=1, nullable=False)
    order_status = Column(String(50), default="Processing", nullable=False)  # Processing, Shipped, Delivered, Returned, Cancelled
    shipping_address = Column(String(500), default="", nullable=False)


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    priority = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, URGENT
    status = Column(String(50), default="Open", nullable=False)  # Open, Pending, Resolved, Closed
    assigned_agent_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details = Column(Text, default="", nullable=False)

    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])


class CartRecovery(Base, TimestampMixin):
    __tablename__ = "cart_recoveries"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_email = Column(String(255), nullable=False)
    abandoned_cart_value = Column(Float, default=0.0, nullable=False)
    items_summary = Column(String(500), default="", nullable=False)
    recovery_status = Column(String(50), default="Email Sent", nullable=False)  # Email Sent, Discount Offered, Recovered, Expired
    recovered_order_id = Column(Integer, ForeignKey("ecommerce_orders.id", ondelete="SET NULL"), nullable=True)


# =========================================================================
# MODULE F: B2B SAAS
# =========================================================================

class SaaSProposal(Base, TimestampMixin):
    __tablename__ = "saas_proposals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    prospect_company = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contract_term_months = Column(Integer, default=12, nullable=False)
    annual_recurring_revenue = Column(Float, default=24000.0, nullable=False)
    status = Column(String(50), default="Draft", nullable=False)  # Draft, Sent, Under Review, Accepted, Declined
    plan_tier = Column(String(50), default="Enterprise Tier", nullable=False)


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True)
    company_name = Column(String(255), nullable=False)
    mrr = Column(Float, default=2000.0, nullable=False)
    plan_name = Column(String(100), default="Growth Plan", nullable=False)
    seats = Column(Integer, default=25, nullable=False)
    start_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    renewal_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="Active", nullable=False)  # Active, Past Due, Churned


class OnboardingTask(Base, TimestampMixin):
    __tablename__ = "onboarding_tasks"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    milestone_name = Column(String(255), nullable=False)
    due_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    csm_assigned_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    csm = relationship("User", foreign_keys=[csm_assigned_id])

