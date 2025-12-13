import os

from pathlib import Path

from typing import Annotated

import typer

from typer.core import TyperGroup

from MemoryFrames import Settings
from MemoryFrames import TextualUserExperience


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):  # noqa: D101
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs) -> list[str]:  # noqa: ARG002, D102
        return list(self.commands.keys())


# ----------------------------------------------------------------------
app = typer.Typer(
    cls=NaturalOrderGrouper,
    help=__doc__,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
)


# ----------------------------------------------------------------------
@app.command("EntryPoint", no_args_is_help=True)
def EntryPoint(
    content_dir: Annotated[
        Path,
        typer.Option(
            "--content-dir",
            exists=True,
            file_okay=False,
            help="Directory containing notes to load.",
            resolve_path=True,
        ),
    ] = Path.cwd(),  # noqa: B008
    verbose: Annotated[  # noqa: ARG001, FBT002
        bool,
        typer.Option("--verbose", help="Write verbose information to the terminal."),
    ] = False,
    debug: Annotated[  # noqa: ARG001, FBT002
        bool,
        typer.Option("--debug", help="Write debug information to the terminal."),
    ] = False,
) -> None:
    """Run MemoryFrames."""

    # Create the data directory
    data_dir = Path.home()

    if os.name == "nt":  # noqa: SIM108
        data_dir = data_dir / "AppData" / "Local"
    else:
        data_dir = data_dir / ".local" / "share"

    data_dir /= "MemoryFrames"

    data_dir.mkdir(parents=True, exist_ok=True)

    # Create the settings used by all plugins
    all_plugins_settings: dict[str, object] = {}

    all_plugins_settings[Settings.CONTENT_DIR_KEY] = content_dir

    # TODO: Read from configuration file
    all_plugins_settings[Settings.MAX_HIERARCHY_HEIGHT_PERCENTAGE_KEY] = 0.66

    TextualUserExperience.Execute(data_dir, all_plugins_settings)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
