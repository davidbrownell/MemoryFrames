from pathlib import Path
from unittest.mock import Mock

from typer.testing import CliRunner

from MemoryFrames.__main__ import app
from MemoryFrames.PluginInfra.Settings import Settings


# ----------------------------------------------------------------------
def test_Standard(monkeypatch):
    settings = _Execute(monkeypatch, [])

    content_dir = Path.cwd()
    assert settings.content_dir == content_dir
    assert settings.content_dir.is_dir(), settings.content_dir

    assert settings.working_dir != content_dir
    assert settings.working_dir.is_dir(), settings.working_dir

    assert settings.verbose is False
    assert settings.debug is False


# ----------------------------------------------------------------------
def test_WorkingDir(monkeypatch):
    settings = _Execute(monkeypatch, ["--working-dir", str(Path.cwd())])

    assert settings.content_dir == Path.cwd()
    assert settings.working_dir == Path.cwd()


# ----------------------------------------------------------------------
def test_Verbose(monkeypatch):
    settings = _Execute(monkeypatch, ["--verbose"])

    assert settings.verbose is True
    assert settings.debug is False


# ----------------------------------------------------------------------
def test_Debug(monkeypatch):
    settings = _Execute(monkeypatch, ["--debug"])

    assert settings.verbose is True
    assert settings.debug is True


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
def _Execute(
    monkeypatch,
    args: list[str],
    executor_name: str = "MemoryFrames.__main__.TextualUserExperience.Execute",
) -> Settings:
    mock = Mock()

    monkeypatch.setattr(executor_name, mock)

    CliRunner().invoke(app, args)

    assert len(mock.mock_calls) == 1
    assert len(mock.mock_calls[0].args) == 1
    return mock.mock_calls[0].args[0]
