"""
OpenAI ChatGPT service handler.
Used for Phase 3: Messaging & Narrative Synthesis.

ChatGPT excels at:
- Narrative clarity and flow
- Audience-specific framing
- Generating multiple variants in parallel
"""

from typing import Optional, Dict, Any, List
import logging

from .base_handler import BaseHandler, ServiceConfig, ServiceResponse

logger = logging.getLogger(__name__)


class ChatGPTHandler(BaseHandler):
    """Handler for OpenAI ChatGPT API."""
    
    SERVICE_NAME = "chatgpt"
    
    def _default_config(self) -> ServiceConfig:
        return ServiceConfig(
            model="gpt-4-turbo",
            max_tokens=4000,
            temperature=0.7,  # Slightly higher for narrative variety
            timeout_seconds=300
        )
    
    async def _initialize_client(self) -> None:
        """Initialize OpenAI async client."""
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)  # allow-secret
        except ImportError:
            raise ImportError(
                "openai package required. "
                "Install with: pip install openai"
            )
    
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request to OpenAI API."""
        
        system_prompt = kwargs.get("system_prompt", 
            "You are an expert writer skilled at crafting compelling narratives "
            "for diverse audiences. You adapt tone and emphasis based on the "
            "target reader while maintaining factual accuracy."
        )
        
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
            
            # Extract content
            content = response.choices[0].message.content
            
            # Try to parse structured JSON
            structured = self._extract_json(content)
            
            # Build metadata
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
            error_msg = str(e)
            
            # Handle specific OpenAI errors
            if "rate_limit" in error_msg.lower():
                error_msg = f"Rate limit exceeded: {error_msg}"
            elif "context_length" in error_msg.lower():
                error_msg = f"Context too long: {error_msg}"
            
            return ServiceResponse(
                success=False,
                content="",
                error=error_msg
            )
    
    async def generate_variants(
        self,
        prompt_template: str,
        variants: List[Dict[str, Any]],
        task_name: str,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple narrative variants in parallel.
        
        Args:
            prompt_template: Template with {placeholders}
            variants: List of dicts with values for each variant
            task_name: Base task name (will be suffixed with variant index)
            timeout: Override timeout
            
        Returns:
            List of results, one per variant
        """
        import asyncio
        
        tasks = []
        for i, variant_context in enumerate(variants):
            variant_task_name = f"{task_name}_variant_{i+1}"
            prompt = prompt_template.format(**variant_context)
            tasks.append(self.execute(prompt, variant_task_name, timeout=timeout))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dicts
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "task": f"{task_name}_variant_{i+1}",
                    "service": self.SERVICE_NAME,
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def close(self) -> None:
        """Close the OpenAI client."""
        if self._client:
            await self._client.close()
            self._client = None


# Convenience function
async def query_chatgpt(
    api_key: str,  # allow-secret
    prompt: str,
    task_name: str = "chatgpt_query",
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Standalone function to query ChatGPT.
    
    Example:
        result = await query_chatgpt(
            api_key="sk-...",  # allow-secret
            prompt="Write a grant narrative for NSF Creative IT",
            system_prompt="You are a grant writing expert."
        )
    """
    handler = ChatGPTHandler(api_key)
    try:
        if system_prompt:
            # Inject system prompt into kwargs
            return await handler.execute(
                prompt, task_name, 
                context={"system_prompt": system_prompt}
            )
        return await handler.execute(prompt, task_name)
    finally:
        await handler.close()
