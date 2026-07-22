"""Lyra 0.0.1 - Memory API Interfaces"""

from typing import List, Optional
from memory.entities import MemoryEntry
from memory.graph_entities import MemoryRelation

class MemoryAPI:
    """Foundation interface for memory operations."""
    
    def create_memory(self, content: str, category: str = "general", 
                     importance: int = 0, source: str = "", 
                     memory_type: str = "general") -> str:
        """
        Create a new memory entry.
        
        Args:
            content: The memory content
            category: Memory category  
            importance: Importance level (1-10)
            source: Origin of the memory
            memory_type: Type classification
            
        Returns:
            Memory ID string
        """
        raise NotImplementedError
    
    def update_memory(self, entry_id: str, content: Optional[str] = None,
                     category: Optional[str] = None, importance: Optional[int] = None,
                     source: Optional[str] = None, memory_type: Optional[str] = None) -> bool:
        """
        Update an existing memory entry.
        
        Args:
            entry_id: Memory ID to update
            content: New content (optional)
            category: New category (optional)
            importance: New importance (optional)
            source: New source (optional)
            memory_type: New type (optional)
            
        Returns:
            True if successful
        """
        raise NotImplementedError
    
    def link_memory(self, source_id: str, target_id: str, 
                   relation_type: str, weight: float = 1.0,
                   metadata: Optional[dict] = None) -> bool:
        """
        Create a relationship between two memories.
        
        Args:
            source_id: Source memory ID
            target_id: Target memory ID  
            relation_type: Type of relationship
            weight: Relationship strength (0.0-1.0)
            metadata: Additional relationship data
            
        Returns:
            True if successful
        """
        raise NotImplementedError
    
    def retrieve_context(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """
        Retrieve relevant memories for context.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching memory entries
        """
        raise NotImplementedError
    
    def search_memory(self, query: str, category: Optional[str] = None,
                     min_confidence: float = 0.0, 
                     memory_type: Optional[str] = None) -> List[MemoryEntry]:
        """
        Search for memories matching criteria.
        
        Args:
            query: Search term
            category: Filter by category
            min_confidence: Minimum confidence level
            memory_type: Filter by memory type
            
        Returns:
            List of matching memory entries
        """
        raise NotImplementedError

# Memory system interface that will be implemented in memory_system.py
class MemorySystemAPI(MemoryAPI):
    """Extended interface for complete memory system operations."""
    
    def get_memory_history(self, entry_id: str) -> List[MemoryEntry]:
        """Get revision history for a memory entry."""
        raise NotImplementedError
        
    def rollback_memory(self, entry_id: str, revision_id: str) -> bool:
        """Revert to a specific revision of a memory."""
        raise NotImplementedError
        
    def get_related_memories(self, entry_id: str, relation_type: Optional[str] = None) -> List[MemoryEntry]:
        """Get memories related to the given memory."""
        raise NotImplementedError