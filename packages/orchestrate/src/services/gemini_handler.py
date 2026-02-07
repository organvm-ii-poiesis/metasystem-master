"""
Google Gemini service handler.
Used for Phase 2: Specification Hardening (edge cases, latency constraints).

Gemini excels at:
- Long-context reasoning (1M+ tokens)
- Cross-document analysis
- Structured output generation
"""

from typing import Optional, Dict, Any
import logging

from .base_handler import BaseHandler, ServiceConfig, ServiceResponse

logger = logging.getLogger(__name__)


class GeminiHandler(BaseHandler):
    """Handler for Google Gemini API."""
    
    SERVICE_NAME = "gemini"
    
    def _default_config(self) -> ServiceConfig:
        return ServiceConfig(
            model="gemini-1.5-pro",
            max_tokens=8000,
            temperature=0.4,
            timeout_seconds=600  # Longer for complex analysis
        )
    
    async def _initialize_client(self) -> None:
        """Initialize Google Generative AI client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)  # allow-secret
            self._client = genai.GenerativeModel(
                model_name=self.config.model,
                generation_config={
                    "max_output_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                }
            )
        except ImportError:
            raise ImportError(
                "google-generativeai package required. "
                "Install with: pip install google-generativeai"
            )
    
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request to Gemini API."""
        import asyncio
        
        try:
            # Gemini's generate_content is synchronous, wrap in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._client.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": self.config.max_tokens,
                        "temperature": self.config.temperature,
                    }
                )
            )
            
            # Extract content
            content = response.text
            
            # Try to parse structured JSON
            structured = self._extract_json(content)
            
            # Build metadata
            metadata = {
                "model": self.config.model,
                "finish_reason": response.candidates[0].finish_reason.name if response.candidates else None,
                "safety_ratings": [
                    {"category": r.category.name, "probability": r.probability.name}
                    for r in (response.candidates[0].safety_ratings if response.candidates else [])
                ],
                "token_usage": getattr(response, 'usage_metadata', {})
            }
            
            return ServiceResponse(
                success=True,
                content=content,
                structured_data=structured,
                metadata=metadata
            )
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle specific Gemini errors
            if "SAFETY" in error_msg.upper():
                error_msg = f"Content blocked by safety filters: {error_msg}"
            elif "QUOTA" in error_msg.upper():
                error_msg = f"API quota exceeded: {error_msg}"
            
            return ServiceResponse(
                success=False,
                content="",
                error=error_msg
            )
    
    async def execute_with_context(
        self,
        prompt: str,
        task_name: str,
        documents: list[str],
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute prompt with multiple documents as context.
        Leverages Gemini's long-context capability.
        
        Args:
            prompt: The main prompt/question
            task_name: Task identifier
            documents: List of document contents to include as context
            timeout: Override timeout
        """
        # Combine documents with prompt
        context_block = "\n\n---\n\n".join([
            f"DOCUMENT {i+1}:\n{doc}" 
            for i, doc in enumerate(documents)
        ])
        
        full_prompt = f"""CONTEXT DOCUMENTS:
{context_block}

---

TASK:
{prompt}"""
        
        return await self.execute(full_prompt, task_name, timeout=timeout)
    
    async def close(self) -> None:
        """Cleanup (Gemini client doesn't need explicit close)."""
        self._client = None


# Convenience function
async def query_gemini(
    api_key: str,  # allow-secret
    prompt: str,
    task_name: str = "gemini_query",
    documents: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    Standalone function to query Gemini.
    
    Example:
        result = await query_gemini(
            api_key="...",  # allow-secret
            prompt="Analyze edge cases in this specification",
            documents=[spec_doc, architecture_doc]
        )
    """
    handler = GeminiHandler(api_key)
    try:
        if documents:
            return await handler.execute_with_context(prompt, task_name, documents)
        return await handler.execute(prompt, task_name)
    finally:
        await handler.close()
