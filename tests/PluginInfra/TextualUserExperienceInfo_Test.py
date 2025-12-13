from unittest.mock import Mock

from MemoryFrames.PluginInfra.TextualUserExperienceInfo import TextualUserExperienceInfo


# ----------------------------------------------------------------------
def test_Create():
    app = Mock()
    hierarchy_container = Mock()

    tuei = TextualUserExperienceInfo(app, hierarchy_container)

    assert tuei.app is app
    assert tuei.hierarchy_container is hierarchy_container
