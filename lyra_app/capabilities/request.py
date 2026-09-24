"""
Capability Request Objects
Represents requests sent by the Brain to capabilities
"""

from dataclasses import dataclass
from typing import Mapping
from types import MappingProxyType


@dataclass(frozen=True)
class CapabilityRequest:
    """
    Request object sent from Lyra's Brain to a capability.
    
    This object contains only brain-decision information - no execution details.
    All execution context is provided by the capability subsystem.
    """
    
    # Identification
    request_id: str
    """Unique identifier for this specific request"""
    
    capability_name: str  
    """Name of the capability to execute"""
    
    # Decision parameters (from brain)
    action: str
    """Specific action to perform"""
    
    parameters: Mapping[str, Any]
    """Parameters required for execution"""
    
    # Request metadata
    priority: int = 0
    """Execution priority (higher numbers execute first)"""
    
    def __post_init__(self):
        object.__setattr__(self, 'parameters', MappingProxyType(dict(self.parameters)))