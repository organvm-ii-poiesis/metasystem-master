"""
Base handler for all AI service integrations.
Provides common interface and utilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ServiceResponse:
    """Standardized response from any AI service."""
    success: bool
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "structured_data": self.structured_data,
            "metadata": self.metadata,
            "error": self.error
        }


@dataclass
class ServiceConfig:
    """Configuration for a service handler."""
    model: str
    max_tokens: int
    temperature: float
    timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: int = 5


class BaseHandler(ABC):
    """
    Abstract base class for AI service handlers.
    All service handlers must implement this interface.
    """
    
    SERVICE_NAME: str = "base"
    
    def __init__(self, api_key: str, config: Optional[ServiceConfig] = None):  # allow-secret
        self.api_key = api_key  # allow-secret
        self.config = config or self._default_config()
        self._client = None
        
    @abstractmethod
    def _default_config(self) -> ServiceConfig:
        """Return default configuration for this service."""
        pass
    
    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the API client."""
        pass
    
    @abstractmethod
    async def _send_request(self, prompt: str, **kwargs) -> ServiceResponse:
        """Send request to the service. Must be implemented by subclasses."""
        pass
    
    async def execute(
        self, 
        prompt: str, 
        task_name: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a prompt against the service with retry logic.
        
        Args:
            prompt: The prompt template (may contain {placeholders})
            task_name: Name of the task for logging/tracking
            context: Dictionary of values to substitute into prompt
            timeout: Override default timeout
            
        Returns:
            Dictionary with response content and metadata
        """
        # Initialize client if needed
        if self._client is None:
            await self._initialize_client()
        
        # Substitute context into prompt
        if context:
            try:
                prompt = prompt.format(**context)
            except KeyError as e:
                logger.warning(f"Missing context key in prompt: {e}")
        
        # Execute with retry
        timeout = timeout or self.config.timeout_seconds
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                logger.info(f"[{self.SERVICE_NAME}] Executing {task_name} (attempt {attempt + 1})")
                
                response = await asyncio.wait_for(
                    self._send_request(prompt),
                    timeout=timeout
                )
                
                if response.success:
                    result = self._format_result(response, task_name)
                    logger.info(f"[{self.SERVICE_NAME}] {task_name} completed successfully")
                    return result
                else:
                    last_error = response.error
                    logger.warning(f"[{self.SERVICE_NAME}] {task_name} failed: {response.error}")
                    
            except asyncio.TimeoutError:
                last_error = f"Timeout after {timeout}s"
                logger.warning(f"[{self.SERVICE_NAME}] {task_name} timeout")
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"[{self.SERVICE_NAME}] {task_name} error: {e}")
            
            # Wait before retry
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay_seconds)
        
        # All retries failed
        return self._format_error(task_name, last_error)
    
    def _format_result(self, response: ServiceResponse, task_name: str) -> Dict[str, Any]:
        """Format successful response into standard output."""
        return {
            "task": task_name,
            "service": self.SERVICE_NAME,
            "status": "success",
            "content": response.content,
            "structured_data": response.structured_data,
            "metadata": {
                **(response.metadata or {}),
                "model": self.config.model,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def _format_error(self, task_name: str, error: str) -> Dict[str, Any]:
        """Format error response into standard output."""
        return {
            "task": task_name,
            "service": self.SERVICE_NAME,
            "status": "error",
            "error": error,
            "content": None,
            "structured_data": None,
            "metadata": {
                "model": self.config.model,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    
    def is_available(self) -> bool:
        """Check if service is available (API key is set)."""
        return bool(self.api_key and self.api_key.strip())
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to extract JSON from response text.
        Handles markdown code blocks and raw JSON.
        """
        import re
        
        # Try to find JSON in code blocks
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # ```json ... ```
            r'```\s*([\s\S]*?)\s*```',       # ``` ... ```
            r'\{[\s\S]*\}',                   # Raw JSON object
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    # Handle tuple from grouped patterns
                    if isinstance(match, tuple):
                        match = match[0]
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} service={self.SERVICE_NAME} model={self.config.model}>"
