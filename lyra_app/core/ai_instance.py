"""
Lyra 0.0.1 - AI Instance Core Model
Represents the user-created AI instance with identity, personality, memory.
This is a core domain model that represents the AI's persistent state.
"""

from datetime import datetime
from typing import Optional
from memory.memory_system import MemorySystem
from model.model_interface import ModelInterface

class Identity:
    """Represents the identity aspects of an AI."""
    
    def __init__(self):
        self.created = False
        self.user_identity_preference: Optional[str] = None  # What the user wants to be called
        
class Personality:
    """Represents personality configuration for an AI."""
    
    def __init__(self):
        self.selected_type: Optional[str] = None  # One of predefined types  
        self.custom_description: Optional[str] = None

class AIInstance:
    """Represents a single AI instance created by the user - core domain object."""
    
    def __init__(self, ai_name: str = "AI", memory_system: MemorySystem = None, model_interface: ModelInterface = None):
        self.ai_name = ai_name
        self.identity = Identity()
        self.personality = Personality()  
        self.memory_system = memory_system  # Injected from outside
        self.model_interface = model_interface  # Injected from outside
        self.creation_timestamp = datetime.now()
        
    def is_complete(self) -> bool:
        """Check if AI has complete onboarding state."""
        return (self.identity.created and 
                self.personality.selected_type is not None)
                
    def __repr__(self):
        return f"AIInstance(name='{self.ai_name}', identity={self.identity.created}, personality={self.personality.selected_type})"