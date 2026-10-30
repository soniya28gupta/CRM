from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import datetime

class MetricCard(BaseModel):
    title: str
    value: Any
    change_percentage: Optional[float] = None
    period: str = "vs last month"
    trend: str = "up"  # up, down, neutral

class DashboardMetricsOut(BaseModel):
    total_leads: int
    total_contacts: int
    conversion_rate: float  # e.g. 14.5%
    active_deals: int
    open_pipeline_value: float
    weighted_pipeline_value: float
    closed_won_revenue: float
    tasks_due_today: int
    cards: List[MetricCard]

class ChartDataPoint(BaseModel):
    label: str
    value: float
    secondary_value: Optional[float] = None

class SalesPerformanceOut(BaseModel):
    monthly_trend: List[ChartDataPoint]
    leads_by_source: List[ChartDataPoint]
    leads_by_status: List[ChartDataPoint]
    deals_by_stage: List[ChartDataPoint]
