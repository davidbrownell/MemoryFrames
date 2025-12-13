from unittest.mock import Mock

from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver


# ----------------------------------------------------------------------
class TestNoteSource:
    # ----------------------------------------------------------------------
    def test_Create(self):
        observer = Mock()

        note_source = NoteSource(observer)

        assert note_source.observer is observer
