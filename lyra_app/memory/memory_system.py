"""
Lyra 0.0.2 - Memory System
Memory abstraction layer that belongs to AI Instance, not Brain.
Prepared for local persistence as specified in REQUIREMENTS.md.
"""

import re
import unicodedata
from typing import List, Optional

from lyra_app.memory.entities import MemoryEntry, Revision
from lyra_app.memory.memory_repository import MemoryRepository
from lyra_app.memory.memory_graph import MemoryGraph
from lyra_app.memory.graph_entities import MemoryRelation
from datetime import datetime
import uuid

_WORD = re.compile(r"[^\W_]+", re.UNICODE)

# Language-independent retrieval: fold PT and EN words onto one concept so a
# Portuguese question can match a key written in English.
_SYNONYMS: dict[str, set[str]] = {
    "name": {"nome", "chamo", "chamas", "chamar", "name", "called"},
    "birthday": {"aniversario", "birthday", "nascimento"},
    "location": {"morada", "cidade", "vivo", "moro", "onde", "location", "live", "address", "city"},
    "likes": {"gosto", "gosta", "adoro", "likes", "like", "love"},
}
_TOKEN_TO_CONCEPT = {token: concept for concept, tokens in _SYNONYMS.items() for token in tokens}


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def _tokens(text: str) -> list[str]:
    return _WORD.findall(_fold(text))


def _expand(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        concept = _TOKEN_TO_CONCEPT.get(token)
        if concept:
            expanded |= _SYNONYMS[concept]
    return expanded

class MemorySystem:
    """Memory abstraction layer for AI instances.
    
    Memory belongs to AI Instance, not Brain. This system
    coordinates access and prepares interface for persistence.
    """
    
    def __init__(self, repository: MemoryRepository):
        self.repository = repository
        self.graph = MemoryGraph()  # Initialize graph infrastructure
        self._rebuild_graph()

    def _rebuild_graph(self) -> None:
        """Rebuild the in-memory graph from the repository on load."""
        try:
            for entry in self.repository.query_memories(limit=100000):
                self.graph.add_node(self._create_node_from_entry(entry))
        except Exception:
            # A broken graph must never prevent the companion from loading.
            pass
        
    def add_memory(self, content: str, category: str = "general", 
                  importance: int = 0, source: str = "", 
                  memory_type: str = "general") -> str:
        """Add a memory entry to AI instance memory.
        
        Delegates to repository for actual storage.
        
        Returns:
            str: Memory entry ID
        """
        entry_id = f"mem_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"  # Unique ID with UUID suffix
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            timestamp=datetime.now(),
            category=category,
            importance=importance,
            source=source,
            memory_type=memory_type,
            confidence=1.0
        )
        
        # Add initial node to graph
        node = self._create_node_from_entry(entry)
        self.graph.add_node(node)
        
        self.repository.save_memory(entry)
        return entry_id
        
    def get_memories(self, category: Optional[str] = None, limit: int = 100) -> List[MemoryEntry]:
        """Retrieve memory entries, optionally filtered by category."""
        return self.repository.query_memories(category=category, limit=limit)

    # -- key/value facts ------------------------------------------------

    def remember_fact(self, key: str, value: str, importance: int = 8) -> str:
        """Store a stable fact under a key, replacing any previous value."""
        for entry in self.repository.query_memories(category="fact", limit=100000):
            if entry.source == key:
                self.repository.delete_memory(entry.id)
        return self.add_memory(
            content=value,
            category="fact",
            importance=importance,
            source=key,
            memory_type="fact",
        )

    def get_fact(self, key: str) -> Optional[MemoryEntry]:
        """Return the fact stored under ``key``, if any."""
        for entry in self.repository.query_memories(category="fact", limit=100000):
            if entry.source == key:
                return entry
        return None

    def forget(self, key: str) -> bool:
        """Delete the fact stored under ``key``. Returns True if it existed."""
        found = False
        for entry in self.repository.query_memories(category="fact", limit=100000):
            if entry.source == key:
                self.repository.delete_memory(entry.id)
                self.graph.nodes.pop(entry.id, None)
                found = True
        return found

    def retrieve(self, query: str, limit: int = 3) -> List[MemoryEntry]:
        """Rank memories by keyword overlap, importance and recency."""
        query_tokens = _expand(set(_tokens(query)))
        if not query_tokens:
            return []
        now = datetime.now()
        scored: list[tuple[float, MemoryEntry]] = []
        for entry in self.repository.query_memories(limit=100000):
            entry_tokens = _expand(set(_tokens(entry.source) + _tokens(entry.content)))
            overlap = len(query_tokens & entry_tokens)
            if overlap == 0:
                continue
            recency = 1.0 / (1.0 + (now - entry.updated_at).total_seconds() / 86400.0)
            score = overlap + (entry.importance / 10.0) + 0.3 * recency
            scored.append((score, entry))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    # -- MemoryRetriever interface (used by the context layer) ----------

    def retrieve_relevant_memories(self, query: str, category: Optional[str] = None,
                                   limit: int = 10) -> List[MemoryEntry]:
        return self.retrieve(query, limit=limit)

    def search_with_context(self, context_state) -> List[MemoryEntry]:
        return self.retrieve(getattr(context_state, "current_input", ""), limit=10)
        
    def get_memory_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve specific memory entry by ID."""
        return self.repository.load_memory(entry_id)
    
    def update_memory(self, entry_id: str, content: Optional[str] = None,
                     category: Optional[str] = None, importance: Optional[int] = None,
                     source: Optional[str] = None, memory_type: Optional[str] = None) -> bool:
        """Update an existing memory entry."""
        # Load current entry
        entry = self.repository.load_memory(entry_id)
        if not entry:
            return False
        
        # Track changes in revision history
        changes = {}
        
        if content is not None and content != entry.content:
            changes['content'] = entry.content
            entry.content = content
            
        if category is not None and category != entry.category:
            changes['category'] = entry.category
            entry.category = category
            
        if importance is not None and importance != entry.importance:
            changes['importance'] = entry.importance
            entry.importance = importance
            
        if source is not None and source != entry.source:
            changes['source'] = entry.source
            entry.source = source
            
        if memory_type is not None and memory_type != entry.memory_type:
            changes['memory_type'] = entry.memory_type
            entry.memory_type = memory_type
        
        # Update timestamps and revision history if there were changes
        if changes:
            entry.updated_at = datetime.now()
            
            # Create revision record
            revision_id = f"rev_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
            revision = Revision(
                revision_id=revision_id,
                timestamp=datetime.now(),
                changes=changes
            )
            entry.revision_history.append(revision)
            
            # Update node in graph  
            node = self._create_node_from_entry(entry)
            self.graph.add_node(node)
        
        # Save updated memory
        return self.repository.save_memory(entry)
    
    def _create_node_from_entry(self, entry: MemoryEntry) -> 'MemoryNode':
        """Create a memory node from a memory entry for graph."""
        from lyra_app.memory.graph_entities import MemoryNode
        return MemoryNode(
            memory_id=entry.id,
            timestamp=entry.timestamp,
            content=entry.content,
            type=entry.memory_type,
            created_at=entry.created_at,
            updated_at=entry.updated_at
        )
    
    def link_memory(self, source_id: str, target_id: str, 
                   relation_type: str, weight: float = 1.0,
                   metadata: Optional[dict] = None) -> bool:
        """Create a relationship between two memories."""
        # Verify both memories exist
        source_entry = self.repository.load_memory(source_id)
        target_entry = self.repository.load_memory(target_id)
        
        if not (source_entry and target_entry):
            return False
            
        # Create relation
        relation_id = f"rel_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:6]}"
        relation = MemoryRelation(
            relation_id=relation_id,
            source_memory_id=source_id,
            target_memory_id=target_id,
            relation_type=relation_type,
            weight=weight,
            metadata=metadata
        )
        
        # Add to graph
        return self.graph.add_relation(relation)
    
    def get_memory_history(self, entry_id: str) -> List[Revision]:
        """Get revision history for a memory entry."""
        entry = self.repository.load_memory(entry_id)
        if entry:
            return entry.revision_history
        return []
    
    def get_related_memories(self, entry_id: str, relation_type: Optional[str] = None) -> List[MemoryEntry]:  
        """Get memories related to the given memory."""
        # Get related node IDs from graph
        related_nodes = self.graph.get_related_nodes(entry_id)
        
        # Convert back to memory entries
        related_entries = []
        for node in related_nodes:
            if relation_type is None or self._get_relation_type_for_node(entry_id, node.memory_id) == relation_type:
                entry = self.repository.load_memory(node.memory_id)
                if entry:
                    related_entries.append(entry)
        
        return related_entries
    
    def _get_relation_type_for_node(self, source_id: str, target_id: str) -> Optional[str]:
        """Get relation type for a specific node connection."""
        relations = self.graph.get_relations_for_node(source_id)
        for relation in relations:
            if relation.target_memory_id == target_id:
                return relation.relation_type
        return None