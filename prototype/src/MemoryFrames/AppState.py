from collections.abc import Callable
from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
from threading import Event, Thread

import pluggy

from MemoryFrames import APP_NAME
from MemoryFrames.HierarchyBridge import HierarchyBridge
from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
from MemoryFrames.PluginInfra import Plugin as PluginModule
from MemoryFrames.PluginInfra.Plugin import Plugin, ThreadInfo
from MemoryFrames.PluginInfra.UserExperienceInfo import UserExperienceInfo


# ----------------------------------------------------------------------
class CreateEventType(Enum):
    """Value signalling progress during the creation of an AppState instance."""

    LoadingPlugins = auto()
    LoadingNoteSources = auto()
    LoadingHierarchies = auto()
    StartingThreads = auto()


# ----------------------------------------------------------------------
@dataclass(frozen=True)
class AppState:
    """MemoryFrames application state."""

    # ----------------------------------------------------------------------
    plugins: list[Plugin]

    _note_sources: list[NoteSource]

    _quit_event: Event
    _threads: list[Thread]

    # ----------------------------------------------------------------------
    @classmethod
    def Create(
        cls,
        root_data_dir: Path,
        all_plugins_settings: dict[str, object],
        user_experience_info: UserExperienceInfo,
        hierarchy_bridge: HierarchyBridge,
        status_callback_func: Callable[[CreateEventType], None],
        on_exception_func: Callable[[Exception], None],
    ) -> "AppState":
        """Create an AppState instance."""

        quit_event = Event()
        thread_infos: list[ThreadInfo] = []

        # Load the plugins
        status_callback_func(CreateEventType.LoadingPlugins)
        plugins = cls._CreatePlugins(
            root_data_dir,
            all_plugins_settings,
            user_experience_info,
            on_exception_func,
        )

        # Load the note sources
        status_callback_func(CreateEventType.LoadingNoteSources)
        note_sources, thread_infos = cls._LoadNoteSources(hierarchy_bridge, on_exception_func, plugins)

        # Load the hierarchies
        status_callback_func(CreateEventType.LoadingHierarchies)
        cls._LoadHierarchies(hierarchy_bridge, on_exception_func, plugins)

        # Create the threads
        status_callback_func(CreateEventType.StartingThreads)

        threads: list[Thread] = []

        if thread_infos:
            # ----------------------------------------------------------------------
            def Execute(thread_info: ThreadInfo) -> None:
                try:
                    thread_info.thread_func(quit_event)
                except Exception as ex:
                    msg = f"An error occurred in '{thread_info.description}'."

                    new_ex = Exception(msg)
                    new_ex.__cause__ = ex

                    on_exception_func(new_ex)

            # ----------------------------------------------------------------------

            threads = [Thread(target=Execute, args=(thread_info,)) for thread_info in thread_infos]

            for thread in threads:
                thread.start()

        # Commit the results
        return cls(plugins, note_sources, quit_event, threads)

    # ----------------------------------------------------------------------
    def Stop(self) -> None:
        """Stop all threads."""

        assert not self._quit_event.is_set()
        self._quit_event.set()

        for thread in self._threads:
            thread.join()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    @staticmethod
    def _CreatePlugins(
        root_data_dir: Path,
        all_plugins_settings: dict[str, object],
        user_experience_info: UserExperienceInfo,
        on_exception_func: Callable[[Exception], None],
    ) -> list[Plugin]:
        plugins: list[Plugin] = []

        try:
            plugin_manager = pluggy.PluginManager(APP_NAME)

            plugin_manager.add_hookspecs(PluginModule)
            plugin_manager.load_setuptools_entrypoints(APP_NAME)

            plugins = plugin_manager.hook.GetPlugin(
                root_data_dir=root_data_dir,
                all_plugins_settings=all_plugins_settings,
                user_experience_info=user_experience_info,
            )

            # We want the highest priority plugins first, and then sort by name. We apply the negative so
            # that higher priority values appear first while still maintaining ascending order for names.
            plugins.sort(key=lambda plugin: (-(plugin.plugin_priority or 0), plugin.name))

        except Exception as ex:
            on_exception_func(ex)

        return plugins

    # ----------------------------------------------------------------------
    @staticmethod
    def _LoadNoteSources(
        observer: NoteSourceObserver,
        on_exception_func: Callable[[Exception], None],
        plugins: list[Plugin],
    ) -> tuple[list[NoteSource], list[ThreadInfo]]:
        note_sources: list[NoteSource] = []
        thread_infos: list[ThreadInfo] = []

        # ----------------------------------------------------------------------
        def AddThreadInfo(thread_info: ThreadInfo) -> None:
            thread_infos.append(thread_info)

        # ----------------------------------------------------------------------

        for plugin in plugins:
            try:
                note_source = plugin.GetNoteSource(observer, AddThreadInfo)
                if note_source is not None:
                    note_sources.append(note_source)

            except Exception as ex:  # noqa: PERF203
                msg = f"An error occurred while loading the note source for the plugin '{plugin.name}'."

                new_ex = Exception(msg)
                new_ex.__cause__ = ex

                on_exception_func(new_ex)

        return note_sources, thread_infos

    # ----------------------------------------------------------------------
    @staticmethod
    def _LoadHierarchies(
        hierarchy_bridge: HierarchyBridge,
        on_exception_func: Callable[[Exception], None],
        plugins: list[Plugin],
    ) -> None:
        for plugin in plugins:
            try:
                hierarchy = plugin.GetHierarchy(hierarchy_bridge)
                if hierarchy is not None:
                    hierarchy_bridge.AddHierarchy(hierarchy)

            except Exception as ex:  # noqa: PERF203
                msg = f"An error occurred while loading the hierarchy for the plugin '{plugin.name}'."

                new_ex = Exception(msg)
                new_ex.__cause__ = ex

                on_exception_func(new_ex)
