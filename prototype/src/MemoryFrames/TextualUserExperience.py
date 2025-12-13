from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Label, LoadingIndicator

from MemoryFrames import APP_NAME, __version__
from MemoryFrames.AppState import AppState, CreateEventType
from MemoryFrames.HierarchyBridge import HierarchyBridge
from MemoryFrames.PluginInfra.TextualUserExperienceInfo import TextualUserExperienceInfo


# ----------------------------------------------------------------------
def Execute(
    root_data_dir: Path,
    all_plugins_settings: dict[str, object],
) -> None:
    """Return the Textual UI experience for MemoryFrames."""

    _App(root_data_dir, all_plugins_settings).run()


# ----------------------------------------------------------------------
class _App(App):
    CSS_PATH = Path(__file__).with_suffix(".tcss")

    # ----------------------------------------------------------------------
    def __init__(
        self,
        root_data_dir: Path,
        all_plugins_settings: dict[str, object],
    ) -> None:
        super().__init__()

        self._root_data_dir = root_data_dir
        self._all_plugins_settings = all_plugins_settings

        self._user_experience = TextualUserExperienceInfo(
            self.app,
            VerticalScroll(id="hierarchies"),
            Horizontal(id="notes"),
        )

        # The app state is initialized in `on_mount`
        self._app_state: AppState | None = None

        self.title = "Memory Frames"
        assert self.title.replace(" ", "") == APP_NAME, (self.title, APP_NAME)

    # ----------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="viewport"):
            yield self._user_experience.hierarchy_container
            yield self._user_experience.notes_container

        with Horizontal(id="footer"):
            yield Footer()
            yield Label(__version__)

    # ----------------------------------------------------------------------
    def on_mount(self) -> None:
        # ----------------------------------------------------------------------
        def OnLoaded(app_state: AppState | None) -> None:
            if app_state is None:
                return

            assert self._app_state is None
            self._app_state = app_state

        # ----------------------------------------------------------------------

        self.push_screen(
            _LoadingModal(self._root_data_dir, self._all_plugins_settings, self._user_experience),
            OnLoaded,
        )


# ----------------------------------------------------------------------
class _LoadingModal(ModalScreen[AppState]):
    CSS_PATH = Path(__file__).with_suffix(".tcss")

    # ----------------------------------------------------------------------
    def __init__(
        self,
        root_data_dir: Path,
        all_plugins_settings: dict[str, object],
        user_experience_info: TextualUserExperienceInfo,
    ) -> None:
        super().__init__()

        self._root_data_dir = root_data_dir
        self._all_plugins_settings = all_plugins_settings
        self._user_experience_info = user_experience_info

        self._status_label = Label("Loading...")

    # ----------------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield LoadingIndicator()
        yield self._status_label

    # ----------------------------------------------------------------------
    async def on_mount(self) -> None:
        # ----------------------------------------------------------------------
        async def Execute() -> None:
            current_event: CreateEventType | None = None

            # ----------------------------------------------------------------------
            def StatusCallback(event: CreateEventType) -> None:
                nonlocal current_event
                current_event = event

                if event == CreateEventType.LoadingPlugins:
                    msg = "Loading plugins..."
                elif event == CreateEventType.LoadingNoteSources:
                    msg = "Loading note sources..."
                elif event == CreateEventType.LoadingHierarchies:
                    msg = "Loading hierarchies..."
                elif event == CreateEventType.StartingThreads:
                    msg = "Starting threads..."
                else:
                    assert False, event  # noqa: B011, PT015

                self._status_label.content = msg

            # ----------------------------------------------------------------------
            def OnException(ex: Exception) -> None:
                if current_event == CreateEventType.LoadingPlugins:
                    # Display inline
                    print("BugBugA")  # noqa: T201
                else:
                    # Display in status window
                    print("BugBugB")  # noqa: T201

                # BugBug - Begin
                import traceback  # noqa: PLC0415

                traceback.print_exception(ex)
                # BugBug - End

            # ----------------------------------------------------------------------

            app_state = AppState.Create(
                self._root_data_dir,
                self._all_plugins_settings,
                self._user_experience_info,
                HierarchyBridge(),
                StatusCallback,
                OnException,
            )

            # Return the results
            self.app.call_from_thread(lambda: self.dismiss(app_state))

        # ----------------------------------------------------------------------

        self.run_worker(Execute(), thread=True)
