from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import logging
from typing import Dict, Any

from ..database import get_db
from ..services.business_memory import BusinessMemoryService
from ..services.ollama_client import OllamaClient
from ..utils.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["AI Intelligence"])

class ChatRequest(BaseModel):
    question: str

# Dependency Providers for loose coupling (SOLID)
def get_ollama_client() -> OllamaClient:
    return OllamaClient()

def get_prompt_builder() -> PromptBuilder:
    return PromptBuilder()

@router.get("/ollama-status")
async def get_ollama_status(client: OllamaClient = Depends(get_ollama_client)):
    return await client.check_status()

@router.post("/chat")
async def chat_with_gemma(
    request: ChatRequest, 
    db: AsyncSession = Depends(get_db),
    client: OllamaClient = Depends(get_ollama_client),
    builder: PromptBuilder = Depends(get_prompt_builder)
):
    # 1. Retrieve database context
    memory = BusinessMemoryService(db)
    
    company_profile = await memory.get_company_profile()
    metrics = await memory.get_aggregate_metrics()
    customers = await memory.get_all_customers()
    suppliers = await memory.get_all_suppliers()
    products = await memory.get_all_products()
    recent_events = await memory.retrieve_events(limit=10)
    
    # 2. Package context object
    context_obj = {
        "recent_events": recent_events,
        "customers": customers,
        "suppliers": suppliers,
        "products": products
    }
    
    # 3. Build optimized dynamic prompts
    system_context = builder.build_system_context(company_profile, metrics)
    prompt = builder.build_chat_prompt(request.question, context_obj)
    
    # 4. Invoke LLM client
    response_text = await client.generate_response(prompt, system_context)
    
    # Log interaction
    await memory.store_event(
        event_type="ai_chat_query",
        description=f"User asked: '{request.question[:40]}...'. AI replied.",
        severity="INFO",
        source="system",
        metadata_dict={"question": request.question, "response": response_text[:100]}
    )
    
    return {
        "response": response_text,
        "model_used": client.model,
        "context_summary": {
            "events_loaded": len(recent_events),
            "customers_loaded": len(customers),
            "suppliers_loaded": len(suppliers),
            "products_loaded": len(products)
        }
    }

@router.get("/executive-brief")
async def generate_executive_brief(
    db: AsyncSession = Depends(get_db),
    client: OllamaClient = Depends(get_ollama_client),
    builder: PromptBuilder = Depends(get_prompt_builder)
):
    memory = BusinessMemoryService(db)
    metrics = await memory.get_aggregate_metrics()
    recent_events = await memory.retrieve_events(limit=10)
    
    prompt = builder.build_brief_prompt(metrics, recent_events)
    raw_response = await client.generate_response(prompt)
    
    try:
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        brief_data = json.loads(cleaned)
    except Exception as e:
        logger.warning(f"Failed to parse LLM response into JSON: {e}. Raw response: {raw_response}")
        brief_data = {
            "morning_summary": raw_response if raw_response else "Failed to compile summary.",
            "critical_alerts": [e.get("description") for e in recent_events if e.get("severity") == "WARNING"][:3],
            "top_opportunities": ["Optimize accounts payable timeline"],
            "business_health_summary": "Stable",
            "top_5_actions": ["Review unpaid invoices", "Verify stock status"]
        }
        
    return brief_data
