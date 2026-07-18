from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Dict, Any, List

from ..database import get_db
from ..services.agent_engine import CEOAgent, FinanceAgent, OperationsAgent, MarketingAgent, SupplierAgent, CustomerAgent, RiskAgent
from ..services.simulation_engine import SimulationEngineService
from ..services.business_memory import BusinessMemoryService
from ..models.models import RecommendationHistory

router = APIRouter(tags=["Multi-Agent Decision Intelligence"])

class SimulateRequest(BaseModel):
    price_change_pct: float
    hiring_cost: float
    supplier_change: str
    inventory_decisions: str
    loan_decisions: str

from typing import Dict, Any, List, Optional

class DecisionLogRequest(BaseModel):
    recommendation_id: int
    action_taken: Optional[str] = None # Approve or Decline (frontend compatibility)
    user_action: Optional[str] = None # APPROVED | REJECTED | MODIFIED (documentation compliance)
    modification_notes: Optional[str] = None
    business_outcome: Optional[str] = None
    outcome_revenue_impact: Optional[float] = 0.0
    feedback: Optional[str] = None

# DI factories
def get_ceo_agent(db: AsyncSession = Depends(get_db)) -> CEOAgent:
    return CEOAgent(db)

def get_simulation_engine_service(db: AsyncSession = Depends(get_db)) -> SimulationEngineService:
    return SimulationEngineService(db)

def get_business_memory_service(db: AsyncSession = Depends(get_db)) -> BusinessMemoryService:
    return BusinessMemoryService(db)

@router.get("/agents")
async def run_agents(db: AsyncSession = Depends(get_db)):
    memory = BusinessMemoryService(db)
    metrics = await memory.get_aggregate_metrics()
    products = await memory.get_all_products()
    suppliers = await memory.get_all_suppliers()
    customers = await memory.get_all_customers()
    events = await memory.retrieve_events(limit=10)
    
    context = {
        "metrics": metrics,
        "products": products,
        "suppliers": suppliers,
        "customers": customers,
        "alerts_count": len([e for e in events if e.get("severity") in ["WARNING", "CRITICAL"]])
    }
    predictions = {}
    
    specialists = [
        FinanceAgent(),
        OperationsAgent(),
        MarketingAgent(),
        SupplierAgent(),
        CustomerAgent(),
        RiskAgent()
    ]
    
    reports = []
    for agent in specialists:
        rep = await agent.analyse(context, predictions)
        reports.append(rep)
        
    return {
        "status": "Agents executed",
        "reports": reports
    }

@router.get("/recommendations")
async def get_recommendations(
    ceo: CEOAgent = Depends(get_ceo_agent),
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    consensus = await ceo.run_consensus_engine()
    
    # Store recommendation text into historical DB so they can be referenced
    for rec in consensus.get("strategic_decisions", []):
        q = select(RecommendationHistory).filter(RecommendationHistory.recommendation_text == rec["action"])
        res = await db.execute(q)
        existing = res.scalar_one_or_none()
        if not existing:
            await memory.store_recommendation(
                agent_name=rec["agent_name"],
                recommendation_text=rec["action"],
                confidence_score=rec["confidence"],
                risk_level=rec["risk"],
                supporting_evidence=rec["evidence"]
            )
            
    result = await db.execute(select(RecommendationHistory).order_by(RecommendationHistory.timestamp.desc()).limit(20))
    recs = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "roi": "Medium-High",
            "risk": r.risk_level,
            "confidence": r.confidence_score,
            "supporting_data": r.supporting_evidence,
            "action": r.recommendation_text,
            "reasoning": f"Calculated by {r.agent_name} with confidence {r.confidence_score*100:.1f}%."
        } for r in recs
    ]

@router.post("/simulate")
async def digital_twin_simulate(
    request: SimulateRequest,
    sim: SimulationEngineService = Depends(get_simulation_engine_service)
):
    return await sim.run_simulation(
        price_change_pct=request.price_change_pct,
        hiring_cost=request.hiring_cost,
        supplier_change=request.supplier_change,
        inventory_decisions=request.inventory_decisions,
        loan_decisions=request.loan_decisions
    )

@router.get("/decision-history")
async def get_decision_history(memory: BusinessMemoryService = Depends(get_business_memory_service)):
    return await memory.retrieve_decisions()

@router.post("/decision-history")
async def log_decision(
    request: DecisionLogRequest,
    memory: BusinessMemoryService = Depends(get_business_memory_service),
    db: AsyncSession = Depends(get_db)
):
    q = select(RecommendationHistory).filter(RecommendationHistory.id == request.recommendation_id)
    res = await db.execute(q)
    rec = res.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    action = request.user_action or request.action_taken or "APPROVED"
    mapped_status = action.upper()
    if mapped_status == "APPROVE":
        mapped_status = "APPROVED"
    elif mapped_status == "DECLINE" or mapped_status == "REJECT":
        mapped_status = "REJECTED"
        
    # Sync status to the recommendation record
    rec.status = mapped_status
    db.add(rec)
    
    outcome = await memory.store_decision(
        recommendation_id=request.recommendation_id,
        action_taken=action,
        business_outcome=request.business_outcome or f"Marked {action}.",
        modification_notes=request.modification_notes,
        outcome_revenue_impact=request.outcome_revenue_impact or 0.0,
        feedback=request.feedback
    )
    return {"status": "decision_logged", "decision_id": outcome.id}

@router.get("/explain/{recommendation_id}")
async def explain_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db)
):
    q = select(RecommendationHistory).filter(RecommendationHistory.id == recommendation_id)
    res = await db.execute(q)
    rec = res.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    dept_map = {
        "FinanceAgent": ["Finance", "Accounting"],
        "OperationsAgent": ["Procurement", "Logistics", "Warehouse"],
        "MarketingAgent": ["Sales", "Marketing"],
        "SupplierAgent": ["Procurement", "Sourcing"],
        "CustomerAgent": ["Sales", "Customer Support"],
        "RiskAgent": ["Compliance", "Legal", "Operations"]
    }
    depts = dept_map.get(rec.agent_name, ["Executive"])
    
    return {
        "reason": rec.recommendation_text,
        "evidence": rec.supporting_evidence,
        "confidence": rec.confidence_score,
        "business_impact": "Resolves immediate alert indicator flags.",
        "affected_departments": depts
    }
