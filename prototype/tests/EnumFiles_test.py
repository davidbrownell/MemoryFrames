from pathlib import Path

import pytest

from MemoryFrames.EnumFiles import *


# ----------------------------------------------------------------------
@pytest.fixture
def filesystem(fs):
    fs.create_file("/one/two/three/a.txt")
    fs.create_file("/one/two/four/b.txt")
    fs.create_file("/one/five/c.txt")
    fs.create_file("/one/five/six/d.txt")
    fs.create_file("/one/five/seven/e.txt")
    fs.create_file("/one/g.txt")
    fs.create_file("/one/f.txt")
    fs.create_file("/one/h.md")


# ----------------------------------------------------------------------
def test_NoStarting(filesystem):
    assert list(EnumFiles(Path("/one"), {".txt"})) == [
        Path("/one/g.txt"),
        Path("/one/f.txt"),
        Path("/one/two/three/a.txt"),
        Path("/one/two/four/b.txt"),
        Path("/one/five/c.txt"),
        Path("/one/five/six/d.txt"),
        Path("/one/five/seven/e.txt"),
    ]


# ----------------------------------------------------------------------
def test_Starting_one_two(filesystem):
    assert list(
        EnumFiles(
            Path("/one"),
            {".txt"},
            [Path("/one/two")],
        ),
    ) == [
        Path("/one/two/three/a.txt"),
        Path("/one/two/four/b.txt"),
        Path("/one/g.txt"),
        Path("/one/f.txt"),
        Path("/one/five/c.txt"),
        Path("/one/five/six/d.txt"),
        Path("/one/five/seven/e.txt"),
    ]


# ----------------------------------------------------------------------
def test_Starting_one_five(filesystem):
    assert list(
        EnumFiles(
            Path("/one"),
            {".txt"},
            [Path("/one/five")],
        ),
    ) == [
        Path("/one/five/c.txt"),
        Path("/one/five/six/d.txt"),
        Path("/one/five/seven/e.txt"),
        Path("/one/g.txt"),
        Path("/one/f.txt"),
        Path("/one/two/three/a.txt"),
        Path("/one/two/four/b.txt"),
    ]


# ----------------------------------------------------------------------
def test_Starting_on_five_six(filesystem):
    assert list(
        EnumFiles(
            Path("/one"),
            {".txt"},
            [Path("/one/five/six")],
        ),
    ) == [
        Path("/one/five/six/d.txt"),
        Path("/one/five/c.txt"),
        Path("/one/five/seven/e.txt"),
        Path("/one/g.txt"),
        Path("/one/f.txt"),
        Path("/one/two/three/a.txt"),
        Path("/one/two/four/b.txt"),
    ]


# ----------------------------------------------------------------------
def test_NestedStartingDir(filesystem):
    assert list(
        EnumFiles(
            Path("/one"),
            {".txt"},
            [
                Path("/one/five"),
                Path("/one/five/six"),
            ],
        ),
    ) == [
        Path("/one/five/c.txt"),
        Path("/one/five/six/d.txt"),
        Path("/one/five/seven/e.txt"),
        Path("/one/g.txt"),
        Path("/one/f.txt"),
        Path("/one/two/three/a.txt"),
        Path("/one/two/four/b.txt"),
    ]
