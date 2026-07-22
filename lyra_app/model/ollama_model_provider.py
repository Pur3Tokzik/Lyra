"""
Lyra 0.0.1 - Ollama Model Provider
Concrete implementation of ModelInterface for communication with local Ollama models.
"""

import requests
import json
from typing import Dict, Any, Optional
from model.model_interface import ModelInterface
from model.entities import ModelResponse

class OllamaModelProvider(ModelInterface):
    """Concrete implementation of ModelInterface that communicates with Ollama backend."""
    
    def __init__(self, model_name: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama model provider.
        
        Args:
            model_name: Name of the Ollama model to use (default: llama3)
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.model_name = model_name
        self.base_url = base_url
        self._available = False
        self._health_check()
    
    def _health_check(self) -> None:
        """Check if Ollama backend is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self._available = response.status_code == 200
        except:
            self._available = False
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """
        Send a message to the Ollama model and receive a response.
        
        Args:
            message: The input message to send to the model
            context: Additional context for processing (optional)
            
        Returns:
            ModelResponse containing the response and metadata
        """
        if not self._available:
            raise RuntimeError("Ollama backend is not available")
        
        # Prepare request payload  
        payload = {
            "model": self.model_name,
            "prompt": message,
            "stream": False
        }
        
        # Add context if provided (can be extended as needed)
        if context:
            payload["context"] = context
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return ModelResponse(
                    content=result.get("response", ""),
                    metadata={
                        "model": self.model_name,
                        "status": "success",
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0)
                    }
                )
            else:
                raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Network error communicating with Ollama: {str(e)}")
    
    def configure_model(self, model_name: str, parameters: Dict[str, Any]) -> bool:
        """
        Configure the model settings.
        
        Args:
            model_name: Name of the model to use
            parameters: Configuration parameters
            
        Returns:
            True if configuration was successful
        """
        self.model_name = model_name
        # In a real implementation, this might update model parameters
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "backend": "Ollama",
            "available": self._available,
            "base_url": self.base_url
        }
    
    def is_model_available(self) -> bool:
        """
        Check if the model backend is available.
        
        Returns:
            True if model backend is ready for use
        """
        return self._available

# For backward compatibility and clear naming
OllamaModelInterface = OllamaModelProvider