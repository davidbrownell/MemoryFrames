from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast, TYPE_CHECKING

from dbrownell_Common.Types import override
from rich.spinner import Spinner
from textual.app import ComposeResult
from textual.containers import Container
from textual.geometry import Size
from textual.widget import Widget
from textual.widgets import Collapsible, Label, Tree

from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemNoteSource import FileSystemNoteSource
from MemoryFrames.Plugins.FileSystemPluginImpl.FileSystemUserExperience import (
    FileSystemUserExperience,
    FileSystemUserExperienceObserver,
)
from MemoryFrames.PluginInfra.Note import Note
from MemoryFrames.PluginInfra.TextualUserExperienceInfo import TextualUserExperienceInfo

if TYPE_CHECKING:
    from textual.timer import Timer


# ----------------------------------------------------------------------
class TextualFileSystemUserExperience(FileSystemUserExperience):
    """Textual-based FileSystem UserExperience."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        user_experience_info: TextualUserExperienceInfo,
        content_dir: Path,
        observer: FileSystemUserExperienceObserver,
        hierarchy_height_percentage: float,
    ) -> None:
        super().__init__(content_dir, observer)

        self._user_experience_info = user_experience_info
        self._hierarchy_height_percentage = hierarchy_height_percentage

        self._root = _DirectoryNode()
        self._tree_widget: _TreeWidget | None = None  # Set in `OnInitializationComplete`

        spinner = Spinner("dots", text="Loading File System content...")
        label = Label(spinner)

        self._container = Container(label)
        self._container.styles.height = "auto"

        collapsible = Collapsible(
            self._container,
            collapsed=False,
            title="File System",
        )  # BugBug: Collapsed should be set based on the previous state

        self._spinner_timer: Timer | None = None

        # ----------------------------------------------------------------------
        def Initialize() -> None:
            # ----------------------------------------------------------------------
            def UpdateSpinner() -> None:
                label.update(spinner)

            # ----------------------------------------------------------------------

            self._spinner_timer = self._user_experience_info.app.set_interval(0.1, UpdateSpinner)
            self._user_experience_info.hierarchy_container.mount(collapsible)

        # ----------------------------------------------------------------------

        self._user_experience_info.app.call_from_thread(Initialize)

    # ----------------------------------------------------------------------
    @override
    def OnInitializationComplete(self) -> None:  # noqa: D102
        # ----------------------------------------------------------------------
        def ReplaceWidgets() -> None:
            # Replace the loading label with the tree widget
            with self._user_experience_info.app.batch_update():
                assert self._spinner_timer is not None
                self._spinner_timer.stop()

                self._container.remove_children()

                # Ensure that we change the size of this container when the size of the tree changes.
                max_lines = self._user_experience_info.app.size.height * self._hierarchy_height_percentage

                # ----------------------------------------------------------------------
                def OnVirtualHeightChanged(new_height: int) -> None:
                    if new_height > max_lines:
                        self._container.styles.height = f"{self._hierarchy_height_percentage * 100}vh"
                    else:
                        self._container.styles.height = new_height

                # ----------------------------------------------------------------------

                self._tree_widget = _TreeWidget(
                    self.content_dir,
                    self._root,
                    OnVirtualHeightChanged,
                    self._OnNoteFocused,
                )

                self._container.mount(self._tree_widget)

        # ----------------------------------------------------------------------

        self._user_experience_info.app.call_from_thread(ReplaceWidgets)

    # ----------------------------------------------------------------------
    @override
    def AddNote(self, note: Note) -> None:  # noqa: D102
        assert isinstance(note.source, FileSystemNoteSource), note.source
        assert isinstance(note.source_data, Path), note.source_data

        path_parts = self._GetRelativePathParts(note.source_data)
        parent_node = self._root

        for path_part_index, path_part in enumerate(path_parts):
            if path_part_index == len(path_parts) - 1:
                # If here, we are looking at the name of the note
                assert path_part not in parent_node.notes, note.source_data
                parent_node.notes[path_part] = note

                return

            # If here, we are looking at the name of a directory
            matching_node = parent_node.directories.get(path_part)

            if matching_node is None:
                parent_node.directories[path_part] = _DirectoryNode()
                matching_node = parent_node.directories[path_part]

            parent_node = matching_node

    # ----------------------------------------------------------------------
    @override
    def SelectNote(self, note: Note) -> None:  # noqa: D102
        assert isinstance(note.source, FileSystemNoteSource), note.source
        assert isinstance(note.source_data, Path), note.source_data

        self._tree_widget.SelectNote(self._GetRelativePathParts(note.source_data))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _GetRelativePathParts(self, fullpath: Path) -> tuple[str, ...]:
        assert fullpath.is_relative_to(self.content_dir), (fullpath, self.content_dir)
        return fullpath.parts[len(self.content_dir.parts) :]

    # ----------------------------------------------------------------------
    def _OnNoteFocused(self, note: Note) -> None:
        self.observer.DisplayNote(note)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _DirectoryNode:
    directories: dict[str, "_DirectoryNode"] = field(default_factory=dict)
    notes: dict[str, Note] = field(default_factory=dict)


# ----------------------------------------------------------------------
class _TreeWidget(Widget):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        content_dir: Path,
        root: _DirectoryNode,
        on_virtual_height_changed_func: Callable[[int], None],
        on_note_focused_func: Callable[[Note], None],
    ) -> None:
        super().__init__()

        self._on_note_focused_func = on_note_focused_func

        self._tree: Tree = Tree(str(content_dir))

        # ----------------------------------------------------------------------
        def OnVirtualHeightChanged(_: Size, new_value: Size) -> None:
            on_virtual_height_changed_func(new_value.height)

        # ----------------------------------------------------------------------

        self.watch(self._tree, "virtual_size", OnVirtualHeightChanged)

        self._tree.styles.padding = 0
        self._tree.root.data = root

        self._tree.root.expand()

    # ----------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield self._tree

    # ----------------------------------------------------------------------
    def on_tree_node_expanded(self, expanded: Tree.NodeExpanded) -> None:
        if isinstance(expanded.node.data, Note):
            return

        # Create a quick data lookup
        tree_children: set[str] = {child.label.plain for child in expanded.node.children}

        # Add any missing nodes
        data = cast(_DirectoryNode, expanded.node.data)

        for dir_name, dir_node in data.directories.items():
            if dir_name in tree_children:
                continue

            expanded.node.add(dir_name, data=dir_node)

        for note_name, note in data.notes.items():
            if note_name in tree_children:
                continue

            expanded.node.add_leaf(note_name, data=note)

    # ----------------------------------------------------------------------
    def on_tree_node_highlighted(self, selected: Tree.NodeHighlighted) -> None:
        if isinstance(selected.node.data, Note):
            self._on_note_focused_func(selected.node.data)

    # ----------------------------------------------------------------------
    def SelectNote(self, path_parts: tuple[str, ...]) -> None:
        parent = self._tree.root

        for path_part in path_parts:
            matching_child = next(
                (child for child in parent.children if child.label.plain == path_part),
                None,
            )

            if matching_child is None:
                return

            parent = matching_child
            parent.expand()

        self._tree.select_node(parent)
