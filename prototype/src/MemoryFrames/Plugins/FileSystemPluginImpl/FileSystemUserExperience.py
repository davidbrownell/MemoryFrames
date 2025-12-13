from abc import ABC, abstractmethod
from pathlib import Path

from MemoryFrames.PluginInfra.Note import Note


# ----------------------------------------------------------------------
class FileSystemUserExperience(ABC):
    """Abstract base class for a FileSystem user experience."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        content_dir: Path,
        observer: "FileSystemUserExperienceObserver",
    ) -> None:
        self.content_dir = content_dir
        self.observer = observer

    # ----------------------------------------------------------------------
    @abstractmethod
    def OnInitializationComplete(self) -> None:
        """Indicate that initialization of the note source is complete."""
        raise Exception("Abstract method")  # noqa: EM101, TRY003  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def AddNote(self, note: Note) -> None:
        """Add a note to the user experience."""
        raise Exception("Abstract method")  # noqa: EM101, TRY003  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def SelectNote(self, note: Note) -> None:
        """Select a note within the user experience."""
        raise Exception("Abstract method")  # noqa: EM101, TRY003  # pragma: no cover


# ----------------------------------------------------------------------
class FileSystemUserExperienceObserver(ABC):
    """Abstract base class for an observer of a FileSystemUserExperience."""

    # ----------------------------------------------------------------------
    @abstractmethod
    def DisplayNote(self, note: Note) -> None:
        """Display a note."""
        raise Exception("Abstract method")  # noqa: EM101, TRY003  # pragma: no cover
