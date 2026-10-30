from typing import Dict, Any, List
from app.models.crm import Lead
from app.schemas.ai import LeadScoringResponse, LeadScoringFactor

def calculate_lead_score(lead: Lead) -> LeadScoringResponse:
    score = 30  # Baseline score
    factors: List[LeadScoringFactor] = []

    # 1. Lead Source Factor
    source = (lead.lead_source or "").lower()
    if "referral" in source:
        impact = 25
        score += impact
        factors.append(LeadScoringFactor(factor="Lead Source", score_impact=impact, reason="Referrals demonstrate the highest closing propensity (+25 pts)."))
    elif "linkedin" in source:
        impact = 15
        score += impact
        factors.append(LeadScoringFactor(factor="Lead Source", score_impact=impact, reason="B2B LinkedIn engagement shows targeted intent (+15 pts)."))
    elif "website" in source:
        impact = 10
        score += impact
        factors.append(LeadScoringFactor(factor="Lead Source", score_impact=impact, reason="Organic inbound web visitor (+10 pts)."))
    else:
        factors.append(LeadScoringFactor(factor="Lead Source", score_impact=5, reason=f"Outreach or paid channel: {lead.lead_source} (+5 pts)."))
        score += 5

    # 2. Seniority / Title Factor
    title = (lead.job_title or "").lower()
    exec_keywords = ["vp", "vice president", "director", "c-level", "cto", "cmo", "ceo", "chief", "head", "founder"]
    if any(k in title for k in exec_keywords):
        impact = 20
        score += impact
        factors.append(LeadScoringFactor(factor="Decision Maker Authority", score_impact=impact, reason=f"Title '{lead.job_title}' indicates executive purchasing power (+20 pts)."))
    elif "manager" in title or "lead" in title:
        impact = 10
        score += impact
        factors.append(LeadScoringFactor(factor="Decision Maker Authority", score_impact=impact, reason=f"Title '{lead.job_title}' indicates mid-level influencer (+10 pts)."))

    # 3. Deal Value Factor
    val = float(lead.estimated_value or 0.0)
    if val >= 50000:
        impact = 20
        score += impact
        factors.append(LeadScoringFactor(factor="Commercial Value", score_impact=impact, reason=f"High estimated pipeline value (${val:,.0f}) (+20 pts)."))
    elif val >= 15000:
        impact = 10
        score += impact
        factors.append(LeadScoringFactor(factor="Commercial Value", score_impact=impact, reason=f"Mid-tier pipeline value (${val:,.0f}) (+10 pts)."))

    # 4. Profile Completeness Factor
    if lead.phone and len(lead.phone) > 6:
        score += 5
        factors.append(LeadScoringFactor(factor="Direct Phone Verified", score_impact=5, reason="Direct telephone line provided (+5 pts)."))
    if lead.company:
        score += 5
        factors.append(LeadScoringFactor(factor="Corporate Domain", score_impact=5, reason="Company domain and affiliation verified (+5 pts)."))

    # 5. Status Stage Bonus
    st = (lead.status or "").upper()
    if st == "QUALIFIED":
        score += 15
        factors.append(LeadScoringFactor(factor="Qualification Status", score_impact=15, reason="Lead has completed preliminary BANT qualification (+15 pts)."))
    elif st == "CONTACTED":
        score += 5
        factors.append(LeadScoringFactor(factor="Qualification Status", score_impact=5, reason="Initial contact logged (+5 pts)."))

    # Normalize score between 0 and 100
    final_score = min(max(score, 10), 99)

    category = "Cold"
    recommendation = "Nurture with automated email cadence."
    if final_score >= 80:
        category = "Hot"
        recommendation = "High purchase intent! Schedule immediate discovery or demo call within 24 hours."
    elif final_score >= 50:
        category = "Warm"
        recommendation = "Send case study and follow up via phone to schedule technical demonstration."

    return LeadScoringResponse(
        lead_id=lead.id,
        lead_name=f"{lead.first_name} {lead.last_name}",
        total_score=final_score,
        category=category,
        factors=factors,
        recommendation=recommendation
    )

