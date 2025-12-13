from unittest.mock import Mock

from dbrownell_Common.Types import override

from MemoryFrames.PluginInfra.Plugin import Plugin


# ----------------------------------------------------------------------
class MyPlugin(Plugin):
    # ----------------------------------------------------------------------
    @override
    @property
    def name(self) -> str:
        return "MyPlugin"

    @override
    @property
    def description(self) -> str:
        return "This is a test plugin."


# ----------------------------------------------------------------------
def test_Standard():
    plugin = MyPlugin()

    assert plugin.name == "MyPlugin"
    assert plugin.description == "This is a test plugin."
    assert plugin.plugin_priority is None
    assert plugin.GetHierarchy(Mock()) is None
