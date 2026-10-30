from pydantic import BaseModel
from typing import Optional, List
import datetime

class ActivityBase(BaseModel):
    activity_type: str  # CALL, EMAIL, MEETING, NOTE, TASK, STATUS_CHANGE, ASSIGNMENT, SYSTEM
    subject: str
    description: str = ""
    entity_type: str  # lead, contact, account, deal, industry
    entity_id: int
    due_date: Optional[datetime.datetime] = None
    is_completed: bool = False

class ActivityCreate(ActivityBase):
    pass

class ActivityOut(ActivityBase):
    id: int
    org_id: int
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[datetime.datetime] = None
    priority: str = "MEDIUM"
    is_completed: bool = False
    assigned_to_id: Optional[int] = None
    entity_type: str = "lead"
    entity_id: int = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime.datetime] = None
    priority: Optional[str] = None
    is_completed: Optional[bool] = None
    assigned_to_id: Optional[int] = None

class TaskOut(TaskBase):
    id: int
    org_id: int
    assigned_to_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class MeetingBase(BaseModel):
    title: str
    description: str = ""
    start_time: datetime.datetime
    end_time: datetime.datetime
    location: str = "Google Meet / Zoom"
    attendees: str = ""
    entity_type: str = "lead"
    entity_id: int = 0
    status: str = "SCHEDULED"

class MeetingCreate(MeetingBase):
    pass

class MeetingOut(MeetingBase):
    id: int
    org_id: int
    created_by_id: Optional[int] = None
    created_by_name: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

