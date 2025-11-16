"""Base interfaces for model configuration."""
from abc import ABC, abstractmethod
from typing import Any


class Gr00tConfigBase(ABC):
    """Abstract base class for GR00T model configuration."""
    
    @property
    @abstractmethod
    def port(self) -> int:
        """Model server port."""
        pass


class OctoConfigBase(ABC):
    """Abstract base class for Octo model configuration."""
    
    @property
    @abstractmethod
    def model_path(self) -> str:
        """Path to Octo model."""
        pass
    
    @abstractmethod
    def get_dataset_statistics(self, model: Any) -> Any:
        """Get dataset statistics for the model."""
        pass

