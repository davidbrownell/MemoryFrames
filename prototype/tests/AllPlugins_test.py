from MemoryFrames.AllPlugins import *


# ----------------------------------------------------------------------
def test_GetPlugins():
    plugins = GetPlugins({})

    assert [plugin.name for plugin in plugins] == ["File System", "Tags"]
