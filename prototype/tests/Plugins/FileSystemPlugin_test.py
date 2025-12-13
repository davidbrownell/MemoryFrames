from MemoryFrames.Plugins.FileSystemPlugin import FileSystemPlugin


# ----------------------------------------------------------------------
def test_Create():
    plugin = FileSystemPlugin()

    assert plugin.name == "File System"
    assert plugin.description == "Navigate notes based on the filesystem hierarchy."
    assert plugin.plugin_priority == 10000
