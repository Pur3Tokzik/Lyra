"""
Lyra 0.0.1 - Brain Interfaces

Contracts and interfaces for the cognitive decision engine components.
Ensures loose coupling between modules while maintaining clear boundaries.
"""

from typing import Optional, Dict, Any
from context.context_state import ContextState
from brain.decision import Decision
from brain.execution_plan import ExecutionPlan

class DecisionEngineInterface:
    """
    Interface for cognitive decision engines.
    
    This contract ensures that any decision engine implementation 
    provides the same core functionality to the system.
    """
    
    def make_decision(self, context_state: ContextState) -> Decision:
        """
        Make a decision based on current context.
        
        Args:
            context_state: Current processing context
            
        Returns:
            A Decision object with metadata about next action
        """
        raise NotImplementedError("Subclasses must implement make_decision")
        
class ExecutionPlanInterface:
    """
    Interface for execution plan generators.
    
    Defines how execution plans are created from decisions.
    """
    
    def generate_plan(self, decision: Decision) -> ExecutionPlan:
        """
        Generate an execution plan based on a decision.
        
        Args:
            decision: The decision to create plan for
            
        Returns:
            An ExecutionPlan object with ordered steps
        """
        raise NotImplementedError("Subclasses must implement generate_plan")

class ExecutorInterface:
    """
    Interface for execution coordinators.
    
    Ensures consistent coordination of system actions based on plans.
    """
    
    def execute_plan(self, 
                    execution_plan: ExecutionPlan,
                    context_state: ContextState,
                    input_text: str) -> Dict[str, Any]:
        """
        Execute the steps in an execution plan.
        
        Args:
            execution_plan: Plan to execute
            context_state: Current processing context  
            input_text: Original user input
            
        Returns:
            Results from execution including final outputs
        """
        raise NotImplementedError("Subclasses must implement execute_plan")
