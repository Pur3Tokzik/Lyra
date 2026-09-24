"""
Lyra 0.0.1 - Decision Types

Enumeration of decision types supported by the cognitive decision engine.
"""

from enum import Enum

class DecisionType(Enum):
    """
    Types of decisions that can be made during AI processing.
    
    These represent high-level actions that the decision engine determines
    should be taken based on context and available information.
    """
    
    # Basic response decisions
    RESPOND = "respond"                    # Generate a standard text response
    
    # LLM interaction decisions  
    CALL_LLM = "call_llm"                  # Request processing from language model
    
    # Memory operations
    LOOKUP_MEMORY = "lookup_memory"        # Query memory system for information
    STORE_MEMORY = "store_memory"          # Save new information to memory
    
    # Interaction decisions
    ASK_CLARIFICATION = "ask_clarification" # Request more information from user
    CONTINUE_TASK = "continue_task"         # Continue with an ongoing task
    
    # System operations
    EXECUTE_ACTION = "execute_action"       # Execute a specific system action
    IGNORE = "ignore"                       # Skip processing entirely (no action)
    
    def __str__(self):
        return self.value
