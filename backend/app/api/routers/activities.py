import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List
from app.core.database import get_db
from app.api.deps import get_current_membership, require_write_access
from app.api.tenant import require_org_entity, require_org_user
from app.models.organization import OrganizationMembership
from app.models.crm import Activity, Task, Meeting
from app.schemas.activity import (
    ActivityCreate, ActivityOut,
    TaskCreate, TaskUpdate, TaskOut,
    MeetingCreate, MeetingOut
)

router = APIRouter(prefix="/activities", tags=["Activities, Tasks & Meetings"])

# =========================================================================
# ACTIVITIES TIMELINE
# =========================================================================

@router.get("", response_model=List[ActivityOut])
def list_activities(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Activity).filter(Activity.org_id == membership.organization_id)

    if entity_type and entity_id:
        query = query.filter(Activity.entity_type == entity_type, Activity.entity_id == entity_id)
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)

    activities = query.order_by(desc(Activity.created_at)).limit(limit).all()
    results = []
    for a in activities:
        out = ActivityOut.model_validate(a)
        out.created_by_name = a.created_by.full_name if a.created_by else "System"
        results.append(out)
    return results

@router.post("", response_model=ActivityOut)
def create_activity(
    act_in: ActivityCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_entity(
        db, act_in.entity_type, act_in.entity_id, membership.organization_id
    )

    act = Activity(
        org_id=membership.organization_id,
        activity_type=act_in.activity_type,
        subject=act_in.subject,
        description=act_in.description,
        entity_type=act_in.entity_type,
        entity_id=act_in.entity_id,
        created_by_id=membership.user_id,
        due_date=act_in.due_date,
        is_completed=act_in.is_completed
    )
    db.add(act)
    db.commit()
    db.refresh(act)

    out = ActivityOut.model_validate(act)
    out.created_by_name = act.created_by.full_name if act.created_by else "System"
    return out

# =========================================================================
# TASKS
# =========================================================================

@router.get("/tasks", response_model=List[TaskOut])
def list_tasks(
    status_filter: Optional[str] = None,  # pending, completed, overdue, today
    priority: Optional[str] = None,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.org_id == membership.organization_id)
    now = datetime.datetime.utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day)
    today_end = today_start + datetime.timedelta(days=1)

    if status_filter == "pending":
        query = query.filter(Task.is_completed == False)
    elif status_filter == "completed":
        query = query.filter(Task.is_completed == True)
    elif status_filter == "overdue":
        query = query.filter(Task.is_completed == False, Task.due_date < now)
    elif status_filter == "today":
        query = query.filter(Task.is_completed == False, Task.due_date >= today_start, Task.due_date < today_end)

    if priority and priority != "ALL":
        query = query.filter(Task.priority == priority)

    tasks = query.order_by(Task.due_date.asc().nullslast()).all()
    results = []
    for t in tasks:
        out = TaskOut.model_validate(t)
        out.assigned_to_name = t.assigned_to.full_name if t.assigned_to else "Unassigned"
        results.append(out)
    return results

@router.post("/tasks", response_model=TaskOut)
def create_task(
    task_in: TaskCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    require_org_user(db, task_in.assigned_to_id, membership.organization_id)
    if task_in.entity_id > 0:
        require_org_entity(
            db, task_in.entity_type, task_in.entity_id, membership.organization_id
        )

    task = Task(
        org_id=membership.organization_id,
        title=task_in.title,
        description=task_in.description,
        due_date=task_in.due_date,
        priority=task_in.priority,
        is_completed=task_in.is_completed,
        assigned_to_id=task_in.assigned_to_id or membership.user_id,
        entity_type=task_in.entity_type,
        entity_id=task_in.entity_id,
        created_by_id=membership.user_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    out = TaskOut.model_validate(task)
    out.assigned_to_name = task.assigned_to.full_name if task.assigned_to else "Unassigned"
    return out

@router.patch("/tasks/{id}", response_model=TaskOut)
def update_task(
    id: int,
    task_in: TaskUpdate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == id, Task.org_id == membership.organization_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    update_data = task_in.model_dump(exclude_unset=True)
    if "assigned_to_id" in update_data:
        require_org_user(db, update_data["assigned_to_id"], membership.organization_id)
    for k, v in update_data.items():
        setattr(task, k, v)

    db.commit()
    db.refresh(task)

    out = TaskOut.model_validate(task)
    out.assigned_to_name = task.assigned_to.full_name if task.assigned_to else "Unassigned"
    return out

# =========================================================================
# MEETINGS
# =========================================================================

@router.get("/meetings", response_model=List[MeetingOut])
def list_meetings(
    status_filter: Optional[str] = None,
    membership: OrganizationMembership = Depends(get_current_membership),
    db: Session = Depends(get_db)
):
    query = db.query(Meeting).filter(Meeting.org_id == membership.organization_id)
    if status_filter:
        query = query.filter(Meeting.status == status_filter)

    meetings = query.order_by(Meeting.start_time.asc()).all()
    results = []
    for m in meetings:
        out = MeetingOut.model_validate(m)
        out.created_by_name = m.created_by.full_name if m.created_by else "System"
        results.append(out)
    return results

@router.post("/meetings", response_model=MeetingOut)
def create_meeting(
    meet_in: MeetingCreate,
    membership: OrganizationMembership = Depends(require_write_access),
    db: Session = Depends(get_db)
):
    if meet_in.entity_id > 0:
        require_org_entity(
            db, meet_in.entity_type, meet_in.entity_id, membership.organization_id
        )

    meeting = Meeting(
        org_id=membership.organization_id,
        title=meet_in.title,
        description=meet_in.description,
        start_time=meet_in.start_time,
        end_time=meet_in.end_time,
        location=meet_in.location,
        attendees=meet_in.attendees,
        entity_type=meet_in.entity_type,
        entity_id=meet_in.entity_id,
        created_by_id=membership.user_id,
        status=meet_in.status
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    out = MeetingOut.model_validate(meeting)
    out.created_by_name = meeting.created_by.full_name if meeting.created_by else "System"
    return out
