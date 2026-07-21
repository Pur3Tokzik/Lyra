"""
Lyra 0.0.1 - Lyra Factory
Factory for creating complete Lyra instances with proper dependency injection.
"""

from .ai_instance import AIInstance
from ..memory.file_memory_repository import FileMemoryRepository
from ..memory.memory_system import MemorySystem
from ..model.model_provider import ModelProvider

class LyraFactory:
    """Factory for creating complete Lyra AI instances with proper dependency injection."""
    
    @staticmethod
    def create_lyra_instance(
        ai_name: str = "AI",
        memory_file_path: str = "memory.json",
        model_provider: ModelProvider = None
    ) -> AIInstance:
        """Create a fully configured Lyra AI instance.
        
        Args:
            ai_name: Name for the AI instance
            memory_file_path: Path to the memory storage file
            model_provider: Optional model provider (to be injected)
            
        Returns:
            Configured AIInstance with all dependencies
        """
        # Create the memory repository
        memory_repository = FileMemoryRepository(memory_file_path)
        
        # Create the memory system with the repository
        memory_system = MemorySystem(memory_repository)
        
        # Create the AI instance with all dependencies
        ai_instance = AIInstance(
            ai_name=ai_name,
            memory_system=memory_system,
            model_interface=model_provider  # This is passed as model_interface to match AIInstance signature
        )
        
        return ai_instance