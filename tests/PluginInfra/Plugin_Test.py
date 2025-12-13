from unittest.mock import Mock
from pathlib import Path

import pytest

from MemoryFrames.PluginInfra.Plugin import ThreadInfo, Plugin


# ----------------------------------------------------------------------
class TestThreadInfo:
    # ----------------------------------------------------------------------
    def test_Create(self):
        description = Mock()
        thread_func = Mock()

        ti = ThreadInfo(description, thread_func)

        assert ti.description is description
        assert ti.thread_func is thread_func


# ----------------------------------------------------------------------
class TestPlugin:
    # ----------------------------------------------------------------------
    def test_Creation(self):
        # ----------------------------------------------------------------------
        class MyPlugin(Plugin):
            @property
            def name(self) -> str:
                return "MyPlugin"

            @property
            def author(self) -> str:
                return "AuthorName"

            @property
            def description(self) -> str:
                return "A description of MyPlugin."

            @property
            def plugin_priority(self) -> int:
                return 10

        # ----------------------------------------------------------------------

        my_plugin = MyPlugin(Path("/tmp"))

        assert my_plugin.name == "MyPlugin"
        assert my_plugin.author == "AuthorName"
        assert my_plugin.description == "A description of MyPlugin."
        assert my_plugin.plugin_priority == 10
        assert my_plugin.unique_name == "AuthorName_MyPlugin"
        assert my_plugin.working_dir == Path("/tmp") / "AuthorName_MyPlugin"
        assert my_plugin.GetNoteSource(Mock(), Mock()) is None

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("invalid_char", ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."])
    def test_ScrubbedDir(self, invalid_char):
        # ----------------------------------------------------------------------
        class MyPlugin(Plugin):
            @property
            def name(self) -> str:
                return f"My{invalid_char}Plugin"

            @property
            def author(self) -> str:
                return f"Author{invalid_char}Name"

            @property
            def description(self) -> str:
                return f"A description of MyPlugin ({invalid_char})."

            @property
            def plugin_priority(self) -> int:
                return 10

        # ----------------------------------------------------------------------

        my_plugin = MyPlugin(Path("/tmp"))

        assert my_plugin.unique_name == f"Author{invalid_char}Name_My{invalid_char}Plugin"
        assert my_plugin.working_dir == Path("/tmp") / "Author_Name_My_Plugin"
