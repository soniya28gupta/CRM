from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AIChatRequest(BaseModel):
    message: str
    context_type: Optional[str] = None  # general, lead, contact, account, deal
    context_id: Optional[int] = None

class AIChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str] = []
    related_records: List[Dict[str, Any]] = []

class LeadScoringFactor(BaseModel):
    factor: str
    score_impact: int
    reason: str

class LeadScoringResponse(BaseModel):
    lead_id: int
    lead_name: str
    total_score: int  # 0 to 100
    category: str     # Hot, Warm, Cold
    factors: List[LeadScoringFactor]
    recommendation: str

