"""Lyra 0.0.1 - Memory Graph Infrastructure"""

from typing import Dict, List, Optional
from memory.graph_entities import MemoryNode, MemoryRelation

class MemoryGraph:
    """Base infrastructure for managing memory relationships."""
    
    def __init__(self):
        self.nodes: Dict[str, MemoryNode] = {}  # memory_id -> node
        self.edges: Dict[str, MemoryRelation] = {}  # relation_id -> relation
        self.node_relations: Dict[str, List[str]] = {}  # memory_id -> list of relation_ids
        
    def add_node(self, node: MemoryNode) -> bool:
        """Add a memory node to the graph."""
        if node.memory_id in self.nodes:
            return False
        self.nodes[node.memory_id] = node
        return True
    
    def get_node(self, memory_id: str) -> Optional[MemoryNode]:
        """Retrieve a memory node by ID."""
        return self.nodes.get(memory_id)
    
    def add_relation(self, relation: MemoryRelation) -> bool:
        """Add a relationship between memories."""
        if relation.relation_id in self.edges:
            return False
        
        self.edges[relation.relation_id] = relation
        
        # Update node relations tracking
        if relation.source_memory_id not in self.node_relations:
            self.node_relations[relation.source_memory_id] = []
        self.node_relations[relation.source_memory_id].append(relation.relation_id)
        
        return True
    
    def get_relations_for_node(self, memory_id: str) -> List[MemoryRelation]:
        """Get all relations connected to a specific memory."""
        relation_ids = self.node_relations.get(memory_id, [])
        return [self.edges[rid] for rid in relation_ids if rid in self.edges]
    
    def get_related_nodes(self, memory_id: str) -> List[MemoryNode]:
        """Get all nodes connected to a specific memory."""
        relations = self.get_relations_for_node(memory_id)
        target_ids = [r.target_memory_id for r in relations]
        return [self.nodes[mid] for mid in target_ids if mid in self.nodes]

    def is_connected(self, source_id: str, target_id: str) -> bool:
        """Check if two memories are connected."""
        # Simple implementation - more complex traversal can be added later
        relations = self.get_relations_for_node(source_id)
        return any(r.target_memory_id == target_id for r in relations)