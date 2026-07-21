"""Lyra 0.0.1 - Memory Entities"""

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