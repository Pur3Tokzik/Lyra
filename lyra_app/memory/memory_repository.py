"""Lyra 0.0.2 - Memory Repository Interface"""

from abc import ABC, abstractmethod
from typing import List, Optional
from lyra_app.memory.entities import MemoryEntry

class MemoryRepository(ABC):
    """Abstract interface for memory storage."""
    
    @abstractmethod
    def save_memory(self, entry: MemoryEntry) -> bool:
        """Save a single memory entry."""
        pass
    
    @abstractmethod
    def load_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load a single memory entry by ID."""
        pass
    
    @abstractmethod
    def query_memories(self, category: Optional[str] = None, 
                      limit: int = 100) -> List[MemoryEntry]:
        """Query memory entries with optional filtering."""
        pass
        
    @abstractmethod
    def save_all_memories(self, entries: List[MemoryEntry]) -> bool:
        """Save multiple memory entries at once."""
        pass
        
    @abstractmethod
    def clear_all_memories(self) -> bool:
        """Clear all memory entries."""
        pass

    @abstractmethod
    def delete_memory(self, entry_id: str) -> bool:
        """Delete a single memory entry by ID."""
        pass