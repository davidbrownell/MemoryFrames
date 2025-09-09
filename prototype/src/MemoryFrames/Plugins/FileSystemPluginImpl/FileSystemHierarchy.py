from typing import TYPE_CHECKING

from dbrownell_Common.Types import override

from MemoryFrames.PluginInfra.Hierarchy import Hierarchy, HierarchyBridge
from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.NoteSource import NoteSource
from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemNoteSource import FileSystemNoteSource

if TYPE_CHECKING:
    from MemoryFrames.Plugins.FileSystemPlugin import FileSystemPlugin


# ----------------------------------------------------------------------
class FileSystemHierarchy(Hierarchy):
    """Hierarchy classed used by the FileSystemPlugin."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        file_system: "FileSystemPlugin",
        bridge: HierarchyBridge,
    ) -> None:
        super().__init__(bridge)

        self.file_system = file_system

    # ----------------------------------------------------------------------
    @override
    def OnNoteChanged(  # noqa: D102
        self,
        new_value: Note | None,
        prev_value: Note | None,
        *,
        is_initializing: bool,
    ) -> None:
        assert new_value is not None, "BugBug: Deletion is not supported yet"
        assert prev_value is None, "BugBug: Update is not supported yet"
        assert is_initializing, "BugBug: Only supporting initialization right now"

        if new_value.source != self.file_system.note_source:
            return

        self.file_system.user_experience.AddNote(new_value)

    # ----------------------------------------------------------------------
    @override
    def OnInitializationComplete(self, note_source: NoteSource) -> None:  # noqa: D102
        if note_source != self.file_system.note_source:
            return

        self.file_system.user_experience.OnInitializationComplete()

    # ----------------------------------------------------------------------
    @override
    def OnNoteDisplayed(  # noqa: D102
        self,
        source_hierarchy: Hierarchy,
        note: Note,
    ) -> None:
        if not isinstance(note.source, FileSystemNoteSource):
            return

        if id(source_hierarchy) == id(self):
            return

        self.file_system.user_experience.SelectNote(note)
