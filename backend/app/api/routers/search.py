from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Dict, Any
from app.core.database import get_db
from app.api.deps import get_current_membership
from app.models.organization import OrganizationMembership
from app.models.crm import Lead, Contact, Account, Deal
from app.models.industries import Property

router = APIRouter(prefix="/search", tags=["Global Search"])

@router.get("", response_model=Dict[str, List[Dict[str, Any]]])
def global_search(
    q: str = Query(..., min_length=1),
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query_str = f"%{q}%"
    org_id = membership.organization_id

    # 1. Leads
    leads = db.query(Lead).filter(
        Lead.org_id == org_id,
        or_(
            Lead.first_name.ilike(query_str),
            Lead.last_name.ilike(query_str),
            Lead.email.ilike(query_str),
            Lead.company.ilike(query_str)
        )
    ).limit(5).all()

    # 2. Contacts
    contacts = db.query(Contact).filter(
        Contact.org_id == org_id,
        or_(
            Contact.first_name.ilike(query_str),
            Contact.last_name.ilike(query_str),
            Contact.email.ilike(query_str)
        )
    ).limit(5).all()

    # 3. Accounts
    accounts = db.query(Account).filter(
        Account.org_id == org_id,
        Account.name.ilike(query_str)
    ).limit(5).all()

    # 4. Deals
    deals = db.query(Deal).filter(
        Deal.org_id == org_id,
        Deal.name.ilike(query_str)
    ).limit(5).all()

    # 5. Properties
    properties = db.query(Property).filter(
        Property.org_id == org_id,
        or_(
            Property.title.ilike(query_str),
            Property.location.ilike(query_str)
        )
    ).limit(5).all()

    return {
        "leads": [
            {"id": l.id, "title": f"{l.first_name} {l.last_name}", "subtitle": l.company or l.email, "url": f"/leads/{l.id}", "type": "Lead"}
            for l in leads
        ],
        "contacts": [
            {"id": c.id, "title": f"{c.first_name} {c.last_name}", "subtitle": c.email, "url": f"/contacts/{c.id}", "type": "Contact"}
            for c in contacts
        ],
        "accounts": [
            {"id": a.id, "title": a.name, "subtitle": a.industry, "url": f"/accounts/{a.id}", "type": "Account"}
            for a in accounts
        ],
        "deals": [
            {"id": d.id, "title": d.name, "subtitle": f"${d.value:,.0f} • {d.status}", "url": f"/deals", "type": "Deal"}
            for d in deals
        ],
        "properties": [
            {"id": p.id, "title": p.title, "subtitle": f"${p.price:,.0f} • {p.location}", "url": f"/industry-modules/real-estate", "type": "Property"}
            for p in properties
        ]
    }

