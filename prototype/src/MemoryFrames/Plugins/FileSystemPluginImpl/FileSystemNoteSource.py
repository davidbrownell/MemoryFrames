import os

from collections.abc import Callable, Iterator
from pathlib import Path
from threading import Event
from typing import TYPE_CHECKING

from MemoryFrames.Plugins.FileSystemPluginImpl.NoteParser import NoteParser
from MemoryFrames.Plugins.FileSystemPluginImpl.MarkdownNoteParser import MarkdownNoteParser
from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
from MemoryFrames.PluginInfra.Plugin import ThreadInfo

if TYPE_CHECKING:
    from MemoryFrames.Plugins.FileSystemPlugin import FileSystemPlugin


# ----------------------------------------------------------------------
_PARSERS: dict[str, NoteParser] = {parser.file_extension: parser for parser in [MarkdownNoteParser()]}


# ----------------------------------------------------------------------
class FileSystemNoteSource(NoteSource):
    """Note source that provides notes based on the filesystem hierarchy."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        plugin: "FileSystemPlugin",
        observer: NoteSourceObserver,
        enqueue_thread_info_func: Callable[[ThreadInfo], None],
    ) -> None:
        # ----------------------------------------------------------------------
        def InitializeFiles(quit_event: Event) -> None:
            # ----------------------------------------------------------------------
            def EnumFilenames() -> Iterator[Path]:
                supported_extensions = set(_PARSERS.keys())

                for this_root_str, _, filenames in os.walk(plugin.user_experience.content_dir):
                    if quit_event.is_set():
                        return

                    this_root = Path(this_root_str)

                    for filename in filenames:
                        fullpath = this_root / filename

                        if fullpath.suffix in supported_extensions:
                            yield fullpath

            # ----------------------------------------------------------------------

            for note_filename in EnumFilenames():
                note = _PARSERS[note_filename.suffix].Deserialize(self, note_filename)

                observer.OnNewNote(note, is_initializing=True)

            observer.OnInitializationComplete(self)

        # ----------------------------------------------------------------------

        enqueue_thread_info_func(ThreadInfo("Initializing File System", InitializeFiles))
        # TODO: Monitor the file system
