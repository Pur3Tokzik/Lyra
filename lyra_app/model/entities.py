"""Lyra 0.0.1 - Model Entities"""

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class ModelResponse:
    """Represents a response from the model."""
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)