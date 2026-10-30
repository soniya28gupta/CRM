from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import require_org_user
from app.models.organization import OrganizationMembership
from app.models.crm import Account, Contact, Deal
from app.schemas.account import AccountCreate, AccountUpdate, AccountOut, AccountPagination

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("", response_model=AccountPagination)
def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    industry: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Account).filter(Account.org_id == membership.organization_id)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Account.name.ilike(s),
                Account.email.ilike(s),
                Account.website.ilike(s),
                Account.phone.ilike(s)
            )
        )
    if industry and industry != "ALL":
        query = query.filter(Account.industry == industry)

    sort_col = getattr(Account, sort_by, Account.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size or 1
    accounts = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in accounts:
        item = AccountOut.model_validate(a)
        item.assigned_to_name = a.assigned_to.full_name if a.assigned_to else "Unassigned"
        item.contacts_count = len(a.contacts)
        item.deals_count = len(a.deals)
        item.total_deal_value = sum(d.value for d in a.deals)
        items.append(item)

    return AccountPagination(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("", response_model=AccountOut)
def create_account(
    account_in: AccountCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_user(db, account_in.assigned_to_id, membership.organization_id)

    account = Account(
        org_id=membership.organization_id,
        name=account_in.name,
        industry=account_in.industry,
        website=account_in.website,
        email=account_in.email,
        phone=account_in.phone,
        address=account_in.address,
        company_size=account_in.company_size,
        assigned_to_id=account_in.assigned_to_id or membership.user_id,
        description=account_in.description or "",
        tags=account_in.tags or ""
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    item = AccountOut.model_validate(account)
    item.assigned_to_name = account.assigned_to.full_name if account.assigned_to else "Unassigned"
    return item

@router.get("/{id}", response_model=AccountOut)
def get_account(
    id: int,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == id, Account.org_id == membership.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    item = AccountOut.model_validate(account)
    item.assigned_to_name = account.assigned_to.full_name if account.assigned_to else "Unassigned"
    item.contacts_count = len(account.contacts)
    item.deals_count = len(account.deals)
    item.total_deal_value = sum(d.value for d in account.deals)
    return item

@router.patch("/{id}", response_model=AccountOut)
def update_account(
    id: int,
    account_in: AccountUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == id, Account.org_id == membership.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    update_data = account_in.model_dump(exclude_unset=True)
    if "assigned_to_id" in update_data:
        require_org_user(db, update_data["assigned_to_id"], membership.organization_id)
    for k, v in update_data.items():
        setattr(account, k, v)

    db.commit()
    db.refresh(account)

    item = AccountOut.model_validate(account)
    item.assigned_to_name = account.assigned_to.full_name if account.assigned_to else "Unassigned"
    item.contacts_count = len(account.contacts)
    item.deals_count = len(account.deals)
    item.total_deal_value = sum(d.value for d in account.deals)
    return item

@router.delete("/{id}")
def delete_account(
    id: int,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    account = db.query(Account).filter(Account.id == id, Account.org_id == membership.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully."}
