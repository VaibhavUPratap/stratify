from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from .business_memory import BusinessMemoryService

class SimulationEngineService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_simulation(self, price_change_pct: float, hiring_cost: float, supplier_change: str, inventory_decisions: str, loan_decisions: str) -> Dict[str, Any]:
        """
        Calculates simulated business KPIs based on mathematical twin multipliers.
        """
        memory = BusinessMemoryService(self.db)
        metrics = await memory.get_aggregate_metrics()
        
        # Baselines
        base_revenue = metrics.get("total_sales_volume", 145800.50)
        base_profit = base_revenue * 0.35 # 35% margin
        base_cash = 25000.0 # base cash flow estimate
        base_risk = 50.0 # scale of 0-100
        base_health = 80.0
        
        # Apply Sliders Multipliers
        # 1. Price Change impact on demand and revenue
        # Elasticity assumption: price hike of +10% reduces demand volume by -5% but increases revenue net.
        demand_elasticity = -0.5
        revenue_multiplier = (1.0 + (price_change_pct / 100.0)) * (1.0 + (price_change_pct / 100.0) * demand_elasticity)
        
        sim_revenue = base_revenue * revenue_multiplier
        sim_profit = base_profit * revenue_multiplier
        
        # 2. Hiring Costs impact cash and profit
        sim_profit -= hiring_cost
        base_cash -= hiring_cost
        
        # 3. Supplier Changes
        supplier_risk_impact = 0.0
        if supplier_change == "diversify":
            base_risk -= 15.0 # reduces supplier concentration risk
            base_health += 5.0
        elif supplier_change == "cheaper_alternative":
            # Cheaper supplier improves profit margin but increases operational risk
            sim_profit += base_revenue * 0.05
            base_risk += 20.0
            base_health -= 5.0
            
        # 4. Inventory Decisions
        if inventory_decisions == "bulk_buy":
            # Bulk buy requires capital (cash outflow) but reduces procurement cost slightly
            base_cash -= 15000.0
            sim_profit += base_revenue * 0.02
        elif inventory_decisions == "just_in_time":
            # Releases capital (increases cash) but raises stockout risk
            base_cash += 10000.0
            base_risk += 15.0
            
        # 5. Loan Decisions
        if loan_decisions == "take_loan":
            # Cash inflow, but interest reduces profit and raises risk slightly
            base_cash += 50000.0
            sim_profit -= 2500.0
            base_risk += 10.0
            
        # Bounds and final health aggregation
        sim_revenue = max(0.0, sim_revenue)
        sim_profit = max(-50000.0, sim_profit)
        sim_cash = max(-20000.0, base_cash)
        sim_risk = min(100.0, max(0.0, base_risk))
        
        # Health metric aggregation
        sim_health = min(100.0, max(0.0, base_health - (sim_risk * 0.2) + (sim_profit / 10000.0)))
        
        return {
            "revenue": round(sim_revenue, 2),
            "profit": round(sim_profit, 2),
            "cash_flow": "Positive" if sim_cash > 0 else "Strained",
            "risk": "HIGH" if sim_risk > 65 else ("MEDIUM" if sim_risk > 35 else "LOW"),
            "inventory": "Optimal" if inventory_decisions == "standard" else ("High" if inventory_decisions == "bulk_buy" else "Low"),
            "business_health": round(sim_health, 2)
        }
