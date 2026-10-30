import io
import csv
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import require_org_user
from app.models.organization import OrganizationMembership
from app.models.crm import Lead, Contact, Account, Deal, Pipeline, PipelineStage, Activity, AuditLog
from app.schemas.lead import LeadCreate, LeadUpdate, LeadOut, LeadPagination, LeadConvert
from app.schemas.ai import LeadScoringResponse
from app.services.scoring_service import calculate_lead_score

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.get("", response_model=LeadPagination)
def list_leads(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    industry: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).filter(Lead.org_id == membership.organization_id)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Lead.first_name.ilike(s),
                Lead.last_name.ilike(s),
                Lead.email.ilike(s),
                Lead.company.ilike(s),
                Lead.tags.ilike(s)
            )
        )
    if status and status != "ALL":
        query = query.filter(Lead.status == status)
    if priority and priority != "ALL":
        query = query.filter(Lead.priority == priority)
    if industry and industry != "ALL":
        query = query.filter(Lead.industry == industry)

    # Sorting
    sort_column = getattr(Lead, sort_by, Lead.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size or 1
    offset = (page - 1) * page_size
    leads = query.offset(offset).limit(page_size).all()

    items = []
    for l in leads:
        lead_dict = LeadOut.model_validate(l)
        lead_dict.assigned_to_name = l.assigned_to.full_name if l.assigned_to else "Unassigned"
        items.append(lead_dict)

    return LeadPagination(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/export/csv")
def export_leads_csv(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    leads = db.query(Lead).filter(Lead.org_id == membership.organization_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Company", "Job Title", "Source", "Industry", "Status", "Priority", "Estimated Value", "Lead Score", "Created At"])
    
    for l in leads:
        writer.writerow([
            l.id, l.first_name, l.last_name, l.email, l.phone or "", l.company or "",
            l.job_title or "", l.lead_source, l.industry, l.status, l.priority,
            l.estimated_value, l.lead_score, l.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )

@router.post("", response_model=LeadOut)
def create_lead(
    lead_in: LeadCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_user(db, lead_in.assigned_to_id, membership.organization_id)

    # Check duplicate email in this org
    existing = db.query(Lead).filter(
        Lead.org_id == membership.organization_id,
        Lead.email == lead_in.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A lead with email '{lead_in.email}' already exists in your organization."
        )

    lead = Lead(
        org_id=membership.organization_id,
        first_name=lead_in.first_name,
        last_name=lead_in.last_name,
        email=lead_in.email,
        phone=lead_in.phone,
        company=lead_in.company,
        job_title=lead_in.job_title,
        lead_source=lead_in.lead_source,
        industry=lead_in.industry,
        status=lead_in.status,
        priority=lead_in.priority,
        estimated_value=lead_in.estimated_value,
        tags=lead_in.tags or "",
        notes=lead_in.notes or "",
        assigned_to_id=lead_in.assigned_to_id or membership.user_id
    )
    db.add(lead)
    db.flush()

    # Calculate initial lead score
    score_res = calculate_lead_score(lead)
    lead.lead_score = score_res.total_score
    lead.score_explanation = f"Score: {score_res.total_score}/100 ({score_res.category}). {score_res.recommendation}"

    # Record activity
    act = Activity(
        org_id=membership.organization_id,
        activity_type="SYSTEM",
        subject=f"Lead Created: {lead.first_name} {lead.last_name}",
        description=f"Initial lead logged from source {lead.lead_source} with priority {lead.priority}.",
        entity_type="lead",
        entity_id=lead.id,
        created_by_id=membership.user_id,
        is_completed=True
    )
    db.add(act)

    db.commit()
    db.refresh(lead)

    out = LeadOut.model_validate(lead)
    out.assigned_to_name = lead.assigned_to.full_name if lead.assigned_to else "Unassigned"
    return out

@router.get("/{id}", response_model=LeadOut)
def get_lead(
    id: int,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == id, Lead.org_id == membership.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    
    out = LeadOut.model_validate(lead)
    out.assigned_to_name = lead.assigned_to.full_name if lead.assigned_to else "Unassigned"
    return out

@router.patch("/{id}", response_model=LeadOut)
def update_lead(
    id: int,
    lead_in: LeadUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == id, Lead.org_id == membership.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    update_data = lead_in.model_dump(exclude_unset=True)
    if "assigned_to_id" in update_data:
        require_org_user(db, update_data["assigned_to_id"], membership.organization_id)
    for field, value in update_data.items():
        setattr(lead, field, value)

    # Recalculate score
    score_res = calculate_lead_score(lead)
    lead.lead_score = score_res.total_score
    lead.score_explanation = f"Score: {score_res.total_score}/100 ({score_res.category}). {score_res.recommendation}"

    db.commit()
    db.refresh(lead)

    out = LeadOut.model_validate(lead)
    out.assigned_to_name = lead.assigned_to.full_name if lead.assigned_to else "Unassigned"
    return out

@router.delete("/{id}")
def delete_lead(
    id: int,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == id, Lead.org_id == membership.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    db.delete(lead)
    db.commit()
    return {"message": "Lead successfully deleted."}

@router.post("/{id}/score", response_model=LeadScoringResponse)
def get_lead_score_breakdown(
    id: int,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == id, Lead.org_id == membership.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")
    
    return calculate_lead_score(lead)

@router.post("/{id}/convert")
def convert_lead(
    id: int,
    convert_in: LeadConvert,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    lead = db.query(Lead).filter(Lead.id == id, Lead.org_id == membership.organization_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found.")

    account_id = None
    if convert_in.create_account:
        acc_name = convert_in.account_name or lead.company or f"{lead.last_name} Enterprises"
        account = Account(
            org_id=membership.organization_id,
            name=acc_name,
            industry=lead.industry,
            phone=lead.phone,
            email=lead.email,
            assigned_to_id=lead.assigned_to_id or membership.user_id,
            description=f"Created via conversion from lead {lead.first_name} {lead.last_name}"
        )
        db.add(account)
        db.flush()
        account_id = account.id

    # Create Contact
    contact = Contact(
        org_id=membership.organization_id,
        account_id=account_id,
        first_name=lead.first_name,
        last_name=lead.last_name,
        email=lead.email,
        phone=lead.phone,
        job_title=lead.job_title,
        assigned_to_id=lead.assigned_to_id or membership.user_id,
        notes=lead.notes or ""
    )
    db.add(contact)
    db.flush()

    # Create Deal if requested
    deal_id = None
    if convert_in.create_deal:
        pipeline = db.query(Pipeline).filter(Pipeline.org_id == membership.organization_id).first()
        stage = db.query(PipelineStage).filter(PipelineStage.pipeline_id == pipeline.id).order_by(PipelineStage.stage_order).first()
        
        deal = Deal(
            org_id=membership.organization_id,
            name=convert_in.deal_name or f"{lead.company or lead.last_name} - Commercial Contract",
            account_id=account_id,
            contact_id=contact.id,
            pipeline_id=pipeline.id,
            stage_id=stage.id if stage else 1,
            value=convert_in.deal_value or lead.estimated_value or 10000.0,
            currency="USD",
            probability=15.0,
            assigned_to_id=lead.assigned_to_id or membership.user_id,
            source=lead.lead_source,
            description="Opportunity converted from qualified lead."
        )
        db.add(deal)
        db.flush()
        deal_id = deal.id

    # Update lead status
    lead.status = "CONVERTED"
    lead.converted_at = datetime.datetime.utcnow()

    # Log activity
    act = Activity(
        org_id=membership.organization_id,
        activity_type="SYSTEM",
        subject=f"Lead Converted: {lead.first_name} {lead.last_name}",
        description=f"Converted to Contact #{contact.id}, Account #{account_id or 'N/A'}, Deal #{deal_id or 'N/A'}.",
        entity_type="lead",
        entity_id=lead.id,
        created_by_id=membership.user_id,
        is_completed=True
    )
    db.add(act)

    db.commit()

    return {
        "message": "Lead successfully converted.",
        "contact_id": contact.id,
        "account_id": account_id,
        "deal_id": deal_id
    }
