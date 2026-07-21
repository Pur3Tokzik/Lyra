"""
Lyra 0.0.1 - Model Provider Interface
Abstract interface for model providers (e.g., Ollama, local LLMs).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from model.entities import ModelResponse

class ModelProvider(ABC):
    """Abstract provider interface for different model backends.
    
    This allows future implementation of Ollama, local LLMs, etc.
    without coupling to specific implementations.
    """
    
    @abstractmethod
    def generate(self, message: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Generate a response from the model.
        
        Args:
            message: The input message to process
            context: Additional context for processing
            
        Returns:
            ModelResponse containing the generated output
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model provider is available and ready to use.
        
        Returns:
            True if provider is available, False otherwise
        """
        pass