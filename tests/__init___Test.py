import MemoryFrames


# ----------------------------------------------------------------------
def test_AppName():
    assert MemoryFrames.APP_NAME == "MemoryFrames"


# ----------------------------------------------------------------------
def test_Version():
    assert MemoryFrames.__version__
