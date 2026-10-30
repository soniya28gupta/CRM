import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.crm import Lead, Deal, Task, Meeting, Account, Contact, PipelineStage
from app.models.user import User
from app.schemas.ai import AIChatResponse
from app.services.scoring_service import calculate_lead_score

def process_crm_ai_query(db: Session, org_id: int, user: User, message: str) -> AIChatResponse:
    query = message.lower().strip()
    now = datetime.datetime.utcnow()

    # Tool 1: High value deals
    if "highest value" in query or "biggest deal" in query or "top deal" in query:
        deals = db.query(Deal).filter(
            Deal.org_id == org_id,
            Deal.status == "OPEN"
        ).order_by(Deal.value.desc()).limit(5).all()

        if not deals:
            return AIChatResponse(
                reply="There are currently no open deals registered in your CRM pipeline.",
                suggested_actions=["Create a new Deal", "Import deals via CSV"]
            )

        reply_lines = [f"Here are the top open deals by value for your organization:"]
        records = []
        for d in deals:
            reply_lines.append(f"• **{d.name}** — ${d.value:,.0f} ({d.probability:.0f}% win probability)")
            records.append({"type": "deal", "id": d.id, "name": d.name, "value": f"${d.value:,.0f}"})

        return AIChatResponse(
            reply="\n".join(reply_lines),
            suggested_actions=["View Deals Pipeline", "Schedule review meeting with assigned rep"],
            related_records=records
        )

    # Tool 2: Negotiation deals
    if "negotiation" in query or "in negotiation" in query:
        stage = db.query(PipelineStage).filter(PipelineStage.name.ilike("%negotiation%")).first()
        deals = []
        if stage:
            deals = db.query(Deal).filter(
                Deal.org_id == org_id,
                Deal.stage_id == stage.id,
                Deal.status == "OPEN"
            ).all()

        count = len(deals)
        total_val = sum(d.value for d in deals)
        reply = f"You currently have **{count} deal(s)** in the **Negotiation** stage totaling **${total_val:,.0f}**."
        records = [{"type": "deal", "id": d.id, "name": d.name, "value": f"${d.value:,.0f}"} for d in deals]
        return AIChatResponse(
            reply=reply,
            suggested_actions=["Open Kanban Pipeline", "Filter deals by Negotiation"],
            related_records=records
        )

    # Tool 3: Overdue tasks
    if "overdue" in query or "pending task" in query or "due today" in query:
        tasks = db.query(Task).filter(
            Task.org_id == org_id,
            Task.is_completed == False,
            Task.due_date <= now
        ).order_by(Task.due_date.asc()).limit(5).all()

        if not tasks:
            return AIChatResponse(
                reply="Great job! You have **no overdue tasks** across your organization right now.",
                suggested_actions=["Create a new Task", "Review upcoming meetings"]
            )

        reply_lines = [f"You have **{len(tasks)} overdue or due task(s)** requiring immediate attention:"]
        records = []
        for t in tasks:
            due_str = t.due_date.strftime("%b %d, %H:%M") if t.due_date else "No due date"
            reply_lines.append(f"• **{t.title}** (Priority: {t.priority}, Due: {due_str})")
            records.append({"type": "task", "id": t.id, "name": t.title, "priority": t.priority})

        return AIChatResponse(
            reply="\n".join(reply_lines),
            suggested_actions=["Go to Tasks page", "Mark tasks as completed"],
            related_records=records
        )

    # Tool 4: Upcoming meetings
    if "meeting" in query or "schedule" in query or "calendar" in query:
        meetings = db.query(Meeting).filter(
            Meeting.org_id == org_id,
            Meeting.start_time >= now,
            Meeting.status == "SCHEDULED"
        ).order_by(Meeting.start_time.asc()).limit(5).all()

        if not meetings:
            return AIChatResponse(
                reply="You have no upcoming meetings scheduled in the calendar.",
                suggested_actions=["Schedule a Meeting", "View Leads to contact"]
            )

        reply_lines = ["Here is a summary of your upcoming meetings:"]
        records = []
        for m in meetings:
            st = m.start_time.strftime("%a, %b %d at %I:%M %p")
            reply_lines.append(f"• **{m.title}** on {st} via {m.location}")
            records.append({"type": "meeting", "id": m.id, "name": m.title, "time": st})

        return AIChatResponse(
            reply="\n".join(reply_lines),
            suggested_actions=["Open Meetings Manager", "Create a Calendar invite"],
            related_records=records
        )

    # Tool 5: Leads / Lead scoring / Assigned to me
    if "lead" in query or "prospect" in query:
        leads_q = db.query(Lead).filter(Lead.org_id == org_id)
        if "assigned to me" in query or "my lead" in query:
            leads_q = leads_q.filter(Lead.assigned_to_id == user.id)

        leads = leads_q.order_by(Lead.lead_score.desc()).limit(5).all()
        total_leads = db.query(func.count(Lead.id)).filter(Lead.org_id == org_id).scalar() or 0

        reply_lines = [f"Found **{total_leads} total lead(s)** in your CRM database. Here are the top qualified leads:"]
        records = []
        for l in leads:
            reply_lines.append(f"• **{l.first_name} {l.last_name}** ({l.company}) — Score: **{l.lead_score}/100** | Est. Value: ${l.estimated_value:,.0f}")
            records.append({"type": "lead", "id": l.id, "name": f"{l.first_name} {l.last_name}", "score": l.lead_score})

        return AIChatResponse(
            reply="\n".join(reply_lines),
            suggested_actions=["View all Leads", "Run AI Score on Lead", "Convert Lead to Deal"],
            related_records=records
        )

    # Tool 6: Revenue / Pipeline overview
    if "pipeline" in query or "revenue" in query or "metrics" in query or "summary" in query:
        open_deals = db.query(Deal).filter(Deal.org_id == org_id, Deal.status == "OPEN").all()
        won_deals = db.query(Deal).filter(Deal.org_id == org_id, Deal.status == "WON").all()
        
        open_val = sum(d.value for d in open_deals)
        weighted_val = sum(d.value * (d.probability / 100.0) for d in open_deals)
        won_val = sum(d.value for d in won_deals)

        reply = (
            f"📊 **Executive Revenue & Pipeline Summary:**\n"
            f"• **Open Pipeline Value:** ${open_val:,.2f} across {len(open_deals)} deals\n"
            f"• **Probability-Weighted Pipeline:** ${weighted_val:,.2f}\n"
            f"• **Closed Won Revenue:** ${won_val:,.2f} across {len(won_deals)} deals"
        )
        return AIChatResponse(
            reply=reply,
            suggested_actions=["Open Sales Dashboard", "Review Pipeline Kanban"],
            related_records=[]
        )

    # Fallback response with helpful CRM suggestions
    return AIChatResponse(
        reply=(
            f"Hello {user.full_name}! I am your AI CRM Assistant. I have secure, authorized access to your organization's CRM records. "
            "You can ask me questions like:\n"
            "• *'Which open deals have the highest value?'*\n"
            "• *'How many deals are in negotiation?'*\n"
            "• *'Summarize my upcoming meetings'*\n"
            "• *'Show overdue tasks and follow-ups'*\n"
            "• *'Show top scored leads'* or *'Revenue pipeline summary'*"
        ),
        suggested_actions=[
            "Show highest value deals",
            "Show deals in negotiation",
            "Summarize upcoming meetings",
            "Show overdue tasks"
        ]
    )

