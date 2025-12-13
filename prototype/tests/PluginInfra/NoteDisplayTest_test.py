from MemoryFrames.PluginInfra.NoteDisplayType import NoteDisplayType


# ----------------------------------------------------------------------
def test_Standard():
    assert list(NoteDisplayType) == [
        NoteDisplayType.CurrentPane,
        NoteDisplayType.NewPane,
        NoteDisplayType.InPlace,
    ]
