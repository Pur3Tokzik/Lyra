"""
Lyra 0.0.1 - Onboarding Flow
Handles the user onboarding process for Lyra instances.
"""

from .persistence import PersistenceManager
from .lyra_factory import LyraFactory
from .ai_instance import AIInstance

class OnboardingFlow:
    """Manages the onboarding process for Lyra AI instances."""
    
    @staticmethod
    def start_onboarding(ai_instance: AIInstance) -> AIInstance:
        """Start the onboarding process for a given AI instance.
        
        Args:
            ai_instance: The AI instance to onboard
            
        Returns:
            The AI instance with onboarding completed
        """
        # In a real implementation, this would guide the user through:
        # 1. Identity setup (name, user identity preference)
        # 2. Personality selection  
        # 3. Model provider configuration (if needed)
        
        # For now, we'll simulate a basic onboarding completion with proper personality selection
        ai_instance.identity.created = True
        print("Starting personality selection process...")
        print("Available personality types:")
        print("1. Friendly - Warm, friendly and easy to talk to")
        print("2. Chill - Calm, casual and relaxed") 
        print("3. Playful - Playful, energetic and always ready for a joke")
        print("4. Direct - Honest, direct and straight to the point")
        print("5. Custom - Define your own personality")
        
        # For this implementation, we'll set a default personality for demo purposes
        ai_instance.personality.selected_type = "friendly"
        print(f"Selected personality: {ai_instance.personality.selected_type}")
        
        # Initialize journal during onboarding (this ensures it's available when needed)
        ai_instance.initialize_journal()
        
        # Create initial event 
        if ai_instance.journal:
            try:
                ai_instance.journal.add_important_event(
                    "creation",
                    "AI instance created"
                )
            except Exception:
                pass  # If journal logging fails, continue
        
        return ai_instance
    
    @staticmethod
    def complete_onboarding(ai_instance: AIInstance) -> bool:
        """Complete the onboarding process and save state.
        
        Args:
            ai_instance: The AI instance to complete onboarding for
            
        Returns:
            True if successful, False otherwise
        """
        # Save the completed onboarding state (this was already implemented)
        persistence_manager = PersistenceManager()
        success = persistence_manager.save_ai_instance(ai_instance)
        
        if success and ai_instance.journal:
            # Register the completion event in the journal if available
            try:
                ai_instance.journal.add_important_event(
                    "onboarding_completed",
                    "Onboarding process completed"
                )
            except Exception:
                pass  # If journal logging fails, continue
        
        return success

    @staticmethod
    def is_onboarding_complete(ai_instance: AIInstance) -> bool:
        """Check if onboarding is complete for the given instance.
        
        Args:
            ai_instance: The AI instance to check
            
        Returns:
            True if onboarding is complete, False otherwise
        """
        return ai_instance.is_complete()
