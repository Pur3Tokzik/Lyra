"""Lyra 0.0.1 - Memory Entities"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class Revision:
    """Represents a revision of a memory entry."""
    revision_id: str
    timestamp: datetime
    changes: dict
    author: Optional[str] = None

@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    content: str
    timestamp: datetime
    category: str = "general"
    importance: int = 0  # 1-10 scale
    
    # New fields for FASE 9 Foundation
    confidence: float = 1.0  # 0.0-1.0 scale
    source: str = ""  # Origin of the memory
    emotional_weight: int = 0  # 1-10 scale 
    memory_type: str = "general"  # Type of memory (fact, preference, relationship, etc.)
    lifecycle_status: str = "active"  # active, archived, deprecated
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    revision_history: List[Revision] = field(default_factory=list)