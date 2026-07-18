import httpx
import logging
from typing import Dict, Any
from ..config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL

    async def generate_response(self, prompt: str, system_context: str = "") -> str:
        async with httpx.AsyncClient(timeout=180.0) as client:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_context,
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            }
            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                logger.error(f"Failed to communicate with Ollama: {str(e)}")
                return f"Error communicating with local AI model: {str(e)}"

    async def check_status(self) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return {"status": "online", "models": response.json().get("models", [])}
            except Exception as e:
                return {"status": "offline", "error": str(e)}
