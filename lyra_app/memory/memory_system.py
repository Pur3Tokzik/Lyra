"""
Lyra 0.0.1 - Memory System
Memory abstraction layer that belongs to AI Instance, not Brain.
Prepared for local persistence as specified in REQUIREMENTS.md.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    content: str
    timestamp: datetime
    category: str = "general"
    importance: int = 0  # 1-10 scale

class MemorySystem:
    """Memory abstraction layer for AI instances.
    
    Memory belongs to AI Instance, not Brain. This system
    coordinates access and prepares interface for persistence.
    """
    
    def __init__(self):
        self._memories: List[MemoryEntry] = []
        self._is_initialized = False
        
    def initialize_from_ai_instance(self, ai_instance_data: Dict[str, Any]) -> None:
        """Initialize memory system from AI instance data structure."""
        # Memory belongs to the AI Instance, not the brain
        # This method prepares interface for persistence integration
        if 'memories' in ai_instance_data:
            # This would integrate with actual persistence layer later  
            self._memories = ai_instance_data['memories']
        self._is_initialized = True
        
    def add_memory(self, content: str, category: str = "general", importance: int = 0) -> str:
        """Add a memory entry to AI instance memory.
        
        Returns:
            str: Memory entry ID
        """
        if not self._is_initialized:
            raise RuntimeError("MemorySystem must be initialized before use")
            
        entry_id = f"mem_{len(self._memories) + 1}"
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            timestamp=datetime.now(),
            category=category,
            importance=importance
        )
        self._memories.append(entry)
        return entry_id
        
    def get_memories(self, category: Optional[str] = None, limit: int = 100) -> List[MemoryEntry]:
        """Retrieve memory entries, optionally filtered by category."""
        if not self._is_initialized:
            return []
            
        if category:
            return [m for m in self._memories if m.category == category][:limit]
        return self._memories[:limit]
        
    def get_memory_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific memory entry by ID."""
        if not self._is_initialized:
            return None
        return next((m for m in self._memories if m.id == entry_id), None)
        
    def save_to_persistence(self) -> bool:
        """Prepare memory for persistence - placeholder for actual implementation.
        
        This method would coordinate with persistence layer as required by REQUIREMENTS.md
        """
        # This is where actual persistence logic would go  
        # For now, it's a coordination point for future integration
        return True
        
    def load_from_persistence(self) -> bool:
        """Load memory from persistence - placeholder for actual implementation.
        
        This method would coordinate with persistence layer as required by REQUIREMENTS.md
        """
        # This is where loading logic would go 
        # For now, it's a coordination point for future integration
        return True
        
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage."""
        if not self._is_initialized:
            return {}
            
        categories = [m.category for m in self._memories]
        return {
            "total_memories": len(self._memories),
            "categories": list(set(categories)),
            "oldest_memory": min([m.timestamp for m in self._memories]) if self._memories else None,
            "newest_memory": max([m.timestamp for m in self._memories]) if self._memories else None
        }