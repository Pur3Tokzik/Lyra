"""
Lyra 0.0.1 - Execution Plan

ExecutionPlan represents an ordered sequence of actions required to fulfill a Decision.
It is a structured description without implementation logic.
"""

from typing import List, Dict, Any, Optional
from brain.decision import Decision

class ExecutionStep:
    """
    A single step in an execution plan.
    
    Represents one operational action that should be taken.
    """
    
    def __init__(self, 
                 action: str,
                 parameters: Optional[Dict[str, Any]] = None,
                 target_module: Optional[str] = None):
        """
        Initialize execution step.
        
        Args:
            action: The action to perform (e.g., "lookup_memory", "call_llm")
            parameters: Action-specific parameters 
            target_module: Which module this step targets (for coordination)
        """
        self.action = action
        self.parameters = parameters or {}
        self.target_module = target_module
        
    def __repr__(self):
        return f"ExecutionStep(action='{self.action}', target='{self.target_module}')"

class ExecutionPlan:
    """
    Ordered sequence of actions required to satisfy a Decision.
    
    The ExecutionPlan is a structured description of what needs to be done,
    but contains no business logic or implementation details - it's purely
    descriptive of execution flow.
    """
    
    def __init__(self, decision: Decision):
        """
        Initialize execution plan from a decision.
        
        Args:
            decision: The decision that generated this plan
        """
        self.decision = decision
        self.steps: List[ExecutionStep] = []
        self._build_plan(decision)
        
    def _build_plan(self, decision: Decision) -> None:
        """
        Build execution steps based on decision metadata.
        
        Args:
            decision: The decision to create plan for  
        """
        # Clear existing steps
        self.steps.clear()
        
        # Create plan based on decision type and requirements
        
        if decision.requires_memory_lookup:
            self.steps.append(ExecutionStep(
                action="lookup_memory",
                target_module="memory"
            ))
            
        if decision.requires_clarification:
            self.steps.append(ExecutionStep(
                action="request_clarification", 
                target_module="interaction"
            ))
            
        if decision.requires_memory_write:
            self.steps.append(ExecutionStep(
                action="store_memory",
                target_module="memory"
            ))
            
        if decision.requires_llm:
            self.steps.append(ExecutionStep(
                action="call_llm",
                target_module="model"
            ))
            
        # Final response step (always added) - this is what determines final output
        self.steps.append(ExecutionStep(
            action="generate_response",
            target_module="output"
        ))
        
    def __len__(self) -> int:
        """Get number of execution steps."""
        return len(self.steps)
        
    def __iter__(self):
        """Make ExecutionPlan iterable."""
        return iter(self.steps)
        
    def __repr__(self):
        return f"ExecutionPlan(steps={len(self.steps)}, decision={self.decision.decision_type})"
