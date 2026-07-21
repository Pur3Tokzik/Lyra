"""
Lyra 0.0.1 - Journal System Core
Central component for tracking conversations and experiences.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from .entities import JournalData, JournalEntry, ImportantEvent, ConversationEntry


class Journal:
    """Main journal system for tracking AI's experiences and conversations."""
    
    def __init__(self, data_dir: str = "./journal_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Journal file path
        self.journal_file = self.data_dir / "journal.json"
        
        # Load existing journal or create new one
        self.journal_data = self._load_journal()
        
    def _load_journal(self) -> JournalData:
        """Load journal data from file."""
        try:
            if self.journal_file.exists():
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert loaded data to JournalData structure
                entries = []
                for entry_data in data.get('entries', []):
                    entry_type = entry_data.get('entry_type')
                    if entry_type == 'conversation':
                        entry = ConversationEntry(
                            timestamp=datetime.fromisoformat(entry_data['timestamp']),
                            entry_type=entry_type,
                            content=entry_data['content'],
                            conversation_id=entry_data['conversation_id'],
                            speaker=entry_data['speaker']
                        )
                    else:
                        entry = JournalEntry(
                            timestamp=datetime.fromisoformat(entry_data['timestamp']),
                            entry_type=entry_type,
                            content=entry_data['content']
                        )
                    entries.append(entry)
                
                important_events = []
                for event_data in data.get('important_events', []):
                    event = ImportantEvent(
                        timestamp=datetime.fromisoformat(event_data['timestamp']),
                        event_type=event_data['event_type'],
                        description=event_data['description']
                    )
                    important_events.append(event)
                    
                return JournalData(
                    entries=entries,
                    important_events=important_events,
                    session_context=data.get('session_context', {}),
                    last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
                )
            else:
                # Return empty journal data
                return JournalData()
                
        except Exception as e:
            print(f"Error loading journal: {e}")
            return JournalData()
    
    def _save_journal(self) -> bool:
        """Save current journal data to file."""
        try:
            # Convert journal data to serializable format
            data = {
                'entries': [],
                'important_events': [],
                'session_context': self.journal_data.session_context,
                'last_updated': self.journal_data.last_updated.isoformat() if self.journal_data.last_updated else None
            }
            
            # Serialize entries
            for entry in self.journal_data.entries:
                entry_dict = {
                    'timestamp': entry.timestamp.isoformat(),
                    'entry_type': entry.entry_type,
                    'content': entry.content
                }
                
                # Add type-specific fields
                if isinstance(entry, ConversationEntry):
                    entry_dict.update({
                        'conversation_id': entry.conversation_id,
                        'speaker': entry.speaker,
                        'message_id': entry.message_id
                    })
                    
                data['entries'].append(entry_dict)
            
            # Serialize important events 
            for event in self.journal_data.important_events:
                event_dict = {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'description': event.description
                }
                data['important_events'].append(event_dict)
            
            # Save to file
            with open(self.journal_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving journal: {e}")
            return False
    
    def add_entry(self, entry: JournalEntry) -> bool:
        """Add a new entry to the journal."""
        self.journal_data.entries.append(entry)
        self.journal_data.last_updated = datetime.now()
        return self._save_journal()
    
    def add_conversation_entry(self, conversation_id: str, speaker: str, content: str, message_id: Optional[str] = None) -> bool:
        """Add a conversation entry to the journal."""
        entry = ConversationEntry(
            timestamp=datetime.now(),
            entry_type='conversation',
            content=content,
            conversation_id=conversation_id,
            speaker=speaker,
            message_id=message_id
        )
        return self.add_entry(entry)
    
    def add_important_event(self, event_type: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add an important event to the journal."""
        event = ImportantEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            metadata=metadata
        )
        self.journal_data.important_events.append(event)
        self.journal_data.last_updated = datetime.now()
        return self._save_journal()
    
    def get_recent_entries(self, limit: int = 10) -> List[JournalEntry]:
        """Get the most recent journal entries."""
        return sorted(self.journal_data.entries, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_conversation_history(self, conversation_id: str) -> List[ConversationEntry]:
        """Get all entries for a specific conversation."""
        return [entry for entry in self.journal_data.entries 
                if isinstance(entry, ConversationEntry) and entry.conversation_id == conversation_id]
    
    def update_session_context(self, context_data: Dict[str, Any]) -> bool:
        """Update session context information."""
        self.journal_data.session_context.update(context_data)
        self.journal_data.last_updated = datetime.now()
        return self._save_journal()
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context."""
        return self.journal_data.session_context.copy()
    
    def get_all_events(self) -> List[ImportantEvent]:
        """Get all important events."""
        return self.journal_data.important_events
    
    def get_journal_summary(self) -> Dict[str, Any]:
        """Get a summary of the journal's contents."""
        return {
            'total_entries': len(self.journal_data.entries),
            'total_events': len(self.journal_data.important_events),
            'last_updated': self.journal_data.last_updated,
            'session_context_keys': list(self.journal_data.session_context.keys())
        }