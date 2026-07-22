"""
Lyra 0.0.1 - Decision Engine

Core cognitive decision engine that analyzes context and determines next steps.

The DecisionEngine is responsible for making intelligent decisions about what 
actions to take based on current context without executing those actions.
"""

from typing import Optional, Dict, Any
from context.context_state import ContextState
from brain.decision import Decision
from brain.decision_types import DecisionType

class DecisionEngine:
    """
    Analyzes context and makes cognitive decisions about how to proceed.
    
    The decision engine is the core of Lyra's reasoning capability. It processes
    the current context state and determines what action should be taken next,
    but does NOT perform any actual execution. All decision logic remains 
    deterministic and separate from implementation details.
    """
    
    def __init__(self):
        """Initialize the decision engine."""
        pass
        
    def make_decision(self, context_state: ContextState) -> Decision:
        """
        Analyze current context and determine appropriate action.
        
        Args:
            context_state: The current state of conversation context
            
        Returns:
            A Decision object with metadata about what to do next
        """
        # Validate input
        if not context_state:
            raise ValueError("ContextState cannot be None")
            
        # Base decision logic - this is the core reasoning engine
        return self._analyze_context(context_state)
        
    def _analyze_context(self, context_state: ContextState) -> Decision:
        """
        Internal method to analyze context and determine decision.
        
        This is where the cognitive reasoning happens. It determines:
        - If we have enough information to respond directly
        - If we need LLM assistance
        - If we need to look up or store memory
        - If clarification is needed
        
        Args:
            context_state: The context to analyze
            
        Returns:
            Decision object with action recommendation and metadata
        """
        
        # Default decision assumes a basic response
        decision_type = DecisionType.RESPOND
        confidence = 0.8
        reason = "Context provides sufficient information for direct response"
        requires_llm = False 
        requires_memory_lookup = False
        requires_memory_write = False
        requires_clarification = False
        metadata = {}
        
        # Analyze the input and context to determine next action
        
        # 1. Check if input is empty or unclear 
        if not context_state.current_input or not context_state.current_input.strip():
            decision_type = DecisionType.IGNORE
            confidence = 0.9
            reason = "Input is empty or contains only whitespace"
            
        # 2. Simple keyword detection for action requirements  
        elif self._is_information_request(context_state.current_input):
            # If user is asking for specific information, we may need to look it up
            decision_type = DecisionType.LOOKUP_MEMORY
            confidence = 0.7
            reason = "User appears to be requesting specific information that may need lookup"
            requires_memory_lookup = True
            
        elif self._is_clarification_needed(context_state):
            # If the input is ambiguous or unclear, request clarification
            decision_type = DecisionType.ASK_CLARIFICATION
            confidence = 0.6
            reason = "Input requires clarification for proper understanding"
            requires_clarification = True
            
        elif self._is_complex_query(context_state.current_input):
            # Complex questions may require LLM processing  
            decision_type = DecisionType.CALL_LLM
            confidence = 0.85
            reason = "Complex query requiring deep understanding or inference"
            requires_llm = True
            
        elif self._requires_memory_storage(context_state.current_input):
            # If input indicates learned information that should be stored
            decision_type = DecisionType.STORE_MEMORY
            confidence = 0.75 
            reason = "New knowledge discovered, should be stored for future reference"
            requires_memory_write = True
            
        # Add more sophisticated logic as needed here
        
        return Decision(
            decision_type=decision_type,
            confidence=confidence,
            reason=reason,
            requires_llm=requires_llm,
            requires_memory_lookup=requires_memory_lookup,
            requires_memory_write=requires_memory_write,
            requires_clarification=requires_clarification,
            metadata=metadata
        )
        
    def _is_information_request(self, input_text: str) -> bool:
        """Detect if input is asking for specific information."""
        # Simple approach - keywords that typically indicate lookup requirements
        lookup_indicators = ["how to", "what is", "tell me about", "explain", 
                           "define", "describe", "where is", "when was", "who is"]
        lower_text = input_text.lower().strip()
        return any(indicator in lower_text for indicator in lookup_indicators)
        
    def _is_clarification_needed(self, context_state: ContextState) -> bool:
        """Detect if clarification is needed based on current context."""
        # Check for ambiguous or unclear input
        return False  # Placeholder - more sophisticated logic can be added
        
    def _is_complex_query(self, input_text: str) -> bool:
        """Detect if input requires LLM inference rather than direct response.""" 
        # Logic for recognizing complex reasoning needs
        lower_text = input_text.lower().strip()
        complex_indicators = ["why", "how", "imagine", "suppose", "what would happen"]
        return any(indicator in lower_text for indicator in complex_indicators)
        
    def _requires_memory_storage(self, input_text: str) -> bool:
        """Detect if new information should be stored in memory."""
        # Simple approach - sentences ending with learning indicators
        lower_text = input_text.lower().strip()
        learn_indicators = ["I learned", "I discovered", "from what I understand"]
        return any(indicator in lower_text for indicator in learn_indicators)
