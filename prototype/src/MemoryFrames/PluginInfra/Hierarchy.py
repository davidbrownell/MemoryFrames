from abc import ABC, abstractmethod

from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.NoteSource import NoteSource


# ----------------------------------------------------------------------
class Hierarchy(ABC):
    """Base class for a user experience that defines how notes are organized and navigated."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        bridge: "HierarchyBridge",
    ) -> None:
        self.bridge = bridge

    # ----------------------------------------------------------------------
    @abstractmethod
    def OnNoteChanged(
        self,
        new_value: Note | None,
        prev_value: Note | None,
        *,
        is_initializing: bool,
    ) -> None:
        """Indicate that a note has changed or has been loaded."""
        raise NotImplementedError()  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def OnInitializationComplete(self, note_source: NoteSource) -> None:
        """Indicate that the NoteSource has completed its initialization."""
        raise NotImplementedError()  # pragma: no cover

    # ----------------------------------------------------------------------
    @abstractmethod
    def OnNoteDisplayed(
        self,
        source_hierarchy: "Hierarchy",
        note: Note,
    ) -> None:
        """Indicate that a note has been displayed."""
        raise NotImplementedError()  # pragma: no cover


# ----------------------------------------------------------------------
class HierarchyBridge(ABC):
    """Base class for a bridge that provides access to core MemoryFrames functionality."""

    # ----------------------------------------------------------------------
    @abstractmethod
    def DisplayNote(
        self,
        source_hierarchy: Hierarchy,
        note: Note,
        # TODO: display_type,-
    ) -> None:
        """Display the given note in the specified manager."""
        raise NotImplementedError()  # pragma: no cover
