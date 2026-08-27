"""Lyra 0.0.1 - Context Builder Implementation"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from context.context_state import ContextState
from context.interfaces import MemoryRetriever, ContextBuilder
from memory.entities import MemoryEntry

class BasicContextBuilder(ContextBuilder):
    """Basic implementation of context builder.
    
    This class constructs context state by combining user input,
    conversation history, and relevant memories from a memory retriever.
    """
    
    def __init__(self, memory_retriever: Optional[MemoryRetriever] = None):
        """
        Initialize the basic context builder.
        
        Args:
            memory_retriever: Optional memory retriever to use for finding relevant memories
        """
        self.memory_retriever = memory_retriever
        
    def build_context(self, 
                     conversation_id: str,
                     current_input: str,
                     recent_messages: List[Dict[str, Any]] = None,
                     memory_retriever: Optional[MemoryRetriever] = None) -> ContextState:
        """
        Build complete context state from inputs and memories.
        
        Args:
            conversation_id: Unique conversation identifier
            current_input: Current user input text 
            recent_messages: Recent conversation history
            memory_retriever: Optional memory retriever (uses instance's if not provided)
            
        Returns:
            Complete ContextState object
        """
        # Use the provided retriever or fall back to instance retriever
        retriever = memory_retriever or self.memory_retriever
        
        # Get relevant memories if we have a retriever
        relevant_memories = []
        if retriever:
            try:
                relevant_memories = retriever.retrieve_relevant_memories(current_input)
            except Exception as e:
                # Log error but continue - context building should not fail completely
                print(f"Warning: Could not retrieve memories for context. Error: {e}")
        
        # Build context state
        context_state = ContextState(
            conversation_id=conversation_id,
            current_input=current_input,
            recent_messages=recent_messages or [],
            relevant_memories=relevant_memories,
            timestamp=datetime.now()
        )
        
        # Simple topic detection based on input content 
        context_state.active_topic = self._detect_topic(current_input)
        
        # Simple intent detection (can be enhanced later)
        context_state.user_intent = self._detect_intent(current_input)
        
        return context_state
        
    def _detect_topic(self, input_text: str) -> Optional[str]:
        """Simple topic detection based on input keywords.
        
        Args:
            input_text: Text to analyze for topic
            
        Returns:
            Detected topic or None
        """
        # This is a placeholder - real implementation would be more sophisticated 
        if not input_text:
            return None
        
        # Simple keyword-based topic detection (would use NLP in future) 
        lower_text = input_text.lower()
        if "memory" in lower_text:
            return "memory_system"
        elif "model" in lower_text or "llm" in lower_text:
            return "model_integration"  
        elif "brain" in lower_text or "cognition" in lower_text:
            return "cognitive_processing"
            
        return "general_conversation"
        
    def _detect_intent(self, input_text: str) -> Optional[str]:
        """Simple intent detection based on input keywords.
        
        Args:
            input_text: Text to analyze for intent
            
        Returns:
            Detected intent or None
        """
        # This is a placeholder - real implementation would be more sophisticated
        if not input_text:
            return None
        
        lower_text = input_text.lower()
        
        # Check for question patterns
        if input_text.strip().endswith("?"):
            return "question"
            
        # Check for directive patterns  
        directives = ["please", "help", "how to", "explain", "tell me"]
        for directive in directives:
            if directive in lower_text:
                return "request_assistance"
                
        return "statement"  # Default case
