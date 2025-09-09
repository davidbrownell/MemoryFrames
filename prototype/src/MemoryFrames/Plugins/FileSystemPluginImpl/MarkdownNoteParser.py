from hashlib import sha512
from pathlib import Path
from typing import cast, TYPE_CHECKING
from uuid import uuid4, UUID

import frontmatter

from dbrownell_Common.Types import override

from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.Plugins.FileSystemPluginImpl.NoteParser import NoteParser

if TYPE_CHECKING:
    from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemNoteSource import FileSystemNoteSource


# ----------------------------------------------------------------------
class MarkdownNoteParser(NoteParser):
    """Parser that supports markdown files."""

    # ----------------------------------------------------------------------
    @property
    @override
    def file_extension(self) -> str:  # noqa: D102
        return ".md"

    # ----------------------------------------------------------------------
    @override
    def Deserialize(self, note_source: "FileSystemNoteSource", path: Path) -> Note:  # noqa: D102
        content = frontmatter.load(str(path))
        assert content

        return Note(
            cast(UUID, content.metadata.pop("id", uuid4())),
            note_source,
            path,
            content.metadata,
            content.content,
            None,  # BugBug
            _CalcContentHash(content.content),
        )

    # ----------------------------------------------------------------------
    @override
    def Serialize(self, note: Note) -> None:  # noqa: D102, ARG002
        raise Exception("Not implemented yet")  # noqa: TRY003, EM101


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CalcContentHash(value: str) -> bytes:
    hasher = sha512()

    hasher.update(value.encode("utf-8"))
    return hasher.digest()
