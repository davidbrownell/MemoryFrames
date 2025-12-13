from dbrownell_Common.Types import override

from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
from MemoryFrames.PluginInfra.Hierarchy import Hierarchy, HierarchyBridge as HierarchyBridgeInterface


# ----------------------------------------------------------------------
class HierarchyBridge(HierarchyBridgeInterface, NoteSourceObserver):
    """Bridge between a plugin's Hierarchy and the MemoryFrames application."""

    # ----------------------------------------------------------------------
    def __init__(self) -> None:
        super().__init__()

        self.hierarchies: list[Hierarchy] = []

    # ----------------------------------------------------------------------
    def AddHierarchy(self, hierarchy: Hierarchy) -> None:
        """Add a hierarchy to the list of Hierarchies."""

        self.hierarchies.append(hierarchy)

    # ----------------------------------------------------------------------
    @override
    def OnNewNote(  # noqa: D102
        self,
        note: Note,
        *,
        is_initializing: bool,
    ) -> None:
        # BugBug: Not checking anything right now
        for hierarchy in self.hierarchies:
            hierarchy.OnNoteChanged(note, None, is_initializing=is_initializing)

    # ----------------------------------------------------------------------
    @override
    def OnInitializationComplete(self, note_source: NoteSource) -> None:  # noqa: D102
        for hierarchy in self.hierarchies:
            hierarchy.OnInitializationComplete(note_source)

    # ----------------------------------------------------------------------
    @override
    def DisplayNote(  # noqa: D102
        self,
        source_hierarchy: Hierarchy,
        note: Note,
        # TODO: display_type,
    ) -> None:
        # TODO: Display the note in the content view

        for hierarchy in self.hierarchies:
            hierarchy.OnNoteDisplayed(source_hierarchy, note)
