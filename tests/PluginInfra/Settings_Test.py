import textwrap

from pathlib import Path
from unittest.mock import Mock

from MemoryFrames.PluginInfra.Settings import Settings


# ----------------------------------------------------------------------
def test_Create():
    content_dir = Mock()
    working_dir = Mock()
    settings_mock = Mock()
    verbose = Mock()
    debug = Mock()

    settings = Settings(content_dir, working_dir, settings_mock, verbose=verbose, debug=debug)

    assert settings.content_dir is content_dir
    assert settings.working_dir is working_dir
    assert settings.verbose is verbose
    assert settings.debug is debug
    assert settings._settings is settings_mock


# ----------------------------------------------------------------------
def test_DebugOverrideVerbose():
    settings = Settings(Mock(), Mock(), {}, verbose=False, debug=False)

    assert settings.verbose is False
    assert settings.debug is False

    settings = Settings(Mock(), Mock(), {}, verbose=False, debug=True)

    assert settings.verbose is True
    assert settings.debug is True

    settings = Settings(Mock(), Mock(), {}, verbose=True, debug=False)

    assert settings.verbose is True
    assert settings.debug is False

    settings = Settings(Mock(), Mock(), {}, verbose=True, debug=True)

    assert settings.verbose is True
    assert settings.debug is True


# ----------------------------------------------------------------------
def test_DeserializeOrCreate_Create(fs):
    content_dir = Mock()
    working_dir = Path("/working_dir")
    verbose = Mock()
    debug = Mock()

    settings = Settings.DeserializeOrCreate(content_dir, working_dir, verbose=verbose, debug=debug)

    assert settings.content_dir is content_dir
    assert settings.working_dir is working_dir
    assert settings.verbose is verbose
    assert settings.debug is debug
    assert settings._settings == {}


# ----------------------------------------------------------------------
def test_DeserializeOrCreate_Deserialize(fs):
    content_dir = Mock()
    working_dir = Path("/working_dir")

    fs.create_file(
        working_dir / "settings.yaml",
        contents=textwrap.dedent(
            """\
            one:
                two: 2
                three: 3

            four:
                five: 5
                six: 6
            """,
        ),
    )

    settings = Settings.DeserializeOrCreate(content_dir, working_dir, verbose=False, debug=False)

    assert settings.content_dir is content_dir
    assert settings.working_dir is working_dir
    assert settings.verbose is False
    assert settings.debug is False
    assert settings._settings == {
        "one": {"two": 2, "three": 3},
        "four": {"five": 5, "six": 6},
    }


# ----------------------------------------------------------------------
def test_SerializeEmpty(fs):
    content_dir = Mock()
    working_dir = Path("/working_dir")

    fs.create_dir(working_dir)

    settings = Settings(content_dir, working_dir, {}, verbose=False, debug=False)

    settings.Serialize()

    expected_contents = textwrap.dedent(
        """\
        {}
        """,
    )

    settings_filename = working_dir / "settings.yaml"

    assert settings_filename.read_text(encoding="utf-8") == expected_contents


# ----------------------------------------------------------------------
def test_SerializePopulated(fs):
    content_dir = Mock()
    working_dir = Path("/working_dir")

    fs.create_dir(working_dir)

    settings = Settings(content_dir, working_dir, {"one": 1, "two": {"three": 3}}, verbose=False, debug=False)

    settings.Serialize()

    expected_contents = textwrap.dedent(
        """\
        one: 1
        two:
          three: 3
        """,
    )

    settings_filename = working_dir / "settings.yaml"

    assert settings_filename.read_text(encoding="utf-8") == expected_contents


# ----------------------------------------------------------------------
def test_GetPluginSettings():
    # ----------------------------------------------------------------------
    class FakePlugin1:
        AUTHOR = "AuthorName"
        NAME = "PluginName"

    # ----------------------------------------------------------------------
    class FakePlugin2:
        AUTHOR = "DoesNotExist"
        NAME = "DoesNotExist"

    # ----------------------------------------------------------------------

    content_dir = Mock()
    working_dir = Mock()

    settings = Settings(
        content_dir,
        working_dir,
        {
            f"{FakePlugin1.AUTHOR}_{FakePlugin1.NAME}": {"setting1": "value1", "setting2": 2},
        },
        verbose=False,
        debug=False,
    )

    assert settings.GetPluginSettings(FakePlugin1) == {"setting1": "value1", "setting2": 2}
    assert settings.GetPluginSettings(FakePlugin2) == {}
