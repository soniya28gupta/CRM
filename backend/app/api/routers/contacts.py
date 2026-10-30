import io
import csv
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import require_org_record, require_org_user
from app.models.organization import OrganizationMembership
from app.models.crm import Contact, Account, Deal, Activity
from app.schemas.contact import ContactCreate, ContactUpdate, ContactOut, ContactPagination

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.get("", response_model=ContactPagination)
def list_contacts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Contact).filter(Contact.org_id == membership.organization_id)

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Contact.first_name.ilike(s),
                Contact.last_name.ilike(s),
                Contact.email.ilike(s),
                Contact.phone.ilike(s),
                Contact.job_title.ilike(s)
            )
        )

    sort_col = getattr(Contact, sort_by, Contact.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size or 1
    contacts = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for c in contacts:
        item = ContactOut.model_validate(c)
        item.account_name = c.account.name if c.account else "Independent"
        item.assigned_to_name = c.assigned_to.full_name if c.assigned_to else "Unassigned"
        items.append(item)

    return ContactPagination(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/export/csv")
def export_contacts_csv(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter(Contact.org_id == membership.organization_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Job Title", "Account Name", "Created At"])
    for c in contacts:
        writer.writerow([
            c.id, c.first_name, c.last_name, c.email, c.phone or "",
            c.job_title or "", c.account.name if c.account else "",
            c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contacts_export.csv"}
    )

@router.post("", response_model=ContactOut)
def create_contact(
    contact_in: ContactCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_record(db, Account, contact_in.account_id, membership.organization_id, "Account")
    require_org_user(db, contact_in.assigned_to_id, membership.organization_id)

    contact = Contact(
        org_id=membership.organization_id,
        first_name=contact_in.first_name,
        last_name=contact_in.last_name,
        email=contact_in.email,
        phone=contact_in.phone,
        job_title=contact_in.job_title,
        account_id=contact_in.account_id,
        assigned_to_id=contact_in.assigned_to_id or membership.user_id,
        tags=contact_in.tags or "",
        notes=contact_in.notes or ""
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)

    item = ContactOut.model_validate(contact)
    item.account_name = contact.account.name if contact.account else "Independent"
    item.assigned_to_name = contact.assigned_to.full_name if contact.assigned_to else "Unassigned"
    return item

@router.get("/{id}", response_model=ContactOut)
def get_contact(
    id: int,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == id, Contact.org_id == membership.organization_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")

    item = ContactOut.model_validate(contact)
    item.account_name = contact.account.name if contact.account else "Independent"
    item.assigned_to_name = contact.assigned_to.full_name if contact.assigned_to else "Unassigned"
    return item

@router.patch("/{id}", response_model=ContactOut)
def update_contact(
    id: int,
    contact_in: ContactUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == id, Contact.org_id == membership.organization_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")

    update_data = contact_in.model_dump(exclude_unset=True)
    if "account_id" in update_data:
        require_org_record(db, Account, update_data["account_id"], membership.organization_id, "Account")
    if "assigned_to_id" in update_data:
        require_org_user(db, update_data["assigned_to_id"], membership.organization_id)
    for k, v in update_data.items():
        setattr(contact, k, v)

    db.commit()
    db.refresh(contact)

    item = ContactOut.model_validate(contact)
    item.account_name = contact.account.name if contact.account else "Independent"
    item.assigned_to_name = contact.assigned_to.full_name if contact.assigned_to else "Unassigned"
    return item

@router.delete("/{id}")
def delete_contact(
    id: int,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id == id, Contact.org_id == membership.organization_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found.")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully."}
