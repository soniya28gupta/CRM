from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.crm import Account, Contact, Deal, Lead, Pipeline, PipelineStage
from app.models.organization import OrganizationMembership

T = TypeVar("T")
ENTITY_MODELS = {
    "account": Account,
    "contact": Contact,
    "deal": Deal,
    "lead": Lead,
}


def require_org_record(
    db: Session,
    model: type[T],
    record_id: int | None,
    organization_id: int,
    label: str,
) -> T | None:
    if record_id is None:
        return None

    record = (
        db.query(model)
        .filter(model.id == record_id, model.org_id == organization_id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} not found in your organization.")
    return record


def require_org_user(db: Session, user_id: int | None, organization_id: int) -> None:
    if user_id is None:
        return

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=404, detail="Assigned user not found in your organization.")


def require_org_pipeline(db: Session, pipeline_id: int, organization_id: int) -> Pipeline:
    pipeline = (
        db.query(Pipeline)
        .filter(Pipeline.id == pipeline_id, Pipeline.org_id == organization_id)
        .first()
    )
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found in your organization.")
    return pipeline


def require_org_stage(
    db: Session,
    stage_id: int,
    organization_id: int,
    pipeline_id: int | None = None,
) -> PipelineStage:
    query = (
        db.query(PipelineStage)
        .join(Pipeline, Pipeline.id == PipelineStage.pipeline_id)
        .filter(
            PipelineStage.id == stage_id,
            Pipeline.org_id == organization_id,
        )
    )
    if pipeline_id is not None:
        query = query.filter(PipelineStage.pipeline_id == pipeline_id)

    stage = query.first()
    if stage is None:
        raise HTTPException(status_code=404, detail="Pipeline stage not found in your organization.")
    return stage


def require_org_entity(
    db: Session,
    entity_type: str,
    entity_id: int,
    organization_id: int,
) -> None:
    model = ENTITY_MODELS.get(entity_type.lower())
    if model is None:
        raise HTTPException(status_code=422, detail="Unsupported CRM activity entity type.")
    require_org_record(db, model, entity_id, organization_id, entity_type.title())
