"""
Lyra 0.0.1 - File-based Memory Repository
Concrete implementation of MemoryRepository using local JSON file storage.
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from memory.memory_repository import MemoryRepository
from memory.entities import MemoryEntry

class FileMemoryRepository(MemoryRepository):
    """File-based implementation of MemoryRepository using local JSON storage."""
    
    def __init__(self, file_path: str = "memory.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(exist_ok=True)
        # Ensure the file exists
        if not self.file_path.exists():
            self._save_entries([])
    
    def save_memory(self, entry: MemoryEntry) -> bool:
        """Save a single memory entry to storage."""
        try:
            entries = self._load_entries()
            entries.append(entry)
            self._save_entries(entries)
            return True
        except Exception:
            return False
    
    def load_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load a single memory entry by ID."""
        try:
            entries = self._load_entries()
            for entry in entries:
                if entry.uuid == entry_id:
                    return entry
            return None
        except Exception:
            return None
    
    def query_memories(self, category: Optional[str] = None, 
                      limit: int = 100) -> List[MemoryEntry]:
        """Query memory entries with optional filtering."""
        try:
            entries = self._load_entries()
            if category:
                entries = [e for e in entries if e.category == category]
            return entries[-limit:]  # Return latest entries first
        except Exception:
            return []
    
    def save_all_memories(self, entries: List[MemoryEntry]) -> bool:
        """Save multiple memory entries at once."""
        try:
            self._save_entries(entries)
            return True
        except Exception:
            return False
    
    def clear_all_memories(self) -> bool:
        """Clear all memory entries."""
        try:
            self._save_entries([])
            return True
        except Exception:
            return False
    
    def _load_entries(self) -> List[MemoryEntry]:
        """Load memory entries from file."""
        if not self.file_path.exists():
            return []
        
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        
        # Convert dict back to MemoryEntry objects
        entries = []
        for entry_data in data:
            entry = MemoryEntry(
                uuid=entry_data['uuid'],
                content=entry_data['content'],
                category=entry_data['category'],
                timestamp=entry_data['timestamp']
            )
            entries.append(entry)
        
        return entries
    
    def _save_entries(self, entries: List[MemoryEntry]) -> None:
        """Save memory entries to file."""
        # Convert MemoryEntry objects to dict for JSON serialization
        data = []
        for entry in entries:
            entry_dict = {
                'uuid': entry.uuid,
                'content': entry.content,
                'category': entry.category,
                'timestamp': entry.timestamp
            }
            data.append(entry_dict)
        
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)