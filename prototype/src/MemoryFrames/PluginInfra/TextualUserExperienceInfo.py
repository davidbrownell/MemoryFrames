from textual.app import App
from textual.containers import Horizontal, Vertical

from MemoryFrames.PluginInfra.UserExperienceInfo import UserExperienceInfo


# ----------------------------------------------------------------------
class TextualUserExperienceInfo(UserExperienceInfo):
    """User experience that leverages Textual for TUI capabilities."""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        app: App,
        hierarchy_container: Vertical,
        notes_container: Horizontal,
    ) -> None:
        super().__init__()

        self.app = app
        self.hierarchy_container = hierarchy_container
        self.notes_container = notes_container
