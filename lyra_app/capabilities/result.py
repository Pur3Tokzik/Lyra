"""
Capability Result Objects
Standardized response format for all capabilities
"""

from dataclasses import dataclass
from typing import Mapping, Optional
from enum import Enum
from types import MappingProxyType


class CapabilityStatus(str, Enum):
    """Standard status indicators for capability execution"""
    SUCCESS = "success"
    FAILURE = "failure" 
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass(frozen=True)
class CapabilityResult:
    """
    Standardized result object returned by every capability.
    
    Provides consistent response structure for all capability operations.
    """
    
    # Result identification
    request_id: str
    """Reference to the original request that generated this result"""
    
    invocation_id: str  
    """Identifier for the execution invocation"""
    
    # Execution status
    status: CapabilityStatus
    """Overall status of the execution"""
    
    # Result data
    data: Optional[Mapping[str, Any]]
    """Main result data returned by capability"""
    
    # Error information (if applicable)
    error_message: Optional[str] = None
    """Human-readable error description (if status is not success)"""
    
    error_code: Optional[str] = None
    """Machine-readable error code (if status is not success)"""
    
    # Performance metrics 
    execution_time: Optional[float] = None
    """Time taken to execute the capability (in seconds)"""
    
    # Additional metadata
    metadata: Optional[Mapping[str, Any]]
    """Additional information about the execution"""
    
    def __post_init__(self):
        if self.data is None:
            object.__setattr__(self, 'data', MappingProxyType({}))
        else:
            object.__setattr__(self, 'data', MappingProxyType(dict(self.data)))
            
        if self.metadata is None:
            object.__setattr__(self, 'metadata', MappingProxyType({}))
        else:
            object.__setattr__(self, 'metadata', MappingProxyType(dict(self.metadata)))