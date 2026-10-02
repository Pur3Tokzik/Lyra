"""
Lyra 0.0.2 - File-based Memory Repository
Concrete implementation of MemoryRepository using local JSON file storage.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from lyra_app.memory.memory_repository import MemoryRepository
from lyra_app.memory.entities import MemoryEntry

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
            # Remove existing entry with same ID
            entries = [e for e in entries if e.id != entry.id]
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
                if entry.id == entry_id:
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

    def delete_memory(self, entry_id: str) -> bool:
        """Delete a single memory entry by ID."""
        try:
            entries = [e for e in self._load_entries() if e.id != entry_id]
            self._save_entries(entries)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _parse_dt(value, fallback: datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return fallback
        return fallback

    def _load_entries(self) -> List[MemoryEntry]:
        """Load memory entries from file."""
        if not self.file_path.exists():
            return []

        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Support both a bare list and the versioned envelope.
        if isinstance(data, dict):
            data = data.get('memories', [])

        # Convert dict back to MemoryEntry objects
        entries = []
        for entry_data in data:
            now = datetime.now()
            try:
                entry = MemoryEntry(
                    id=entry_data.get('id', entry_data.get('uuid', '')),
                    content=entry_data['content'],
                    timestamp=self._parse_dt(entry_data.get('timestamp'), now),
                    category=entry_data.get('category', 'general'),
                    importance=entry_data.get('importance', 0),
                    confidence=entry_data.get('confidence', 1.0),
                    source=entry_data.get('source', ''),
                    emotional_weight=entry_data.get('emotional_weight', 0),
                    memory_type=entry_data.get('memory_type', 'general'),
                    lifecycle_status=entry_data.get('lifecycle_status', 'active'),
                    created_at=self._parse_dt(entry_data.get('created_at'), now),
                    updated_at=self._parse_dt(entry_data.get('updated_at'), now)
                )
            except Exception:
                # Fallback to basic MemoryEntry if something goes wrong
                entry = MemoryEntry(
                    id=entry_data.get('id', entry_data.get('uuid', '')),
                    content=entry_data['content'],
                    timestamp=self._parse_dt(entry_data.get('timestamp'), datetime.now())
                )
            entries.append(entry)

        return entries
    
    def _save_entries(self, entries: List[MemoryEntry]) -> None:
        """Save memory entries to file."""
        # Convert MemoryEntry objects to dict for JSON serialization
        data = []
        for entry in entries:
            entry_dict = {
                'id': entry.id,
                'content': entry.content,
                'timestamp': entry.timestamp.isoformat() if hasattr(entry.timestamp, 'isoformat') else str(entry.timestamp),
                'category': entry.category,
                'importance': entry.importance,
                'confidence': entry.confidence,
                'source': entry.source,
                'emotional_weight': entry.emotional_weight,
                'memory_type': entry.memory_type,
                'lifecycle_status': entry.lifecycle_status,
                'created_at': entry.created_at.isoformat() if hasattr(entry.created_at, 'isoformat') else str(entry.created_at),
                'updated_at': entry.updated_at.isoformat() if hasattr(entry.updated_at, 'isoformat') else str(entry.updated_at)
            }
            # Convert revision histories to dict format  
            if hasattr(entry, 'revision_history') and entry.revision_history:
                entry_dict['revision_history'] = [
                    {
                        'revision_id': rev.revision_id,
                        'timestamp': rev.timestamp.isoformat() if hasattr(rev.timestamp, 'isoformat') else str(rev.timestamp),
                        'changes': rev.changes,
                        'author': getattr(rev, 'author', None)
                    } for rev in entry.revision_history
                ]
            data.append(entry_dict)

        payload = {"format_version": 1, "memories": data}
        fd, tmp_name = tempfile.mkstemp(dir=str(self.file_path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, self.file_path)
        finally:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)