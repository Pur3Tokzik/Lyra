"""
Lyra 0.0.1 - Brain System
Coordination system for AI operations - manages identity, personality, memory,
and prepares integration with model capabilities.
"""

from typing import Optional
from core.ai_instance import AIInstance

class Brain:
    """The coordinator for an AI instance operations."""
    
    def __init__(self):
        self.ai_instance: Optional[AIInstance] = None
        
    def initialize_ai(self, ai_instance: AIInstance) -> None:
        """Initialize the brain with a specific existing AI instance."""
        if not isinstance(ai_instance, AIInstance):
            raise TypeError("Must initialize with an AIInstance")
        self.ai_instance = ai_instance
        
    def get_identity(self) -> dict:
        """Get current identity state from the AI instance."""
        if not self.ai_instance or not self.ai_instance.identity:
            return {}
        return {
            "name": self.ai_instance.identity.name,
            "created": self.ai_instance.identity.created
        }
        
    def get_personality(self) -> dict:
        """Get current personality configuration."""
        if not self.ai_instance or not self.ai_instance.personality:
            return {}
        return {
            "selected_type": self.ai_instance.personality.selected_type,
            "custom_description": self.ai_instance.personality.custom_description
        }
        
    def get_state(self) -> dict:
        """Get complete AI state for coordination purposes."""
        if not self.ai_instance:
            return {}
        return {
            "identity": self.get_identity(),
            "personality": self.get_personality(),
            "name": self.ai_instance.ai_name
        }