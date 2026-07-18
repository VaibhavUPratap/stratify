from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.prediction_engine import PredictionEngineService

router = APIRouter(tags=["Risk & Pricing"])

# DI factories
def get_prediction_engine_service(db: AsyncSession = Depends(get_db)) -> PredictionEngineService:
    return PredictionEngineService(db)

@router.get("/risk/customers")
async def risk_customers(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.predict_customer_risk()

@router.get("/risk/suppliers")
async def risk_suppliers(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.predict_supplier_risk()

@router.get("/pricing")
async def pricing(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.recommend_pricing()
