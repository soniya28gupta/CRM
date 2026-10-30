import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from app.core.database import get_db
from app.api.deps import get_current_membership
from app.models.organization import OrganizationMembership
from app.models.crm import Deal, Lead, Pipeline, PipelineStage, Task, Contact, Account
from app.schemas.dashboard import DashboardMetricsOut, MetricCard, SalesPerformanceOut, ChartDataPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/metrics", response_model=DashboardMetricsOut)
def get_dashboard_metrics(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    org_id = membership.organization_id
    now = datetime.datetime.utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day)
    today_end = today_start + datetime.timedelta(days=1)

    # 1. Total Leads
    total_leads = db.query(func.count(Lead.id)).filter(Lead.org_id == org_id).scalar() or 0
    converted_leads = db.query(func.count(Lead.id)).filter(Lead.org_id == org_id, Lead.status == "CONVERTED").scalar() or 0
    conversion_rate = round((converted_leads / total_leads * 100), 1) if total_leads > 0 else 0.0

    # 2. Total Contacts
    total_contacts = db.query(func.count(Contact.id)).filter(Contact.org_id == org_id).scalar() or 0

    # 3. Deals & Pipeline
    active_deals = db.query(func.count(Deal.id)).filter(Deal.org_id == org_id, Deal.status == "OPEN").scalar() or 0
    
    open_deals = db.query(Deal).filter(Deal.org_id == org_id, Deal.status == "OPEN").all()
    won_deals = db.query(Deal).filter(Deal.org_id == org_id, Deal.status == "WON").all()

    open_pipeline_val = sum(d.value for d in open_deals)
    weighted_pipeline_val = sum(d.value * (d.probability / 100.0) for d in open_deals)
    closed_won_revenue = sum(d.value for d in won_deals)

    # 4. Tasks due today
    tasks_due_today = db.query(func.count(Task.id)).filter(
        Task.org_id == org_id,
        Task.is_completed == False,
        Task.due_date >= today_start,
        Task.due_date < today_end
    ).scalar() or 0

    cards = [
        MetricCard(title="Total Leads", value=total_leads, period="All records in organization"),
        MetricCard(title="Total Contacts", value=total_contacts, period="All records in organization"),
        MetricCard(title="Conversion Rate", value=f"{conversion_rate}%", period="Converted leads / total leads"),
        MetricCard(title="Active Deals", value=active_deals, period="Deals with OPEN status"),
        MetricCard(title="Open Pipeline", value=f"${open_pipeline_val:,.0f}", period="Sum of OPEN deal values"),
        MetricCard(title="Tasks Due Today", value=tasks_due_today, period="Incomplete tasks due today")
    ]

    return DashboardMetricsOut(
        total_leads=total_leads,
        total_contacts=total_contacts,
        conversion_rate=conversion_rate,
        active_deals=active_deals,
        open_pipeline_value=open_pipeline_val,
        weighted_pipeline_value=weighted_pipeline_val,
        closed_won_revenue=closed_won_revenue,
        tasks_due_today=tasks_due_today,
        cards=cards
    )

@router.get("/charts", response_model=SalesPerformanceOut)
def get_sales_performance_charts(
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    org_id = membership.organization_id
    now = datetime.datetime.utcnow()
    current_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def month_offset(month_offset: int) -> datetime.datetime:
        month_index = current_month.year * 12 + current_month.month - 1 + month_offset
        year, month = divmod(month_index, 12)
        return current_month.replace(year=year, month=month + 1)

    first_month = month_offset(-5)
    next_month = month_offset(1)

    # Leads by source
    sources = db.query(Lead.lead_source, func.count(Lead.id)).filter(
        Lead.org_id == org_id
    ).group_by(Lead.lead_source).all()
    leads_by_source = [ChartDataPoint(label=s[0] or "Unknown", value=float(s[1])) for s in sources]

    # Leads by status
    statuses = db.query(Lead.status, func.count(Lead.id)).filter(
        Lead.org_id == org_id
    ).group_by(Lead.status).all()
    leads_by_status = [ChartDataPoint(label=st[0] or "Unknown", value=float(st[1])) for st in statuses]

    # Deals by stage
    stages = (
        db.query(PipelineStage)
        .join(Pipeline, Pipeline.id == PipelineStage.pipeline_id)
        .filter(Pipeline.org_id == org_id)
        .order_by(Pipeline.is_default.desc(), PipelineStage.stage_order.asc())
        .all()
    )
    deal_counts = {
        row[0]: (float(row[1] or 0), int(row[2] or 0))
        for row in (
            db.query(Deal.stage_id, func.sum(Deal.value), func.count(Deal.id))
            .filter(Deal.org_id == org_id)
            .group_by(Deal.stage_id)
            .all()
        )
    }
    deals_by_stage = [
        ChartDataPoint(
            label=stage.name,
            value=deal_counts.get(stage.id, (0.0, 0))[0],
            secondary_value=float(deal_counts.get(stage.id, (0.0, 0))[1]),
        )
        for stage in stages
    ]

    lead_counts = {
        (int(year), int(month)): int(count)
        for year, month, count in (
            db.query(
                extract("year", Lead.created_at),
                extract("month", Lead.created_at),
                func.count(Lead.id),
            )
            .filter(
                Lead.org_id == org_id,
                Lead.created_at >= first_month,
                Lead.created_at < next_month,
            )
            .group_by(extract("year", Lead.created_at), extract("month", Lead.created_at))
            .all()
        )
    }
    conversions_by_month = {
        (int(year), int(month)): int(count)
        for year, month, count in (
            db.query(
                extract("year", Lead.converted_at),
                extract("month", Lead.converted_at),
                func.count(Lead.id),
            )
            .filter(
                Lead.org_id == org_id,
                Lead.converted_at.isnot(None),
                Lead.converted_at >= first_month,
                Lead.converted_at < next_month,
            )
            .group_by(extract("year", Lead.converted_at), extract("month", Lead.converted_at))
            .all()
        )
    }
    monthly_trend = []
    for offset in range(-5, 1):
        month = month_offset(offset)
        key = (month.year, month.month)
        monthly_trend.append(
            ChartDataPoint(
                label=month.strftime("%b"),
                value=float(lead_counts.get(key, 0)),
                secondary_value=float(conversions_by_month.get(key, 0)),
            )
        )

    return SalesPerformanceOut(
        monthly_trend=monthly_trend,
        leads_by_source=leads_by_source,
        leads_by_status=leads_by_status,
        deals_by_stage=deals_by_stage
    )
