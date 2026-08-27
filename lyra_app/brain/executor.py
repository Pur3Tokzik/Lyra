"""
Lyra 0.0.1 - Executor

The executor coordinates the actual execution of actions based on an ExecutionPlan.
It calls the appropriate modules but never makes decisions or generates responses.
"""

from typing import Optional, Dict, Any
from collections.abc import Mapping
from brain.decision import Decision
from brain.execution_plan import ExecutionPlan, ExecutionStep
from context.context_state import ContextState
from memory.memory_system import MemorySystem
from model.model_interface import ModelInterface
from capabilities.base import BaseCapability

class Executor:
    """
    Coordinates module execution based on execution plans.
    
    The executor is responsible for taking an ExecutionPlan and carrying out 
    the required actions by calling appropriate modules. It never makes decisions
    or performs reasoning - only orchestrates existing capabilities.
    """
    
    def __init__(self, 
                 memory_system: MemorySystem = None,
                 model_interface: ModelInterface = None,
                 capabilities: Mapping[str, BaseCapability] | None = None):
        """
        Initialize the executor with system dependencies.
        
        Args:
            memory_system: Optional memory system to use for memory operations
            model_interface: Optional model interface for LLM calls
            capabilities: Optional mapping of available capabilities
        """
        self.memory_system = memory_system 
        self.model_interface = model_interface
        self.capabilities = capabilities or {}
        
    def execute_plan(self, 
                    execution_plan: ExecutionPlan,
                    context_state: ContextState,
                    input_text: str) -> Dict[str, Any]:
        """
        Execute the actions described in an execution plan.
        
        Args:
            execution_plan: The plan to execute
            context_state: Current context for reference  
            input_text: Original input for use in execution
            
        Returns:
            Dictionary containing execution results and outputs
        """
        # Validate inputs 
        if not execution_plan or not context_state:
            raise ValueError("Execution requires valid plan and context")
            
        results = {
            "status": "success",
            "outputs": [],
            "final_response": None
        }
        
        # Execute each step in the plan  
        for step in execution_plan:
            try:
                result = self._execute_step(step, context_state, input_text)
                if result is not None:
                    results["outputs"].append(result)
                    
                # If this is a response step, capture final result
                if step.action == "generate_response":
                    results["final_response"] = result
                    
            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)
                break
                
        return results
        
    def _execute_step(self, 
                     step: ExecutionStep,
                     context_state: ContextState,
                     input_text: str) -> Optional[str]:
        """
        Execute a single step from the plan.
        
        Args:
            step: The execution step to perform
            context_state: Current processing context
            input_text: Original user input
            
        Returns:
            Output from step execution, or None if no output 
        """
        
        # Coordinate memory operations if needed
        if step.action == "lookup_memory" and self.memory_system:
            return self._lookup_memory(context_state)
            
        elif step.action == "store_memory" and self.memory_system:
            # Store the context information in memory  
            return self._store_memory(context_state, input_text)
            
        elif step.action == "call_llm" and self.model_interface:
            # Call model provider when needed
            return self._call_model(context_state, input_text)
            
        elif step.action == "request_clarification":
            # Simple placeholder for clarification requests
            return f"Could you clarify: '{input_text[:50]}...'"
            
        elif step.action == "generate_response":
            # Final processing step - in a real implementation this would 
            # involve the actual response generation process
            return self._create_final_response(context_state, input_text)
            
        return None  # No action needed or unsupported
        
    def _lookup_memory(self, context_state: ContextState) -> str:
        """Perform memory lookup operations."""
        # In a real implementation this would use memory_system
        # Here we're just returning a placeholder result
        if self.memory_system:
            # Placeholder for actual memory lookup functionality
            return "Memory lookup completed"
        return "No memory system available"
        
    def _store_memory(self, context_state: ContextState, input_text: str) -> str:
        """Store information to memory."""
        # In a real implementation this would use memory_system  
        # Here we're just returning a placeholder result
        if self.memory_system:
            # Placeholder for actual memory store functionality
            return "Memory stored successfully"
        return "No memory system available"
        
    def _call_model(self, context_state: ContextState, input_text: str) -> str:
        """Call the model provider for LLM processing."""
        # In a real implementation this would use model_interface 
        # Here we're just returning a placeholder result
        if self.model_interface:
            # Placeholder for actual LLM calling functionality 
            return "LLM processing completed with answer"
        return "No model interface available"
        
    def _create_final_response(self, context_state: ContextState, input_text: str) -> str:
        """Create final response from execution results."""
        # In a real implementation this would integrate all outputs
        # For now just return a standard completion message
        return "Response generated"
