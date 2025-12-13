from collections.abc import Callable
from pathlib import Path
from typing import cast

import pluggy

from dbrownell_Common.Types import override

from MemoryFrames import APP_NAME
from MemoryFrames import Settings
from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemHierarchy import FileSystemHierarchy
from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemNoteSource import FileSystemNoteSource
from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemUserExperience import (
    FileSystemUserExperience,
    FileSystemUserExperienceObserver as FileSystemUserExperienceObserverBase,
)
from MemoryFrames.Plugins.FileSystemPluginImpl.TextualFileSystemUserExperience import (
    TextualFileSystemUserExperience,
)
from MemoryFrames.PluginInfra.Hierarchy import Hierarchy, HierarchyBridge
from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
from MemoryFrames.PluginInfra.Plugin import Plugin, ThreadInfo
from MemoryFrames.PluginInfra.TextualUserExperienceInfo import TextualUserExperienceInfo
from MemoryFrames.PluginInfra.UserExperienceInfo import UserExperienceInfo


# ----------------------------------------------------------------------
@pluggy.HookimplMarker(APP_NAME)
def GetPlugin(  # noqa: D103
    root_data_dir: Path,
    all_plugins_settings: dict[str, object],
    user_experience_info: UserExperienceInfo,
) -> Plugin:
    # Get the content directory
    content_dir = all_plugins_settings.get(Settings.CONTENT_DIR_KEY)
    assert isinstance(content_dir, Path), content_dir

    # Get the starting note paths
    previously_displayed_notes = all_plugins_settings.get(Settings.PREVIOUSLY_DISPLAYED_NOTES_KEY) or []
    assert isinstance(previously_displayed_notes, list), previously_displayed_notes
    assert all(isinstance(item, Path) for item in previously_displayed_notes), previously_displayed_notes

    hierarchy_height_percentage = (
        all_plugins_settings.get(Settings.MAX_HIERARCHY_HEIGHT_PERCENTAGE_KEY) or 0.66
    )
    if (
        not isinstance(hierarchy_height_percentage, float)
        or hierarchy_height_percentage < 0.0
        or hierarchy_height_percentage > 1.0
    ):
        msg = f"'{hierarchy_height_percentage}' is not a valid percentage for '{Settings.MAX_HIERARCHY_HEIGHT_PERCENTAGE_KEY}'."
        raise ValueError(msg)

    # Create an observer for the file-system user experience
    plugin: FileSystemPlugin | None = None

    # ----------------------------------------------------------------------
    class FileSystemUserExperienceObserver(FileSystemUserExperienceObserverBase):
        # ----------------------------------------------------------------------
        @override
        def DisplayNote(self, note: Note) -> None:
            assert plugin is not None
            assert plugin.hierarchy is not None

            plugin.hierarchy.bridge.DisplayNote(plugin.hierarchy, note)

    # ----------------------------------------------------------------------

    # Create the file-system specific user experience
    if isinstance(user_experience_info, TextualUserExperienceInfo):
        user_experience = TextualFileSystemUserExperience(
            user_experience_info,
            content_dir,
            FileSystemUserExperienceObserver(),
            hierarchy_height_percentage,
        )
    else:
        msg = "Unrecognized UserExperienceInfo"
        raise TypeError(msg)

    plugin = FileSystemPlugin(root_data_dir, user_experience, previously_displayed_notes)

    return plugin


# ----------------------------------------------------------------------
class FileSystemPlugin(Plugin):
    """Source and navigate notes based on the filesystem hierarchy."""

    # ----------------------------------------------------------------------
    @property
    @override
    def name(self) -> str:  # noqa: D102
        return "File System"

    @property
    @override
    def author(self) -> str:  # noqa: D102
        return "davidbrownell"

    @property
    @override
    def description(self) -> str:  # noqa: D102
        return cast(str, self.__class__.__doc__)

    @property
    @override
    def plugin_priority(self) -> int:  # noqa: D102
        return 10000

    # ----------------------------------------------------------------------
    def __init__(
        self,
        root_data_dir: Path,
        user_experience: FileSystemUserExperience,
        starting_note_paths: list[Path],
    ) -> None:
        super().__init__(root_data_dir)

        self.user_experience = user_experience
        self.starting_note_paths = starting_note_paths

        self.note_source: NoteSource | None = None  # Set in `GetNoteSource`
        self.hierarchy: FileSystemHierarchy | None = None  # Set in `GetHierarchy`

    # ----------------------------------------------------------------------
    @override
    def GetNoteSource(  # noqa: D102
        self,
        observer: NoteSourceObserver,
        enqueue_thread_info_func: Callable[[ThreadInfo], None],
    ) -> NoteSource | None:
        assert self.note_source is None
        self.note_source = FileSystemNoteSource(self, observer, enqueue_thread_info_func)

        return self.note_source

    # ----------------------------------------------------------------------
    @override
    def GetHierarchy(self, bridge: HierarchyBridge) -> Hierarchy | None:  # noqa: D102
        assert self.hierarchy is None
        self.hierarchy = FileSystemHierarchy(self, bridge)

        return self.hierarchy
