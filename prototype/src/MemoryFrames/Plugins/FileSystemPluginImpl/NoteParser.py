from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from MemoryFrames.PluginInfra.Note import Note

if TYPE_CHECKING:
    from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemNoteSource import FileSystemNoteSource


# ----------------------------------------------------------------------
class NoteParser(ABC):
    """Base class for an object that is able to serialize and deserialize a Note."""

    # ----------------------------------------------------------------------
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for files supported by the parser."""
        raise NotImplementedError()  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Deserialize(self, note_source: "FileSystemNoteSource", path: Path) -> Note:
        """Read the Note from the filesystem."""
        raise NotImplementedError()  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def Serialize(self, note: Note) -> None:
        """Write the Note to the filesystem."""
        raise NotImplementedError()  # pragma: no cover
