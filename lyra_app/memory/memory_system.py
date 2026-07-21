"""
Lyra 0.0.1 - Memory System
Memory abstraction layer that belongs to AI Instance, not Brain.
Prepared for local persistence as specified in REQUIREMENTS.md.
"""

from typing import List, Optional
from memory.entities import MemoryEntry
from memory.memory_repository import MemoryRepository
from datetime import datetime

class MemorySystem:
    """Memory abstraction layer for AI instances.
    
    Memory belongs to AI Instance, not Brain. This system
    coordinates access and prepares interface for persistence.
    """
    
    def __init__(self, repository: MemoryRepository):
        self.repository = repository
        
    def add_memory(self, content: str, category: str = "general", importance: int = 0) -> str:
        """Add a memory entry to AI instance memory.
        
        Delegates to repository for actual storage.
        
        Returns:
            str: Memory entry ID
        """
        entry_id = f"mem_{int(datetime.now().timestamp())}"  # Simple unique ID
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            timestamp=datetime.now(),
            category=category,
            importance=importance
        )
        self.repository.save_memory(entry)
        return entry_id
        
    def get_memories(self, category: Optional[str] = None, limit: int = 100) -> List[MemoryEntry]:
        """Retrieve memory entries, optionally filtered by category."""
        return self.repository.query_memories(category=category, limit=limit)
        
    def get_memory_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific memory entry by ID."""
        return self.repository.load_memory(entry_id)