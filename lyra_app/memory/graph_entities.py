"""Lyra 0.0.1 - Memory Graph Entities"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass
class MemoryNode:
    """Represents a node in the memory graph - a memory entry."""
    memory_id: str
    timestamp: datetime
    content: str
    type: str  # The memory_type classification 
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class MemoryRelation:
    """Represents a relationship between two memories in the graph."""
    relation_id: str
    source_memory_id: str
    target_memory_id: str
    relation_type: str  # causal, temporal, emotional, semantic, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    weight: float = 1.0  # 0.0-1.0 scale
    metadata: Optional[dict] = None

# Memory relationship types
RELATION_TYPES = {
    "causal": "Causal relationship",
    "temporal": "Temporal sequence", 
    "emotional": "Emotional connection",
    "semantic": "Semantic similarity or meaning",
    "ontological": "Ontological relationship (is-a, part-of)",
    "contextual": "Contextual relevance"
}