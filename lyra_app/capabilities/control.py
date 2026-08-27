"""
Execution Control Objects
Execution governance and control parameters
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class ExecutionControl:
    """
    Execution governance and control parameters.
    
    Defines policies that govern how an execution proceeds.
    """
    
    # Execution configuration
    timeout: float = 30.0
    """Maximum time allowed for execution (in seconds)"""
    
    cancellation_token: Optional[str] = None
    """Token for execution cancellation if needed"""