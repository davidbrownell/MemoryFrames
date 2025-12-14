from unittest.mock import Mock
from pathlib import Path
from typing import ClassVar

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
            NAME: ClassVar[str] = "MyPlugin"
            AUTHOR: ClassVar[str] = "AuthorName"
            DESCRIPTION: ClassVar[str] = "A description of MyPlugin."
            PLUGIN_PRIORITY: ClassVar[int] = 10

        # ----------------------------------------------------------------------

        my_plugin = MyPlugin(Path("/tmp"))

        assert my_plugin.NAME == "MyPlugin"
        assert my_plugin.AUTHOR == "AuthorName"
        assert my_plugin.DESCRIPTION == "A description of MyPlugin."
        assert my_plugin.PLUGIN_PRIORITY == 10
        assert my_plugin.unique_name == "AuthorName_MyPlugin"
        assert my_plugin.working_dir == Path("/tmp") / "AuthorName_MyPlugin"
        assert my_plugin.GetNoteSource(Mock(), Mock()) is None

    # ----------------------------------------------------------------------
    @pytest.mark.parametrize("invalid_char", ["<", ">", ":", '"', "/", "\\", "|", "?", "*", "."])
    def test_ScrubbedDir(self, invalid_char):
        # ----------------------------------------------------------------------
        class MyPlugin(Plugin):
            NAME: ClassVar[str] = f"My{invalid_char}Plugin"
            AUTHOR: ClassVar[str] = f"Author{invalid_char}Name"
            DESCRIPTION: ClassVar[str] = f"A description of MyPlugin ({invalid_char})."
            PLUGIN_PRIORITY: ClassVar[int] = 10

        # ----------------------------------------------------------------------

        my_plugin = MyPlugin(Path("/tmp"))

        assert my_plugin.unique_name == f"Author{invalid_char}Name_My{invalid_char}Plugin"
        assert my_plugin.working_dir == Path("/tmp") / "Author_Name_My_Plugin"
