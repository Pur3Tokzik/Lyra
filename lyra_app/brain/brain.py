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
            "name": self.ai_instance.ai_name,
            "created": self.ai_instance.identity.created,
            "user_identity_preference": self.ai_instance.identity.user_identity_preference
        }
        
    def get_personality(self) -> dict:
        """Get current personality configuration."""
        if not self.ai_instance or not self.ai_instance.personality:
            return {}
        return {
            "selected_type": self.ai_instance.personality.selected_type,
            "custom_description": self.ai_instance.personality.custom_description,
            "description": self.ai_instance.personality.get_personality_description()
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
    
    def set_personality(self, personality_type: str, custom_description: Optional[str] = None) -> bool:
        """Set the personality for this AI instance.
        
        Args:
            personality_type: The type of personality to set
            custom_description: Optional custom description for 'custom' personality
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ai_instance:
            return False
            
        # Validate personality type
        if not self.ai_instance.personality.is_valid_personality_type(personality_type):
            return False
            
        self.ai_instance.personality.selected_type = personality_type.lower()
        self.ai_instance.personality.custom_description = custom_description
        
        return True

    def get_personality_prompt(self) -> str:
        """Get the personality prompt that can be used when communicating with model.
        
        Returns:
            String containing personality guidelines for AI responses
        """
        if not self.ai_instance or not self.ai_instance.personality.selected_type:
            return "You are a helpful AI assistant."
            
        personality = self.ai_instance.personality.selected_type.lower()
        custom_desc = self.ai_instance.personality.custom_description
        
        prompts = {
            "friendly": "You are warm and friendly when responding. Always be kind, approachable, and easy to talk to.",
            "chill": "You are calm and relaxed in your responses. Keep it casual and comfortable, but remain helpful.",
            "playful": "You are energetic and playful in your responses. Feel free to add humor, jokes, or fun elements, while staying helpful.",
            "direct": "You provide honest, direct answers with clarity. Be succinct, straightforward, and to the point.",
            "custom": f"You follow custom instructions: {custom_desc}" if custom_desc else "You are a helpful AI assistant with a custom personality."
        }
        
        return prompts.get(personality, prompts["friendly"])