"""
Lyra 0.0.1 - Journal-Memory Adapter
Adapter for integrating journal system with memory management.
"""

import json
from typing import Optional, Dict, Any
from lyra_app.memory.memory_system import MemorySystem
from lyra_app.journal.entities import JournalData


class JournalMemoryAdapter:
    """Adapter to connect journal system with memory system."""
    
    def __init__(self, journal_system, memory_system: MemorySystem):
        self.journal = journal_system
        self.memory = memory_system
        
    def save_session_context_to_memory(self) -> bool:
        """Save current session context to memory system."""
        try:
            context = self.journal.get_session_context()
            if context:
                # Store in memory with a specific category for session context
                self.memory.add_memory(
                    json.dumps(context, ensure_ascii=False),
                    category="session_context"
                )
            return True
        except Exception as e:
            print(f"Error saving session context to memory: {e}")
            return False
            
    def load_session_context_from_memory(self) -> Dict[str, Any]:
        """Load session context from memory system."""
        try:
            # Load session context memories
            context_memories = self.memory.get_memories(category="session_context")
            if context_memories:
                # Get the most recent session context by timestamp
                latest_context = max(context_memories, key=lambda x: x.timestamp)
                context = json.loads(latest_context.content)
                self.journal.update_session_context(context)
                return context
            return {}
        except Exception as e:
            print(f"Error loading session context from memory: {e}")
            return {}
            
    def save_journal_summary_to_memory(self) -> bool:
        """Save journal summary to memory system."""
        try:
            summary = self.journal.get_journal_summary()
            if summary:
                self.memory.add_memory(
                    json.dumps(summary, ensure_ascii=False, default=str),
                    category="journal_summary"
                )
            return True
        except Exception as e:
            print(f"Error saving journal summary to memory: {e}")
            return False
            
    def get_journal_context_for_prompt(self) -> str:
        """Get formatted journal context for prompting AI."""
        try:
            # Get recent conversations and important events
            recent_entries = self.journal.get_recent_entries(20)  # Last 20 entries
            events = self.journal.get_all_events()
            
            context_lines = []
            
            if events:
                context_lines.append("Recent important events:")
                for event in events[-5:]:  # Last 5 events
                    context_lines.append(f"- [{event.timestamp.strftime('%Y-%m-%d %H:%M')}] {event.event_type}: {event.description}")
                
            if recent_entries:
                context_lines.append("\nRecent conversation history:")
                for entry in recent_entries[-10:]:  # Last 10 entries
                    speaker = "User" if entry.speaker == "user" else "AI"
                    context_lines.append(f"{speaker}: {entry.content}")
            
            return "\n".join(context_lines) if context_lines else "No conversation history available."
            
        except Exception as e:
            print(f"Error generating journal prompt context: {e}")
            return "No context information available."