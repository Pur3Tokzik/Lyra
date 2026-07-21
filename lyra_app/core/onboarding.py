"""
Lyra 0.0.1 - Onboarding System 
Implements the complete Lyra onboarding process following ONBOARDING.MD requirements.
"""

from typing import Optional
from .ai_instance import AIInstance
from .persistence import PersistenceManager

class OnboardingSystem:
    """Manages the complete AI creation process with proper state handling."""
    
    def __init__(self):
        self.current_ai: Optional[AIInstance] = None
        self.persistence = PersistenceManager()
        
    def start_onboarding(self) -> AIInstance:
        """Begin the onboarding process and create initial AI instance."""
        # Create a new AI instance 
        self.current_ai = AIInstance()
        return self.current_ai
        
    def set_ai_name(self, name: str) -> None:
        """Set the AI's name."""
        if not self.current_ai:
            raise RuntimeError("Onboarding not started")
        self.current_ai.ai_name = name
        
    def set_user_identity_preference(self, preference: str) -> None:
        """Set how user wants to be addressed (this is part of identity configuration)."""
        if not self.current_ai:
            raise RuntimeError("Onboarding not started")
        # The identity is marked as complete when the name and user identity are set
        self.current_ai.identity.user_identity_preference = preference
        self.current_ai.identity.created = True  # Mark this specific aspect as established
        
    def set_personality(self, personality_type: str, custom_desc: Optional[str] = None) -> None:
        """Set AI personality."""
        if not self.current_ai:
            raise RuntimeError("Onboarding not started")
        self.current_ai.personality.selected_type = personality_type
        if custom_desc:
            self.current_ai.personality.custom_description = custom_desc
            
    def complete_onboarding(self) -> bool:
        """Finish the onboarding process and persist AI state."""
        if not self.current_ai or not self.current_ai.is_complete():
            raise RuntimeError("Incomplete onboarding")
            
        # Save the created AI
        return self.persistence.save_ai_instance(self.current_ai)
        
    def load_existing_ai(self) -> Optional[AIInstance]:
        """Load previously created AI instance.""" 
        ai = self.persistence.load_ai_instance()
        if ai:
            self.current_ai = ai
        return ai
        
    def get_current_ai(self) -> Optional[AIInstance]:
        """Get currently active AI instance."""
        return self.current_ai
