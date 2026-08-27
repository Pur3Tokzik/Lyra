"""
Execution Environment Objects
Contains environmental context for capability execution
"""

from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID


@dataclass(frozen=True)
class ExecutionEnvironment:
    """
    Environmental context for capability execution.
    
    Provides execution setting information without system dependencies.
    """
    
    # Context information (provided by system)
    locale: str = "en-US"
    """User's preferred language/locale"""
    
    timezone: str = "UTC"
    """User's timezone"""
    
    session_id: str = ""
    """Identifier for user session"""