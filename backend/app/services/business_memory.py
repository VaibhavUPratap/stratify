from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from ..models.models import (
    BusinessEvent, Company, Customer, Supplier, Product, 
    RecommendationHistory, DecisionHistory, Invoice, Sales
)
from typing import List, Dict, Any
import json

class BusinessMemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 1. Semantic Memory Fetchers
    async def get_company_profile(self) -> Dict[str, Any]:
        result = await self.db.execute(select(Company).limit(1))
        company = result.scalar_one_or_none()
        if company:
            return {
                "name": company.name,
                "industry": company.industry,
                "tax_id": company.tax_id,
                "registration_number": company.registration_number,
                "address": company.address,
                "phone": company.phone,
                "email": company.email,
                "cash_balance": company.cash_balance,
                "annual_revenue_target": company.annual_revenue_target,
                "founded_year": company.founded_year
            }
        return {}

    async def get_all_customers(self) -> List[Dict[str, Any]]:
        result = await self.db.execute(select(Customer))
        customers = result.scalars().all()
        return [
            {
                "id": c.id, "name": c.name, "email": c.email, 
                "company_name": c.company_name, "credit_score": c.credit_score,
                "credit_limit": c.credit_limit, "payment_terms_days": c.payment_terms_days,
                "clv": c.clv, "is_active": c.is_active
            } for c in customers
        ]

    async def get_all_suppliers(self) -> List[Dict[str, Any]]:
        result = await self.db.execute(select(Supplier))
        suppliers = result.scalars().all()
        return [
            {
                "id": s.id, "name": s.name, "email": s.email, 
                "payment_terms_days": s.payment_terms_days, 
                "reliability_score": s.reliability_score,
                "average_lead_days": s.average_lead_days,
                "total_orders_placed": s.total_orders_placed,
                "total_delayed_orders": s.total_delayed_orders
            } for s in suppliers
        ]

    async def get_all_products(self) -> List[Dict[str, Any]]:
        result = await self.db.execute(select(Product))
        products = result.scalars().all()
        return [
            {
                "id": p.id, "sku": p.sku, "name": p.name, 
                "category": p.category, "price": p.price, 
                "cost": p.cost, "stock_level": p.stock_level,
                "reorder_point": p.reorder_point, "reorder_quantity": p.reorder_quantity
            } for p in products
        ]

    # 2. Episodic Memory Fetchers & Event Logging
    async def store_event(self, event_type: str, description: str, severity: str = "INFO", source: str = "system", entity_type: str = None, entity_id: int = None, metadata_dict: Dict[str, Any] = None):
        metadata_json = json.dumps(metadata_dict) if metadata_dict else None
        new_event = BusinessEvent(
            event_type=event_type,
            description=description,
            severity=severity,
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json
        )
        self.db.add(new_event)
        await self.db.commit()
        await self.db.refresh(new_event)
        return new_event

    async def retrieve_events(self, limit: int = 20, event_type: str = None) -> List[Dict[str, Any]]:
        query = select(BusinessEvent).order_by(BusinessEvent.timestamp.desc())
        if event_type:
            query = query.filter(BusinessEvent.event_type == event_type)
        result = await self.db.execute(query.limit(limit))
        events = result.scalars().all()
        return [
            {
                "id": e.id, "event_type": e.event_type, "description": e.description,
                "severity": e.severity, "source": e.source, "entity_type": e.entity_type,
                "entity_id": e.entity_id, "metadata": json.loads(e.metadata_json) if e.metadata_json else None,
                "timestamp": e.timestamp.isoformat()
            } for e in events
        ]

    # 3. Decision Memory Store & Retrieve
    async def store_recommendation(self, agent_name: str, recommendation_text: str, confidence_score: float, risk_level: str, supporting_evidence: str) -> RecommendationHistory:
        rec = RecommendationHistory(
            agent_name=agent_name,
            recommendation_text=recommendation_text,
            confidence_score=confidence_score,
            risk_level=risk_level,
            supporting_evidence=supporting_evidence
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def store_decision(self, recommendation_id: int, action_taken: str, business_outcome: str = None) -> DecisionHistory:
        dec = DecisionHistory(
            recommendation_id=recommendation_id,
            action_taken=action_taken,
            business_outcome=business_outcome
        )
        self.db.add(dec)
        await self.db.commit()
        await self.db.refresh(dec)
        return dec

    async def retrieve_decisions(self, limit: int = 20) -> List[Dict[str, Any]]:
        query = select(DecisionHistory).order_by(DecisionHistory.timestamp.desc()).limit(limit)
        result = await self.db.execute(query)
        decisions = result.scalars().all()
        
        recs_query = select(RecommendationHistory)
        recs_result = await self.db.execute(recs_query)
        recs_dict = {r.id: r for r in recs_result.scalars().all()}
        
        output = []
        for d in decisions:
            rec = recs_dict.get(d.recommendation_id)
            output.append({
                "decision_id": d.id,
                "recommendation_id": d.recommendation_id,
                "recommendation_text": rec.recommendation_text if rec else "N/A",
                "agent_name": rec.agent_name if rec else "N/A",
                "action_taken": d.action_taken,
                "business_outcome": d.business_outcome,
                "timestamp": d.timestamp.isoformat()
            })
        return output

    # 4. Aggregated Metrics helper for Prompt Context
    async def get_aggregate_metrics(self) -> Dict[str, Any]:
        # Count totals
        total_customers = await self.db.execute(select(func.count(Customer.id)))
        total_suppliers = await self.db.execute(select(func.count(Supplier.id)))
        total_products = await self.db.execute(select(func.count(Product.id)))
        
        # Financial summary
        invoices = await self.db.execute(select(Invoice))
        all_invoices = invoices.scalars().all()
        
        ar = sum(inv.total_amount - inv.paid_amount for inv in all_invoices if inv.invoice_type == "AR" and inv.status != "PAID")
        ap = sum(inv.total_amount - inv.paid_amount for inv in all_invoices if inv.invoice_type == "AP" and inv.status != "PAID")
        
        sales_result = await self.db.execute(select(Sales))
        total_sales = sum(s.total_price for s in sales_result.scalars().all())
        
        return {
            "total_customers": total_customers.scalar() or 0,
            "total_suppliers": total_suppliers.scalar() or 0,
            "total_products": total_products.scalar() or 0,
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "total_sales_volume": total_sales
        }
