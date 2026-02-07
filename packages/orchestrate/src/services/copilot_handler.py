"""
GitHub Copilot service handler.
Used for Phase 4: Implementation Planning (code review, budget allocation).

Note: This uses the OpenAI API with a Copilot-optimized system prompt,
as direct Copilot Chat API access is limited. For full Copilot integration,
consider using the GitHub Copilot CLI or VS Code extension.

Copilot/Code-focused prompting excels at:
- Code architecture review
- Dependency analysis
- Timeline and resource estimation
- Technical risk assessment
"""

from typing import Optional, Dict, Any
import logging

from .base_handler import BaseHandler, ServiceConfig, ServiceResponse

logger = logging.getLogger(__name__)


class CopilotHandler(BaseHandler):
    """
    Handler for code-focused analysis.
    Uses OpenAI API with engineering-focused prompting.
    """
    
    SERVICE_NAME = "copilot"
    
    def _default_config(self) -> ServiceConfig:
        return ServiceConfig(
            model="gpt-4-turbo",  # Or gpt-4o for latest
            max_tokens=4000,
            temperature=0.3,  # Lower for technical accuracy
            timeout_seconds=300
        )
    
    async def _initialize_client(self) -> None:
        """Initialize OpenAI client with engineering focus."""
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)  # allow-secret
        except ImportError:
            raise ImportError(
                "openai package required. "
                "Install with: pip install openai"
            )
    
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request with engineering-focused system prompt."""
        
        system_prompt = """You are an expert software architect and engineering lead with deep experience in:
- Real-time systems and latency optimization
- Distributed systems and scalability
- Rust, Flutter, and audio programming (SuperCollider)
- Project estimation and risk assessment
- Technical debt and dependency management

When reviewing code or architectures:
1. Be specific about potential issues with line-level detail
2. Quantify risks where possible (latency in ms, memory in MB, etc.)
3. Provide concrete alternatives, not just critiques
4. Consider both technical debt and timeline pressure
5. Flag assumptions that need validation

Always structure your analysis with clear sections and actionable recommendations."""

        try:
            response = await self._client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            
            content = response.choices[0].message.content
            structured = self._extract_json(content)
            
            metadata = {
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "token_usage": response.usage.total_tokens
            }
            
            return ServiceResponse(
                success=True,
                content=content,
                structured_data=structured,
                metadata=metadata
            )
            
        except Exception as e:
            return ServiceResponse(
                success=False,
                content="",
                error=str(e)
            )
    
    async def review_architecture(
        self,
        architecture_spec: str,
        constraints: Dict[str, Any],
        task_name: str = "architecture_review"
    ) -> Dict[str, Any]:
        """
        Specialized method for architecture review.
        
        Args:
            architecture_spec: The architecture document/code
            constraints: Dict of constraints (latency, scale, etc.)
            task_name: Task identifier
        """
        constraints_text = "\n".join([
            f"- {k}: {v}" for k, v in constraints.items()
        ])
        
        prompt = f"""ARCHITECTURE SPECIFICATION:
```
{architecture_spec}
```

CONSTRAINTS:
{constraints_text}

TASK: Perform a comprehensive architecture review addressing:
1. Dependency risk assessment
2. Latency bottleneck analysis  
3. Scalability validation
4. Development timeline realism
5. Top 3 recommendations

Provide both narrative analysis and structured JSON output."""

        return await self.execute(prompt, task_name)
    
    async def estimate_budget(
        self,
        project_scope: str,
        timeline_weeks: int,
        team_size: int,
        task_name: str = "budget_estimation"
    ) -> Dict[str, Any]:
        """
        Specialized method for budget estimation.
        """
        prompt = f"""PROJECT SCOPE:
{project_scope}

PARAMETERS:
- Timeline: {timeline_weeks} weeks
- Team size: {team_size} developer(s)

TASK: Create a detailed budget allocation including:
1. Personnel costs (breakdown by role/phase)
2. Infrastructure costs (cloud, tools, hardware)
3. Contingency planning (risk-based)
4. Alternative scenarios (lean/full/accelerated)
5. ROI analysis

Output both narrative analysis and structured JSON with CSV-compatible budget table."""

        return await self.execute(prompt, task_name)
    
    async def close(self) -> None:
        """Close the client."""
        if self._client:
            await self._client.close()
            self._client = None


# Convenience function
async def query_copilot(
    api_key: str,  # allow-secret
    prompt: str,
    task_name: str = "copilot_query"
) -> Dict[str, Any]:
    """Standalone function to query with Copilot-style prompting."""
    handler = CopilotHandler(api_key)
    try:
        return await handler.execute(prompt, task_name)
    finally:
        await handler.close()
