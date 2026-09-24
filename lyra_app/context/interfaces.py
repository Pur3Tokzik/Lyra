"""Lyra 0.0.1 - Context Intelligence Layer Interfaces"""

from typing import List, Optional, Dict, Any
from memory.entities import MemoryEntry
from context.context_state import ContextState

class MemoryRetriever:
    """Abstract interface for memory retrieval systems.
    
    This abstraction allows the context layer to query memories 
    without knowing具体的存储实现细节 (specific storage implementation details).
    """
    
    def retrieve_relevant_memories(self, query: str, 
                                 category: Optional[str] = None,
                                 limit: int = 10) -> List[MemoryEntry]:
        """Retrieve memories relevant to the given query.
        
        Args:
            query: Search query for memory retrieval
            category: Filter by memory category (optional)
            limit: Maximum number of results to return
            
        Returns:
            List of MemoryEntry objects that match the query
        """
        raise NotImplementedError("Subclasses must implement retrieve_relevant_memories")
    
    def search_with_context(self, context_state: ContextState) -> List[MemoryEntry]:
        """Search memories based on current context state.
        
        Args:
            context_state: Current context to search within
            
        Returns:
            List of relevant MemoryEntry objects
        """
        raise NotImplementedError("Subclasses must implement search_with_context")

class ContextBuilder:
    """Abstract interface for building context from inputs and memories."""
    
    def build_context(self, 
                     conversation_id: str,
                     current_input: str,
                     recent_messages: List[Dict[str, Any]] = None,
                     memory_retriever: Optional[MemoryRetriever] = None) -> ContextState:
        """Build a complete context state from inputs.
        
        Args:
            conversation_id: Unique conversation identifier
            current_input: Current user input text 
            recent_messages: Recent conversation history
            memory_retriever: Memory system for retrieving relevant memories
            
        Returns:
            Complete ContextState object with all components assembled
        """
        raise NotImplementedError("Subclasses must implement build_context")

class ContextManager:
    """Interface for managing context lifecycle."""
    
    def __init__(self, context_builder: ContextBuilder):
        """Initialize context manager with a builder.
        
        Args:
            context_builder: Builder to use for creating contexts
        """
        self.context_builder = context_builder
    
    def create_context(self, 
                      conversation_id: str,
                      current_input: str,
                      recent_messages: List[Dict[str, Any]] = None) -> ContextState:
        """Create a new context state.
        
        Args:
            conversation_id: Unique conversation identifier
            current_input: Current user input text
            recent_messages: Recent conversation history
            
        Returns:
            New ContextState object
        """
        raise NotImplementedError("Subclasses must implement create_context")
