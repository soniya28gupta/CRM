from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.organization import OrganizationMembership

def get_token_from_request(request: Request, authorization: Optional[str] = Header(None)) -> Optional[str]:
    # Check Bearer Authorization header
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    # Check Cookie session
    cookie_token = request.cookies.get("crm_access_token")
    if cookie_token:
        return cookie_token
    return None

def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    token = get_token_from_request(request, authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token."
        )

    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated."
        )
    return user

def get_current_membership(
    request: Request,
    authorization: Optional[str] = Header(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OrganizationMembership:
    token = get_token_from_request(request, authorization)
    payload = decode_access_token(token) if token else None
    organization_id = payload.get("org_id") if payload else None

    memberships = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == current_user.id
    )
    if organization_id is not None:
        memberships = memberships.filter(
            OrganizationMembership.organization_id == organization_id
        )
    matches = memberships.all()

    if len(matches) != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a unique active organization."
        )
    membership = matches[0]
    if not membership.organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user's organization is inactive."
        )
    return membership

def require_admin(
    membership: OrganizationMembership = Depends(get_current_membership)
) -> OrganizationMembership:
    if membership.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required for this action."
        )
    return membership

def require_write_access(
    membership: OrganizationMembership = Depends(get_current_membership)
) -> OrganizationMembership:
    if membership.role == "VIEWER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only permissions. Modifying CRM records is restricted."
        )
    return membership
