import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(100), nullable=True)
    lead_source = Column(String(100), default="Website", nullable=False)  # Website, Referral, Cold Outreach, LinkedIn, Google Ads, Event
    industry = Column(String(100), default="Technology", nullable=False)
    status = Column(String(50), default="NEW", nullable=False)  # NEW, CONTACTED, QUALIFIED, UNQUALIFIED, CONVERTED
    priority = Column(String(50), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    estimated_value = Column(Float, default=0.0, nullable=False)
    tags = Column(String(500), default="", nullable=False)  # Comma separated
    notes = Column(Text, default="", nullable=False)
    lead_score = Column(Integer, default=50, nullable=False)
    score_explanation = Column(Text, default="", nullable=False)
    converted_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="leads")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), index=True, nullable=False)
    industry = Column(String(100), default="Technology", nullable=False)
    website = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    company_size = Column(String(50), default="10-50", nullable=True)  # 1-10, 10-50, 50-200, 200-1000, 1000+
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, default="", nullable=False)
    tags = Column(String(500), default="", nullable=False)

    organization = relationship("Organization", back_populates="accounts")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    contacts = relationship("Contact", back_populates="account", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="account", cascade="all, delete-orphan")


class Contact(Base, TimestampMixin):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tags = Column(String(500), default="", nullable=False)
    notes = Column(Text, default="", nullable=False)

    organization = relationship("Organization", back_populates="contacts")
    account = relationship("Account", back_populates="contacts")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    deals = relationship("Deal", back_populates="contact")


class Pipeline(Base, TimestampMixin):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)

    organization = relationship("Organization", back_populates="pipelines")
    stages = relationship("PipelineStage", back_populates="pipeline", order_by="PipelineStage.stage_order", cascade="all, delete-orphan")
    deals = relationship("Deal", back_populates="pipeline")


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    stage_order = Column(Integer, default=0, nullable=False)
    probability = Column(Float, default=10.0, nullable=False)  # 0 to 100%
    color = Column(String(20), default="#3b82f6", nullable=False)

    pipeline = relationship("Pipeline", back_populates="stages")
    deals = relationship("Deal", back_populates="stage")


class Deal(Base, TimestampMixin):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"), nullable=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id", ondelete="RESTRICT"), nullable=False)
    stage_id = Column(Integer, ForeignKey("pipeline_stages.id", ondelete="RESTRICT"), nullable=False)
    value = Column(Float, default=0.0, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    probability = Column(Float, default=10.0, nullable=False)
    expected_close_date = Column(DateTime, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    source = Column(String(100), default="Inbound", nullable=False)
    description = Column(Text, default="", nullable=False)
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN, WON, LOST

    organization = relationship("Organization", back_populates="deals")
    account = relationship("Account", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    pipeline = relationship("Pipeline", back_populates="deals")
    stage = relationship("PipelineStage", back_populates="deals")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # CALL, EMAIL, MEETING, NOTE, TASK, STATUS_CHANGE, ASSIGNMENT, SYSTEM
    subject = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    entity_type = Column(String(50), nullable=False)  # lead, contact, account, deal, industry
    entity_id = Column(Integer, nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)

    created_by = relationship("User", foreign_keys=[created_by_id])


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH
    is_completed = Column(Boolean, default=False, nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    entity_type = Column(String(50), default="lead", nullable=False)
    entity_id = Column(Integer, default=0, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    created_by = relationship("User", foreign_keys=[created_by_id])


class Meeting(Base, TimestampMixin):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="", nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(255), default="Google Meet / Zoom", nullable=False)
    attendees = Column(String(500), default="", nullable=False)
    entity_type = Column(String(50), default="lead", nullable=False)
    entity_id = Column(Integer, default=0, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default="SCHEDULED", nullable=False)  # SCHEDULED, COMPLETED, CANCELLED

    created_by = relationship("User", foreign_keys=[created_by_id])


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", foreign_keys=[user_id])

