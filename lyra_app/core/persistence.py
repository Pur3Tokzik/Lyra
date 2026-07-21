"""
Lyra 0.0.1 - Persistence Layer
Handles storage and retrieval of AI instance data according to Lyra's architecture.
"""

import json
import os
from pathlib import Path
from typing import Optional
from .ai_instance import AIInstance

class PersistenceManager:
    """Manages persistent storage of Lyra AI instances."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def save_ai_instance(self, ai_instance: AIInstance, filename: str = "current_ai.json") -> bool:
        """Save AI instance to persistent storage."""
        try:
            file_path = self.data_dir / filename
            data = {
                "ai_name": ai_instance.ai_name,
                "identity": {
                    "created": ai_instance.identity.created,
                    "user_identity_preference": ai_instance.identity.user_identity_preference
                },
                "personality": {
                    "selected_type": ai_instance.personality.selected_type,
                    "custom_description": ai_instance.personality.custom_description
                },
                "model_configuration": getattr(ai_instance, 'model_configuration', None),
                "memory": getattr(ai_instance, 'memory', {}),
                "creation_timestamp": ai_instance.creation_timestamp.isoformat(),
                # Journal state - store only configuration, not the object itself
                "journal": {
                    "data_dir": str(ai_instance.journal.data_dir) if ai_instance.journal else None
                } if hasattr(ai_instance, 'journal') and ai_instance.journal is not None else None
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"Error saving AI instance: {e}")
            return False
            
    def load_ai_instance(self, filename: str = "current_ai.json") -> Optional[AIInstance]:
        """Load AI instance from persistent storage."""
        try:
            file_path = self.data_dir / filename
            if not file_path.exists():
                return None
                
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            ai_instance = AIInstance(ai_name=data.get("ai_name", "AI"))
            ai_instance.identity.created = data.get("identity", {}).get("created", False)
            ai_instance.identity.user_identity_preference = data.get("identity", {}).get("user_identity_preference")
            
            ai_instance.personality.selected_type = data.get("personality", {}).get("selected_type")
            ai_instance.personality.custom_description = data.get("personality", {}).get("custom_description")
            
            # Set model configuration and memory as attributes if they exist
            model_config = data.get("model_configuration")
            if model_config is not None:
                ai_instance.model_configuration = model_config
                
            memory_data = data.get("memory", {})
            if memory_data:
                ai_instance.memory = memory_data
            
            # Note: creation_timestamp is loaded as string and would need parsing if needed
            timestamp_str = data.get("creation_timestamp")
            if timestamp_str:
                ai_instance.creation_timestamp = datetime.fromisoformat(timestamp_str)
            else:
                ai_instance.creation_timestamp = datetime.now()  # fallback
            
            # Handle journal state - compatible with old data (no journal field)
            journal_config = data.get("journal")
            if journal_config and journal_config.get("data_dir"):
                # Initialize journal from saved configuration
                try:
                    # Initialize the journal without event logging for loading
                    ai_instance.initialize_journal(journal_config["data_dir"])
                except Exception:
                    pass  # If initialization fails, keep journal as None
            
            return ai_instance
            
        except Exception as e:
            print(f"Error loading AI instance: {e}")
            return None