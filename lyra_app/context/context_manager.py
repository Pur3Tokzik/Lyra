"""Lyra 0.0.1 - Context Manager Implementation"""

from typing import List, Optional, Dict, Any
from context.context_state import ContextState
from context.interfaces import ContextBuilder, ContextManager as ContextManagerInterface

class BasicContextManager(ContextManagerInterface):
    """Basic implementation of context manager.
    
    This class handles the lifecycle of context creation and management,
    using a provided context builder to assemble context states.
    """
    
    def __init__(self, context_builder: ContextBuilder):
        """
        Initialize context manager with a builder.
        
        Args:
            context_builder: Builder to use for creating contexts
        """
        super().__init__(context_builder)
        self.context_builder = context_builder
        
    def create_context(self, 
                      conversation_id: str,
                      current_input: str,
                      recent_messages: List[Dict[str, Any]] = None) -> ContextState:
        """
        Create a new context state.
        
        Args:
            conversation_id: Unique conversation identifier
            current_input: Current user input text
            recent_messages: Recent conversation history
            
        Returns:
            New ContextState object with all components assembled
        """
        return self.context_builder.build_context(
            conversation_id=conversation_id,
            current_input=current_input,
            recent_messages=recent_messages
        )
