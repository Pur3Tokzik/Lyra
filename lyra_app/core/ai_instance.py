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
    
    def is_valid_personality_type(self, personality_type: str) -> bool:
        """Check if the personality type is one of the supported types."""
        valid_types = ["friendly", "chill", "playful", "direct", "custom"]
        return personality_type.lower() in valid_types
    
    def get_personality_description(self) -> str:
        """Get descriptive text for the current personality type."""
        descriptions = {
            "friendly": "Warm, friendly and easy to talk to",
            "chill": "Calm, casual and relaxed",
            "playful": "Playful, energetic and always ready for a joke",
            "direct": "Honest, direct and straight to the point",
            "custom": "Custom personality defined by user"
        }
        return descriptions.get(self.selected_type.lower(), "Default personality")

class AIInstance:
    """Represents a single AI instance created by the user - core domain object."""
    
    def __init__(self, ai_name: str = "AI", memory_system: MemorySystem = None, model_interface: ModelInterface = None):
        self.ai_name = ai_name
        self.identity = Identity()
        self.personality = Personality()  
        self.memory_system = memory_system  # Injected from outside
        self.model_interface = model_interface  # Injected from outside
        self.creation_timestamp = datetime.now()
        # Journal integration - will be initialized during onboarding
        self.journal = None
        
    def initialize_journal(self, data_dir: str = "./journal_data"):
        """Initialize the journal system for this AI instance.
        
        Args:
            data_dir: Directory where journal data should be stored
        """
        try:
            # Lazy import to avoid circular dependencies
            from journal.journal import Journal
            self.journal = Journal(data_dir)
        except ImportError as e:
            print(f"Failed to initialize journal: {e}")
            self.journal = None
        
    def is_complete(self) -> bool:
        """Check if AI has complete onboarding state."""
        return (self.identity.created and 
                self.personality.selected_type is not None)
    
    def process_message(self, user_input: str) -> str:
        """Process a user message through the AI interaction lifecycle.
        
        Args:
            user_input (str): The user's message
            
        Returns:
            str: The AI's response
        """
        # Validate required dependencies
        if not self.model_interface:
            raise ValueError("AIInstance requires model_interface to process messages")
            
        if not self.memory_system:
            raise ValueError("AIInstance requires memory_system to process messages")
        
        # Get personality context from Brain (if available)
        personality_context = ""
        if hasattr(self, 'brain') and self.brain:
            try:
                personality_context = self.brain.get_personality_prompt()
            except Exception:
                # If brain is not available or has issues, proceed without personality context
                pass
        
        # Prepare conversation context
        conversation_context = ""
        
        # Add journal entry if available 
        if self.journal:
            try:
                # Add the user's message to the journal
                self.journal.add_conversation_entry(
                    conversation_id=f"conv_{len(self.journal.get_recent_entries(10))}", 
                    speaker="user", 
                    content=user_input
                )
            except Exception as e:
                # If journal fails, continue without logging this entry
                print(f"Warning: Failed to log user message to journal: {e}")
        
        # Retrieve relevant memory content
        try:
            # Get any recent memories for context
            memory_entries = self.memory_system.get_memories(category="conversation_history", limit=10)
            if memory_entries:
                # Convert MemoryEntry objects to text for prompt context
                memory_context_items = [f"- {entry.content}" for entry in memory_entries]
                conversation_context = f"Previous conversation context:\n" + "\n".join(memory_context_items) + "\n"
        except Exception as e:
            # If memory fails, continue without context
            print(f"Warning: Failed to retrieve memory context: {e}")
        
        # Combine all context for prompting
        full_prompt = f"{personality_context}\n{conversation_context}User: {user_input}"
        
        try:
            # Send request through model interface
            response = self.model_interface.process_message(full_prompt)
            
            # Extract content from ModelResponse
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Record AI's response in journal if available
            if self.journal and response_content:
                try:
                    self.journal.add_conversation_entry(
                        conversation_id=f"conv_{len(self.journal.get_recent_entries(10))}",
                        speaker="ai", 
                        content=response_content
                    )
                except Exception as e:
                    # If journal fails, continue without logging this response
                    print(f"Warning: Failed to log AI response to journal: {e}")
            
            return response_content
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            print(error_msg)
            return error_msg
    
    def __repr__(self):
        return f"AIInstance(name='{self.ai_name}', identity={self.identity.created}, personality={self.personality.selected_type})"