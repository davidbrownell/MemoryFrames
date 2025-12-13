from dbrownell_Common.Types import override

from MemoryFrames.PluginInfra.Hierarchy import Hierarchy, HierarchyBridge
from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.NoteDisplayType import NoteDisplayType


# ----------------------------------------------------------------------
class MyHierarchy(Hierarchy):
    # ----------------------------------------------------------------------
    @override
    def OnNoteChanged(
        self,
        new_value: Note | None,
        prev_value: Note | None,
    ) -> None:
        pass


# ----------------------------------------------------------------------
class MyHierarchyBridge(HierarchyBridge):
    # ----------------------------------------------------------------------
    @override
    def DisplayNote(
        self,
        note: Note,
        display_type: NoteDisplayType = NoteDisplayType.CurrentPane,
    ) -> None:
        pass


# ----------------------------------------------------------------------
def test_Hierarchy():
    MyHierarchy()
    assert True


# ----------------------------------------------------------------------
def test_HierarchyBridge():
    MyHierarchyBridge()
    assert True
