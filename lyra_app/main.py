"""
Lyra 0.0.1 - Main Entry Point
First point of entry for the Lyra application.
"""

import os
from pathlib import Path
from core.lyra_factory import LyraFactory
from core.persistence import PersistenceManager
from core.onboarding import OnboardingFlow

def main():
    """Main entry point for Lyra application."""
    # Initialize persistence manager
    persistence_manager = PersistenceManager()
    
    # Check if a saved AI instance exists
    saved_ai = persistence_manager.load_ai_instance()
    
    if saved_ai:
        print("Lyra started (loaded from persistent storage).")
        lyra = saved_ai
    else:
        # Create a new Lyra instance using the factory  
        print("Lyra started (new instance).")
        lyra = LyraFactory.create_lyra_instance()
        
        # Start onboarding process
        print("Starting onboarding...")
        lyra = OnboardingFlow.start_onboarding(lyra)
        
        # Complete onboarding and save
        success = OnboardingFlow.complete_onboarding(lyra)
        if success:
            print("Onboarding completed and state saved.")
        else:
            print("Warning: Failed to save onboarding state.")
    
    # Print basic information about the instance
    print(f"Name: {lyra.ai_name}")
    print(f"Memory system: {'connected' if lyra.memory_system else 'not configured'}")
    print(f"Model provider: {'configured' if lyra.model_interface else 'not configured'}")
    print(f"Identity created: {lyra.identity.created}")
    print(f"Personality selected: {lyra.personality.selected_type}")

if __name__ == "__main__":
    main()