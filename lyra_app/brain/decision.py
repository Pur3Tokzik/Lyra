"""
Lyra 0.0.1 - Decision Object

Immutable decision object that represents a cognitive choice made by the AI.

Decision objects contain only metadata about what action should be taken,
not actual implementation details or business logic.
"""

from typing import Optional, Dict, Any
from brain.decision_types import DecisionType

class Decision:
    """
    Immutable object representing a cognitive decision made by the AI.
    
    A Decision encapsulates all information needed to determine what action 
    should be taken next in the processing pipeline. The Decision object itself
    contains no implementation logic - it only stores metadata about the decision.
    """
    
    def __init__(self, 
                 decision_type: DecisionType,
                 confidence: float,
                 reason: str,
                 requires_llm: bool = False,
                 requires_memory_lookup: bool = False,
                 requires_memory_write: bool = False,
                 requires_clarification: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a Decision object with immutable metadata.
        
        Args:
            decision_type: Type of decision to make
            confidence: Confidence level (0.0 to 1.0) in the decision
            reason: Natural language explanation for the decision
            requires_llm: Whether LLM processing is required 
            requires_memory_lookup: Whether reading from memory is required
            requires_memory_write: Whether writing to memory is required
            requires_clarification: Whether user clarification is needed
            metadata: Additional arbitrary metadata about the decision
        """
        # Make sure confidence is in valid range
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
            
        # Store immutable fields
        self._decision_type = decision_type  
        self._confidence = confidence
        self._reason = reason
        self._requires_llm = requires_llm
        self._requires_memory_lookup = requires_memory_lookup
        self._requires_memory_write = requires_memory_write
        self._requires_clarification = requires_clarification
        self._metadata = metadata or {}
        
    @property
    def decision_type(self) -> DecisionType:
        """Get the type of decision made."""
        return self._decision_type
        
    @property 
    def confidence(self) -> float:
        """Get the confidence level (0.0 to 1.0) in this decision."""
        return self._confidence
        
    @property
    def reason(self) -> str:
        """Get natural language explanation for this decision."""
        return self._reason
        
    @property
    def requires_llm(self) -> bool:
        """Check if LLM is required to fulfill this decision."""
        return self._requires_llm
        
    @property
    def requires_memory_lookup(self) -> bool:
        """Check if memory lookup is required to fulfill this decision."""
        return self._requires_memory_lookup
        
    @property
    def requires_memory_write(self) -> bool:
        """Check if memory write is required to fulfill this decision.""" 
        return self._requires_memory_write
        
    @property
    def requires_clarification(self) -> bool:
        """Check if user clarification is required."""
        return self._requires_clarification
        
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get additional metadata for this decision."""
        return self._metadata.copy()  # Return copy to maintain immutability
        
    def __repr__(self):
        return (f"Decision(type={self.decision_type}, "
                f"confidence={self.confidence:.2f}, "
                f"requires_llm={self.requires_llm})")
