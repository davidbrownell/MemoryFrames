from MemoryFrames.Plugins.TagsPlugin import TagsPlugin


# ----------------------------------------------------------------------
def test_Create():
    plugin = TagsPlugin()

    assert plugin.name == "Tags"
    assert plugin.description == "Navigate notes based on tags."
    assert plugin.plugin_priority is None
