import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.business import Company, Customer, Supplier, Product
from app.models.history import BusinessEvent, RecommendationHistory, DecisionHistory
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class BusinessMemoryService:
    """Maintains unified episodic and decision history context arrays."""

    @staticmethod
    async def get_company_profile(db: AsyncSession) -> Dict[str, Any]:
        stmt = select(Company).limit(1)
        company = (await db.execute(stmt)).scalars().first()
        if company:
            return {
                "name": company.name,
                "industry": company.industry,
                "tax_id": company.tax_id,
                "cash_balance": company.cash_balance
            }
        return {"name": "Default SME Ltd", "industry": "Retail", "cash_balance": 50000.0}

    @staticmethod
    async def get_episodic_memory(db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        stmt = select(BusinessEvent).order_by(BusinessEvent.timestamp.desc()).limit(limit)
        events = (await db.execute(stmt)).scalars().all()
        return [
            {
                "event_type": ev.event_type,
                "description": ev.description,
                "timestamp": ev.timestamp.isoformat(),
                "severity": ev.severity,
                "metadata_json": ev.metadata_json
            } for ev in events
        ]

    @staticmethod
    async def get_decision_memory(db: AsyncSession, limit: int = 5) -> List[Dict[str, Any]]:
        stmt = select(DecisionHistory).order_by(DecisionHistory.timestamp.desc()).limit(limit)
        decisions = (await db.execute(stmt)).scalars().all()
        return [
            {
                "user_action": d.user_action,
                "business_outcome": d.business_outcome,
                "feedback": d.feedback,
                "timestamp": d.timestamp.isoformat()
            } for d in decisions
        ]

    @staticmethod
    async def compile_context(db: AsyncSession) -> Dict[str, Any]:
        profile = await BusinessMemoryService.get_company_profile(db)
        recent_events = await BusinessMemoryService.get_episodic_memory(db)
        recent_decisions = await BusinessMemoryService.get_decision_memory(db)

        low_stock_products = []
        try:
            stmt = select(Product).where(Product.stock_level <= Product.reorder_point)
            products = (await db.execute(stmt)).scalars().all()
            low_stock_products = [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "stock_level": p.stock_level,
                    "stock": p.stock_level,
                    "reorder_point": p.reorder_point,
                    "reorder": p.reorder_point
                } for p in products
            ]
        except Exception as e:
            logger.error("Could not fetch low stock products for context: %s", e)

        top_customers = []
        try:
            stmt = select(Customer).order_by(Customer.clv.desc()).limit(5)
            customers = (await db.execute(stmt)).scalars().all()
            top_customers = [
                {
                    "name": c.name,
                    "clv": c.clv,
                    "credit_score": c.credit_score
                } for c in customers
            ]
        except Exception as e:
            logger.error("Could not fetch top customers for context: %s", e)

        risky_suppliers = []
        try:
            stmt = select(Supplier).order_by(Supplier.reliability_score.asc()).limit(5)
            suppliers = (await db.execute(stmt)).scalars().all()
            risky_suppliers = [
                {
                    "name": s.name,
                    "reliability_score": s.reliability_score,
                    "average_lead_days": s.average_lead_days
                } for s in suppliers
            ]
        except Exception as e:
            logger.error("Could not fetch risky suppliers for context: %s", e)

        return {
            "profile": profile,
            "recent_events": recent_events,
            "recent_decisions": recent_decisions,
            "decision_history": recent_decisions,
            "low_stock_products": low_stock_products,
            "top_customers": top_customers,
            "risky_suppliers": risky_suppliers
        }

