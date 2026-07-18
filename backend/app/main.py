from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .models import models # To register tables
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up on shutdown
    await engine.dispose()

app = FastAPI(
    title="SME Business Operating System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "SME Business Operating System",
        "version": "1.0.0",
        "status": "operational",
        "environment": "development",
        "docs": "/docs",
        "api_base": "/api/v1",
        "phases_active": [
            "Phase 1: CRUD",
            "Phase 2: AI",
            "Phase 3: Predictive",
            "Phase 4: Decision"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "sme-os-backend"
    }

from .routers import business, upload, dashboard, ai, forecast, risk, decision

# Include routers here...
app.include_router(business.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(forecast.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(decision.router, prefix="/api/v1")
