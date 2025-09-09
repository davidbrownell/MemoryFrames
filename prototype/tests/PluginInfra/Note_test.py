from unittest.mock import Mock

from MemoryFrames.PluginInfra.Note import Note


# ----------------------------------------------------------------------
def test_Create():
    id = Mock()
    fullpath = Mock()
    metadata_hash = Mock()
    content_hash = Mock()
    metadata = Mock()
    content = Mock()

    note = Note(id, fullpath, metadata_hash, content_hash, metadata, content)

    assert note.id is id
    assert note.fullpath is fullpath
    assert note.metadata_hash is metadata_hash
    assert note.content_hash is content_hash
    assert note.metadata is metadata
    assert note.content is content
