from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token, decode_access_token
from app.models.user import User
from app.models.organization import Organization, OrganizationMembership
from app.models.crm import Pipeline, PipelineStage
from app.schemas.auth import UserCreate, UserLogin, Token, UserOut
from app.api.deps import get_current_user, get_current_membership
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
def register(user_in: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Create new Organization
    org_name = user_in.organization_name or "My Enterprise CRM"
    slug = org_name.lower().replace(" ", "-").replace(".", "") + f"-{db.query(Organization).count() + 1}"
    org = Organization(name=org_name, slug=slug, plan="ENTERPRISE")
    db.add(org)
    db.flush()

    # Create User as ADMIN
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    db.flush()

    # Membership
    membership = OrganizationMembership(
        organization_id=org.id,
        user_id=user.id,
        role="ADMIN"
    )
    db.add(membership)

    # Initialize default pipeline for this org
    pipeline = Pipeline(org_id=org.id, name="Standard Sales Pipeline", is_default=True)
    db.add(pipeline)
    db.flush()

    default_stages = [
        ("New Lead", 1, 10.0, "#3b82f6"),
        ("Contacted", 2, 25.0, "#6366f1"),
        ("Demo", 3, 50.0, "#8b5cf6"),
        ("Negotiation", 4, 75.0, "#ec4899"),
        ("Won", 5, 100.0, "#10b981"),
        ("Lost", 6, 0.0, "#ef4444")
    ]
    for s_name, s_order, s_prob, s_color in default_stages:
        db.add(PipelineStage(pipeline_id=pipeline.id, name=s_name, stage_order=s_order, probability=s_prob, color=s_color))

    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "org_id": org.id, "role": "ADMIN"})
    response.set_cookie(
        key="crm_access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.COOKIE_SECURE
    )

    user_out = UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role="ADMIN",
        organization_id=org.id,
        organization_name=org.name
    )
    return Token(access_token=token, user=user_out)

@router.post("/login", response_model=Token)
def login(login_in: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if (
        not user
        or not user.is_active
        or not verify_password(login_in.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    membership = db.query(OrganizationMembership).filter(OrganizationMembership.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=403, detail="User does not belong to any organization.")
    if not membership.organization.is_active:
        raise HTTPException(status_code=403, detail="The user's organization is inactive.")

    token = create_access_token(data={"sub": str(user.id), "org_id": membership.organization_id, "role": membership.role})
    response.set_cookie(
        key="crm_access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.COOKIE_SECURE
    )

    user_out = UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role=membership.role,
        organization_id=membership.organization.id,
        organization_name=membership.organization.name
    )
    return Token(access_token=token, user=user_out)

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("crm_access_token")
    return {"message": "Successfully logged out."}

@router.get("/session")
def get_session_status(request: Request, db: Session = Depends(get_db)) -> Dict[str, bool]:
    token = request.cookies.get("crm_access_token")
    payload = decode_access_token(token) if token else None
    if not payload or not payload.get("sub") or not payload.get("org_id"):
        return {"authenticated": False}

    try:
        user_id = int(payload["sub"])
        organization_id = int(payload["org_id"])
    except (TypeError, ValueError):
        return {"authenticated": False}

    membership = db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.organization_id == organization_id,
    ).first()
    return {
        "authenticated": bool(
            membership
            and membership.user.is_active
            and membership.organization.is_active
        )
    }

@router.get("/me", response_model=UserOut)
def get_me(
    user: User = Depends(get_current_user),
    membership: OrganizationMembership = Depends(get_current_membership)
):
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        role=membership.role,
        organization_id=membership.organization.id,
        organization_name=membership.organization.name
    )

@router.get("/team", response_model=List[Dict[str, Any]])
def get_team_members(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    members = db.query(OrganizationMembership).filter(
        OrganizationMembership.organization_id == membership.organization_id
    ).all()
    result = []
    for m in members:
        result.append({
            "id": m.user.id,
            "full_name": m.user.full_name,
            "email": m.user.email,
            "role": m.role,
            "avatar_url": m.user.avatar_url,
            "created_at": m.created_at
        })
    return result
