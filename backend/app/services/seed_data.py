import datetime
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.organization import Organization, OrganizationMembership
from app.models.user import User
from app.models.crm import (
    Lead, Contact, Account, Pipeline, PipelineStage, Deal,
    Activity, Task, Meeting, AuditLog
)
from app.models.industries import (
    RealEstateProject, Property, SiteVisit, PropertyBooking,
    Course, StudentApplication, DemoSession, Enrollment,
    ClientPortfolio, DocumentChecklist, Renewal,
    HealthcareProvider, Appointment, PatientFollowUp,
    EcommerceOrder, SupportTicket, CartRecovery,
    SaaSProposal, Subscription, OnboardingTask
)

def seed_database_if_empty(db: Session):
    existing_org = db.query(Organization).first()
    if existing_org:
        return  # Database already seeded

    print("Seeding initial CRM demo data...")

    # 1. Organizations
    org = Organization(
        name="NexusCRM Enterprise",
        slug="nexuscrm-enterprise",
        domain="nexuscrm.example",
        plan="ENTERPRISE",
        is_active=True
    )
    db.add(org)
    db.flush()

    # 2. Users
    admin_user = User(
        email="admin@crm.io",
        hashed_password=hash_password("admin123"),
        full_name="Sarah Jenkins (Admin)",
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150",
        is_active=True,
        is_superuser=True
    )
    sales_user = User(
        email="alex.sales@crm.io",
        hashed_password=hash_password("sales123"),
        full_name="Alex Rivera (Sales Lead)",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150",
        is_active=True,
        is_superuser=False
    )
    db.add_all([admin_user, sales_user])
    db.flush()

    # Memberships
    m1 = OrganizationMembership(organization_id=org.id, user_id=admin_user.id, role="ADMIN")
    m2 = OrganizationMembership(organization_id=org.id, user_id=sales_user.id, role="SALES_REP")
    db.add_all([m1, m2])
    db.flush()

    # 3. Pipelines & Stages
    pipeline = Pipeline(org_id=org.id, name="Standard B2B Sales Pipeline", is_default=True)
    db.add(pipeline)
    db.flush()

    stages_data = [
        ("New Lead", 1, 10.0, "#3b82f6"),
        ("Contacted", 2, 25.0, "#6366f1"),
        ("Demo", 3, 50.0, "#8b5cf6"),
        ("Negotiation", 4, 75.0, "#ec4899"),
        ("Won", 5, 100.0, "#10b981"),
        ("Lost", 6, 0.0, "#ef4444")
    ]
    created_stages = []
    for name, order, prob, color in stages_data:
        stage = PipelineStage(pipeline_id=pipeline.id, name=name, stage_order=order, probability=prob, color=color)
        db.add(stage)
        created_stages.append(stage)
    db.flush()

    # 4. Accounts
    accounts_data = [
        ("CloudScale Systems", "Technology", "https://cloudscale.io", "contact@cloudscale.io", "+1 (555) 234-5678", "San Francisco, CA", "50-200", "High-growth DevOps and Cloud management platform"),
        ("Apex Health Solutions", "Healthcare", "https://apexhealth.org", "info@apexhealth.org", "+1 (555) 345-6789", "Boston, MA", "200-1000", "Regional hospital network and outpatient diagnostics"),
        ("Vanguard Financial Group", "BFSI", "https://vanguardfg.com", "advisors@vanguardfg.com", "+1 (555) 456-7890", "New York, NY", "1000+", "Institutional wealth management and retirement funds"),
        ("Nordic Retail Ventures", "Retail & E-commerce", "https://nordicretail.dk", "hello@nordicretail.dk", "+45 32 45 67 89", "Copenhagen, Denmark", "10-50", "D2C sustainable lifestyle and apparel brand"),
        ("Horizon Construction & Realty", "Real Estate", "https://horizoncr.com", "sales@horizoncr.com", "+1 (555) 678-9012", "Austin, TX", "50-200", "Commercial and luxury residential developments")
    ]
    created_accounts = []
    for name, ind, web, em, ph, addr, sz, desc in accounts_data:
        acc = Account(
            org_id=org.id, name=name, industry=ind, website=web, email=em,
            phone=ph, address=addr, company_size=sz, assigned_to_id=sales_user.id,
            description=desc, tags="Enterprise, Key Account"
        )
        db.add(acc)
        created_accounts.append(acc)
    db.flush()

    # 5. Contacts
    contacts_data = [
        ("Michael", "Chen", "m.chen@cloudscale.io", "+1 (555) 234-0001", "VP of Engineering", created_accounts[0].id),
        ("Elena", "Rostova", "e.rostova@cloudscale.io", "+1 (555) 234-0002", "Head of Cloud Ops", created_accounts[0].id),
        ("Dr. Marcus", "Vance", "m.vance@apexhealth.org", "+1 (555) 345-0001", "Chief Medical Officer", created_accounts[1].id),
        ("Rebecca", "Sterling", "r.sterling@vanguardfg.com", "+1 (555) 456-0001", "Senior Portfolio Director", created_accounts[2].id),
        ("Soren", "Kierk", "soren@nordicretail.dk", "+45 32 45 00 01", "Managing Director", created_accounts[3].id),
        ("David", "Kowalski", "dkowalski@horizoncr.com", "+1 (555) 678-0001", "Procurement Director", created_accounts[4].id)
    ]
    created_contacts = []
    for fn, ln, em, ph, title, acc_id in contacts_data:
        contact = Contact(
            org_id=org.id, first_name=fn, last_name=ln, email=em, phone=ph,
            job_title=title, account_id=acc_id, assigned_to_id=sales_user.id,
            tags="Decision Maker, Qualified"
        )
        db.add(contact)
        created_contacts.append(contact)
    db.flush()

    # 6. Leads
    leads_data = [
        ("Jessica", "Taylor", "jtaylor@fintechpro.co", "+1 (555) 888-1001", "FinTech Pro", "CTO", "LinkedIn", "BFSI", "NEW", "HIGH", 45000.0, 88, "High executive title (CTO); Verified company domain; $45K deal value; Urgent inbound inquiry."),
        ("Robert", "Langdon", "rlangdon@symbology.edu", "+1 (555) 888-1002", "Symbology Institute", "Dean of Academics", "Website", "EdTech", "CONTACTED", "MEDIUM", 18500.0, 72, "Inquired through pricing calculator; Attended introductory overview; Budget approved for Q4."),
        ("Amina", "Zahir", "amina@skylineproperties.ae", "+971 4 234 5678", "Skyline UAE", "Commercial Director", "Referral", "Real Estate", "QUALIFIED", "HIGH", 120000.0, 94, "Referred by VIP client; Actively looking to onboard 4 luxury towers; Highest buyer intent."),
        ("Liam", "O'Connor", "liam@dublinlogistics.ie", "+353 1 496 0000", "Dublin Logistics", "Operations Lead", "Cold Outreach", "Technology", "CONTACTED", "LOW", 12000.0, 48, "Opened cold email 3 times; Has not booked demo yet; Follow-up scheduled."),
        ("Sofia", "Gomez", "sofia@medicarehub.org", "+1 (555) 888-1005", "MediCare Hub", "Clinic Administrator", "Google Ads", "Healthcare", "NEW", "MEDIUM", 28000.0, 65, "Clicked Google Ads campaign for Clinic CRM; Downloaded whitepaper.")
    ]
    created_leads = []
    for fn, ln, em, ph, co, jt, src, ind, st, pri, val, sc, expl in leads_data:
        lead = Lead(
            org_id=org.id, first_name=fn, last_name=ln, email=em, phone=ph,
            company=co, job_title=jt, lead_source=src, industry=ind, status=st,
            priority=pri, estimated_value=val, tags=f"{ind}, Q4 Target",
            assigned_to_id=sales_user.id, lead_score=sc, score_explanation=expl,
            notes=f"Initial contact logged from {src}."
        )
        db.add(lead)
        created_leads.append(lead)
    db.flush()

    # 7. Deals
    deals_data = [
        ("CloudScale Enterprise License", created_accounts[0].id, created_contacts[0].id, created_stages[3].id, 85000.0, 75.0, "Negotiation", "Legal team currently reviewing master service agreement and SOC2 compliance."),
        ("Apex Health Clinic Rollout", created_accounts[1].id, created_contacts[2].id, created_stages[2].id, 62000.0, 50.0, "Demo", "Completed product demo with Dr. Vance. Next step: security architecture review."),
        ("Vanguard Wealth Advisory Portal", created_accounts[2].id, created_contacts[3].id, created_stages[4].id, 140000.0, 100.0, "Won", "Contract signed! 3-year enterprise software and integration engagement."),
        ("Nordic Retail Headless POS", created_accounts[3].id, created_contacts[4].id, created_stages[1].id, 24000.0, 25.0, "Contacted", "Discovery call completed with Soren. Outlining proposal scope."),
        ("Horizon SkyTower Commercial Suite", created_accounts[4].id, created_contacts[5].id, created_stages[0].id, 95000.0, 10.0, "New Lead", "Inbound inquiry regarding real-estate lease management.")
    ]
    for name, acc_id, con_id, stg_id, val, prob, stg_name, desc in deals_data:
        deal = Deal(
            org_id=org.id, name=name, account_id=acc_id, contact_id=con_id,
            pipeline_id=pipeline.id, stage_id=stg_id, value=val, currency="USD",
            probability=prob, expected_close_date=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            assigned_to_id=sales_user.id, source="Direct Sales", description=desc,
            status="WON" if prob == 100.0 else ("LOST" if prob == 0.0 else "OPEN")
        )
        db.add(deal)
    db.flush()

    # 8. Tasks & Meetings
    today = datetime.datetime.utcnow()
    tasks_data = [
        ("Send revised proposal to CloudScale", "Finalize terms with Michael Chen regarding tier discount", today + datetime.timedelta(hours=4), "HIGH", False, "account", created_accounts[0].id),
        ("Follow up with Sofia Gomez (MediCare)", "Check if she reviewed the compliance whitepaper", today + datetime.timedelta(days=1), "MEDIUM", False, "lead", created_leads[4].id),
        ("Schedule Site Visit with Amina Zahir", "Coordinate physical walk-through at Skyline Towers", today + datetime.timedelta(days=2), "HIGH", False, "lead", created_leads[2].id),
        ("Log signed agreement for Vanguard", "Upload executed contract into legal repository", today - datetime.timedelta(days=1), "LOW", True, "account", created_accounts[2].id)
    ]
    for title, desc, due, pri, comp, ent_t, ent_id in tasks_data:
        t = Task(
            org_id=org.id, title=title, description=desc, due_date=due,
            priority=pri, is_completed=comp, assigned_to_id=sales_user.id,
            entity_type=ent_t, entity_id=ent_id, created_by_id=admin_user.id
        )
        db.add(t)

    meetings_data = [
        ("CloudScale Contract Review", "Review MSA clause 14 with legal and VP Engineering", today + datetime.timedelta(days=1, hours=3), today + datetime.timedelta(days=1, hours=4), "Google Meet", "m.chen@cloudscale.io, alex.sales@crm.io"),
        ("Apex Health Security Architecture Call", "Discuss HIPAA safeguards and zero-trust proxy", today + datetime.timedelta(days=2, hours=2), today + datetime.timedelta(days=2, hours=3), "Zoom", "m.vance@apexhealth.org, sarah.rep@crm.io")
    ]
    for title, desc, st_time, end_time, loc, atts in meetings_data:
        m = Meeting(
            org_id=org.id, title=title, description=desc, start_time=st_time,
            end_time=end_time, location=loc, attendees=atts, entity_type="deal",
            entity_id=1, created_by_id=admin_user.id, status="SCHEDULED"
        )
        db.add(m)

    # 9. Activities (Timeline)
    activities_data = [
        ("CALL", "Call with Michael Chen", "Discussed security SLA requirements and cloud compliance standards.", "contact", created_contacts[0].id),
        ("EMAIL", "Sent Pricing Tier Matrix", "Dispatched formal enterprise tier sheet with 20% annual pre-pay option.", "lead", created_leads[0].id),
        ("STATUS_CHANGE", "Stage changed to Negotiation", "Deal moved from Demo to Negotiation following technical validation.", "deal", 1),
        ("NOTE", "Customer expressed strong budget intent", "Sofia indicated budget is pre-allocated for Q4 software renewals.", "lead", created_leads[4].id)
    ]
    for act_type, subj, desc, ent_type, ent_id in activities_data:
        act = Activity(
            org_id=org.id, activity_type=act_type, subject=subj, description=desc,
            entity_type=ent_type, entity_id=ent_id, created_by_id=sales_user.id,
            is_completed=True
        )
        db.add(act)

    # 10. Industry Modules Seed Data
    # Real Estate
    proj = RealEstateProject(
        org_id=org.id, name="Skyline Marina Residences", location="Waterfront Boulevard, Marina Bay",
        project_type="Residential Luxury", status="Ready to Move", total_units=120, available_units=18,
        description="Luxury 2-4 bedroom apartments overlooking the marina with concierge service."
    )
    db.add(proj)
    db.flush()

    prop1 = Property(
        org_id=org.id, project_id=proj.id, title="Marina Penthouse Suite 14B",
        property_type="Penthouse", price=1250000.0, bedrooms=4, bathrooms=4,
        area_sqft=3400.0, location="Marina Bay Tower A", status="Available",
        assigned_broker_id=sales_user.id
    )
    prop2 = Property(
        org_id=org.id, project_id=proj.id, title="Waterfront 2BR Executive",
        property_type="Apartment", price=450000.0, bedrooms=2, bathrooms=2,
        area_sqft=1450.0, location="Marina Bay Tower B", status="Available",
        assigned_broker_id=sales_user.id
    )
    db.add_all([prop1, prop2])
    db.flush()

    visit = SiteVisit(
        org_id=org.id, property_id=prop1.id, scheduled_at=today + datetime.timedelta(days=2),
        visitor_name="Amina Zahir", visitor_phone="+971 4 234 5678", status="Scheduled",
        feedback="Interested in high-floor ocean view with private lift access."
    )
    db.add(visit)

    booking = PropertyBooking(
        org_id=org.id, property_id=prop2.id, customer_name="Marcus Vance",
        customer_email="m.vance@apexhealth.org", customer_phone="+1 555 345 0001",
        booking_amount=25000.0, agreed_price=440000.0, status="Confirmed"
    )
    db.add(booking)

    # EdTech
    course1 = Course(org_id=org.id, title="Executive AI & Full-Stack Architecture", category="Computer Science", duration_weeks=16, fee=2400.0, instructor="Dr. Aris Vance")
    course2 = Course(org_id=org.id, title="Financial Engineering & Quantitative Risk", category="Finance", duration_weeks=12, fee=1850.0, instructor="Prof. Sterling")
    db.add_all([course1, course2])
    db.flush()

    app_ed = StudentApplication(
        org_id=org.id, course_id=course1.id, applicant_name="Robert Langdon",
        applicant_email="rlangdon@symbology.edu", applicant_phone="+1 555 888 1002",
        stage="Applied", education_level="Doctorate", notes="Faculty member aiming to integrate modern AI."
    )
    db.add(app_ed)

    # BFSI
    portfolio = ClientPortfolio(
        org_id=org.id, client_name="Vanguard Endowment Trust", client_email="advisors@vanguardfg.com",
        portfolio_type="Institutional Wealth", total_asset_value=12500000.0, risk_profile="Moderate",
        status="Active", relationship_manager_id=sales_user.id
    )
    db.add(portfolio)
    db.flush()

    renewal = Renewal(
        org_id=org.id, portfolio_id=portfolio.id, product_name="Annual Advisory Framework",
        renewal_due_date=today + datetime.timedelta(days=45), renewal_amount=65000.0, status="Upcoming"
    )
    db.add(renewal)

    # Healthcare
    provider = HealthcareProvider(
        org_id=org.id, name="Dr. Evelyn Harper, MD", specialty="Cardiology",
        department="Heart & Vascular", contact_phone="+1 555 777 9999", availability_hours="08:00 AM - 04:00 PM"
    )
    db.add(provider)
    db.flush()

    appt = Appointment(
        org_id=org.id, provider_id=provider.id, patient_name="David Kowalski",
        patient_phone="+1 555 678 0001", patient_email="dkowalski@horizoncr.com",
        appointment_time=today + datetime.timedelta(days=3, hours=10),
        reason_for_visit="Annual cardiac stress test & consultation", status="Confirmed",
        notes="Pre-op clearance evaluation requested."
    )
    db.add(appt)

    # E-Commerce
    order1 = EcommerceOrder(
        org_id=org.id, order_number="ORD-2026-9812", customer_name="Soren Kierk",
        customer_email="soren@nordicretail.dk", order_value=1420.50, item_count=6,
        order_status="Processing", shipping_address="Stroget 42, Copenhagen"
    )
    ticket1 = SupportTicket(
        org_id=org.id, ticket_number="TCK-4091", customer_email="soren@nordicretail.dk",
        subject="Request for split pallet freight dispatch", priority="MEDIUM",
        status="Open", details="Needs shipment partitioned across two warehouse docks."
    )
    db.add_all([order1, ticket1])

    # B2B SaaS
    prop_saas = SaaSProposal(
        org_id=org.id, prospect_company="CloudScale Systems", contact_person="Michael Chen",
        contact_email="m.chen@cloudscale.io", contract_term_months=24, annual_recurring_revenue=48000.0,
        plan_tier="Enterprise Custom", status="Under Review"
    )
    sub_saas = Subscription(
        org_id=org.id, account_id=created_accounts[0].id, company_name="CloudScale Systems",
        mrr=4000.0, plan_name="Enterprise Platform", seats=85,
        start_date=today - datetime.timedelta(days=90), renewal_date=today + datetime.timedelta(days=275),
        status="Active"
    )
    db.add_all([prop_saas, sub_saas])

    db.commit()
    print("Database seeding completed successfully.")
