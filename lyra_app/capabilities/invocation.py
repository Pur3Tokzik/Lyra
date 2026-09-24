"""
Capability Invocation
Represents the execution environment created by CapabilityManager/CapabilityExecutor
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from uuid import UUID


@dataclass(frozen=True)
class CapabilityInvocation:
    """
    Complete execution environment for capability.
    
    Created exclusively by CapabilityManager/CapabilityExecutor.
    Contains all execution context needed by capabilities.
    """
    
    # Reference to the original request
    request: "CapabilityRequest"
    """Reference to the brain decision that triggered this invocation"""
    
    # Execution identification  
    invocation_id: str
    """Unique identifier for this specific execution"""
    
    # Execution environment information
    environment: "ExecutionEnvironment"
    """Environmental context for this execution"""
    
    # Permission information
    permissions: "CapabilityPermissions" 
    """Permissions granted to this execution"""
    
    # Execution control policies
    control: "ExecutionControl"
    """Governance and control parameters for this execution"""