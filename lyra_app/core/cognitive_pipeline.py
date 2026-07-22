"""
Lyra 0.0.1 - Cognitive Pipeline

Orchestration layer that coordinates the cognitive decision and execution pipeline.

This module is responsible for coordinating brain components without implementing
any cognition, LLM logic, or memory operations itself. All these are handled by
their respective specialized modules.

Responsibilities:
- Receive ContextState
- Request decisions from DecisionEngine  
- Create ExecutionPlans
- Execute plans via Executor
- Return results

The CognitivePipeline maintains strict separation of concerns - it only coordinates,
never makes decisions or performs operations.
"""

from typing import Optional, Dict, Any
from context.context_state import ContextState
from brain.decision_engine import DecisionEngine
from brain.execution_plan import ExecutionPlan
from brain.executor import Executor
from brain.decision import Decision

class CognitivePipeline:
    """
    Primary orchestration layer for cognitive processing.
    
    This is the entry point for cognitive decision making in Lyra. It coordinates
    between all cognitive components and ensures proper execution flow without
    implementing any business logic or reasoning itself.
    """
    
    def __init__(self, 
                 memory_system = None,
                 model_interface = None):
        """
        Initialize cognitive pipeline with system dependencies.
        
        Args:
            memory_system: Optional memory system for memory operations  
            model_interface: Optional model interface for LLM access
        """
        self._decision_engine = DecisionEngine()
        self._executor = Executor(memory_system=memory_system, model_interface=model_interface)
        
    def process(self, 
                context_state: ContextState,
                input_text: str) -> Dict[str, Any]:
        """
        Process input through cognitive pipeline.
        
        Args:
            context_state: The current conversation context
            input_text: Original user input
            
        Returns:
            Dictionary containing processing results and outputs
        """
        # Validate input
        if not context_state or not input_text:
            raise ValueError("ContextState and input_text are required")
            
        try:
            # Step 1: Make cognitive decision based on context
            decision: Decision = self._decision_engine.make_decision(context_state)
            
            # Step 2: Generate execution plan from decision
            execution_plan = ExecutionPlan(decision)
            
            # Step 3: Execute the plan using coordinator
            results = self._executor.execute_plan(
                execution_plan=execution_plan,
                context_state=context_state,
                input_text=input_text
            )
            
            return results
            
        except Exception as e:
            # Return error information in standard format
            return {
                "status": "error",
                "error": str(e),
                "outputs": []
            }
