"""Lyra 0.0.1 - Context State Definition"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from memory.entities import MemoryEntry

class ContextState:
    """Represents the current context state for AI processing.
    
    This object contains all information needed to understand the 
    current interaction situation including conversation history,
    relevant memories, and user intent.
    """
    
    def __init__(self, 
                 conversation_id: str,
                 current_input: str,
                 recent_messages: List[Dict[str, Any]] = None,
                 relevant_memories: List[MemoryEntry] = None,
                 active_topic: Optional[str] = None,
                 user_intent: Optional[str] = None,
                 timestamp: Optional[datetime] = None):
        """
        Initialize context state.
        
        Args:
            conversation_id: Unique identifier for the current conversation
            current_input: The user's current input text
            recent_messages: Recent conversation history (message, role pairs)
            relevant_memories: Memory entries relevant to current context  
            active_topic: Currently discussed topic
            user_intent: Detected user intention
            timestamp: When this context was created
        """
        self.conversation_id = conversation_id
        self.current_input = current_input
        self.recent_messages = recent_messages or []
        self.relevant_memories = relevant_memories or []
        self.active_topic = active_topic
        self.user_intent = user_intent
        self.timestamp = timestamp or datetime.now()
        
    def __repr__(self):
        return (f"ContextState(conversation_id='{self.conversation_id}', "
                f"current_input='{self.current_input[:50]}...', "
                f"recent_messages={len(self.recent_messages)}, "
                f"relevant_memories={len(self.relevant_memories)})")
