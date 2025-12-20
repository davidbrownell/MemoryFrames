from collections.abc import Callable
from pathlib import Path
from threading import Event
from typing import ClassVar
from unittest.mock import Mock

from dbrownell_Common.Types import override

from MemoryFrames.AppState import AppState, AppStateObserver
from MemoryFrames.PluginInfra.NoteSource import NoteSource, NoteSourceObserver
from MemoryFrames.PluginInfra.Plugin import Plugin, ThreadInfo


# ----------------------------------------------------------------------
def test_Initialize():
    plugins = Mock()

    app_state = AppState(plugins)

    assert app_state.plugins is plugins


# ----------------------------------------------------------------------
def test_CreateNoPlugins(monkeypatch):
    # ----------------------------------------------------------------------
    def LoadPlugins(*args, **kwargs) -> list[Plugin]:
        return []

    # ----------------------------------------------------------------------

    monkeypatch.setattr("MemoryFrames.AppState.LoadPlugins", LoadPlugins)

    observer = Mock()

    app_state = AppState.Create(Mock(), Mock(), observer)
    assert app_state is not None

    assert app_state.plugins == []
    assert [arg_list.args[0] for arg_list in observer.OnEvent.call_args_list] == [
        AppStateObserver.EventType.LoadingPlugins,
    ]


# ----------------------------------------------------------------------
def test_CreatePlugin(monkeypatch):
    # ----------------------------------------------------------------------
    def LoadPlugins(*args, **kwargs) -> list[Plugin]:
        return [_CreatePlugin()]

    # ----------------------------------------------------------------------

    monkeypatch.setattr("MemoryFrames.AppState.LoadPlugins", LoadPlugins)

    observer = Mock()

    app_state = AppState.Create(Mock(), Mock(), observer)
    assert app_state is not None

    assert len(app_state.plugins) == 1
    assert app_state.plugins[0].NAME == "TestPlugin"
    assert app_state.plugins[0].AUTHOR == "TestAuthor"
    assert app_state.plugins[0].DESCRIPTION == "TestDescription"
    assert app_state.plugins[0].PLUGIN_PRIORITY == 10

    assert [arg_list.args[0] for arg_list in observer.OnEvent.call_args_list] == [
        AppStateObserver.EventType.LoadingPlugins,
    ]


# ----------------------------------------------------------------------
def test_CreatePluginWithException(monkeypatch):
    # ----------------------------------------------------------------------
    def LoadPlugins(*args, **kwargs) -> list[Plugin]:
        raise Exception("This is the exception")

    # ----------------------------------------------------------------------

    monkeypatch.setattr("MemoryFrames.AppState.LoadPlugins", LoadPlugins)

    observer = Mock()

    app_state = AppState.Create(Mock(), Mock(), observer)
    assert app_state is None
    assert observer.OnException.call_count == 1
    assert str(observer.OnException.call_args.args[0].args[0]) == "This is the exception"


# ----------------------------------------------------------------------
def test_SortPlugins(monkeypatch):
    # ----------------------------------------------------------------------
    def LoadPlugins(*args, **kwargs) -> list[Plugin]:
        return [
            _CreatePlugin(name="PluginA", priority=1),
            _CreatePlugin(name="PluginB", priority=10),
        ]

    # ----------------------------------------------------------------------

    monkeypatch.setattr("MemoryFrames.AppState.LoadPlugins", LoadPlugins)

    app_state = AppState.Create(Mock(), Mock(), Mock())

    assert app_state is not None
    assert len(app_state.plugins) == 2
    assert app_state.plugins[0].NAME == "PluginB"
    assert app_state.plugins[1].NAME == "PluginA"


# ----------------------------------------------------------------------
def test_SortPluginsUsingNames(monkeypatch):
    # ----------------------------------------------------------------------
    def LoadPlugins(*args, **kwargs) -> list[Plugin]:
        return [
            _CreatePlugin(name="PluginA", priority=10),
            _CreatePlugin(name="PluginB", priority=10),
        ]

    # ----------------------------------------------------------------------

    monkeypatch.setattr("MemoryFrames.AppState.LoadPlugins", LoadPlugins)

    app_state = AppState.Create(Mock(), Mock(), Mock())

    assert app_state is not None
    assert len(app_state.plugins) == 2
    assert app_state.plugins[0].NAME == "PluginA"
    assert app_state.plugins[1].NAME == "PluginB"


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _CreatePlugin(
    root_data_dir: Path = Path.cwd(),
    name: str = "TestPlugin",
    author: str = "TestAuthor",
    description: str = "TestDescription",
    priority: int = 10,
) -> Plugin:
    # ----------------------------------------------------------------------
    class TestPlugin(Plugin):
        NAME: ClassVar[str] = name
        AUTHOR: ClassVar[str] = author
        DESCRIPTION: ClassVar[str] = description
        PLUGIN_PRIORITY: ClassVar[int] = priority

    # ----------------------------------------------------------------------

    return TestPlugin(root_data_dir)
