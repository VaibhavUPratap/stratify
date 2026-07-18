from typing import Dict, Any, List
import asyncio
from .business_memory import BusinessMemoryService
from .prediction_engine import PredictionEngineService

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class FinanceAgent(BaseAgent):
    def __init__(self):
        super().__init__("FinanceAgent", "Finance and Liquidity Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        metrics = context.get("metrics", {})
        ar = metrics.get("accounts_receivable", 0.0)
        ap = metrics.get("accounts_payable", 0.0)
        sales_vol = metrics.get("total_sales_volume", 0.0)
        
        # Calculate mock Gross Profit Margin
        # Let's say cost is ~65% of sales
        estimated_cost = sales_vol * 0.65
        gpm = ((sales_vol - estimated_cost) / sales_vol) * 100 if sales_vol > 0 else 30.0
        
        recommendations = []
        alerts = []
        confidence = 0.90
        
        if gpm < 25.0:
            alerts.append("Gross Profit Margin is critically low (< 25%). Urgent cost review required.")
            recommendations.append({
                "action": "Immediate audit of operations to reduce direct costs.",
                "roi": "High", "risk": "MEDIUM", "confidence": 0.95,
                "reasoning": "Unhealthy GPM erodes cash reserves rapidly."
            })
        elif gpm < 35.0:
            recommendations.append({
                "action": "Optimize vendor pricing or increase customer prices by 5%.",
                "roi": "Medium", "risk": "LOW", "confidence": 0.85,
                "reasoning": "Restores margins back to standard 35% target."
            })
            
        if ap > ar:
            alerts.append("Accounts Payable exceeds Accounts Receivable. Cash flow strain predicted.")
            recommendations.append({
                "action": "Defer non-critical supplier payments and expedite collections.",
                "roi": "High", "risk": "HIGH", "confidence": 0.90,
                "reasoning": "Preserves working capital during payment mismatches."
            })
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"Gross Profit Margin estimated at {gpm:.1f}%. Outstanding AR: ${ar:,.2f}, AP: ${ap:,.2f}.",
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": confidence,
            "supporting_evidence": f"AR/AP Ratio: {ar/ap if ap > 0 else 'N/A'}"
        }

class OperationsAgent(BaseAgent):
    def __init__(self):
        super().__init__("OperationsAgent", "Supply Chain & Warehouse Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        products = context.get("products", [])
        suppliers = context.get("suppliers", [])
        
        out_of_stock = sum(1 for p in products if p.get("stock_level", 0) == 0)
        below_reorder = sum(1 for p in products if p.get("stock_level", 0) <= p.get("reorder_point", 10))
        
        low_reliability_suppliers = [s for s in suppliers if s.get("reliability_score", 1.0) < 0.8]
        
        recommendations = []
        alerts = []
        
        if out_of_stock > 0:
            alerts.append(f"{out_of_stock} product SKU(s) are currently out of stock.")
            recommendations.append({
                "action": "Expedite reorder POs for out-of-stock SKUs immediately.",
                "roi": "High", "risk": "LOW", "confidence": 0.95,
                "reasoning": "Restores lost sales potential from out-of-stock items."
            })
            
        if below_reorder > 0:
            recommendations.append({
                "action": f"Trigger automatic inventory replenishment orders for {below_reorder} SKUs.",
                "roi": "Medium", "risk": "LOW", "confidence": 0.90,
                "reasoning": "Maintains warehouse buffer levels above reorder points."
            })
            
        if low_reliability_suppliers:
            alerts.append(f"{len(low_reliability_suppliers)} vendor(s) are operating below 80% reliability threshold.")
            recommendations.append({
                "action": "Initiate sourcing protocols for backup logistics suppliers.",
                "roi": "Medium", "risk": "MEDIUM", "confidence": 0.80,
                "reasoning": "Mitigates delivery delay exposure on core supply items."
            })
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"Inventory health shows {out_of_stock} out-of-stock and {below_reorder} below safety line.",
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": 0.88,
            "supporting_evidence": f"OOS items: {out_of_stock}, Low safety items: {below_reorder}"
        }

class MarketingAgent(BaseAgent):
    def __init__(self):
        super().__init__("MarketingAgent", "Growth and Retention Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        customers = context.get("customers", [])
        vip_customers = [c for c in customers if c.get("clv", 0.0) > 5000.0]
        
        # High churn probability mock count
        high_churn_risk = sum(1 for c in customers if c.get("credit_score", 700) < 620)
        
        recommendations = []
        alerts = []
        
        if vip_customers:
            recommendations.append({
                "action": f"Launch premium rewards/loyalty campaign targeting {len(vip_customers)} VIP customers.",
                "roi": "High", "risk": "LOW", "confidence": 0.85,
                "reasoning": "Secures long-term recurring CLV from high-value entities."
            })
            
        if high_churn_risk > 0:
            alerts.append(f"{high_churn_risk} customer(s) flagged at high risk of churn.")
            recommendations.append({
                "action": "Offer dynamic 5% credit limit extensions or payment holiday incentives.",
                "roi": "Medium", "risk": "MEDIUM", "confidence": 0.75,
                "reasoning": "Reduces immediate relationship termination triggers."
            })
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"VIP cohort includes {len(vip_customers)} clients. Churn warning on {high_churn_risk} account(s).",
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": 0.82,
            "supporting_evidence": f"VIP cohort count: {len(vip_customers)}"
        }

class SupplierAgent(BaseAgent):
    def __init__(self):
        super().__init__("SupplierAgent", "Procurement and Sourcing Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        suppliers = context.get("suppliers", [])
        total_suppliers = len(suppliers)
        
        recommendations = []
        alerts = []
        
        if total_suppliers < 3:
            alerts.append(f"Supplier concentration risk active ({total_suppliers} total suppliers).")
            recommendations.append({
                "action": "Diversify vendor database to include at least 3 distinct suppliers.",
                "roi": "High", "risk": "LOW", "confidence": 0.90,
                "reasoning": "Prevents single-point-of-failure supply chain disruptions."
            })
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"Procurement network active with {total_suppliers} vendors registered.",
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": 0.85,
            "supporting_evidence": f"Total active suppliers: {total_suppliers}"
        }

class CustomerAgent(BaseAgent):
    def __init__(self):
        super().__init__("CustomerAgent", "Client Ledger & Credit Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        customers = context.get("customers", [])
        bad_credit_accounts = [c for c in customers if c.get("credit_score", 700) < 650]
        
        recommendations = []
        alerts = []
        
        if bad_credit_accounts:
            alerts.append(f"{len(bad_credit_accounts)} account(s) present elevated credit defaults risk.")
            recommendations.append({
                "action": "Tighter credit terms (e.g. Net 15 instead of Net 30) for low credit score customers.",
                "roi": "Medium", "risk": "LOW", "confidence": 0.88,
                "reasoning": "Mitigates accounts receivable aging delays and write-offs."
            })
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"Evaluated accounts database; {len(bad_credit_accounts)} accounts exceed risk metrics.",
            "alerts": alerts,
            "recommendations": recommendations,
            "confidence": 0.86,
            "supporting_evidence": f"Sub-650 Credit score accounts: {len(bad_credit_accounts)}"
        }

class RiskAgent(BaseAgent):
    def __init__(self):
        super().__init__("RiskAgent", "Enterprise Risk Aggregation Specialist")

    async def analyse(self, context: Dict[str, Any], predictions: Dict[str, Any]) -> Dict[str, Any]:
        # Collects alerts from context or calculations
        # Aggregates overall warning signals
        active_alerts_count = context.get("alerts_count", 0)
        
        if active_alerts_count >= 5:
            risk_level = "CRITICAL"
        elif active_alerts_count >= 3:
            risk_level = "HIGH"
        elif active_alerts_count >= 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
            
        return {
            "agent_name": self.name,
            "role": self.role,
            "analysis": f"Enterprise risk context calculated as {risk_level} based on {active_alerts_count} system warnings.",
            "alerts": [f"Enterprise risk warning state is {risk_level}"] if risk_level in ["HIGH", "CRITICAL"] else [],
            "recommendations": [],
            "confidence": 0.95,
            "supporting_evidence": f"Warning count: {active_alerts_count}"
        }

class CEOAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.specialists = [
            FinanceAgent(),
            OperationsAgent(),
            MarketingAgent(),
            SupplierAgent(),
            CustomerAgent(),
            RiskAgent()
        ]

    async def run_consensus_engine(self) -> Dict[str, Any]:
        memory = BusinessMemoryService(self.db)
        predictor = PredictionEngineService(self.db)
        
        # 1. Load context payload
        profile = await memory.get_company_profile()
        metrics = await memory.get_aggregate_metrics()
        customers = await memory.get_all_customers()
        suppliers = await memory.get_all_suppliers()
        products = await memory.get_all_products()
        events = await memory.retrieve_events(limit=20)
        
        # Fetch forecasts
        revenue_f = await predictor.forecast_revenue()
        cash_f = await predictor.forecast_cashflow()
        
        context = {
            "profile": profile,
            "metrics": metrics,
            "customers": customers,
            "suppliers": suppliers,
            "products": products,
            "events": events,
            "alerts_count": len([e for e in events if e.get("severity") in ["WARNING", "CRITICAL"]])
        }
        
        predictions = {
            "revenue": revenue_f,
            "cashflow": cash_f
        }
        
        # 2. Run all specialist agents in parallel
        tasks = [agent.analyse(context, predictions) for agent in self.specialists]
        reports = await asyncio.gather(*tasks)
        
        # 3. Consolidate and sort recommendations
        # Sorting formula: Score = Confidence * Risk Weight
        # Weight mapping
        weights = {
            "LOW": 1.0,
            "MEDIUM": 0.7,
            "HIGH": 0.5,
            "CRITICAL": 0.3
        }
        
        consolidated_recs = []
        for rep in reports:
            agent_name = rep["agent_name"]
            confidence = rep["confidence"]
            for rec in rep["recommendations"]:
                risk = rec["risk"]
                weight = weights.get(risk, 0.5)
                score = confidence * weight
                
                consolidated_recs.append({
                    "agent_name": agent_name,
                    "action": rec["action"],
                    "roi": rec["roi"],
                    "risk": risk,
                    "confidence": confidence,
                    "score": round(score, 2),
                    "reasoning": rec["reasoning"],
                    "evidence": rep["supporting_evidence"]
                })
                
        # Sort highest score first
        consolidated_recs.sort(key=lambda x: x["score"], reverse=True)
        
        # Compile executive brief text
        summaries = [r["analysis"] for r in reports]
        summary_str = " | ".join(summaries)
        
        return {
            "executive_summary": f"CEO Consensus complete. {summary_str}",
            "top_priorities": [rec["action"] for rec in consolidated_recs[:3]],
            "strategic_decisions": consolidated_recs,
            "business_risks": [alert for rep in reports for alert in rep["alerts"]],
            "reports_compiled": len(reports)
        }
