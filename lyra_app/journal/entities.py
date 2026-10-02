"""
Lyra 0.0.2 - Journal Entities
Data models for the journal system.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any


class JournalEntry:
    """Represents a single entry in the journal."""
    
    def __init__(self, timestamp: datetime, entry_type: str, content: str, 
                 entry_id: str = "", metadata: Optional[Dict[str, Any]] = None):
        self.timestamp = timestamp
        self.entry_type = entry_type
        self.content = content
        self.entry_id = entry_id
        self.metadata = metadata or {}


class ConversationEntry(JournalEntry):
    """Represents a conversation entry in the journal."""
    
    def __init__(self, timestamp: datetime, entry_type: str, content: str,
                 conversation_id: str, speaker: str, 
                 message_id: Optional[str] = None, entry_id: str = "", 
                 metadata: Optional[Dict[str, Any]] = None):
        super().__init__(timestamp, entry_type, content, entry_id, metadata)
        self.conversation_id = conversation_id
        self.speaker = speaker
        self.message_id = message_id


class ImportantEvent:
    """Represents an important event in the AI's life."""
    
    def __init__(self, timestamp: datetime, event_type: str, description: str,
                 metadata: Optional[Dict[str, Any]] = None, event_id: str = ""):
        self.timestamp = timestamp
        self.event_type = event_type
        self.description = description
        self.metadata = metadata or {}
        self.event_id = event_id


class JournalData:
    """Complete journal data structure."""
    
    def __init__(self, entries: Optional[List] = None,
                 important_events: Optional[List] = None,
                 session_context: Optional[Dict[str, Any]] = None,
                 last_updated: Optional[datetime] = None):
        self.entries: List = entries if entries is not None else []
        self.important_events: List = important_events if important_events is not None else []
        self.session_context: Dict[str, Any] = session_context if session_context is not None else {}
        self.last_updated: Optional[datetime] = last_updated