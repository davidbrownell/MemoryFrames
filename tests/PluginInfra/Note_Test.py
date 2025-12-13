import re

from unittest.mock import Mock

from MemoryFrames.PluginInfra.Note import Note


# ----------------------------------------------------------------------
def test_Creation():
    id = Mock()
    source = Mock()
    source_data = Mock()
    metadata = Mock()
    content = Mock()
    metadata_hash = Mock()
    content_hash = Mock()

    note = Note(id, source, source_data, metadata, content, metadata_hash, content_hash)

    assert note.id is id
    assert note.source is source
    assert note.source_data is source_data
    assert note.metadata is metadata
    assert note.content is content
    assert note.metadata_hash is metadata_hash
    assert note.content_hash is content_hash


# ----------------------------------------------------------------------
def test_Repr():
    note = Note(Mock(), Mock(), Mock(), Mock(), Mock(), Mock(), Mock())
    repr = str(note)

    srcubbed = re.sub(r"\<Mock id='.+?'\>", "<Mock>", repr)

    assert srcubbed == "Note(id=<Mock>, source=<Mock>, source_data=<Mock>)"
