"""
xAI Grok service handler.
Used for Phase 5: Vulnerability Audit (assumption critique, failure scenarios).

Grok excels at:
- Adversarial critique and edge cases
- Provocative questioning
- Assumption-busting
- Unconventional perspectives
"""

from typing import Optional, Dict, Any
import aiohttp
import json
import logging

from .base_handler import BaseHandler, ServiceConfig, ServiceResponse

logger = logging.getLogger(__name__)


class GrokHandler(BaseHandler):
    """Handler for xAI Grok API."""
    
    SERVICE_NAME = "grok"
    API_BASE = "https://api.x.ai/v1"
    
    def _default_config(self) -> ServiceConfig:
        return ServiceConfig(
            model="grok-beta",  # Or grok-2 when available
            max_tokens=4000,
            temperature=0.8,  # Higher for provocative critique
            timeout_seconds=300
        )
    
    async def _initialize_client(self) -> None:
        """Initialize aiohttp session for Grok API."""
        self._client = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request to Grok API."""
        
        system_prompt = kwargs.get("system_prompt", """You are an adversarial critic and devil's advocate. Your job is NOT to be helpful or encouraging—it's to find weaknesses, challenge assumptions, and identify what could go wrong.

When analyzing projects or claims:
1. Assume Murphy's Law applies
2. Question every assumption, especially the "obvious" ones
3. Look for what's NOT being said
4. Identify the single point of failure
5. Be provocative but substantive
6. Don't pull punches, but be specific

You're the skeptic the project needs, not the cheerleader it wants.""")
        
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
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
                
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                structured = self._extract_json(content)
                
                metadata = {
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
    
    async def critique_assumptions(
        self,
        project_summary: str,
        claims: list[str],
        task_name: str = "assumption_critique"
    ) -> Dict[str, Any]:
        """
        Specialized method for assumption-busting critique.
        
        Args:
            project_summary: Overview of the project
            claims: List of claims/assumptions to challenge
            task_name: Task identifier
        """
        claims_text = "\n".join([f"- {claim}" for claim in claims])
        
        prompt = f"""PROJECT SUMMARY:
{project_summary}

KEY CLAIMS BEING MADE:
{claims_text}

ADVERSARIAL AUDIT TASK:
For EACH claim, ask "What if this is WRONG?" and identify:
1. The hidden assumption beneath the claim
2. Conditions under which it would fail
3. Worst-case scenario if wrong
4. How to validate/invalidate it
5. Severity rating (RED/YELLOW/ORANGE/GREEN)

Be ruthless. Find the assumptions that, if wrong, would sink the entire project.

Output both narrative critique and structured JSON with risk matrix."""

        return await self.execute(prompt, task_name)
    
    async def model_failures(
        self,
        system_description: str,
        known_risks: list[str],
        task_name: str = "failure_modeling"
    ) -> Dict[str, Any]:
        """
        Specialized method for failure scenario modeling.
        
        Args:
            system_description: Description of the system
            known_risks: Already-identified risks to build on
            task_name: Task identifier
        """
        risks_text = "\n".join([f"- {risk}" for risk in known_risks])
        
        prompt = f"""SYSTEM DESCRIPTION:
{system_description}

KNOWN RISKS (from prior analysis):
{risks_text}

FAILURE SCENARIO TASK:
Generate 10 detailed failure scenarios across categories:
- Technical failures (3)
- Artistic/creative failures (2)
- Adoption/market failures (2)
- Funding failures (2)
- Personal/capacity failures (1)

For each scenario:
1. Specific trigger event
2. Cascade sequence (step-by-step)
3. Warning signs that would appear beforehand
4. Recovery options (if any)
5. Prevention strategies

Identify which scenarios could trigger each other (failure clusters).
Find the "nightmare scenario"—the one failure that ends everything.

Output narrative and structured JSON."""

        return await self.execute(prompt, task_name)
    
    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._client:
            await self._client.close()
            self._client = None


# Convenience function
async def query_grok(
    api_key: str,  # allow-secret
    prompt: str,
    task_name: str = "grok_query"
) -> Dict[str, Any]:
    """Standalone function to query Grok."""
    handler = GrokHandler(api_key)
    try:
        return await handler.execute(prompt, task_name)
    finally:
        await handler.close()
