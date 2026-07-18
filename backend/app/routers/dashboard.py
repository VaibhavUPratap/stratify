from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard")
async def get_dashboard():
    # Phase 1: Return realistic dummy values calculated from database (or mocked for now)
    return {
        "metrics": {
            "total_revenue": 145800.50,
            "monthly_revenue": 12400.00,
            "accounts_receivable": 45000.00,
            "accounts_payable": 18200.00,
            "net_working_capital": 26800.00,
            "low_stock_alerts": 3,
            "active_customers": 18,
            "monthly_orders": 24
        },
        "generated_at": datetime.now().isoformat()
    }

@router.get("/business-health")
async def get_business_health():
    return {
        "status": "Healthy",
        "health_score": 85,
        "gross_profit_margin_pct": 42.50,
        "operating_ratio": 0.5750,
        "overdue_invoices": 1,
        "low_stock_products": 2,
        "gross_profit": 61965.20,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/alerts")
async def get_alerts():
    return [
        {
            "severity": "CRITICAL",
            "category": "FINANCIAL",
            "title": "Overdue Invoices Require Immediate Action",
            "message": "1 invoice(s) are past due, totalling $2,500.00.",
            "count": 1
        },
        {
            "severity": "WARNING",
            "category": "INVENTORY",
            "title": "Low Stock: Industrial Widget A",
            "message": "SKU PROD-A100 has 15 units remaining.",
            "product_id": 1
        }
    ]

@router.get("/timeline")
async def get_timeline(limit: int = 20):
    return [
        {
            "id": 1,
            "event_type": "invoice_created",
            "description": "Invoice INV-2026-001 created for $1,425.00",
            "severity": "INFO",
            "timestamp": datetime.now().isoformat()
        }
    ]
