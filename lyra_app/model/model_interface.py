"""
Lyra 0.0.1 - Model Interface
Abstract interface for communication with local language models.
Prepared for integration with Ollama and other local model providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from model.entities import ModelResponse

class ModelInterface(ABC):
    """Abstract interface for communication with local language models.
    
    This interface prepares integration with Ollama and other local model providers
    without containing specific implementation details.
    """
    
    @abstractmethod
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Send a message to the model and receive a response.
        
        Args:
            message: The input message to send to the model
            context: Additional context for processing
            
        Returns:
            ModelResponse containing the response and metadata
        """
        pass
    
    @abstractmethod
    def configure_model(self, model_name: str, parameters: Dict[str, Any]) -> bool:
        """Configure the model settings.
        
        Args:
            model_name: Name of the model to use
            parameters: Configuration parameters
            
        Returns:
            True if configuration was successful
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        pass
    
    @abstractmethod
    def is_model_available(self) -> bool:
        """Check if the model backend is available.
        
        Returns:
            True if model backend is ready for use
        """
        pass