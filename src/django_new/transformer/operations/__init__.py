from abc import ABC, abstractmethod
from pathlib import Path


class Operation(ABC):
    """Base class for all operations"""

    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the operation"""
        pass

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        """Check if this operation can handle the given file"""
        pass

    @abstractmethod
    def apply(self, content: str) -> str:
        """Apply the operation to the given content and return the modified content"""
        pass
