from pydantic import BaseModel
from typing import Optional, List
import datetime

class PipelineStageBase(BaseModel):
    name: str
    stage_order: int
    probability: float
    color: str

class PipelineStageOut(PipelineStageBase):
    id: int
    pipeline_id: int

    class Config:
        from_attributes = True

class PipelineOut(BaseModel):
    id: int
    org_id: int
    name: str
    is_default: bool
    stages: List[PipelineStageOut] = []

    class Config:
        from_attributes = True

class DealBase(BaseModel):
    name: str
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    pipeline_id: int
    stage_id: int
    value: float = 0.0
    currency: str = "USD"
    probability: float = 10.0
    expected_close_date: Optional[datetime.datetime] = None
    assigned_to_id: Optional[int] = None
    source: str = "Inbound"
    description: Optional[str] = ""
    status: str = "OPEN"

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    name: Optional[str] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    stage_id: Optional[int] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    probability: Optional[float] = None
    expected_close_date: Optional[datetime.datetime] = None
    assigned_to_id: Optional[int] = None
    source: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class DealStageUpdate(BaseModel):
    stage_id: int

class DealOut(DealBase):
    id: int
    org_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    account_name: Optional[str] = None
    contact_name: Optional[str] = None
    stage_name: Optional[str] = None
    assigned_to_name: Optional[str] = None

    class Config:
        from_attributes = True

class DealKanbanColumn(BaseModel):
    stage: PipelineStageOut
    deals: List[DealOut]
    total_value: float
    deal_count: int

class DealKanbanBoard(BaseModel):
    columns: List[DealKanbanColumn]
    total_pipeline_value: float
    weighted_pipeline_value: float

