"""
Perplexity AI service handler.
Used for Phase 1: Research Validation (precedent verification, funding landscape).

Perplexity excels at:
- Deep research synthesis with citations
- Source aggregation and verification
- Finding contradictions in claims
"""

from typing import Optional, Dict, Any
import aiohttp
import json
import logging

from .base_handler import BaseHandler, ServiceConfig, ServiceResponse

logger = logging.getLogger(__name__)


class PerplexityHandler(BaseHandler):
    """Handler for Perplexity AI API."""
    
    SERVICE_NAME = "perplexity"
    API_BASE = "https://api.perplexity.ai"
    
    def _default_config(self) -> ServiceConfig:
        return ServiceConfig(
            model="llama-3.1-sonar-large-128k-online",  # Online model for research
            max_tokens=4000,
            temperature=0.3,  # Lower for factual accuracy
            timeout_seconds=300
        )
    
    async def _initialize_client(self) -> None:
        """Initialize aiohttp session for Perplexity API."""
        self._client = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request to Perplexity API."""
        
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant providing accurate, well-sourced information. Always cite your sources and be explicit about uncertainty."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "return_citations": True,
            "return_related_questions": False
        }
        
        try:
            async with self._client.post(
                f"{self.API_BASE}/chat/completions",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    return ServiceResponse(
                        success=False,
                        content="",
                        error=f"API error {response.status}: {error_text}"
                    )
                
                data = await response.json()
                
                # Extract content
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Extract citations if available
                citations = data.get("citations", [])
                
                # Try to parse structured JSON from response
                structured = self._extract_json(content)
                
                # Build metadata
                metadata = {
                    "citations": citations,
                    "model": data.get("model"),
                    "usage": data.get("usage", {}),
                    "token_usage": data.get("usage", {}).get("total_tokens", 0)
                }
                
                return ServiceResponse(
                    success=True,
                    content=content,
                    structured_data=structured,
                    metadata=metadata
                )
                
        except aiohttp.ClientError as e:
            return ServiceResponse(
                success=False,
                content="",
                error=f"Network error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            return ServiceResponse(
                success=False,
                content="",
                error=f"JSON decode error: {str(e)}"
            )
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._client:
            await self._client.close()
            self._client = None


# Convenience function for standalone usage
async def query_perplexity(
    api_key: str,  # allow-secret
    prompt: str,
    task_name: str = "perplexity_query"
) -> Dict[str, Any]:
    """
    Standalone function to query Perplexity.
    
    Example:
        result = await query_perplexity(
            api_key="pplx-...",  # allow-secret
            prompt="Find academic sources for audience participation in live performance",
            task_name="precedent_research"
        )
    """
    handler = PerplexityHandler(api_key)
    try:
        return await handler.execute(prompt, task_name)
    finally:
        await handler.close()
