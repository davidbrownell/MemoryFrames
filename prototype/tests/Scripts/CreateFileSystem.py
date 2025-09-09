# noqa: D100
import random

from pathlib import Path
from typing import Annotated

import typer

from dbrownell_Common.Streams.DoneManager import DoneManager, Flags as DoneManagerFlags
from faker import Faker
from faker_file.providers.txt_file import TxtFileProvider
from faker_file.storages.filesystem import FileSystemStorage
from rich.progress import Progress
from typer.core import TyperGroup


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
@app.command("EntryPoint", no_args_is_help=False)
def EntryPoint(
    num_files: Annotated[
        int,
        typer.Option("--num-files", min=1, help="Number of files to create."),
    ] = 10000,
    root_directory: Annotated[
        Path | None,
        typer.Option(
            "--root-dir",
            file_okay=False,
            resolve_path=True,
            help="Root directory under which to create the file system.",
        ),
    ] = None,
    seed: Annotated[
        int | None,
        typer.Option(
            "--seed",
            min=1,
            help="Random number generator seed.",
        ),
    ] = None,
    verbose: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--verbose", help="Write verbose information to the terminal."),
    ] = False,
    debug: Annotated[  # noqa: FBT002
        bool,
        typer.Option("--debug", help="Write debug information to the terminal."),
    ] = False,
) -> None:
    """Create a random file system to help with performance testing."""

    with DoneManager.CreateCommandLine(
        flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        # Initialize random number generation
        if seed is None:
            seed = random.randint(0, 2**32 - 1)

        random.seed(seed)
        dm.WriteLine(f"Random Seed: {seed}\n\n")

        # Initialize storage and providers
        args: dict[str, object] = {}

        if root_directory is not None:
            args["root_path"] = str(root_directory)

        storage = FileSystemStorage(**args)
        storage.root_path = Path(storage.root_path) / "FakeFileSystem"

        if Path(storage.root_path).exists():
            dm.WriteError(f"'{storage.root_path}' already exists and will not be overwritten.")
            return

        TxtFileProvider.extension = "md"

        # Write the files
        faker = Faker()
        faker.add_provider(TxtFileProvider)

        file_counter = 0

        with dm.YieldStdout():
            with Progress(transient=True) as progress:
                working_dir = Path("")

                task = progress.add_task("Creating Files...", total=num_files)

                while file_counter < num_files:
                    instruction = random.randrange(0, 100)

                    if instruction < 10:
                        # Create a new directory
                        while True:
                            potential_working_dir = working_dir / faker.name()
                            if not (storage.root_path / potential_working_dir).exists():
                                working_dir = potential_working_dir
                                break

                    elif instruction < 30:
                        # Pop a directory
                        if working_dir.parts:
                            working_dir = working_dir.parent

                    else:
                        # Write a file
                        storage.rel_path = str(working_dir)

                        f = faker.txt_file(storage=storage)

                        file_counter += 1
                        progress.update(task, completed=file_counter)

        dm.WriteLine(f"'{storage.root_path}' has been populated.\n\n")


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
