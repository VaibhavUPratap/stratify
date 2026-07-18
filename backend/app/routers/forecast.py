from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.prediction_engine import PredictionEngineService

router = APIRouter(prefix="/forecast", tags=["Predictive Forecasts"])

# DI factories
def get_prediction_engine_service(db: AsyncSession = Depends(get_db)) -> PredictionEngineService:
    return PredictionEngineService(db)

@router.get("/revenue")
async def forecast_revenue(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.forecast_revenue()

@router.get("/cashflow")
async def forecast_cashflow(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.forecast_cashflow()

@router.get("/demand")
async def forecast_demand(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.forecast_demand()

@router.get("/inventory")
async def forecast_inventory(engine: PredictionEngineService = Depends(get_prediction_engine_service)):
    return await engine.forecast_inventory()
