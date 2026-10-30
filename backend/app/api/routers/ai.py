from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_membership
from app.models.user import User
from app.models.organization import OrganizationMembership
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_service import process_crm_ai_query

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

@router.post("/chat", response_model=AIChatResponse)
def ai_chat(
    chat_in: AIChatRequest,
    current_user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    return process_crm_ai_query(
        db=db,
        org_id=membership.organization_id,
        user=current_user,
        message=chat_in.message
    )

