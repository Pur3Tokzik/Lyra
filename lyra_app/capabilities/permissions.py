"""
Capability Permissions
Permission management for capability execution
"""

from dataclasses import dataclass
from typing import Mapping
from types import MappingProxyType


@dataclass(frozen=True)
class CapabilityPermissions:
    """
    Permission granting information for capability execution.
    
    Defines what resources and capabilities are available to an execution.
    """
    
    permissions_granted: Mapping[str, bool]
    """Dictionary of granted permissions for this execution"""
    
    def __post_init__(self):
        object.__setattr__(self, 'permissions_granted', MappingProxyType(dict(self.permissions_granted)))