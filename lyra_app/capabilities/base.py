"""
Base Capability Interface Contract
Defines the abstract contract that every capability must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseCapability(ABC):
    """
    Abstract base class defining the contract that every capability must implement.
    
    This interface ensures all capabilities maintain consistent behavior
    while remaining isolated from core Lyra architecture.
    """
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the capability independently.
        
        Returns:
            True if initialization succeeded, False otherwise
            
        Note: This method should not require any external context or 
        system information. Initialization must be self-contained.
        """
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """
        Gracefully shut down the capability.
        
        Returns:
            True if shutdown succeeded, False otherwise
            
        Note: This method should clean up resources without affecting
        core system state or identity.
        """
        pass
    
    @abstractmethod
    def validate(self, request: "CapabilityRequest") -> bool:
        """
        Validate that this capability can handle the given request.
        
        Args:
            request: The capability request from brain decision
            
        Returns:
            True if this capability can execute the request, False otherwise
            
        Note: Validation should not modify system state or make decisions,
        it should only check compatibility and requirements.
        """
        pass
    
    @abstractmethod
    def execute(self, invocation: "CapabilityInvocation") -> "CapabilityResult":
        """
        Execute the requested capability operation with execution context.
        
        Args:
            invocation: Execution environment containing all needed context
            
        Returns:
            Standardized result object containing execution outcome
            
        Note: This is the only method that performs actual work.
        It must not make decisions or modify identity - this is delegated
        to the decision engine through CognitivePipeline.
        """
        pass
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Report the current health status of the capability.
        
        Returns:
            Dictionary containing health metrics and status information
            
        Note: This should provide diagnostic information without side effects.
        """
        pass