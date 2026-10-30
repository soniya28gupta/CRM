from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import require_org_record, require_org_user
from app.models.organization import OrganizationMembership
from app.models.crm import Contact, Lead
from app.models.industries import (
    Property, RealEstateProject, SiteVisit, PropertyBooking,
    Course, StudentApplication, DemoSession, Enrollment,
    ClientPortfolio, DocumentChecklist, Renewal,
    HealthcareProvider, Appointment, PatientFollowUp,
    EcommerceOrder, SupportTicket, CartRecovery,
    SaaSProposal, Subscription, OnboardingTask
)
from app.schemas.industry import (
    PropertyCreate, PropertyOut,
    SiteVisitCreate, SiteVisitOut,
    PropertyBookingCreate, PropertyBookingOut,
    CourseCreate, CourseOut,
    StudentApplicationCreate, StudentApplicationOut,
    ClientPortfolioCreate, ClientPortfolioOut,
    HealthcareProviderOut, AppointmentCreate, AppointmentOut,
    EcommerceOrderOut, SupportTicketCreate, SupportTicketOut,
    SaaSProposalCreate, SaaSProposalOut, SubscriptionOut
)

router = APIRouter(prefix="/industries", tags=["Industry-Specific Modules"])

# =========================================================================
# MODULE A: REAL ESTATE & CONSTRUCTION
# =========================================================================

@router.get("/real-estate/properties", response_model=List[PropertyOut])
def get_properties(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    props = db.query(Property).filter(Property.org_id == membership.organization_id).all()
    results = []
    for p in props:
        out = PropertyOut.model_validate(p)
        out.project_name = p.project.name if p.project else "Independent Listing"
        out.broker_name = p.broker.full_name if p.broker else "Unassigned"
        results.append(out)
    return results

@router.post("/real-estate/properties", response_model=PropertyOut)
def create_property(
    prop_in: PropertyCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(
        db, RealEstateProject, prop_in.project_id, membership.organization_id, "Project"
    )
    require_org_user(db, prop_in.assigned_broker_id, membership.organization_id)

    prop = Property(
        org_id=membership.organization_id,
        title=prop_in.title,
        property_type=prop_in.property_type,
        price=prop_in.price,
        bedrooms=prop_in.bedrooms,
        bathrooms=prop_in.bathrooms,
        area_sqft=prop_in.area_sqft,
        location=prop_in.location,
        status=prop_in.status,
        project_id=prop_in.project_id,
        assigned_broker_id=prop_in.assigned_broker_id or membership.user_id
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)

    out = PropertyOut.model_validate(prop)
    out.project_name = prop.project.name if prop.project else "Independent Listing"
    out.broker_name = prop.broker.full_name if prop.broker else "Unassigned"
    return out

@router.get("/real-estate/site-visits", response_model=List[SiteVisitOut])
def get_site_visits(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    visits = db.query(SiteVisit).filter(SiteVisit.org_id == membership.organization_id).all()
    results = []
    for v in visits:
        out = SiteVisitOut.model_validate(v)
        out.property_title = v.property.title if v.property else ""
        results.append(out)
    return results

@router.post("/real-estate/site-visits", response_model=SiteVisitOut)
def schedule_site_visit(
    visit_in: SiteVisitCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(
        db, Property, visit_in.property_id, membership.organization_id, "Property"
    )
    require_org_record(
        db, Lead, visit_in.lead_id, membership.organization_id, "Lead"
    )
    require_org_record(
        db, Contact, visit_in.contact_id, membership.organization_id, "Contact"
    )

    visit = SiteVisit(
        org_id=membership.organization_id,
        property_id=visit_in.property_id,
        lead_id=visit_in.lead_id,
        contact_id=visit_in.contact_id,
        visitor_name=visit_in.visitor_name,
        visitor_phone=visit_in.visitor_phone,
        scheduled_at=visit_in.scheduled_at,
        feedback=visit_in.feedback or "",
        conducted_by_id=membership.user_id
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)

    out = SiteVisitOut.model_validate(visit)
    out.property_title = visit.property.title if visit.property else ""
    return out

@router.get("/real-estate/bookings", response_model=List[PropertyBookingOut])
def get_property_bookings(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    bookings = db.query(PropertyBooking).filter(PropertyBooking.org_id == membership.organization_id).all()
    results = []
    for b in bookings:
        out = PropertyBookingOut.model_validate(b)
        out.property_title = b.property.title if b.property else ""
        results.append(out)
    return results

@router.post("/real-estate/bookings", response_model=PropertyBookingOut)
def create_property_booking(
    booking_in: PropertyBookingCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(
        db, Property, booking_in.property_id, membership.organization_id, "Property"
    )

    booking = PropertyBooking(
        org_id=membership.organization_id,
        property_id=booking_in.property_id,
        customer_name=booking_in.customer_name,
        customer_email=booking_in.customer_email,
        customer_phone=booking_in.customer_phone,
        booking_amount=booking_in.booking_amount,
        agreed_price=booking_in.agreed_price,
        status="Confirmed"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    out = PropertyBookingOut.model_validate(booking)
    out.property_title = booking.property.title if booking.property else ""
    return out

# =========================================================================
# MODULE B: EDTECH & TRAINING
# =========================================================================

@router.get("/edtech/courses", response_model=List[CourseOut])
def get_courses(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(Course).filter(Course.org_id == membership.organization_id).all()

@router.post("/edtech/courses", response_model=CourseOut)
def create_course(
    course_in: CourseCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    course = Course(org_id=membership.organization_id, **course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/edtech/applications", response_model=List[StudentApplicationOut])
def get_student_applications(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    apps = db.query(StudentApplication).filter(StudentApplication.org_id == membership.organization_id).all()
    results = []
    for a in apps:
        out = StudentApplicationOut.model_validate(a)
        out.course_title = a.course.title if a.course else ""
        results.append(out)
    return results

@router.post("/edtech/applications", response_model=StudentApplicationOut)
def create_student_application(
    app_in: StudentApplicationCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(
        db, Course, app_in.course_id, membership.organization_id, "Course"
    )

    app_record = StudentApplication(
        org_id=membership.organization_id,
        course_id=app_in.course_id,
        applicant_name=app_in.applicant_name,
        applicant_email=app_in.applicant_email,
        applicant_phone=app_in.applicant_phone,
        education_level=app_in.education_level,
        notes=app_in.notes or "",
        counsellor_id=membership.user_id
    )
    db.add(app_record)
    db.commit()
    db.refresh(app_record)

    out = StudentApplicationOut.model_validate(app_record)
    out.course_title = app_record.course.title if app_record.course else ""
    return out

# =========================================================================
# MODULE C: BFSI & FINANCE
# =========================================================================

@router.get("/bfsi/portfolios", response_model=List[ClientPortfolioOut])
def get_client_portfolios(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(ClientPortfolio).filter(ClientPortfolio.org_id == membership.organization_id).all()

@router.post("/bfsi/portfolios", response_model=ClientPortfolioOut)
def create_client_portfolio(
    portfolio_in: ClientPortfolioCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    portfolio = ClientPortfolio(
        org_id=membership.organization_id,
        client_name=portfolio_in.client_name,
        client_email=portfolio_in.client_email,
        portfolio_type=portfolio_in.portfolio_type,
        total_asset_value=portfolio_in.total_asset_value,
        risk_profile=portfolio_in.risk_profile,
        relationship_manager_id=membership.user_id
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio

# =========================================================================
# MODULE D: HEALTHCARE
# =========================================================================

@router.get("/healthcare/providers", response_model=List[HealthcareProviderOut])
def get_providers(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(HealthcareProvider).filter(HealthcareProvider.org_id == membership.organization_id).all()

@router.get("/healthcare/appointments", response_model=List[AppointmentOut])
def get_appointments(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    appts = db.query(Appointment).filter(Appointment.org_id == membership.organization_id).all()
    results = []
    for a in appts:
        out = AppointmentOut.model_validate(a)
        out.provider_name = a.provider.name if a.provider else ""
        results.append(out)
    return results

@router.post("/healthcare/appointments", response_model=AppointmentOut)
def create_appointment(
    appt_in: AppointmentCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(
        db, HealthcareProvider, appt_in.provider_id, membership.organization_id, "Provider"
    )

    appt = Appointment(
        org_id=membership.organization_id,
        provider_id=appt_in.provider_id,
        patient_name=appt_in.patient_name,
        patient_phone=appt_in.patient_phone,
        patient_email=appt_in.patient_email,
        appointment_time=appt_in.appointment_time,
        reason_for_visit=appt_in.reason_for_visit,
        notes=appt_in.notes or ""
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)

    out = AppointmentOut.model_validate(appt)
    out.provider_name = appt.provider.name if appt.provider else ""
    return out

# =========================================================================
# MODULE E: E-COMMERCE & D2C
# =========================================================================

@router.get("/ecommerce/orders", response_model=List[EcommerceOrderOut])
def get_ecommerce_orders(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(EcommerceOrder).filter(EcommerceOrder.org_id == membership.organization_id).all()

@router.get("/ecommerce/tickets", response_model=List[SupportTicketOut])
def get_support_tickets(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(SupportTicket).filter(SupportTicket.org_id == membership.organization_id).all()

@router.post("/ecommerce/tickets", response_model=SupportTicketOut)
def create_support_ticket(
    ticket_in: SupportTicketCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    ticket_count = db.query(SupportTicket).count() + 1
    ticket = SupportTicket(
        org_id=membership.organization_id,
        ticket_number=f"TCK-{ticket_count:04d}",
        customer_email=ticket_in.customer_email,
        subject=ticket_in.subject,
        priority=ticket_in.priority,
        details=ticket_in.details,
        assigned_agent_id=membership.user_id
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

# =========================================================================
# MODULE F: B2B SAAS
# =========================================================================

@router.get("/b2b-saas/proposals", response_model=List[SaaSProposalOut])
def get_saas_proposals(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(SaaSProposal).filter(SaaSProposal.org_id == membership.organization_id).all()

@router.post("/b2b-saas/proposals", response_model=SaaSProposalOut)
def create_saas_proposal(
    prop_in: SaaSProposalCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    prop = SaaSProposal(
        org_id=membership.organization_id,
        prospect_company=prop_in.prospect_company,
        contact_person=prop_in.contact_person,
        contact_email=prop_in.contact_email,
        contract_term_months=prop_in.contract_term_months,
        annual_recurring_revenue=prop_in.annual_recurring_revenue,
        plan_tier=prop_in.plan_tier
    )
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop

@router.get("/b2b-saas/subscriptions", response_model=List[SubscriptionOut])
def get_saas_subscriptions(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(Subscription).filter(Subscription.org_id == membership.organization_id).all()
