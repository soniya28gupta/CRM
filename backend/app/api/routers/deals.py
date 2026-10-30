from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import (
    require_org_record,
    require_org_stage,
    require_org_pipeline,
    require_org_user,
)
from app.models.organization import OrganizationMembership
from app.models.crm import Account, Activity, Contact, Deal, Pipeline, PipelineStage
from app.schemas.deal import (
    DealCreate, DealUpdate, DealStageUpdate, DealOut,
    DealKanbanBoard, DealKanbanColumn, PipelineOut, PipelineStageOut
)

router = APIRouter(prefix="/deals", tags=["Deals & Pipelines"])

@router.get("", response_model=List[DealOut])
def list_deals(
    stage_id: Optional[int] = None,
    status: Optional[str] = None,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Deal).filter(Deal.org_id == membership.organization_id)
    if stage_id:
        query = query.filter(Deal.stage_id == stage_id)
    if status:
        query = query.filter(Deal.status == status)

    deals = query.order_by(Deal.created_at.desc()).all()
    results = []
    for d in deals:
        item = DealOut.model_validate(d)
        item.account_name = d.account.name if d.account else "No Account"
        item.contact_name = f"{d.contact.first_name} {d.contact.last_name}" if d.contact else "No Contact"
        item.stage_name = d.stage.name if d.stage else ""
        item.assigned_to_name = d.assigned_to.full_name if d.assigned_to else "Unassigned"
        results.append(item)
    return results

@router.get("/pipelines", response_model=List[PipelineOut])
def get_pipelines(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return db.query(Pipeline).filter(Pipeline.org_id == membership.organization_id).all()

@router.get("/kanban", response_model=DealKanbanBoard)
def get_kanban_board(
    pipeline_id: Optional[int] = None,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    if not pipeline_id:
        default_pipe = db.query(Pipeline).filter(
            Pipeline.org_id == membership.organization_id
        ).order_by(Pipeline.is_default.desc()).first()
        if not default_pipe:
            return DealKanbanBoard(columns=[], total_pipeline_value=0.0, weighted_pipeline_value=0.0)
        pipeline_id = default_pipe.id
    else:
        require_org_pipeline(db, pipeline_id, membership.organization_id)

    stages = db.query(PipelineStage).filter(
        PipelineStage.pipeline_id == pipeline_id,
        PipelineStage.pipeline_id.in_(
            db.query(Pipeline.id).filter(Pipeline.org_id == membership.organization_id)
        ),
    ).order_by(PipelineStage.stage_order.asc()).all()

    deals = db.query(Deal).filter(
        Deal.org_id == membership.organization_id,
        Deal.pipeline_id == pipeline_id
    ).all()

    columns = []
    total_pipeline_val = 0.0
    weighted_pipeline_val = 0.0

    for s in stages:
        stage_deals = [d for d in deals if d.stage_id == s.id]
        stage_val = sum(d.value for d in stage_deals)
        total_pipeline_val += stage_val
        weighted_pipeline_val += sum(d.value * (s.probability / 100.0) for d in stage_deals)

        deal_outs = []
        for d in stage_deals:
            out = DealOut.model_validate(d)
            out.account_name = d.account.name if d.account else "No Account"
            out.contact_name = f"{d.contact.first_name} {d.contact.last_name}" if d.contact else "No Contact"
            out.stage_name = s.name
            out.assigned_to_name = d.assigned_to.full_name if d.assigned_to else "Unassigned"
            deal_outs.append(out)

        columns.append(DealKanbanColumn(
            stage=PipelineStageOut.model_validate(s),
            deals=deal_outs,
            total_value=stage_val,
            deal_count=len(deal_outs)
        ))

    return DealKanbanBoard(
        columns=columns,
        total_pipeline_value=total_pipeline_val,
        weighted_pipeline_value=weighted_pipeline_val
    )

@router.post("", response_model=DealOut)
def create_deal(
    deal_in: DealCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_pipeline(db, deal_in.pipeline_id, membership.organization_id)
    stage = require_org_stage(
        db, deal_in.stage_id, membership.organization_id, deal_in.pipeline_id
    )
    require_org_record(db, Account, deal_in.account_id, membership.organization_id, "Account")
    require_org_record(db, Contact, deal_in.contact_id, membership.organization_id, "Contact")
    require_org_user(db, deal_in.assigned_to_id, membership.organization_id)
    probability = stage.probability

    status_val = "OPEN"
    if stage.name.lower() in {"won", "closed won"}:
        status_val = "WON"
    elif stage.name.lower() in {"lost", "closed lost"}:
        status_val = "LOST"

    deal = Deal(
        org_id=membership.organization_id,
        name=deal_in.name,
        account_id=deal_in.account_id,
        contact_id=deal_in.contact_id,
        pipeline_id=deal_in.pipeline_id,
        stage_id=deal_in.stage_id,
        value=deal_in.value,
        currency=deal_in.currency,
        probability=probability,
        expected_close_date=deal_in.expected_close_date,
        assigned_to_id=deal_in.assigned_to_id or membership.user_id,
        source=deal_in.source,
        description=deal_in.description or "",
        status=status_val
    )
    db.add(deal)
    db.flush()

    # Log creation activity
    act = Activity(
        org_id=membership.organization_id,
        activity_type="SYSTEM",
        subject=f"New Deal Created: {deal.name}",
        description=f"Valued at ${deal.value:,.2f} in stage '{stage.name}'.",
        entity_type="deal",
        entity_id=deal.id,
        created_by_id=membership.user_id,
        is_completed=True
    )
    db.add(act)

    db.commit()
    db.refresh(deal)

    out = DealOut.model_validate(deal)
    out.account_name = deal.account.name if deal.account else "No Account"
    out.contact_name = f"{deal.contact.first_name} {deal.contact.last_name}" if deal.contact else "No Contact"
    out.stage_name = stage.name
    out.assigned_to_name = deal.assigned_to.full_name if deal.assigned_to else "Unassigned"
    return out

@router.patch("/{id}/stage", response_model=DealOut)
def update_deal_stage(
    id: int,
    stage_update: DealStageUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    deal = db.query(Deal).filter(Deal.id == id, Deal.org_id == membership.organization_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    new_stage = require_org_stage(
        db, stage_update.stage_id, membership.organization_id, deal.pipeline_id
    )

    old_stage_name = deal.stage.name if deal.stage else "Unknown"
    deal.stage_id = new_stage.id
    deal.probability = new_stage.probability

    if new_stage.name.lower() in {"won", "closed won"}:
        deal.status = "WON"
    elif new_stage.name.lower() in {"lost", "closed lost"}:
        deal.status = "LOST"
    else:
        deal.status = "OPEN"

    # Log stage change in Activity timeline
    act = Activity(
        org_id=membership.organization_id,
        activity_type="STATUS_CHANGE",
        subject=f"Stage Changed for Deal: {deal.name}",
        description=f"Moved from '{old_stage_name}' to '{new_stage.name}' (Win Probability: {new_stage.probability:.0f}%).",
        entity_type="deal",
        entity_id=deal.id,
        created_by_id=membership.user_id,
        is_completed=True
    )
    db.add(act)

    db.commit()
    db.refresh(deal)

    out = DealOut.model_validate(deal)
    out.account_name = deal.account.name if deal.account else "No Account"
    out.contact_name = f"{deal.contact.first_name} {deal.contact.last_name}" if deal.contact else "No Contact"
    out.stage_name = new_stage.name
    out.assigned_to_name = deal.assigned_to.full_name if deal.assigned_to else "Unassigned"
    return out


@router.patch("/{id}", response_model=DealOut)
def update_deal(
    id: int,
    deal_in: DealUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db),
):
    deal = db.query(Deal).filter(
        Deal.id == id, Deal.org_id == membership.organization_id
    ).first()
    if deal is None:
        raise HTTPException(status_code=404, detail="Deal not found.")

    update_data = deal_in.model_dump(exclude_unset=True)
    pipeline_id = update_data.get("pipeline_id", deal.pipeline_id)
    stage_id = update_data.get("stage_id", deal.stage_id)
    require_org_pipeline(db, pipeline_id, membership.organization_id)
    stage = require_org_stage(db, stage_id, membership.organization_id, pipeline_id)
    if "account_id" in update_data:
        require_org_record(db, Account, update_data["account_id"], membership.organization_id, "Account")
    if "contact_id" in update_data:
        require_org_record(db, Contact, update_data["contact_id"], membership.organization_id, "Contact")
    if "assigned_to_id" in update_data:
        require_org_user(db, update_data["assigned_to_id"], membership.organization_id)

    for field, value in update_data.items():
        if field not in {"status", "probability"}:
            setattr(deal, field, value)
    deal.pipeline_id = pipeline_id
    deal.stage_id = stage.id
    deal.probability = stage.probability
    if stage.name.lower() in {"won", "closed won"}:
        deal.status = "WON"
    elif stage.name.lower() in {"lost", "closed lost"}:
        deal.status = "LOST"
    else:
        deal.status = "OPEN"

    db.commit()
    db.refresh(deal)
    out = DealOut.model_validate(deal)
    out.account_name = deal.account.name if deal.account else "No Account"
    out.contact_name = f"{deal.contact.first_name} {deal.contact.last_name}" if deal.contact else "No Contact"
    out.stage_name = stage.name
    out.assigned_to_name = deal.assigned_to.full_name if deal.assigned_to else "Unassigned"
    return out

@router.delete("/{id}")
def delete_deal(
    id: int,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    deal = db.query(Deal).filter(Deal.id == id, Deal.org_id == membership.organization_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found.")

    db.delete(deal)
    db.commit()
    return {"message": "Deal successfully deleted."}
